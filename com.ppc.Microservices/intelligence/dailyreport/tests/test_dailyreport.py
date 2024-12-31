
from botengine_pytest import BotEnginePyTest

from locations.location import Location
from devices.gateway.gateway import GatewayDevice
import utilities.utilities as utilities

from intelligence.dailyreport.location_dailyreport_microservice import *

from unittest.mock import patch, MagicMock

class TestDailyReportMicroservice():

    def test_dailyreport_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.deviceless_trends = True
        
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = LocationDailyReportMicroservice(botengine, location_object)

        assert mut is not None
        assert mut.current_report_ms is None
        assert mut.current_weekly_report_ms is None
        assert mut.current_monthly_report_ms is None
        assert mut.started_sleeping_ms is None
        assert mut.last_emailed_report_ms is None
        assert mut.weekly_reports == {}
        assert mut.monthly_reports == {}
        
        # This microservice gets triggered by the location_reminder_microservice during initialization
        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        assert mut is not None
        
        comment = "A task was added: Add People to your Trusted Circle."
        dailyreport.add_entry(botengine, mut.parent, dailyreport.SECTION_ID_TASKS, comment=comment, include_timestamp=True)

        assert mut.current_report_ms == location_object.timezone_aware_datetime_to_unix_timestamp(botengine, location_object.get_midnight_last_night(botengine))
        assert mut.current_weekly_report_ms is None
        assert mut.current_monthly_report_ms is None
        assert mut.started_sleeping_ms is None
        assert mut.last_emailed_report_ms is None
        assert mut.weekly_reports == {}
        assert mut.monthly_reports == {}

        report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                "color": "00AD9D",
                "icon": "clipboard-list-check",
                "id": "tasks",
                "items": [
                    {
                    "comment": "8:06 AM - A task was added: Add People to your Trusted Circle.",
                    "comment_raw": "A task was added: Add People to your Trusted Circle.",
                    "timestamp_ms": 1684076795000,
                    "timestamp_str": "8:06 AM"
                    }
                ],
                "subtitle": "Updated one task today.",
                "title": "Today's Tasks",
                "weight": 10
                }
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT"
        }

        report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms)
        assert report is None

        report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms)
        assert report is None

    @patch('signals.dailyreport.report_status_updated')
    def test_dailyreport_midnight_fired(self, mock_report_status_updated):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684004400000)

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]

        comment = "A task was added: Add People to your Trusted Circle."
        dailyreport.add_entry(botengine, mut.parent, dailyreport.SECTION_ID_TASKS, comment=comment, include_timestamp=True)

        # Delegate should be called 2 times: First completing the previous report, then creating the new report
        status = [dailyreport.REPORT_STATUS_COMPLETED, dailyreport.REPORT_STATUS_CREATED]
        def check_report(*args, status):
            assert args[0] == botengine
            assert args[1] == location_object
            assert args[2] is not None
            if status == dailyreport.REPORT_STATUS_COMPLETED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT COMPLETION: " + str(args[1]) + " " + str(args[2]) + str(status))
            elif status == dailyreport.REPORT_STATUS_CREATED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT: " + str(args[1]) + " " + str(args[2]) + str(status))
            else:
                assert False

        mock_report_status_updated.side_effect = check_report
        midnight_last_night_ms = location_object.timezone_aware_datetime_to_unix_timestamp(botengine, location_object.get_midnight_last_night(botengine))
        assert mut.current_report_ms == midnight_last_night_ms
        assert mut.last_emailed_report_ms == None

        # Midnight fired
        botengine.set_timestamp(1684047600000)
        import signals.daylight as daylight
        daylight.midnight_fired(botengine, location_object)

        assert mut.current_report_ms == botengine.get_timestamp()
        assert mut.last_emailed_report_ms == midnight_last_night_ms

        report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT"
        }

        report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=mut.last_emailed_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1683961200000,
            "period": "dailyreport",
            "sections": [
                {
                "color": "00AD9D",
                "icon": "clipboard-list-check",
                "id": "tasks",
                "items": [
                    {
                    "comment": "12:00 PM - A task was added: Add People to your Trusted Circle.",
                    "comment_raw": "A task was added: Add People to your Trusted Circle.",
                    "timestamp_ms": 1684004400000,
                    "timestamp_str": "12:00 PM"
                    }
                ],
                "subtitle": "Updated one task today.",
                "title": "Today's Tasks",
                "weight": 10
                },
                {
                "color": "946C49",
                "icon": "moon",
                "id": "sleep",
                "items": [
                    {
                    "comment": "12:00 AM Sunday - Hasn't gone to sleep by midnight.",
                    "comment_raw": "Hasn't gone to sleep by midnight.",
                    "timestamp_ms": 1684047600000,
                    "timestamp_str": "12:00 AM Sunday"
                    }
                ],
                "title": "Sleep",
                "weight": 15
                }
            ],
            "subtitle": "Daily Report for Saturday May 13, 2023",
            "title": "RESIDENT AND RESIDENT"
        }