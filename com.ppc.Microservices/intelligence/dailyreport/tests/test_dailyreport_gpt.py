
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities
import signals.dailyreport as dailyreport

from intelligence.dailyreport.location_dailyreport_microservice import *
from intelligence.dailyreport.location_dailyreport_gpt_microservice import *

import utilities.genai as genai

from unittest.mock import patch, MagicMock

class TestDailyReportGPTMicroservice():

    def test_dailyreport_gpt_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_gpt_microservice"]
        assert mut is not None

        # Test default values
        assert mut.version == VERSION
        assert mut.report_content == {}
        assert mut.messages == {}

        # Test disabled if ChatGPT Reports organization property disabled
        botengine.organization_properties[DOMAIN_KEY_GPT_ENABLED] = False
        mut._ask_questions(botengine)
        assert mut._is_active(botengine) is False

        botengine.organization_properties[DOMAIN_KEY_GPT_ENABLED] = True
        mut._ask_questions(botengine)
        assert mut._is_active(botengine) is True

    @patch('intelligence.dailyreport.location_dailyreport_gpt_microservice.LocationDailyReportGPTMicroservice._is_active')
    def test_dailyreport_gpt_daily_report_status_updated(self, is_active_mock):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_gpt_microservice"]
        assert mut is not None

        # Enable for further tests
        is_active_mock.return_value = False

        # Test disabled (default)
        mut.daily_report_status_updated(botengine, {"report": {"period": WEEKLY_REPORT_ADDRESS, "sections": []}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {}})
        assert mut.report_content == {}
        assert mut.messages == {}

        # Enable for further tests
        is_active_mock.return_value = True

        # Test no action when created
        mut.daily_report_status_updated(botengine, {"report": {"sections": []}, "status": dailyreport.REPORT_STATUS_CREATED, "metadata": {}})
        assert mut.report_content == {}
        assert mut.messages == {}

        # Test no action for daily reports
        mut.daily_report_status_updated(botengine, {"report": {"period": DAILY_REPORT_ADDRESS, "sections": []}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {}})
        assert mut.report_content == {}
        assert mut.messages == {}

        # Test pending actions for weekly / monthly reports
        mut.daily_report_status_updated(botengine, {"report": {"period": WEEKLY_REPORT_ADDRESS, "sections": [{"id": "wellness", "items": [{"id": "trend.care_score.0"}]}]}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {"some": "value"}})
        assert mut.report_content == {
            WEEKLY_REPORT_ADDRESS: {'report': {'period': WEEKLY_REPORT_ADDRESS, "sections": [{"id": "wellness", "items": [{"id": "trend.care_score.0"}]}]}, 'metadata': {'some': 'value'}}
        }
        assert mut.messages == {
            'weeklyreport': {}
        }
        for report_type in DEFAULT_REPORT_TYPES:
            reference = PUBLISH_REPORT_TIMER.replace('<period>', WEEKLY_REPORT_ADDRESS).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)

        mut.daily_report_status_updated(botengine, {"report": {"period": MONTHLY_REPORT_ADDRESS, "sections": [{"id": "wellness", "items": [{"id": "trend.care_score.0"}]}]}, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": {"some": "value"}})
        assert mut.report_content == {
            WEEKLY_REPORT_ADDRESS: {'report': {'period': WEEKLY_REPORT_ADDRESS, "sections": [{"id": "wellness", "items": [{"id": "trend.care_score.0"}]}]}, 'metadata': {'some': 'value'}},
            MONTHLY_REPORT_ADDRESS: {'report': {'period': MONTHLY_REPORT_ADDRESS, "sections": [{"id": "wellness", "items": [{"id": "trend.care_score.0"}]}]}, 'metadata': {'some': 'value'}}
        }
        assert mut.messages == {
            WEEKLY_REPORT_ADDRESS: {},
            MONTHLY_REPORT_ADDRESS: {},
        }
        for report_type in DEFAULT_REPORT_TYPES:
            reference = PUBLISH_REPORT_TIMER.replace('<period>', WEEKLY_REPORT_ADDRESS).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)
            reference = PUBLISH_REPORT_TIMER.replace('<period>', MONTHLY_REPORT_ADDRESS).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)

    @patch('intelligence.dailyreport.location_dailyreport_gpt_microservice.LocationDailyReportGPTMicroservice._is_active', MagicMock(return_value=True))
    def test_dailyreport_publish_gpt_report_weekly_report(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        dailyreport_microservice = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_gpt_microservice"]
        assert mut is not None

        # TEST DATA
        report_sample = {"title": "My Home", "subtitle": "Weekly Report", "sections": [{"title": "Wellness", "comment": "You had a wonderful week.", "id": "wellness", "items": [{"timestamp_ms": 1685646000000, "comment": "Care Score: 20%", "comment_raw": "Care Score: 20%", "timestamp_str": "12:00 PM", "id": "trend.care_score.0"}]}], "period": "weeklyreport"}
        report_sample_metadata = {"wellness_score": {"2023_39": {"value": 100.0}}}

        # Disabled by default
        # May be overriden by domain property, set to false for consistent testing
        botengine.organization_properties["GPT_PRIMARY_CAREGIVER_REPORT_ENABLED"] = False

        mut.daily_report_status_updated(botengine, {"report": report_sample, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": report_sample_metadata})

        assert mut.report_content[report_sample["period"]] is not None
        assert mut.report_content[report_sample["period"]]["report"] == report_sample
        assert mut.report_content[report_sample["period"]]["metadata"] == report_sample_metadata
        for report_type in DEFAULT_REPORT_TYPES:
            reference = PUBLISH_REPORT_TIMER.replace('<period>', report_sample["period"]).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)
            botengine.fire_next_timer_or_alarm(mut, reference)

            mocked_response = "MOCK REPORT RESPONSE"
            openai_response = {
                "key": "dailyreport_gpt.{}.{}.{}".format(report_sample["period"], report_type["id"], 0),
                "id" : "chatcmpl-86GKbsl3bP5YmmxutIY8aS5c5o5gK",
                "object" : "chat.completion",
                "created" : 1696503437,
                "model" : "gpt-3.5-turbo-0613",
                "choices" : [ {
                    "index" : 0,
                    "message" : {
                        "role" : "assistant",
                        "content" : mocked_response
                    },
                    "finish_reason" : "stop"
                } ],
                "usage" : {
                    "prompt_tokens" : 13,
                    "completion_tokens" : 5,
                    "total_tokens" : 18
                }
            }
            
            location_object.distribute_datastream_message(botengine, "openai", openai_response, internal=True, external=False)
            
            assert mut.report_content[report_sample["period"]]["responses"][report_type["id"]] is not None
            assert len(mut.messages[report_sample["period"]][report_type["id"]]["messages"]) == len(mut.report_content[report_sample["period"]]["responses"][report_type["id"]])
            
        # FAILS UNTIL WE MOCK THE openai DATASTREAM
        daily_report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=dailyreport_microservice.current_report_ms)
        assert daily_report is not None
        # assert daily_report["sections"][0]["items"][0]["comment"] != mocked_response
        # assert daily_report["sections"][0]["items"][0]["comment_raw"] != mocked_response

    @patch('intelligence.dailyreport.location_dailyreport_gpt_microservice.LocationDailyReportGPTMicroservice._is_active', MagicMock(return_value=True))
    def test_dailyreport_publish_gpt_report_weekly_report_enabled(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        dailyreport_microservice = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_gpt_microservice"]
        assert mut is not None

        # TEST DATA
        report_sample = {"title": "My Home", "subtitle": "Weekly Report", "sections": [{"title": "Wellness", "comment": "You had a wonderful week.", "id": "wellness", "items": [{"timestamp_ms": 1685646000000, "comment": "Care Score: 20%", "comment_raw": "Care Score: 20%", "timestamp_str": "12:00 PM", "id": "trend.care_score.0"}]}], "period": "weeklyreport"}
        report_sample_metadata = {"wellness_score": {"2023_39": {"value": 100.0}}}

        # Disabled by default
        # May be overriden by domain property, set to false for consistent testing
        botengine.organization_properties["GPT_PRIMARY_CAREGIVER_REPORT_ENABLED"] = True

        mut.daily_report_status_updated(botengine, {"report": report_sample, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": report_sample_metadata})

        assert mut.report_content[report_sample["period"]] is not None
        assert mut.report_content[report_sample["period"]]["report"] == report_sample
        assert mut.report_content[report_sample["period"]]["metadata"] == report_sample_metadata
        for report_type in DEFAULT_REPORT_TYPES:
            reference = PUBLISH_REPORT_TIMER.replace('<period>', report_sample["period"]).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)
            botengine.fire_next_timer_or_alarm(mut, reference)

            mocked_response = "MOCK REPORT RESPONSE"
            openai_response = {
                "key": "dailyreport_gpt.{}.{}.{}".format(report_sample["period"], report_type["id"], 0),
                "id" : "chatcmpl-86GKbsl3bP5YmmxutIY8aS5c5o5gK",
                "object" : "chat.completion",
                "created" : 1696503437,
                "model" : "gpt-3.5-turbo-0613",
                "choices" : [ {
                    "index" : 0,
                    "message" : {
                        "role" : "assistant",
                        "content" : mocked_response
                    },
                    "finish_reason" : "stop"
                } ],
                "usage" : {
                    "prompt_tokens" : 13,
                    "completion_tokens" : 5,
                    "total_tokens" : 18
                }
            }
            
            location_object.distribute_datastream_message(botengine, "openai", openai_response, internal=True, external=False)

            assert mut.report_content[report_sample["period"]]["responses"][report_type["id"]] is not None
            assert len(mut.messages[report_sample["period"]][report_type["id"]]["messages"]) == len(mut.report_content[report_sample["period"]]["responses"][report_type["id"]])

            reference = PUBLISH_REPORT_TIMER.replace('<period>', report_sample["period"]).replace('<report_type_id>', str(report_type["id"]))
            assert mut.is_timer_running(botengine, reference)
            botengine.fire_next_timer_or_alarm(mut, reference)
            
        # FAILS UNTIL WE MOCK THE openai DATASTREAM
        daily_report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=dailyreport_microservice.current_report_ms)
        assert daily_report is not None
        # assert daily_report["sections"][0]["items"][0]["comment"] == mocked_response
        # assert daily_report["sections"][0]["items"][0]["comment_raw"] == mocked_response
        # assert daily_report["sections"][0]["items"][0]["id"] == "gpt_report_weeklyreport"
        
    @patch('intelligence.dailyreport.location_dailyreport_gpt_microservice.LocationDailyReportGPTMicroservice._is_active', MagicMock(return_value=True))
    def test_dailyreport_publish_gpt_report_monthly_report_enabled(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)
        location_object.new_version(botengine)
        location_object.initialize(botengine)

        dailyreport_microservice = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_microservice"]
        mut = location_object.intelligence_modules["intelligence.dailyreport.location_dailyreport_gpt_microservice"]
        assert mut is not None

        # TEST DATA
        report_sample = {
            "title": "RESIDENT AND RESIDENT", 
            "subtitle": "Monthly Report for May 2023", 
            "created_ms": 1685516400000, 
            "sections": [
                {"id": "wellness", "weight": -5, "title": "Care Daily Wellness", "icon": "heart", "color": "F47174", "items": [
                    {"timestamp_ms": 1685516400000, "comment": "Overall Care Score - 50%", "comment_raw": "Overall Care Score - 50%", "id": "trend.care_score.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Illbeing Score - 20%", "comment_raw": "Illbeing Score - 20%", "id": "trend.illbeing_score.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Beck's Anxiety Inventory - 20%", "comment_raw": "Beck's Anxiety Inventory - 20%", "id": "illbeing.bai.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Center for Epidemiologic Studies Depression - 20%", "comment_raw": "Center for Epidemiologic Studies Depression - 20%", "id": "illbeing.cesd.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Positive and Negative Affect Schedule (Negative) - 20%", "comment_raw": "Positive and Negative Affect Schedule (Negative) - 20%", "id": "illness.panas_negative.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Positivity Score - 20%", "comment_raw": "Positivity Score - 20%", "id": "trend.positivity_score.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Positive and Negative Affect Schedule (Positive) - 20%", "comment_raw": "Positive and Negative Affect Schedule (Positive) - 20%", "id": "positivity.panas_positive.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Positive Aspects of Caregiving Questionnaire - 20%", "comment_raw": "Positive Aspects of Caregiving Questionnaire - 20%", "id": "positivity.pacq.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Dyadic Adjustment Scale - 20%", "comment_raw": "Dyadic Adjustment Scale - 20%", "id": "positivity.das.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Sleep Diary - 20%", "comment_raw": "Sleep Diary - 20%", "id": "trend.sleep_diary.0"}, 
                    {"timestamp_ms": 1685516400000, "comment": "Percieved Stress Scale - 20%", "comment_raw": "Percieved Stress Scale - 20%", "id": "trend.percieved_stress_scale.0"}]}], 
            "period": "monthlyreport"}
        report_sample_metadata = {
            'trend.care_score.0': {
                '2023_19': {'value': 50.0, 'std': 0.0, 'avg': 50.0, 'zscore': 0.0, 'display': '50%', 'updated_ms': 1683572700000, 'trend_id': 'trend.care_score.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 50.0, 'std': 0.0, 'avg': 50.0, 'zscore': 0.0, 'display': '50%', 'updated_ms': 1684177500000, 'trend_id': 'trend.care_score.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 50.0, 'std': 0.0, 'avg': 50.0, 'zscore': 0.0, 'display': '50%', 'updated_ms': 1684782300000, 'trend_id': 'trend.care_score.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 50.0, 'std': 0.0, 'avg': 50.0, 'zscore': 0.0, 'display': '50%', 'updated_ms': 1685387100000, 'trend_id': 'trend.care_score.0', 'trend_category': 'category.care'}}, 
            'trend.illbeing_score.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'trend.illbeing_score.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'trend.illbeing_score.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'trend.illbeing_score.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'trend.illbeing_score.0', 'trend_category': 'category.care'}}, 
            'illbeing.bai.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'illbeing.bai.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'illbeing.bai.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'illbeing.bai.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'illbeing.bai.0', 'trend_category': 'category.care'}}, 
            'illbeing.cesd.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'illbeing.cesd.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'illbeing.cesd.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'illbeing.cesd.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'illbeing.cesd.0', 'trend_category': 'category.care'}}, 
            'illness.panas_negative.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'illness.panas_negative.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'illness.panas_negative.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'illness.panas_negative.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'illness.panas_negative.0', 'trend_category': 'category.care'}}, 
            'trend.positivity_score.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'trend.positivity_score.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'trend.positivity_score.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'trend.positivity_score.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'trend.positivity_score.0', 'trend_category': 'category.care'}}, 
            'positivity.panas_positive.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'positivity.panas_positive.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'positivity.panas_positive.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'positivity.panas_positive.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'positivity.panas_positive.0', 'trend_category': 'category.care'}}, 
            'positivity.pacq.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'positivity.pacq.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'positivity.pacq.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'positivity.pacq.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'positivity.pacq.0', 'trend_category': 'category.care'}}, 
            'positivity.das.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'positivity.das.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'positivity.das.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'positivity.das.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'positivity.das.0', 'trend_category': 'category.care'}}, 
            'trend.sleep_diary.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'trend.sleep_diary.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'trend.sleep_diary.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'trend.sleep_diary.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'trend.sleep_diary.0', 'trend_category': 'category.care'}}, 
            'trend.percieved_stress_scale.0': {
                '2023_19': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1683572700000, 'trend_id': 'trend.percieved_stress_scale.0', 'trend_category': 'category.care'}, 
                '2023_20': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684177500000, 'trend_id': 'trend.percieved_stress_scale.0', 'trend_category': 'category.care'}, 
                '2023_21': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1684782300000, 'trend_id': 'trend.percieved_stress_scale.0', 'trend_category': 'category.care'}, 
                '2023_22': {'value': 20.0, 'std': 0.0, 'avg': 20.0, 'zscore': 0.0, 'display': '20%', 'updated_ms': 1685387100000, 'trend_id': 'trend.percieved_stress_scale.0', 'trend_category': 'category.care'}}}

        # Add trends_metadata and trends_category state information
        trend_metadata = {'trend.care_score.0': {'parent_id': None, 'category': 'category.care', 'icon': 'hand-heart', 'title': 'Overall Care Score', 'units': '%', 'window': 30, 'comment': "User 0's overall health.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'trend.illbeing_score.0': {'parent_id': 'trend.care_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Illbeing Score', 'units': '%', 'window': 30, 'comment': "Measures User 0's general illbeing.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'illbeing.bai.0': {'parent_id': 'trend.illbeing_score.0', 'category': 'category.care', 'icon': 'spa', 'title': "Beck's Anxiety Inventory", 'units': '%', 'window': 30, 'comment': "Measures User 0's severity of anxiety.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'illbeing.cesd.0': {'parent_id': 'trend.illbeing_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Center for Epidemiologic Studies Depression', 'units': '%', 'window': 30, 'comment': "Measures User 0's depressive symptoms severity.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'illness.panas_negative.0': {'parent_id': 'trend.illbeing_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Positive and Negative Affect Schedule (Negative)', 'units': '%', 'window': 30, 'comment': "Measures User 0's negative affect.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'trend.positivity_score.0': {'parent_id': 'trend.care_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Positivity Score', 'units': '%', 'window': 30, 'comment': "Tracking the status of User 0's positive emotions!", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'positivity.panas_positive.0': {'parent_id': 'trend.positivity_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Positive and Negative Affect Schedule (Positive)', 'units': '%', 'window': 30, 'comment': "Measures User 0's positive affect.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'positivity.pacq.0': {'parent_id': 'trend.positivity_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Positive Aspects of Caregiving Questionnaire', 'units': '%', 'window': 30, 'comment': "Measures User 0's positive aspects of caregiving.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'positivity.das.0': {'parent_id': 'trend.positivity_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Dyadic Adjustment Scale', 'units': '%', 'window': 30, 'comment': "Measures User 0's relationship quality.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'trend.sleep_diary.0': {'parent_id': 'trend.care_score.0', 'category': 'category.care', 'icon': 'spa', 'title': 'Sleep Diary', 'units': '%', 'window': 30, 'comment': "Tracking the status of User 0's sleep!", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}, 'trend.percieved_stress_scale.0': {'parent_id': 'trend.care_score.0', 'category': 'category.care', 'icon': 'flower-tulip', 'title': 'Percieved Stress Scale', 'units': '%', 'window': 30, 'comment': "Measures User 0's situations that are appraised as stressful.", 'services': [], 'operation': 2, 'daily': True, 'hidden': False, 'updated_ms': 1685646000000, 'min_value': 0, 'max_value': 100}}
        location_object.set_location_property_separately(botengine, TRENDS_METADATA_NAME, trend_metadata)
        trends_category = {"category.care": {"title": _("Care Score"), "description": _("Care score takes in to account Wellness Survey questions."), "primary_trend": "trend.care_score", "primary_trend_title": _("Score"), "sub_trends": ["trend.illbeing_score", "trend.positivity_score", "trend.sleep_diary", "trend.percieved_stress_scale"]}}
        location_object.set_location_property_separately(botengine, "trends_category", trends_category)

        # Disabled by default
        # May be overriden by domain property, set to false for consistent testing
        botengine.organization_properties["GPT_PRIMARY_CAREGIVER_REPORT_ENABLED"] = True

        mut.daily_report_status_updated(botengine, {"report": report_sample, "status": dailyreport.REPORT_STATUS_COMPLETED, "metadata": report_sample_metadata})

        assert mut.report_content[report_sample["period"]] is not None
        assert mut.report_content[report_sample["period"]]["report"] == report_sample
        assert mut.report_content[report_sample["period"]]["metadata"] == report_sample_metadata

        for report_type in DEFAULT_REPORT_TYPES:
            reference = PUBLISH_REPORT_TIMER.replace('<period>', report_sample["period"]).replace('<report_type_id>', str(report_type["id"]))

            # Initialize the report and iterate through each message
            assert mut.is_timer_running(botengine, reference)
            botengine.fire_next_timer_or_alarm(mut, reference)
            while len(mut.messages[report_sample["period"]][report_type["id"]]["responses"]) != len(mut.messages[report_sample["period"]][report_type["id"]]["messages"]):

                mocked_response = "MOCK REPORT RESPONSE"
                openai_response = {
                    "key": "dailyreport_gpt.{}.{}.{}".format(report_sample["period"], report_type["id"], len(mut.messages[report_sample["period"]][report_type["id"]]["responses"])),
                    "id" : "chatcmpl-86GKbsl3bP5YmmxutIY8aS5c5o5gK",
                    "object" : "chat.completion",
                    "created" : 1696503437,
                    "model" : "gpt-3.5-turbo-0613",
                    "choices" : [ {
                        "index" : 0,
                        "message" : {
                            "role" : "assistant",
                            "content" : mocked_response
                        },
                        "finish_reason" : "stop"
                    } ],
                    "usage" : {
                        "prompt_tokens" : 13,
                        "completion_tokens" : 5,
                        "total_tokens" : 18
                    }
                }
                
                location_object.distribute_datastream_message(botengine, "openai", openai_response, internal=True, external=False)

                assert mut.report_content[report_sample["period"]]["responses"][report_type["id"]] is not None
                assert len(mut.messages[report_sample["period"]][report_type["id"]]["responses"]) == len(mut.report_content[report_sample["period"]]["responses"][report_type["id"]])
            
            # Complete the report
            assert mut.is_timer_running(botengine, reference)
            botengine.fire_next_timer_or_alarm(mut, reference)
            
        # FAILS UNTIL WE MOCK THE openai DATASTREAM
        daily_report = botengine.get_state(DAILY_REPORT_ADDRESS, timestamp_ms=dailyreport_microservice.current_report_ms)
        assert daily_report is not None
        # assert daily_report["sections"][0]["items"][0]["comment"] == "\n".join([mocked_response for i in range(len(mut.messages[report_sample["period"]][DEFAULT_REPORT_TYPES[0]["id"]]["responses"]))])
        # assert daily_report["sections"][0]["items"][0]["comment_raw"] == "\n".join([mocked_response for i in range(len(mut.messages[report_sample["period"]][DEFAULT_REPORT_TYPES[0]["id"]]["responses"]))])
        # assert daily_report["sections"][0]["items"][0]["id"] == "gpt_report_monthlyreport"
        