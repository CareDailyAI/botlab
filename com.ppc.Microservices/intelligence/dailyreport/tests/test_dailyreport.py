import unittest
from unittest.mock import patch

import properties
import signals.dailyreport as dailyreport
import signals.daylight as daylight
import utilities.utilities as utilities
from intelligence.dailyreport.location_dailyreport_microservice import (
    DAILY_REPORT_ADDRESS,
    DEFAULT_SECTION_PROPERTIES,
    LocationDailyReportMicroservice,
    MONTHLY_REPORT_ADDRESS,
    WEEKLY_REPORT_ADDRESS,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest
import pytest

class TestDailyReportMicroservice(unittest.TestCase):
    def test_dailyreport_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        # TODO: Deprecated deviceless_trends
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
        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        assert mut is not None

        # comment = "A task was added: Add People to your Trusted Circle."
        # dailyreport.add_entry(botengine, mut.parent, dailyreport.SECTION_ID_TASKS, comment=comment, include_timestamp=True)

        assert (
            mut.current_report_ms
            == location_object.timezone_aware_datetime_to_unix_timestamp(
                botengine, location_object.get_midnight_last_night(botengine)
            )
        )
        assert mut.current_weekly_report_ms is None
        assert mut.current_monthly_report_ms is None
        assert mut.started_sleeping_ms is None
        assert mut.last_emailed_report_ms is None
        assert mut.weekly_reports == {}
        assert mut.monthly_reports == {}

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                    "color": "00AD9D",
                    "icon": "clipboard-list-check",
                    "description": "List of to-do items scheduled for today.",
                    "id": "tasks",
                    "items": [
                        {
                            "comment": "8:06 AM - A task was added: Add People to your Trusted Circle.",
                            "comment_raw": "A task was added: Add People to your Trusted Circle.",
                            "timestamp_ms": 1684076795000,
                            "timestamp_str": "8:06 AM",
                        }
                    ],
                    "subtitle": "Updated one task today.",
                    "title": "Today's Tasks",
                    "weight": 10,
                }
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

        report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms
        )
        assert report is None

        report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms
        )
        assert report is None

    @patch("signals.dailyreport.report_status_updated")
    def test_dailyreport_midnight_fired(self, mock_report_status_updated):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684004400000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        # comment = "A task was added: Add People to your Trusted Circle."
        # dailyreport.add_entry(botengine, mut.parent, dailyreport.SECTION_ID_TASKS, comment=comment, include_timestamp=True)

        def check_report(*args, status):
            assert args[0] == botengine
            assert args[1] == location_object
            assert args[2] is not None
            if status == dailyreport.REPORT_STATUS_COMPLETED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "CHECK REPORT COMPLETION: "
                    + str(args[1])
                    + " "
                    + str(args[2])
                    + str(status)
                )
            elif status == dailyreport.REPORT_STATUS_CREATED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "CHECK REPORT: " + str(args[1]) + " " + str(args[2]) + str(status)
                )
            else:
                assert False

        mock_report_status_updated.side_effect = check_report
        midnight_last_night_ms = (
            location_object.timezone_aware_datetime_to_unix_timestamp(
                botengine, location_object.get_midnight_last_night(botengine)
            )
        )
        assert mut.current_report_ms == midnight_last_night_ms
        assert mut.last_emailed_report_ms is None

        # Midnight fired
        botengine.set_timestamp(1684047600000)

        daylight.midnight_fired(botengine, location_object)

        assert mut.current_report_ms == botengine.get_timestamp()
        assert mut.last_emailed_report_ms == midnight_last_night_ms

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.last_emailed_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1683961200000,
            "period": "dailyreport",
            "sections": [
                {
                    "color": "00AD9D",
                    "icon": "clipboard-list-check",
                    "description": "List of to-do items scheduled for today.",
                    "id": "tasks",
                    "items": [
                        {
                            "comment": "12:00 PM - A task was added: Add People to your Trusted Circle.",
                            "comment_raw": "A task was added: Add People to your Trusted Circle.",
                            "timestamp_ms": 1684004400000,
                            "timestamp_str": "12:00 PM",
                        }
                    ],
                    "subtitle": "Updated one task today.",
                    "title": "Today's Tasks",
                    "weight": 10,
                },
                {
                    "color": "946C49",
                    "description": "Sleep quality and other insightful information.",
                    "icon": "moon",
                    "id": "sleep",
                    "items": [
                        {
                            "comment": "12:00 AM Sunday - Hasn't gone to sleep by midnight.",
                            "comment_raw": "Hasn't gone to sleep by midnight.",
                            "timestamp_ms": 1684047600000,
                            "timestamp_str": "12:00 AM Sunday",
                        }
                    ],
                    "title": "Sleep",
                    "weight": 15,
                },
            ],
            "subtitle": "Daily Report for Saturday May 13, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

    def test_dailyreport_report_key(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        date_keys = {
            # January 1, 2023 Midnight Pacific Time
            1672560000000: {
                DAILY_REPORT_ADDRESS: "2023_01_01",
                WEEKLY_REPORT_ADDRESS: "2022_52",  # Note: January 1, 2023 falls in the last week of the 2022 gregorian calendar.
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 2, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 1: {
                DAILY_REPORT_ADDRESS: "2023_01_02",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 3, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 2: {
                DAILY_REPORT_ADDRESS: "2023_01_03",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 4, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 3: {
                DAILY_REPORT_ADDRESS: "2023_01_04",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 5, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 4: {
                DAILY_REPORT_ADDRESS: "2023_01_05",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 6, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 5: {
                DAILY_REPORT_ADDRESS: "2023_01_06",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 7, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 6: {
                DAILY_REPORT_ADDRESS: "2023_01_07",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 8, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 7: {
                DAILY_REPORT_ADDRESS: "2023_01_08",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # January 9, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 8: {
                DAILY_REPORT_ADDRESS: "2023_01_09",
                WEEKLY_REPORT_ADDRESS: "2023_02",
                MONTHLY_REPORT_ADDRESS: "2023_01",
            },
            # December 21, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 0: {
                DAILY_REPORT_ADDRESS: "2023_12_21",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 22, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 1: {
                DAILY_REPORT_ADDRESS: "2023_12_22",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 23, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 2: {
                DAILY_REPORT_ADDRESS: "2023_12_23",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 24, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 3: {
                DAILY_REPORT_ADDRESS: "2023_12_24",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 25, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 4: {
                DAILY_REPORT_ADDRESS: "2023_12_25",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 26, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 5: {
                DAILY_REPORT_ADDRESS: "2023_12_26",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 27, 2023 Midnight Pacific Time :)
            1703145600000 + utilities.ONE_DAY_MS * 6: {
                DAILY_REPORT_ADDRESS: "2023_12_27",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 28, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 7: {
                DAILY_REPORT_ADDRESS: "2023_12_28",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 29, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 8: {
                DAILY_REPORT_ADDRESS: "2023_12_29",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 30, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 9: {
                DAILY_REPORT_ADDRESS: "2023_12_30",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # December 31, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 10: {
                DAILY_REPORT_ADDRESS: "2023_12_31",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12",
            },
            # January 1, 2024 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 11: {
                DAILY_REPORT_ADDRESS: "2024_01_01",
                WEEKLY_REPORT_ADDRESS: "2024_01",
                MONTHLY_REPORT_ADDRESS: "2024_01",
            },
        }

        for timestamp in date_keys.keys():
            botengine.set_timestamp(timestamp)

            date = location_object.get_local_datetime(botengine)
            for address in date_keys[timestamp].keys():
                assert (
                    mut._report_key(botengine, report_address=address, date=date)
                    == date_keys[timestamp][address]
                ), "{} {} malformed".format(timestamp, address)

        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.deviceless_trends = True
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        import signals.insights as insights
        try:
            import signals.trends as trends
        except ImportError:
            pytest.skip("Trends module not available, skipping test.")

        for section in DEFAULT_SECTION_PROPERTIES.keys():
            for trend_id in DEFAULT_SECTION_PROPERTIES[section][
                dailyreport.SECTION_KEY_TREND_IDS
            ]:
                trends.capture(
                    botengine,
                    location_object=location_object,
                    trend_id=trend_id,
                    value=0.0,
                    display_value=0.0,
                    title="Test",
                    comment="Test",
                    icon="",
                    units="",
                    window=15,
                    once=True,
                    trend_category=trends.TREND_CATEGORY_OTHER,
                    operation=trends.OPERATION_TYPE_INSTANTANEOUS,
                    related_services=[],
                    timestamp_override_ms=None,
                )
            for insight_id in DEFAULT_SECTION_PROPERTIES[section][
                dailyreport.SECTION_KEY_INSIGHT_IDS
            ]:
                insights.capture_insight(
                    botengine,
                    location_object=location_object,
                    insight_id=insight_id,
                    value=0.0,
                    title="Test",
                    description="Test is 0.0",
                    device_object=None,
                )

        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_TASKS,
            comment="A task was added: {}".format("Test"),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_TASKS,
            comment="{} added a task: {}".format("User", "Test"),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_TASKS,
            comment="A task was assigned to {}: {}".format("User", "Test"),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_TASKS,
            comment="{} will take on a new task: {}".format("User", "Test"),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_TASKS,
            comment="{} assigned a task to {}: {}".format("User", "User2", "Test"),
        )

        # dailyreport.add_entry(botengine,location_object,dailyreport.SECTION_ID_TASKS,description,None,None,True)
        # dailyreport.add_entry(botengine,location_object,dailyreport.SECTION_ID_WELLNESS,response,subtitle,"gpt_report_{}".format(period),None)
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "Missed evening medication",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "May have missed morning medication because we woke up late.",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "May have missed morning medication.",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "May have missed lunchtime medication.",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "May have missed afternoon medication.",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "1 bathroom visit last night.",
            None,
            None,
            None,
        )

        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Woke up after {} hours.".format(8.2),
            "Occupant slept about 8.2 hours last night",
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "{}% sleep score last night.".format(75),
            None,
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Summary: Seems to be sleeping longer than usual, and with a higher number of bathroom visits last night.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Summary: Seems to have gotten more sleep than usual last night.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Summary: Seems to be sleeping less than usual, and with a higher number of bathroom visits last night.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Summary: Seems to have gotten less sleep than usual last night.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Summary: Did not sleep well last night.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            "Recommend going to bed at a more consistent time.",
            None,
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_BATHROOM,
            "Bathroom visited.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "Took a shower.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Left home once today",
            None,
            "Away count",
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Left home once today",
            None,
            "Away count",
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Hasn't left the home today.",
            None,
            "Away count",
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            None,
            None,
            "Away count",
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            None,
            None,
            "sleep_prediction",
            None,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Optimal time to go to sleep is around {} tonight.".format("08:20PM"),
            None,
            "sleep_prediction",
            None,
            (botengine.get_timestamp() + utilities.ONE_SECOND_MS * 10),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "Medication button pressed.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            "Assist button pressed",
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            "Security Alarm",
            "The wired security system triggered an alarm.",
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "Medication sensor moved.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_BATHROOM,
            "Toilet flushed.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            "Assist button pressed",
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "'{}' powered on.".format("My home"),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Took a nap in bed for {}.".format(10),
            None,
            None,
            True,
            botengine.get_timestamp(),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEDICATION,
            "Opened.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEALS,
            "'{}' opened.".format("My home"),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "'{}' powered on.".format("My home"),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEALS,
            "Made coffee.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ALERTS,
            "Keypad SOS pressed",
            "Someone pressed and held the SOS button on the keypad.",
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_MEALS,
            "Microwave cooked something for {} minutes.".format(10),
            None,
            None,
            True,
            botengine.get_timestamp(),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "Came back home after {} hours.".format(10),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "Came back home after {} minutes.".format(10),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "Came back home immediately.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_ACTIVITIES,
            "Left the home.",
            None,
            None,
            True,
            botengine.get_timestamp(),
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Might have gone to sleep. {} is still learning your sleep patterns.".format(
                properties.get_property(botengine, "SERVICE_NAME")
            ),
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Went to sleep.",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Hopefully enjoying a vacation.",
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "{} reached out on {}.".format("Member", "Thursday"),
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Didn't remind anyone to reach out today because there aren't enough people. Please add more friends and family in the Trusted Circle tab of your {} app.".format(
                properties.get_property(botengine, "SERVICE_NAME")
            ),
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Didn't remind anyone to reach out today because everyone already reached out recently. Please add more friends and family in the Trusted Circle tab of your {} app.".format(
                properties.get_property(botengine, "SERVICE_NAME")
            ),
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            "Today is {}'s day to reach out.".format("John Doe"),
            None,
            None,
            False,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SOCIAL,
            None,
            "Add friends and family in the Trusted Circle tab.",
            None,
            None,
        )

    def test_dailyreport_config(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging
        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)
        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        import json

        default_section_properties = json.loads(json.dumps(DEFAULT_SECTION_PROPERTIES))
        # Test default config
        section_config = {
            dailyreport.SECTION_ID_SLEEP: {  # Updated
                dailyreport.SECTION_KEY_WEIGHT: 15,
                dailyreport.SECTION_KEY_TITLE: "Sleep Analysis",
                dailyreport.SECTION_KEY_DESCRIPTION: "Analyze sleep patterns and quality.",
                dailyreport.SECTION_KEY_ICON: "moon",
                dailyreport.SECTION_KEY_COLOR: "946C49",
                dailyreport.SECTION_KEY_TREND_IDS: ["trend.mobility_rooms"],
                dailyreport.SECTION_KEY_INSIGHT_IDS: ["my_insight"],
            },
            dailyreport.SECTION_ID_WELLNESS: {},  # Removed
            "habits": {  # Added
                dailyreport.SECTION_KEY_TITLE: "Habits"
            },
        }
        dailyreport.set_section_config(botengine, location_object, section_config)

        daily_report_state = botengine.get_state(DAILY_REPORT_ADDRESS)
        assert "section_config" in daily_report_state
        assert daily_report_state["section_config"] == section_config

        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_weekly_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_monthly_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_SLEEP,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_WELLNESS,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_weekly_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_WELLNESS,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_monthly_entry(
            botengine,
            location_object,
            dailyreport.SECTION_ID_WELLNESS,
            "Test",
            None,
            None,
            True,
        )
        dailyreport.add_entry(
            botengine, location_object, "habits", "Test", None, None, True
        )
        dailyreport.add_weekly_entry(
            botengine, location_object, "habits", "Test", None, None, True
        )
        dailyreport.add_monthly_entry(
            botengine, location_object, "habits", "Test", None, None, True
        )

        try:
            import signals.trends as trends
        except ImportError:
            pytest.skip("Trends module not available, skipping test.")

        trends.capture(
            botengine,
            location_object=location_object,
            trend_id="trend.mobility_rooms",
            value=1,
            display_value=lambda x: "{}%".format(int(x)),
            title="My Trend",
            comment="My test trend",
            icon="star",
            units="%",
            window=30,
            once=False,
            trend_category=trends.TREND_CATEGORY_SUMMARY,
            operation=trends.OPERATION_TYPE_INSTANTANEOUS,
            related_services=None,
            min_value=0,
            max_value=100,
        )

        import signals.insights as insights

        insights.capture_insight(
            botengine,
            location_object=location_object,
            insight_id="my_insight",
            value=0.0,
            title="Test",
            description="Test is 0.0",
            device_object=None,
        )

        daily_report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        weekly_report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms
        )
        monthly_report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms
        )
        for report in [daily_report, weekly_report, monthly_report]:
            assert report is not None
            assert dailyreport.SECTION_ID_SLEEP in [
                section["id"] for section in report["sections"]
            ]
            assert dailyreport.SECTION_ID_WELLNESS not in [
                section["id"] for section in report["sections"]
            ]
            assert "habits" in [section["id"] for section in report["sections"]]
            for section in report["sections"]:
                if section["id"] == dailyreport.SECTION_ID_SLEEP:
                    assert (
                        section[dailyreport.SECTION_KEY_WEIGHT]
                        == section_config[dailyreport.SECTION_ID_SLEEP][
                            dailyreport.SECTION_KEY_WEIGHT
                        ]
                    )
                    assert (
                        section[dailyreport.SECTION_KEY_TITLE]
                        == section_config[dailyreport.SECTION_ID_SLEEP][
                            dailyreport.SECTION_KEY_TITLE
                        ]
                    )
                    assert (
                        section[dailyreport.SECTION_KEY_DESCRIPTION]
                        == section_config[dailyreport.SECTION_ID_SLEEP][
                            dailyreport.SECTION_KEY_DESCRIPTION
                        ]
                    )
                    assert (
                        section[dailyreport.SECTION_KEY_ICON]
                        == section_config[dailyreport.SECTION_ID_SLEEP][
                            dailyreport.SECTION_KEY_ICON
                        ]
                    )
                    assert (
                        section[dailyreport.SECTION_KEY_COLOR]
                        == section_config[dailyreport.SECTION_ID_SLEEP][
                            dailyreport.SECTION_KEY_COLOR
                        ]
                    )
                    if report["period"] == "dailyreport":
                        assert "trend-{}".format(
                            section_config[dailyreport.SECTION_ID_SLEEP][
                                dailyreport.SECTION_KEY_TREND_IDS
                            ][0]
                        ) in [item.get("id", None) for item in section["items"]]
                        assert "insight-{}".format(
                            section_config[dailyreport.SECTION_ID_SLEEP][
                                dailyreport.SECTION_KEY_INSIGHT_IDS
                            ][0]
                        ) in [item.get("id", None) for item in section["items"]]

                if section["id"] == "habits":
                    assert section["title"] == "Habits"

        for section_id in default_section_properties:
            DEFAULT_SECTION_PROPERTIES[section_id] = default_section_properties[
                section_id
            ]
