import unittest
from unittest.mock import patch

import signals.dailyreport as dailyreport
import utilities.utilities as utilities
from intelligence.dailyreport.location_dailyreport_microservice import (
    DEFAULT_SECTION_PROPERTIES,
    MONTHLY_REPORT_ADDRESS,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest
import pytest

class TestDailyReportSurveyMicroservice(unittest.TestCase):
    @patch("signals.dailyreport.report_status_updated")
    def test_dailyreport_survey_monthly(self, mock_report_status_updated):
        last_day_of_month_ms = 1685516400000
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        # botengine.logging_service_names = ["dailyreport"]
        botengine.set_timestamp(
            last_day_of_month_ms
            - (utilities.ONE_DAY_MS * 7 * 4)
            + utilities.ONE_HOUR_MS * 12
        )  # 4 weeks before the end of the month at noon

        # botengine.logging_service_names = ["dailyreport"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.dailyreport.location_dailyreport_microservice"
        ]
        wellness_trend_ids = DEFAULT_SECTION_PROPERTIES[
            dailyreport.SECTION_ID_WELLNESS
        ][dailyreport.SECTION_KEY_TREND_IDS]
        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = [
            "trend.care_score",
            "trend.illbeing_score",
            "trend.positivity_score",
            "trend.sleep_diary",
            "trend.percieved_stress_scale",
        ]
        report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms
        )
        assert report is None

        survey_microservice = location_object.intelligence_modules.get("intelligence.surveys.location_survey_microservice")

        if survey_microservice is None:
            pytest.skip("Survey microservice not available in this test environment.")

        survey_microservice.ask_question(botengine)
        from intelligence.surveys.location_survey_microservice import (
            CARE_QUESTIONS,
            SERVICE_KEY_SURVEY_DAY,
            SERVICE_KEY_SURVEY_TIME,
            SURVEY_RESULTS_STATE_VARIABLE,
            SURVEY_STATISTICS_STATE_VARIABLE,
        )

        survey_day_question_object = botengine.retrieve_question(SERVICE_KEY_SURVEY_DAY)
        survey_time_question_object = botengine.retrieve_question(
            SERVICE_KEY_SURVEY_TIME
        )

        survey_day_question_object.default_answer = "0"
        survey_time_question_object.default_answer = "12.0"

        survey_microservice.question_answered(botengine, survey_day_question_object)
        survey_microservice.question_answered(botengine, survey_time_question_object)

        botengine.users = [
            {
                "id": 0,
                "firstName": "John",
                "category": 1,
            }
        ]

        timestamp_ms = location_object.local_timestamp_ms_from_relative_hours(
            botengine, "0", "12.0", future=False
        )
        if timestamp_ms - botengine.get_timestamp() < 0:
            timestamp_ms += utilities.ONE_DAY_MS * 7

        # Test that statistics are described, week over week, for completed surveys
        for i in range(8):
            botengine.set_timestamp(timestamp_ms + (utilities.ONE_DAY_MS * 7 * i))

            survey_microservice._make_survey_call(botengine)
            assert survey_microservice.executed_answers == {}
            assert survey_microservice.executed_questions is not None
            botengine.set_timestamp(
                botengine.get_timestamp() + utilities.ONE_MINUTE_MS * 5
            )
            answers_string = "{}:1,Q2:1,Q16:1,Q4:1,Q14:1,Q3:1,Q1:1,Q5:1,Q10:1,Q18:1,Q8:1,Q15:1,Q17:1,Q20:1,Q13:1,Q6:1,Q9:1,Q7:1,Q12:1,Q19:1,Q11:1".format(
                survey_microservice.intelligence_id
            )
            survey_microservice.VOICE(
                botengine,
                {
                    "callUuid": "CON-55c9e398-155c-4e6c-8b91-9720d3e69bbe",
                    "status": 2,
                    "direction": 0,
                    "userId": 0,
                    "startTime": 1687994053000,
                    "endTime": 1687994243000,
                    "answers": answers_string,
                    "log": "0:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,11:1,12:1,13:1,14:1,15:1,16:1,17:1,18:1,19:1",
                },
            )

            survey_statistics = botengine.get_state(SURVEY_STATISTICS_STATE_VARIABLE)
            assert survey_statistics is not None
            assert survey_statistics["survey_list"] == [
                "COMPLETED" for i in range(i + 1)
            ]
            assert survey_statistics["missed"] == 0
            assert survey_statistics["completed"] == i + 1
            assert (
                survey_statistics["last_updated_ms"]
                <= survey_statistics["survey_timestamp_ms"]
            )
            assert (
                survey_statistics["time_remaining_ms"] >= 0
                and survey_statistics["time_remaining_ms"] <= utilities.ONE_DAY_MS * 7
            )

            survey_results = botengine.get_state(
                SURVEY_RESULTS_STATE_VARIABLE,
                timestamp_ms=survey_statistics["survey_timestamp_ms"],
            )
            assert survey_results is not None
            assert survey_results["survey_result"] == "COMPLETED"
            assert survey_results["survey_answers"] is not None
            for key in survey_results["survey_answers"].keys():
                assert key in CARE_QUESTIONS.keys()

        # Midnight fired
        botengine.set_timestamp(last_day_of_month_ms)

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

        import signals.daylight as daylight

        daylight.midnight_fired(botengine, location_object)

        report = botengine.get_state(
            MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms
        )
        assert report is not None
        assert report == {
            "created_ms": 1685516400000,
            "period": "monthlyreport",
            "sections": [
                {
                    "color": "F47174",
                    "description": "Overall physical and mental health status.",
                    "icon": "heart",
                    "id": "wellness",
                    "items": [
                        {
                            "comment": "Overall Care Score - 50%",
                            "comment_raw": "Overall Care Score - 50%",
                            "id": "trend-trend.care_score.0",
                            "timestamp_ms": 1685516400000,
                        },
                        {
                            "comment": "Illbeing Score - 20%",
                            "comment_raw": "Illbeing Score - 20%",
                            "id": "trend-trend.illbeing_score.0",
                            "timestamp_ms": 1685516400000,
                        },
                        {
                            "comment": "Positivity Score - 20%",
                            "comment_raw": "Positivity Score - 20%",
                            "id": "trend-trend.positivity_score.0",
                            "timestamp_ms": 1685516400000,
                        },
                        {
                            "comment": "Sleep Diary - 20%",
                            "comment_raw": "Sleep Diary - 20%",
                            "id": "trend-trend.sleep_diary.0",
                            "timestamp_ms": 1685516400000,
                        },
                        {
                            "comment": "Percieved Stress Scale - 20%",
                            "comment_raw": "Percieved Stress Scale - 20%",
                            "id": "trend-trend.percieved_stress_scale.0",
                            "timestamp_ms": 1685516400000,
                        },
                    ],
                    "title": "People Power Family Wellness",
                    "weight": -5,
                }
            ],
            "subtitle": "Monthly Report for May 2023",
            "title": "RESIDENT AND RESIDENT",
        }

        assert mut.monthly_reports == {
            "2023_05": {
                "trend-trend.care_score.0": {
                    "2023_19": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1683572700000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_20": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1684177500000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_21": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1684782300000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_22": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1685387100000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.illbeing_score.0": {
                    "2023_19": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1683572700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.percieved_stress_scale.0": {
                    "2023_19": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1683572700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.positivity_score.0": {
                    "2023_19": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1683572700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.sleep_diary.0": {
                    "2023_19": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1683572700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
            },
            "2023_06": {
                "trend-trend.care_score.0": {
                    "2023_23": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1685991900000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_24": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1686596700000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_25": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1687201500000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                    "2023_26": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1687806300000,
                        "value": 50.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.illbeing_score.0": {
                    "2023_23": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1685991900000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.percieved_stress_scale.0": {
                    "2023_23": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1685991900000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.positivity_score.0": {
                    "2023_23": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1685991900000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
                "trend-trend.sleep_diary.0": {
                    "2023_23": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1685991900000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0,
                    },
                },
            },
        }

        DEFAULT_SECTION_PROPERTIES[dailyreport.SECTION_ID_WELLNESS][
            dailyreport.SECTION_KEY_TREND_IDS
        ] = wellness_trend_ids
