from unittest.mock import patch

import signals.dailyreport as dailyreport
import signals.daylight as daylight
import utilities.utilities as utilities
from intelligence.dailyreport.location_dailyreport_microservice import (
    DAILY_REPORT_ADDRESS,
    MONTHLY_REPORT_ADDRESS,
    WEEKLY_REPORT_ADDRESS,
)
from intelligence.dailyreport.location_dailyreport_summary_microservice import (
    DOMAIN_KEY_SUMMARY_ENABLED,
    VERSION,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestDailyReportSummaryMicroservice:
    def test_dailyreport_summary_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_summary_microservice"
        ]
        assert mut is not None

        # Test default values
        assert mut.version == VERSION

        # Test disabled if Summary Reports organization property disabled
        botengine.organization_properties[DOMAIN_KEY_SUMMARY_ENABLED] = False
        mut._ask_questions(botengine)
        assert mut._is_summary_active(botengine) is False

        botengine.organization_properties[DOMAIN_KEY_SUMMARY_ENABLED] = True
        mut._ask_questions(botengine)
        assert mut._is_summary_active(botengine) is True

    @patch(
        "intelligence.dailyreport.location_dailyreport_summary_microservice.LocationDailyReportSummaryMicroservice._is_active"
    )
    def test_dailyreport_summary_daily_report_status_updated(self, is_active_mock):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        botengine.users = [
            {
                "id": 123,
                "userName": "john.smith@gmail.com",
                "altUsername": "1234567890",
                "firstName": "John",
                "lastName": "Smith",
                "nickname": "Johnny",
                "email": {
                    "email": "john.smith@gmail.com",
                    "verified": True,
                    "status": 0,
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
                    {"daysOfWeek": 127, "startTime": 10800, "endTime": 20800}
                ],
            }
        ]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_summary_microservice"
        ]
        assert mut is not None

        # Enable for further tests
        is_active_mock.return_value = False

        # Test disabled (default)
        mut.daily_report_status_updated(
            botengine,
            {
                "report": {"period": DAILY_REPORT_ADDRESS, "sections": []},
                "status": dailyreport.REPORT_STATUS_COMPLETED,
                "metadata": {},
            },
        )
        # TODO: Assert something...

        # Enable for further tests
        is_active_mock.return_value = True

        # Test no action when created
        mut.daily_report_status_updated(
            botengine,
            {
                "report": {"sections": []},
                "status": dailyreport.REPORT_STATUS_CREATED,
                "metadata": {},
            },
        )
        # TODO: Assert something...

        # Test sms actions for daily reports
        mut.daily_report_status_updated(
            botengine,
            {
                "report": {
                    "period": DAILY_REPORT_ADDRESS,
                    "sections": [
                        {
                            "title": "Wellness",
                            "icon": "heart",
                            "id": "wellness",
                            "items": [
                                {
                                    "id": "trend.care_score.0",
                                    "comment": "Care Score: 50%",
                                    "timestamp_ms": botengine.get_timestamp(),
                                }
                            ],
                        },
                        {
                            "title": "Alerts",
                            "icon": "alarm",
                            "id": "alerts",
                            "items": [
                                {
                                    "id": "falls",
                                    "comment": "0 falls today",
                                    "timestamp_ms": botengine.get_timestamp(),
                                }
                            ],
                        },
                    ],
                },
                "status": dailyreport.REPORT_STATUS_COMPLETED,
                "metadata": {"some": "value"},
            },
        )
        # TODO: Assert something...
        assert len(mut.items_to_notify) > 0

        # Test no actions for weekly / monthly reports
        mut.daily_report_status_updated(
            botengine,
            {
                "report": {"period": WEEKLY_REPORT_ADDRESS, "sections": []},
                "status": dailyreport.REPORT_STATUS_COMPLETED,
                "metadata": {"some": "value"},
            },
        )
        # TODO: Assert something...

        mut.daily_report_status_updated(
            botengine,
            {
                "report": {"period": MONTHLY_REPORT_ADDRESS, "sections": []},
                "status": dailyreport.REPORT_STATUS_COMPLETED,
                "metadata": {"some": "value"},
            },
        )
        # TODO: Assert something...

    @patch(
        "intelligence.dailyreport.location_dailyreport_summary_microservice.LocationDailyReportSummaryMicroservice._is_active"
    )
    @patch(
        "intelligence.dailyreport.location_dailyreport_summary_microservice.LocationDailyReportSummaryMicroservice._get_randomly_weighted_sections"
    )
    @patch("signals.analytics.track")
    def test_dailyreport_summary_daily_report_sms_delivery(
        self, track_mock, get_randomly_weighted_sections_mock, is_active_mock
    ):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Set initial timestamp to 10 PM to enable sunrise timer
        botengine.set_timestamp(botengine.get_timestamp() + utilities.ONE_HOUR_MS * 10)

        # Simplified logging
        # botengine.logging_service_names = ["dailyreport", "daylight"] # Uncomment to see logging

        # Enable daily reports summary services
        is_active_mock.return_value = True
        get_randomly_weighted_sections_mock.return_value = ["alerts", "tasks", "sleep"]

        # Provide users for delivery
        botengine.users = [
            {
                "id": 123,
                "userName": "john.smith@gmail.com",
                "altUsername": "1234567890",
                "firstName": "John",
                "lastName": "Smith",
                "nickname": "Johnny",
                "email": {
                    "email": "john.smith@gmail.com",
                    "verified": True,
                    "status": 0,
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
                    {"daysOfWeek": 127, "startTime": 10800, "endTime": 20800}
                ],
            }
        ]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        # Update coordinates to trigger initialization of the sunrise timer
        location_object.update_coordinates(botengine, "37.7749", "-122.4194")

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_summary_microservice"
        ]
        assert mut is not None

        # Add a new entry to be modified later
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            comment="My Entry",
            identifier="my_entry",
        )

        # Set time to midnight and fire the schedule
        # Use the signal class because there is no timer associated with Midnight
        botengine.set_timestamp(botengine.get_timestamp() + utilities.ONE_HOUR_MS * 2)

        daylight.midnight_fired(botengine, location_object)

        # Check that we've aligned new items for notification
        assert len(mut.items_to_notify) > 0

        # Copy the items to notify for comparison later
        items_to_notify = mut.items_to_notify.copy()
        assert any(
            item["comment"] == "My Entry"
            for item in items_to_notify
            if item.get("id", "") == "my_entry"
        )

        # Add a new entry, to replace the previous days entry with the same identifier
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            comment="My New Entry",
            identifier="my_entry",
        )

        # Check the updated entry is provided during delivery
        def check_items(*args):
            botengine.get_logger("Test dailyreport").info(
                "Side effect called: {}".format(args)
            )
            assert args[0] == botengine
            assert args[1] == location_object
            assert args[2] is not None
            if (
                args[2]
                == "dailyreport_summary_notify_professional_caregivers_delivered"
            ):
                assert args[3] is not None
                assert args[3].get("items_to_notify") is not None
                assert any(
                    item["comment"] == "My New Entry"
                    for item in args[3].get("items_to_notify")
                    if item.get("id", "") == "my_entry"
                )
            else:
                pass

        track_mock.side_effect = check_items
        # Trigger the sunrise event
        # Use the timer so the botengine timestamp gets updated properly
        daylight_microservice = location_object.intelligence_modules[
            "intelligence.daylight.location_daylight_microservice"
        ]
        assert daylight_microservice.is_timer_running(botengine)
        botengine.fire_next_timer_or_alarm(
            daylight_microservice, reference=daylight_microservice.intelligence_id
        )

        # Check that we've aligned new items for notification
        assert mut.items_to_notify is None
