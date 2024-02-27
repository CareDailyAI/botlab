
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities
import signals.dailyreport as dailyreport

from intelligence.dailyreport.location_dailyreport_microservice import *
from intelligence.dailyreport.location_dailyreport_summary_microservice import *

from unittest.mock import patch, MagicMock

class TestDailyReportSummaryMicroservice():

    def test_dailyreport_summary_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_summary_microservice"]
        assert mut is not None

        # Test default values
        assert mut.version == VERSION
    
        # Test disabled if Summary Reports organization property disabled
        botengine.organization_properties[DOMAIN_KEY_SUMMARY_ENABLED] = False
        mut._ask_questions(botengine)
        assert mut._is_active(botengine) is False

        botengine.organization_properties[DOMAIN_KEY_SUMMARY_ENABLED] = True
        mut._ask_questions(botengine)
        assert mut._is_active(botengine) is True

    @patch('intelligence.dailyreport.location_dailyreport_summary_microservice.LocationDailyReportSummaryMicroservice._is_active')
    def test_dailyreport_summary_daily_report_status_updated(self, is_active_mock):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        botengine.users = [{
            "id": 123,
            "userName": "john.smith@gmail.com",
            "altUsername": "1234567890",
            "firstName": "John",
            "lastName": "Smith",
            "nickname": "Johnny",
            "email": {
                "email": "john.smith@gmail.com",
                "verified": True,
                "status": 0
            },
            "phone": "1234567890",
            "phoneType": 1,
            "smsStatus": 1,
            "locationAccess": 10,
            "temporary": True,
            "accessEndDate": "2019-01-29T02:45:30Z",
            "accessEndDateMs": 1548747995000,
            "category": 1,
            "role": 4,
            "smsPhone": "1234567890",
            "language": "en",
            "avatarFileId": 123,
            "schedules": [
                {
                    "daysOfWeek": 127,
                    "startTime": 10800,
                    "endTime": 20800
                }
            ]
        }]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_summary_microservice"]
        assert mut is not None

        # Enable for further tests
        is_active_mock.return_value = False

        # Test disabled (default)
        mut.daily_report_status_updated(botengine, {"report": {"period": DAILY_REPORT_ADDRESS, "sections": []}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {}})
        # TODO: Assert something...

        # Enable for further tests
        is_active_mock.return_value = True

        # Test no action when created
        mut.daily_report_status_updated(botengine, {"report": {"sections": []}, "status": dailyreport.REPORT_STATUS_CREATED, "metadata": {}})
        # TODO: Assert something...

        # Test sms actions for daily reports
        mut.daily_report_status_updated(botengine, {"report": {"period": DAILY_REPORT_ADDRESS, "sections": [{"title": "Wellness", "icon": "heart", "id": "wellness", "items": [{"id": "trend.care_score.0", "comment": "Care Score: 50%"}]},{"title": "Alerts", "icon": "alarm", "id": "alerts", "items": [{"id": "falls", "comment": "0 falls today"}]}]}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {"some": "value"}})
        # TODO: Assert something...
        assert len(mut.items_to_notify) > 0

        # Test no actions for weekly / monthly reports
        mut.daily_report_status_updated(botengine, {"report": {"period": WEEKLY_REPORT_ADDRESS, "sections": []}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {"some": "value"}})
        # TODO: Assert something...

        mut.daily_report_status_updated(botengine, {"report": {"period": MONTHLY_REPORT_ADDRESS, "sections": []}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {"some": "value"}})
        # TODO: Assert something...