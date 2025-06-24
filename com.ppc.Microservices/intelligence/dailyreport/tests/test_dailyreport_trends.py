from unittest.mock import patch

import properties
import signals.dailyreport as dailyreport
import signals.daylight as daylight
import signals.insights as insights
import utilities.utilities as utilities
from intelligence.dailyreport.location_dailyreport_microservice import (
    DAILY_REPORT_ADDRESS,
    DEFAULT_SECTION_PROPERTIES,
    MONTHLY_REPORT_ADDRESS,
    WEEKLY_REPORT_ADDRESS,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest

import unittest
import pytest

class TestDailyReportTrendsMicroservice(unittest.TestCase):
    @patch(
        "intelligence.dailyreport.location_dailyreport_microservice.LocationDailyReportMicroservice.get_daily_comment"
    )
    def test_dailyreport_capture_trend_data(self, mock_get_daily_comment):
        try:
            import signals.services as services
            import signals.trends as trends
        except ImportError:
            pytest.skip("Module 'signals.services' or 'signals.trends' not available.")
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        botengine.logging_service_names = ["dailyreport"]  # Uncomment to see logging

        mock_get_daily_comment.return_value = "Sleep was just as normal."

        # Initialize the location
        location_object = Location(botengine, 0)
        # TODO: Deprecated deviceless_trends
        location_object.deviceless_trends = True
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        wellness_trend_ids = DEFAULT_SECTION_PROPERTIES[
            dailyreport.SECTION_ID_WELLNESS
        ][dailyreport.SECTION_KEY_TREND_IDS].copy()
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = [
            "trend.sleep_score",
        ]

        trends.capture(
            botengine,
            location_object=location_object,
            trend_id="trend.sleep_duration",
            value=80,
            display_value=lambda x: "{}%".format(int(x)),
            title="Wellness Score",
            comment="This metric assesses historical trends by scoring various lifestyle activities, including sleep, bathroom habits, mobility, stability, and social interactions.",
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
                },
                {
                    "color": "946C49",
                    "description": "Sleep quality and other insightful information.",
                    "icon": "moon",
                    "id": "sleep",
                    "items": [
                        {
                            "comment": "Sleep was just as normal.",
                            "comment_raw": "Sleep was just as normal.",
                            "id": "trend-trend.sleep_duration",
                            "timestamp_ms": 1684076795000,
                        },
                    ],
                    "title": "Sleep",
                    "weight": 15,
                },
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

        assert mut.weekly_reports == {
            "2023_19": {
                "trend-trend.sleep_duration": {
                    "2023_05_14": {
                        "avg": 80.0,
                        "display": "80%",
                        "std": 0.0,
                        "trend_category": "category.summary",
                        "trend_id": "trend.sleep_duration",
                        "updated_ms": 1684076795000,
                        "value": 80.0,
                        "zscore": 0.0,
                    }
                }
            }
        }
        assert mut.monthly_reports == {
            "2023_05": {
                "trend-trend.sleep_duration": {
                    "2023_19": {
                        "avg": 80.0,
                        "display": "80%",
                        "std": 0.0,
                        "trend_category": "category.summary",
                        "trend_id": "trend.sleep_duration",
                        "updated_ms": 1684076795000,
                        "value": 80.0,
                        "zscore": 0.0,
                    }
                }
            }
        }

        assert mut.current_monthly_report_ms is None
        assert mut.current_weekly_report_ms is None

        report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is None
        report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is None
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = wellness_trend_ids

    def test_dailyreport_capture_trend_data_without_extended_reports(self):
        try:
            import signals.trends as trends
            import signals.services as services
        except ImportError:
            pytest.skip("Module 'signals.services' or 'signals.trends' not available.")
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Disable weekly and monthly reports
        botengine.organization_properties["WEEKLY_REPORTS_ENABLED"] = False
        botengine.organization_properties["MONTHLY_REPORTS_ENABLED"] = False

        # Initialize the location
        location_object = Location(botengine, 0)
        # TODO: Deprecated deviceless_trends
        location_object.deviceless_trends = True
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

        wellness_trend_ids = DEFAULT_SECTION_PROPERTIES[
            dailyreport.SECTION_ID_WELLNESS
        ][dailyreport.SECTION_KEY_TREND_IDS].copy()
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = [
            "trend.sleep_score",
        ]
        trends.capture(
            botengine,
            location_object=location_object,
            trend_id="trend.sleep_duration",
            value=80,
            display_value=lambda x: "{}%".format(int(x)),
            title="Wellness Score",
            comment="This metric assesses historical trends by scoring various lifestyle activities, including sleep, bathroom habits, mobility, stability, and social interactions.",
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

        report = botengine.get_state(
            DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is not None

        assert mut.weekly_reports == {}
        assert mut.monthly_reports == {}

        assert mut.current_monthly_report_ms is None
        assert mut.current_weekly_report_ms is None

        report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is None
        report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms
        )
        assert report is None
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = wellness_trend_ids

    @patch("signals.dailyreport.report_status_updated")
    def test_dailyreport_weekly(self, mock_report_status_updated):
        try:
            import signals.trends as trends
            import signals.services as services
        except ImportError:
            pytest.skip("Module 'signals.services' or 'signals.trends' not available.")
        first_day_of_week_ms = 1685343600000
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(
            first_day_of_week_ms - utilities.ONE_DAY_MS * 6 + utilities.ONE_HOUR_MS * 12
        )  # 6 days before the end of the month at noon

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.deviceless_trends = True

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        wellness_trend_ids = DEFAULT_SECTION_PROPERTIES[
            dailyreport.SECTION_ID_WELLNESS
        ][dailyreport.SECTION_KEY_TREND_IDS].copy()
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = [
            "trend.sleep_score",
        ]
        report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms
        )
        assert report is None

        # Capture 7 days of sleep trends
        for i in range(6):
            values = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
            trends.capture(
                botengine,
                location_object=location_object,
                trend_id="trend.sleep_score",
                value=int(values[i] * 100.0),
                display_value="{}% sleep score".format(int(values[i] * 100.0)),
                title="Sleep Score",
                comment="Relative sleep quality score.",
                icon="snooze",
                units="%",
                window=30,
                once=True,
                trend_category=trends.TREND_CATEGORY_SLEEP,
                related_services=[services.SERVICE_KEY_BEDTIME],
                min_value=0,
                max_value=100,
            )

            assert mut.weekly_reports != {}
            assert mut.monthly_reports != {}

            botengine.set_timestamp(botengine.get_timestamp() + utilities.ONE_DAY_MS)

        # Midnight fired
        botengine.set_timestamp(first_day_of_week_ms)

        def check_report(*args, status, metadata=None):
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
                    + str(metadata)
                )
            elif status == dailyreport.REPORT_STATUS_CREATED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "CHECK REPORT: "
                    + str(args[1])
                    + " "
                    + str(args[2])
                    + str(status)
                    + str(metadata)
                )
            else:
                assert False

        mock_report_status_updated.side_effect = check_report

        daylight.midnight_fired(botengine, location_object)

        report = botengine.get_state(
            WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1685343600000,
            "period": "weeklyreport",
            "sections": [
                {
                    "color": "F47174",
                    "icon": "heart",
                    "description": "Overall physical and mental health status.",
                    "id": "wellness",
                    "items": [
                        {
                            "comment": "Sleep Score - 30% sleep score",
                            "comment_raw": "Sleep Score - 30% sleep score",
                            "id": "trend-trend.sleep_score",
                            "timestamp_ms": 1685343600000,
                        }
                    ],
                    "title": "People Power Family Wellness",
                    "weight": -5,
                }
            ],
            "subtitle": "Weekly Report for Monday May 29, 2023",
            "title": "RESIDENT AND RESIDENT",
        }

        assert mut.weekly_reports == {
            "2023_21": {
                "trend-trend.sleep_score": {
                    "2023_05_23": {
                        "avg": 80.0,
                        "display": "80% sleep score",
                        "std": 0.0,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1684868400000,
                        "value": 80.0,
                        "zscore": 0.0,
                    },
                    "2023_05_24": {
                        "avg": 75.0,
                        "display": "70% sleep score",
                        "std": 7.07,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1684954800000,
                        "value": 70.0,
                        "zscore": -0.71,
                    },
                    "2023_05_25": {
                        "avg": 70.0,
                        "display": "60% sleep score",
                        "std": 10.0,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685041200000,
                        "value": 60.0,
                        "zscore": -1.0,
                    },
                    "2023_05_26": {
                        "avg": 65.0,
                        "display": "50% sleep score",
                        "std": 12.91,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685127600000,
                        "value": 50.0,
                        "zscore": -1.16,
                    },
                    "2023_05_27": {
                        "avg": 60.0,
                        "display": "40% sleep score",
                        "std": 15.81,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685214000000,
                        "value": 40.0,
                        "zscore": -1.27,
                    },
                    "2023_05_28": {
                        "avg": 55.0,
                        "display": "30% sleep score",
                        "std": 18.71,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685300400000,
                        "value": 30.0,
                        "zscore": -1.34,
                    },
                }
            }
        }
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = wellness_trend_ids

    def test_dailyreport_entries(self):
        try:
            import signals.trends as trends
            import signals.services as services
        except ImportError:
            pytest.skip("Module 'signals.services' or 'signals.trends' not available.")
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.deviceless_trends = True
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[  # noqa: F841
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]

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
