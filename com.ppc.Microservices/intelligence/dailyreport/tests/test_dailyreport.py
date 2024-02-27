
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
        return # Not Supported In Public Release
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

    def test_dailyreport_occupancy_status_updated_sleep_beforenoon(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        botengine.logging_service_names = ["dailyreport"]
        
        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(botengine, location_object, "A", 10031, "Test Gateway")
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        return # Not Supported In Public Release
        import signals.occupancy as occupancy
        occupancy.update_occupancy_status(botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", "")
        assert mut.started_sleeping_ms == botengine.get_timestamp()

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
                },
                {
                "color": "946C49",
                "icon": "moon",
                "id": "sleep",
                "items": [
                    {
                    "comment": "Expected to go to sleep tonight around 10:00 PM.",
                    "comment_raw": "Expected to go to sleep tonight around 10:00 PM.",
                    "id": "insight-sleep.sleep_prediction_ms",
                    "timestamp_ms": 1684076795000
                    },
                    {
                    "comment": "8:06 AM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "timestamp_ms": 1684076795000,
                    "timestamp_str": "8:06 AM Sunday"
                    }
                ],
                "title": "Sleep",
                "weight": 15
                },
                {
                "color": "787F84",
                "icon": "brain",
                "id": "system",
                "items": [
                    {
                    "comment": "Appears to be sleeping.",
                    "comment_raw": "Appears to be sleeping.",
                    "id": "insight-occupancy.status",
                    "timestamp_ms": 1684076795000
                    }
                ],
                "title": "System Status",
                "weight": 50
                }
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT"
        }

    def test_dailyreport_occupancy_status_updated_sleep_afternoon(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684109195000)

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(botengine, location_object, "A", 10031, "Test Gateway")
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        return # Not Supported In Public Release
        import signals.occupancy as occupancy
        occupancy.update_occupancy_status(botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", "")
        assert mut.started_sleeping_ms == botengine.get_timestamp()
        assert mut.last_emailed_report_ms == mut.current_report_ms

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
                    "comment": "5:06 PM - A task was added: Add People to your Trusted Circle.",
                    "comment_raw": "A task was added: Add People to your Trusted Circle.",
                    "timestamp_ms": 1684109195000,
                    "timestamp_str": "5:06 PM"
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
                    "comment": "Expected to go to sleep tonight around 10:00 PM.",
                    "comment_raw": "Expected to go to sleep tonight around 10:00 PM.",
                    "id": "insight-sleep.sleep_prediction_ms",
                    "timestamp_ms": 1684109195000
                    },
                    {
                    "comment": "5:06 PM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "timestamp_ms": 1684109195000,
                    "timestamp_str": "5:06 PM Sunday"
                    }
                ],
                "title": "Sleep",
                "weight": 15
                },
                {
                "color": "787F84",
                "icon": "brain",
                "id": "system",
                "items": [
                    {
                    "comment": "Appears to be sleeping.",
                    "comment_raw": "Appears to be sleeping.",
                    "id": "insight-occupancy.status",
                    "timestamp_ms": 1684109195000
                    }
                ],
                "title": "System Status",
                "weight": 50
                }
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT"
        }

    
    def test_dailyreport_occupancy_status_updated_sleep_to_home(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)

        gateway_device = GatewayDevice(botengine, location_object, "A", 10031, "Test Gateway")
        gateway_device.is_connected = True
        location_object.born_on = botengine.get_timestamp()
        gateway_device.measurements["rssi"] = [[-67, botengine.get_timestamp()]]

        location_object.devices[gateway_device.device_id] = gateway_device

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        return # Not Supported In Public Release
        import signals.occupancy as occupancy
        occupancy.update_occupancy_status(botengine, location_object, "HOME.:.SLEEP", REASON_ML, "", "")
        assert mut.started_sleeping_ms == botengine.get_timestamp()

        occupancy.update_occupancy_status(botengine, location_object, "HOME.:.PRESENT", REASON_ML, "", "")
        assert mut.started_sleeping_ms is None

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
                },
                {
                "color": "946C49",
                "icon": "moon",
                "id": "sleep",
                "items": [
                    {
                    "comment": "Expected to go to sleep tonight around 10:00 PM.",
                    "comment_raw": "Expected to go to sleep tonight around 10:00 PM.",
                    "id": "insight-sleep.sleep_prediction_ms",
                    "timestamp_ms": 1684076795000
                    },
                    {
                    "comment": "8:06 AM Sunday - Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "comment_raw": "Might have gone to sleep. People Power Family is still learning your sleep patterns.",
                    "timestamp_ms": 1684076795000,
                    "timestamp_str": "8:06 AM Sunday"
                    }
                ],
                "title": "Sleep",
                "weight": 15
                },
                {
                "color": "787F84",
                "icon": "brain",
                "id": "system",
                "items": [
                    {
                    "comment": "Appears to be home.",
                    "comment_raw": "Appears to be home.",
                    "id": "insight-occupancy.status",
                    "timestamp_ms": 1684076795000
                    }
                ],
                "title": "System Status",
                "weight": 50
                }
            ],
            "subtitle": "Daily Report for Sunday May 14, 2023",
            "title": "RESIDENT AND RESIDENT"
        }

    def test_dailyreport_capture_trend_data(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(1684076795000)

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.deviceless_trends = True
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        return # Not Supported In Public Release
        import signals.trends as trends
        import signals.services as services
        
        trends.capture(botengine,
                        location_object=location_object,
                        trend_id="trend.sleep_score",
                        value=int(0.8 * 100.0),
                        display_value=_("{}% sleep score").format(int(0.8 * 100.0)),
                        title=_("Sleep Score"),
                        comment=_("Relative sleep quality score."),
                        icon="snooze",
                        units="%",
                        window=30,
                        once=True,
                        trend_category=trends.TREND_CATEGORY_SLEEP,
                        related_services=[services.SERVICE_KEY_BEDTIME],
                        min_value=0,
                        max_value=100)
        
        report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1684047600000,
            "period": "dailyreport",
            "sections": [
                {
                "color": "F47174",
                "icon": "heart",
                "id": "wellness",
                "items": [
                    {
                    "comment": "Sleep Score: 80% sleep score",
                    "comment_raw": "Sleep Score: 80% sleep score",
                    "id": "trend-trend.sleep_score",
                    "timestamp_ms": 1684076795000
                    }
                ],
                "title": "People Power Family Wellness",
                "weight": -5
                },
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
        
        assert mut.weekly_reports == {
            "2023_19": {
                "trend-trend.sleep_score": {
                    "2023_05_14": {
                        "avg": 80.0,
                        "display": "80% sleep score",
                        "std": 0.0,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1684076795000,
                        "value": 80.0,
                        "zscore": 0.0
                    }
                }
            }
        }
        assert mut.monthly_reports == {
            "2023_05": {
                "trend-trend.sleep_score": {
                    "2023_19": {
                        "avg": 80.0,
                        "display": "80% sleep score",
                        "std": 0.0,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1684076795000,
                        "value": 80.0,
                        "zscore": 0.0
                    }
                }
            }
        }

        assert mut.current_monthly_report_ms == None
        assert mut.current_weekly_report_ms == None

        report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms)
        assert report is None
        report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_report_ms)
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
        return # Not Supported In Public Release

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

    @patch('signals.dailyreport.report_status_updated')
    def test_dailyreport_monthly(self, mock_report_status_updated):
        last_day_of_month_ms = 1685516400000
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(last_day_of_month_ms - (utilities.ONE_DAY_MS * 7 * 4) + utilities.ONE_HOUR_MS * 12) # 4 weeks before the end of the month at noon

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms)
        assert report is None
        return # Not Supported In Public Release

        survey_microservice = location_object.intelligence_modules["intelligence.surveys.location_survey_microservice"]
        assert survey_microservice is not None

        survey_microservice.ask_question(botengine)
        from intelligence.surveys.location_survey_microservice import SERVICE_KEY_SURVEY_DAY, SERVICE_KEY_SURVEY_TIME, SURVEY_STATISTICS_STATE_VARIABLE, SURVEY_RESULTS_STATE_VARIABLE, CARE_QUESTIONS
  
        survey_day_question_object = botengine.retrieve_question(SERVICE_KEY_SURVEY_DAY)
        survey_time_question_object = botengine.retrieve_question(SERVICE_KEY_SURVEY_TIME)

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

        timestamp_ms = location_object.local_timestamp_ms_from_relative_hours(botengine, "0", "12.0", future=False)
        if timestamp_ms - botengine.get_timestamp() < 0:
            timestamp_ms += utilities.ONE_DAY_MS * 7

        # Test that statistics are described, week over week, for completed surveys
        for i in range(8):

            botengine.set_timestamp(timestamp_ms + (utilities.ONE_DAY_MS * 7 * i))

            survey_microservice._make_survey_call(botengine)
            assert survey_microservice.executed_answers == {}
            assert survey_microservice.executed_questions != None
            botengine.set_timestamp(botengine.get_timestamp() + utilities.ONE_MINUTE_MS * 5)
            answers_string = "{}:1,Q2:1,Q16:1,Q4:1,Q14:1,Q3:1,Q1:1,Q5:1,Q10:1,Q18:1,Q8:1,Q15:1,Q17:1,Q20:1,Q13:1,Q6:1,Q9:1,Q7:1,Q12:1,Q19:1,Q11:1".format(survey_microservice.intelligence_id)
            survey_microservice.VOICE(botengine, {
                "callUuid": "CON-55c9e398-155c-4e6c-8b91-9720d3e69bbe", 
                "status": 2, 
                "direction": 0, 
                "userId": 0, 
                "startTime": 1687994053000, 
                "endTime": 1687994243000, 
                "answers": answers_string, 
                "log": "0:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,11:1,12:1,13:1,14:1,15:1,16:1,17:1,18:1,19:1"
                })
            

            survey_statistics = botengine.get_state(SURVEY_STATISTICS_STATE_VARIABLE)
            assert survey_statistics != None
            assert survey_statistics["survey_list"] == ["COMPLETED" for i in range(i+1)]
            assert survey_statistics["missed"] == 0
            assert survey_statistics["completed"] == i + 1
            assert survey_statistics["last_updated_ms"] <= survey_statistics["survey_timestamp_ms"]
            assert survey_statistics["time_remaining_ms"] >= 0 and survey_statistics["time_remaining_ms"] <= utilities.ONE_DAY_MS * 7


            survey_results = botengine.get_state(SURVEY_RESULTS_STATE_VARIABLE, timestamp_ms=survey_statistics["survey_timestamp_ms"])
            assert survey_results != None
            assert survey_results["survey_result"] == "COMPLETED"
            assert survey_results["survey_answers"] != None
            for key in survey_results["survey_answers"].keys():
                assert key in CARE_QUESTIONS.keys()
        

        # Midnight fired
        botengine.set_timestamp(last_day_of_month_ms)

        def check_report(*args, status, metadata=None):
            assert args[0] == botengine
            assert args[1] == location_object
            assert args[2] is not None
            if status == dailyreport.REPORT_STATUS_COMPLETED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT COMPLETION: " + str(args[1]) + " " + str(args[2]) + str(status) + str(metadata))
            elif status == dailyreport.REPORT_STATUS_CREATED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT: " + str(args[1]) + " " + str(args[2]) + str(status) + str(metadata))
            else:
                assert False

        mock_report_status_updated.side_effect = check_report

        import signals.daylight as daylight
        daylight.midnight_fired(botengine, location_object)

        report = botengine.get_state(MONTHLY_REPORT_ADDRESS, timestamp_ms=mut.current_monthly_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1685516400000,
            "period": "monthlyreport",
            "sections": [
                {
                    "color": "F47174",
                    "icon": "heart",
                    "id": "wellness",
                    "items": [
                        {
                            "comment": "Overall Care Score - 50%",
                            "comment_raw": "Overall Care Score - 50%",
                            "id": "trend-trend.care_score.0",
                            "timestamp_ms": 1685516400000
                        },
                        {
                            "comment": "Illbeing Score - 20%",
                            "comment_raw": "Illbeing Score - 20%",
                            "id": "trend-trend.illbeing_score.0",
                            "timestamp_ms": 1685516400000
                        },
                        {
                            "comment": "Positivity Score - 20%",
                            "comment_raw": "Positivity Score - 20%",
                            "id": "trend-trend.positivity_score.0",
                            "timestamp_ms": 1685516400000
                        },
                        {
                            "comment": "Sleep Diary - 20%",
                            "comment_raw": "Sleep Diary - 20%",
                            "id": "trend-trend.sleep_diary.0",
                            "timestamp_ms": 1685516400000
                        },
                        {
                            "comment": "Percieved Stress Scale - 20%",
                            "comment_raw": "Percieved Stress Scale - 20%",
                            "id": "trend-trend.percieved_stress_scale.0",
                            "timestamp_ms": 1685516400000
                        }
                    ],
                    "title": "People Power Family Wellness",
                    "weight": -5
                }
            ],
            "subtitle": "Monthly Report for May 2023",
            "title": "RESIDENT AND RESIDENT"
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
                        "zscore": 0.0
                    },
                    "2023_20": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1684177500000,
                        "value": 50.0,
                        "zscore": 0.0
                    },
                    "2023_21": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1684782300000,
                        "value": 50.0,
                        "zscore": 0.0
                    },
                    "2023_22": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1685387100000,
                        "value": 50.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_20": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1684177500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_21": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1684782300000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_22": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1685387100000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
                }
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
                        "zscore": 0.0
                    },
                    "2023_24": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1686596700000,
                        "value": 50.0,
                        "zscore": 0.0
                    },
                    "2023_25": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1687201500000,
                        "value": 50.0,
                        "zscore": 0.0
                    },
                    "2023_26": {
                        "avg": 50.0,
                        "display": "50%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.care_score.0",
                        "updated_ms": 1687806300000,
                        "value": 50.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.illbeing_score.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.percieved_stress_scale.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.positivity_score.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
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
                        "zscore": 0.0
                    },
                    "2023_24": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1686596700000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_25": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1687201500000,
                        "value": 20.0,
                        "zscore": 0.0
                    },
                    "2023_26": {
                        "avg": 20.0,
                        "display": "20%",
                        "std": 0.0,
                        "trend_category": "category.care",
                        "trend_id": "trend.sleep_diary.0",
                        "updated_ms": 1687806300000,
                        "value": 20.0,
                        "zscore": 0.0
                    }
                }
            }
        }

    @patch('signals.dailyreport.report_status_updated')
    def test_dailyreport_weekly(self, mock_report_status_updated):
        first_day_of_week_ms = 1685343600000
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()
        botengine.set_timestamp(first_day_of_week_ms - utilities.ONE_DAY_MS * 6 + utilities.ONE_HOUR_MS * 12) # 6 days before the end of the month at noon

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.deviceless_trends = True

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms)
        assert report is None
        return # Not Supported in Public Release
        import signals.trends as trends
        import signals.services as services
        
        # Capture 7 days of sleep trends
        for i in range(6):
            values = [0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
            trends.capture(botengine,
                            location_object=location_object,
                            trend_id="trend.sleep_score",
                            value=int(values[i] * 100.0),
                            display_value=_("{}% sleep score").format(int(values[i] * 100.0)),
                            title=_("Sleep Score"),
                            comment=_("Relative sleep quality score."),
                            icon="snooze",
                            units="%",
                            window=30,
                            once=True,
                            trend_category=trends.TREND_CATEGORY_SLEEP,
                            related_services=[services.SERVICE_KEY_BEDTIME],
                            min_value=0,
                            max_value=100)
            
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
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT COMPLETION: " + str(args[1]) + " " + str(args[2]) + str(status) + str(metadata))
            elif status == dailyreport.REPORT_STATUS_CREATED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("CHECK REPORT: " + str(args[1]) + " " + str(args[2]) + str(status) + str(metadata))
            else:
                assert False

        mock_report_status_updated.side_effect = check_report

        import signals.daylight as daylight
        daylight.midnight_fired(botengine, location_object)

        report = botengine.get_state(WEEKLY_REPORT_ADDRESS, timestamp_ms=mut.current_weekly_report_ms)
        assert report is not None
        assert report == {
            "created_ms": 1685343600000,
            "period": "weeklyreport",
            "sections": [
                {
                    "color": "F47174",
                    "icon": "heart",
                    "id": "wellness",
                    "items": [
                        {
                            "comment": "Sleep Score - 30% sleep score",
                            "comment_raw": "Sleep Score - 30% sleep score",
                            "id": "trend-trend.sleep_score",
                            "timestamp_ms": 1685343600000
                        }
                    ],
                    "title": "People Power Family Wellness",
                    "weight": -5
                }
            ],
            "subtitle": "Weekly Report for Monday May 29, 2023",
            "title": "RESIDENT AND RESIDENT"
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
                        "zscore": 0.0
                    },
                    "2023_05_24": {
                        "avg": 75.0,
                        "display": "70% sleep score",
                        "std": 7.07,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1684954800000,
                        "value": 70.0,
                        "zscore": -0.71
                    },
                    "2023_05_25": {
                        "avg": 70.0,
                        "display": "60% sleep score",
                        "std": 10.0,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685041200000,
                        "value": 60.0,
                        "zscore": -1.0
                    },
                    "2023_05_26": {
                        "avg": 65.0,
                        "display": "50% sleep score",
                        "std": 12.91,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685127600000,
                        "value": 50.0,
                        "zscore": -1.16
                    },
                    "2023_05_27": {
                        "avg": 60.0,
                        "display": "40% sleep score",
                        "std": 15.81,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685214000000,
                        "value": 40.0,
                        "zscore": -1.27
                    },
                    "2023_05_28": {
                        "avg": 55.0,
                        "display": "30% sleep score",
                        "std": 18.71,
                        "trend_category": "category.sleep",
                        "trend_id": "trend.sleep_score",
                        "updated_ms": 1685300400000,
                        "value": 30.0,
                        "zscore": -1.34
                    }
                }
            }
        }

    def test_dailyreport_report_key(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        botengine.logging_service_names = ["dailyreport"]

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]

        date_keys = {
            # January 1, 2023 Midnight Pacific Time
            1672560000000: {
                DAILY_REPORT_ADDRESS: "2023_01_01",
                WEEKLY_REPORT_ADDRESS: "2022_52", # Note: January 1, 2023 falls in the last week of the 2022 gregorian calendar.
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 2, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 1: {
                DAILY_REPORT_ADDRESS: "2023_01_02",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 3, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 2: {
                DAILY_REPORT_ADDRESS: "2023_01_03",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 4, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 3: {
                DAILY_REPORT_ADDRESS: "2023_01_04",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 5, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 4: {
                DAILY_REPORT_ADDRESS: "2023_01_05",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 6, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 5: {
                DAILY_REPORT_ADDRESS: "2023_01_06",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 7, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 6: {
                DAILY_REPORT_ADDRESS: "2023_01_07",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 8, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 7: {
                DAILY_REPORT_ADDRESS: "2023_01_08",
                WEEKLY_REPORT_ADDRESS: "2023_01",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # January 9, 2023 Midnight Pacific Time
            1672560000000 + utilities.ONE_DAY_MS * 8: {
                DAILY_REPORT_ADDRESS: "2023_01_09",
                WEEKLY_REPORT_ADDRESS: "2023_02",
                MONTHLY_REPORT_ADDRESS: "2023_01"
            },
            # December 21, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 0: {
                DAILY_REPORT_ADDRESS: "2023_12_21",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 22, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 1: {
                DAILY_REPORT_ADDRESS: "2023_12_22",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 23, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 2: {
                DAILY_REPORT_ADDRESS: "2023_12_23",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 24, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 3: {
                DAILY_REPORT_ADDRESS: "2023_12_24",
                WEEKLY_REPORT_ADDRESS: "2023_51",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 25, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 4: {
                DAILY_REPORT_ADDRESS: "2023_12_25",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 26, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 5: {
                DAILY_REPORT_ADDRESS: "2023_12_26",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 27, 2023 Midnight Pacific Time :)
            1703145600000 + utilities.ONE_DAY_MS * 6: {
                DAILY_REPORT_ADDRESS: "2023_12_27",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 28, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 7: {
                DAILY_REPORT_ADDRESS: "2023_12_28",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 29, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 8: {
                DAILY_REPORT_ADDRESS: "2023_12_29",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 30, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 9: {
                DAILY_REPORT_ADDRESS: "2023_12_30",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # December 31, 2023 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 10: {
                DAILY_REPORT_ADDRESS: "2023_12_31",
                WEEKLY_REPORT_ADDRESS: "2023_52",
                MONTHLY_REPORT_ADDRESS: "2023_12"
            },
            # January 1, 2024 Midnight Pacific Time
            1703145600000 + utilities.ONE_DAY_MS * 11: {
                DAILY_REPORT_ADDRESS: "2024_01_01",
                WEEKLY_REPORT_ADDRESS: "2024_01",
                MONTHLY_REPORT_ADDRESS: "2024_01"
            },
        }

        for timestamp in date_keys.keys():
            botengine.set_timestamp(timestamp)
            
            date = location_object.get_local_datetime(botengine)
            for address in date_keys[timestamp].keys():
                assert mut._report_key(botengine, report_address=address, date=date) == date_keys[timestamp][address], "{} {} malformed".format(timestamp, address)