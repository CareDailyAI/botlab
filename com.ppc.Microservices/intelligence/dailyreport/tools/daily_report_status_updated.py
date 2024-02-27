#!/usr/bin/env python
# encoding: utf-8
'''
Created on September 28, 2023

@author: Destry Teeter
'''

# Data Stream Address
DATASTREAM_ADDRESS = "daily_report_status_updated"

REPORT_STATUS_CREATED   = 0
REPORT_STATUS_COMPLETED = 1

# MOCKED WEEKLY REPORT SAMPLE FOR SURVEY RESULTS
# USER_ID = 36213

# import random 
# def rand(a: float, b: float) -> float:
#     return float(random.randint(a * 100, b * 100)) / 100.0
# REPORT = {
#     "title": "JOHN SMITH", 
#     "subtitle": "Weekly Report for Monday November 20, 2023", 
#     "created_ms": 1700456400000, 
#     "sections": [
#         {"id": "wellness", "weight": -5, "title": "Care Daily Wellness", "icon": "heart", "color": "F47174", "items": [
#             {"timestamp_ms": 1685646000000, "comment": "Overall Care Score: 78%", "comment_raw": "Overall Care Score: 78%", "id": "trend.care_score.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Illbeing Score: 12%", "comment_raw": "Illbeing Score: 12%", "id": "trend.illbeing_score.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Beck's Anxiety Inventory: 4%", "comment_raw": "Beck's Anxiety Inventory: 4%", "id": "illbeing.bai.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Center for Epidemiologic Studies Depression: 17%", "comment_raw": "Center for Epidemiologic Studies Depression: 17%", "id": "illbeing.cesd.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Positive and Negative Affect Schedule (Negative): 8%", "comment_raw": "Positive and Negative Affect Schedule (Negative): 8%", "id": "illness.panas_negative.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Positivity Score: 90%", "comment_raw": "Positivity Score: 90%", "id": "trend.positivity_score.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Positive and Negative Affect Schedule (Positive): 86%", "comment_raw": "Positive and Negative Affect Schedule (Positive): 86%", "id": "positivity.panas_positive.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Positive Aspects of Caregiving Questionnaire: 92%", "comment_raw": "Positive Aspects of Caregiving Questionnaire: 92%", "id": "positivity.pacq.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Dyadic Adjustment Scale: 90%", "comment_raw": "Dyadic Adjustment Scale: 90%", "id": "positivity.das.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Sleep Diary: 86%", "comment_raw": "Sleep Diary: 86%", "id": "trend.sleep_diary.{}".format(USER_ID)}, 
#             {"timestamp_ms": 1685646000000, "comment": "Percieved Stress Scale: 24%", "comment_raw": "Percieved Stress Scale: 24%", "id": "trend.percieved_stress_scale.{}".format(USER_ID)}]} 
#     ],
#     "period": "weeklyreport"
# }
# STATUS = REPORT_STATUS_COMPLETED
# METADATA = {
#     "trend.care_score.{}".format(USER_ID): {
#         "2023_11_17": {"value": 78.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "78%", "updated_ms": 1700249400000, "trend_id": "trend.care_score.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "trend.illbeing_score.{}".format(USER_ID): {
#         "2023_11_17": {"value": 12.0, "std": rand(0,3), "avg": rand(0,50), "zscore": rand(-1,1), "display": "12%", "updated_ms": 1700249400000, "trend_id": "trend.illbeing_score.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "illbeing.bai.{}".format(USER_ID): {
#         "2023_11_17": {"value": 4.0, "std": rand(0,3), "avg": rand(0,50), "zscore": rand(-1,1), "display": "4%", "updated_ms": 1700249400000, "trend_id": "illbeing.bai.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "illbeing.cesd.{}".format(USER_ID): {
#         "2023_11_17": {"value": 17.0, "std": rand(0,3), "avg": rand(0,50), "zscore": rand(-1,1), "display": "17%", "updated_ms": 1700249400000, "trend_id": "illbeing.cesd.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "illness.panas_negative.{}".format(USER_ID): {
#         "2023_11_17": {"value": 8.0, "std": rand(0,3), "avg": rand(0,50), "zscore": rand(-1,1), "display": "8%", "updated_ms": 1700249400000, "trend_id": "illness.panas_negative.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "trend.positivity_score.{}".format(USER_ID): {
#         "2023_11_17": {"value": 90.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "90%", "updated_ms": 1700249400000, "trend_id": "trend.positivity_score.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "positivity.panas_positive.{}".format(USER_ID): {
#         "2023_11_17": {"value": 86.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "86%", "updated_ms": 1700249400000, "trend_id": "positivity.panas_positive.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "positivity.pacq.{}".format(USER_ID): {
#         "2023_11_17": {"value": 92.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "92%", "updated_ms": 1700249400000, "trend_id": "positivity.pacq.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "positivity.das.{}".format(USER_ID): {
#         "2023_11_17": {"value": 90.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "90%", "updated_ms": 1700249400000, "trend_id": "positivity.das.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "trend.sleep_diary.{}".format(USER_ID): {
#         "2023_11_17": {"value": 86.0, "std": rand(0,3), "avg": rand(50,100), "zscore": rand(-1,1), "display": "86%", "updated_ms": 1700249400000, "trend_id": "trend.sleep_diary.{}".format(USER_ID), "trend_category": "category.care"}
#     },
#     "trend.percieved_stress_scale.{}".format(USER_ID): {
#         "2023_11_17": {"value": 24.0, "std": rand(0,3), "avg": rand(0,50), "zscore": rand(-1,1), "display": "24%", "updated_ms": 1700249400000, "trend_id": "trend.percieved_stress_scale.{}".format(USER_ID), "trend_category": "category.care"}
#     },
# }

# MOCKED MONTHLY REPORT SAMPLE
# REPORT = {
#     "title": "JOHN SMITH",
#     "subtitle": "Monthly Report for January 2024",
#     "created_ms": 1706677200000,
#     "sections": [
#       {
#         "id": "wellness",
#         "weight": -5,
#         "title": "Care Daily Wellness",
#         "icon": "heart",
#         "color": "F47174",
#         "items": [
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Stability Score - 100%",
#             "comment_raw": "Stability Score - 100%",
#             "id": "trend-trend.stability_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Mobility Score - 51%",
#             "comment_raw": "Mobility Score - 51%",
#             "id": "trend-trend.mobility_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Social Score - 0%",
#             "comment_raw": "Social Score - 0%",
#             "id": "trend-trend.social_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Wellness Score - 85%",
#             "comment_raw": "Wellness Score - 85%",
#             "id": "trend-trend.wellness_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Sleep Score - 86%",
#             "comment_raw": "Sleep Score - 86%",
#             "id": "trend-trend.sleep_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Bedtime Score - 100%",
#             "comment_raw": "Bedtime Score - 100%",
#             "id": "trend-trend.bedtime_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Wakeup Score - 100%",
#             "comment_raw": "Wakeup Score - 100%",
#             "id": "trend-trend.wakeup_score"
#           }
#         ]
#       },
#       {
#         "id": "sleep",
#         "weight": 15,
#         "title": "Sleep",
#         "icon": "moon",
#         "color": "946C49",
#         "items": [
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Predicted Bedtime - 23.8",
#             "comment_raw": "Predicted Bedtime - 23.8",
#             "id": "insight-sleep.sleep_prediction_ms"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Predicted time to wake up - 7.0",
#             "comment_raw": "Predicted time to wake up - 7.0",
#             "id": "insight-sleep.wake_prediction_ms"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "On average, you went to sleep at 11:28 PM this month",
#             "comment_raw": "On average, you went to sleep at 11:28 PM this month",
#             "id": "insight-sleep.bedtime_ms"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "You selpt the best on Wednesday, January 17",
#             "comment_raw": "You selpt the best on Wednesday, January 17",
#             "id": "insight-sleep.sleep_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Bedtime consistency - 1.0",
#             "comment_raw": "Bedtime consistency - 1.0",
#             "id": "insight-sleep.bedtime_score"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "You woke up the latest on Thursday, January 18 at 10:30 AM.",
#             "comment_raw": "You woke up the latest on Thursday, January 18 at 10:30 AM.",
#             "id": "insight-sleep.wakeup_ms"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Your longest sleep was 8.9 hours on Thursday, January 18.",
#             "comment_raw": "Your longest sleep was 8.9 hours on Thursday, January 18.",
#             "id": "insight-sleep.duration_ms"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Underslept - 1.0",
#             "comment_raw": "Underslept - 1.0",
#             "id": "insight-sleep.underslept"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Overslept - 1.0",
#             "comment_raw": "Overslept - 1.0",
#             "id": "insight-sleep.overslept"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Bedtime - 1:14 AM on Tuesday",
#             "comment_raw": "Bedtime - 1:14 AM on Tuesday",
#             "id": "trend-trend.bedtime"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Sleep Duration - 7.0 hours",
#             "comment_raw": "Sleep Duration - 7.0 hours",
#             "id": "trend-trend.sleep_duration"
#           },
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Wake Time - 8:14 AM on Tuesday",
#             "comment_raw": "Wake Time - 8:14 AM on Tuesday",
#             "id": "trend-trend.wakeup"
#           }
#         ]
#       },
#       {
#         "id": "activities",
#         "weight": 20,
#         "title": "Activities",
#         "icon": "walking",
#         "color": "27195F",
#         "items": [
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Time spent in motion - 19 minutes",
#             "comment_raw": "Time spent in motion - 19 minutes",
#             "id": "trend-trend.mobility_duration"
#           }
#         ]
#       },
#       {
#         "id": "social",
#         "weight": 40,
#         "title": "Social",
#         "icon": "user-friends",
#         "color": "B6B038",
#         "items": [
#           {
#             "timestamp_ms": 1706677200000,
#             "comment": "Time Away from Home - 0 hours",
#             "comment_raw": "Time Away from Home - 0 hours",
#             "id": "trend-trend.absent"
#           }
#         ]
#       }
#     ],
#     "period": "monthlyreport"
#   }
# STATUS = REPORT_STATUS_COMPLETED
# METADATA = {
#     "insight-sleep.sleep_prediction_ms": {
#       "title": "Predicted Bedtime",
#       "values": {
#         "16": [22.0],
#         "17": [22.0],
#         "18": [22.716666666666665],
#         "19": [23.433333333333334],
#         "20": [23.533333333333335],
#         "21": [23.75],
#         "22": [23.866666666666667],
#         "23": [23.85],
#         "24": [24.25],
#         "25": [24.383333333333333],
#         "26": [24.433333333333334],
#         "27": [24.6],
#         "28": [24.633333333333333],
#         "29": [24.45],
#         "30": [24.55]
#       },
#       "statistics": {
#         "average": 23,
#         "max": { "value": 0.6, "index": 28 },
#         "min": { "value": 22.0, "index": 16 }
#       },
#       "reported": 23.8
#     },
#     "insight-occupancy.status": {
#       "title": "Home",
#       "values": {
#         "16": ["PRESENT", "H2S", "H2A", "H2S"],
#         "17": [
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "SLEEP",
#           "SLEEP",
#           "SLEEP"
#         ],
#         "18": [
#           "SLEEP",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "19": [
#           "S2H",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "20": [
#           "H2A",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "H2A",
#           "H2S",
#           "H2A",
#           "SLEEP"
#         ],
#         "21": [
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "A2H",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "ABSENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "22": [
#           "H2A",
#           "ABSENT",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "23": [
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2S",
#           "H2A",
#           "SLEEP",
#           "H2A",
#           "SLEEP"
#         ],
#         "24": [
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2S"
#         ],
#         "25": [
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "26": [
#           "H2A",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "PRESENT",
#           "H2S"
#         ],
#         "27": [
#           "SLEEP",
#           "H2A",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2S"
#         ],
#         "28": [
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "29": [
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "ABSENT",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2S",
#           "SLEEP"
#         ],
#         "30": [
#           "H2A",
#           "SLEEP",
#           "S2H",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "PRESENT",
#           "H2A",
#           "PRESENT",
#           "H2S"
#         ]
#       },
#       "statistics": {
#         "16": { "max": "H2S", "min": "PRESENT" },
#         "17": { "max": "PRESENT", "min": "S2H" },
#         "18": { "max": "PRESENT", "min": "S2H" },
#         "19": { "max": "PRESENT", "min": "S2H" },
#         "20": { "max": "H2A", "min": "S2H" },
#         "21": { "max": "PRESENT", "min": "S2H" },
#         "22": { "max": "PRESENT", "min": "S2H" },
#         "23": { "max": "PRESENT", "min": "S2H" },
#         "24": { "max": "PRESENT", "min": "S2H" },
#         "25": { "max": "PRESENT", "min": "S2H" },
#         "26": { "max": "PRESENT", "min": "SLEEP" },
#         "27": { "max": "PRESENT", "min": "S2H" },
#         "28": { "max": "PRESENT", "min": "S2H" },
#         "29": { "max": "PRESENT", "min": "S2H" },
#         "30": { "max": "PRESENT", "min": "SLEEP" }
#       }
#     },
#     "trend-trend.stability_score": {
#       "2024_03": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1705896000000,
#         "trend_id": "trend.stability_score",
#         "trend_category": "category.stability"
#       },
#       "2024_04": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706500800000,
#         "trend_id": "trend.stability_score",
#         "trend_category": "category.stability"
#       },
#       "2024_05": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706673600000,
#         "trend_id": "trend.stability_score",
#         "trend_category": "category.stability"
#       }
#     },
#     "trend-trend.mobility_score": {
#       "2024_03": {
#         "value": 47.608695652173914,
#         "std": 10.42,
#         "avg": 46.33,
#         "zscore": 0.12,
#         "display": "48%",
#         "updated_ms": 1705896000000,
#         "trend_id": "trend.mobility_score",
#         "trend_category": "category.activity"
#       },
#       "2024_04": {
#         "value": 46.78260869565217,
#         "std": 7.22,
#         "avg": 47.5,
#         "zscore": -0.1,
#         "display": "47%",
#         "updated_ms": 1706500800000,
#         "trend_id": "trend.mobility_score",
#         "trend_category": "category.activity"
#       },
#       "2024_05": {
#         "value": 51.17391304347826,
#         "std": 6.77,
#         "avg": 47.99,
#         "zscore": 0.47,
#         "display": "51%",
#         "updated_ms": 1706673600000,
#         "trend_id": "trend.mobility_score",
#         "trend_category": "category.activity"
#       }
#     },
#     "trend-trend.mobility_duration": {
#       "2024_03": {
#         "value": 1146572.0,
#         "std": 208335.17,
#         "avg": 969366.83,
#         "zscore": 0.85,
#         "display": "19 minutes",
#         "updated_ms": 1705896000000,
#         "trend_id": "trend.mobility_duration",
#         "trend_category": "category.activity"
#       },
#       "2024_04": {
#         "value": 1197506.0,
#         "std": 225981.26,
#         "avg": 1087001.38,
#         "zscore": 0.49,
#         "display": "20 minutes",
#         "updated_ms": 1706500800000,
#         "trend_id": "trend.mobility_duration",
#         "trend_category": "category.activity"
#       },
#       "2024_05": {
#         "value": 1139472.0,
#         "std": 214773.8,
#         "avg": 1103076.8,
#         "zscore": 0.17,
#         "display": "19 minutes",
#         "updated_ms": 1706673600000,
#         "trend_id": "trend.mobility_duration",
#         "trend_category": "category.activity"
#       }
#     },
#     "trend-trend.social_score": {
#       "2024_03": {
#         "value": 70.0,
#         "std": 46.07,
#         "avg": 62.17,
#         "zscore": 0.17,
#         "display": "70%",
#         "updated_ms": 1705896000000,
#         "trend_id": "trend.social_score",
#         "trend_category": "category.social"
#       },
#       "2024_04": {
#         "value": 0.0,
#         "std": 43.09,
#         "avg": 29.85,
#         "zscore": -0.69,
#         "display": "0%",
#         "updated_ms": 1706500800000,
#         "trend_id": "trend.social_score",
#         "trend_category": "category.social"
#       },
#       "2024_05": {
#         "value": 0.0,
#         "std": 40.72,
#         "avg": 27.0,
#         "zscore": -0.66,
#         "display": "0%",
#         "updated_ms": 1706673600000,
#         "trend_id": "trend.social_score",
#         "trend_category": "category.social"
#       }
#     },
#     "insight-security_mode": {
#       "title": "Disarmed",
#       "values": {
#         "16": ["HOME", "HOME", "HOME"],
#         "17": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "18": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "19": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "20": ["HOME", "HOME", "HOME", "HOME", "HOME", "HOME", "HOME", "HOME"],
#         "21": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "AWAY",
#           "HOME",
#           "HOME"
#         ],
#         "22": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "23": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "24": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "25": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "26": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "27": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "28": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "29": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ],
#         "30": [
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME",
#           "HOME"
#         ]
#       },
#       "statistics": {
#         "16": { "max": "HOME", "min": "HOME" },
#         "17": { "max": "HOME", "min": "HOME" },
#         "18": { "max": "HOME", "min": "HOME" },
#         "19": { "max": "HOME", "min": "HOME" },
#         "20": { "max": "HOME", "min": "HOME" },
#         "21": { "max": "HOME", "min": "AWAY" },
#         "22": { "max": "HOME", "min": "HOME" },
#         "23": { "max": "HOME", "min": "HOME" },
#         "24": { "max": "HOME", "min": "HOME" },
#         "25": { "max": "HOME", "min": "HOME" },
#         "26": { "max": "HOME", "min": "HOME" },
#         "27": { "max": "HOME", "min": "HOME" },
#         "28": { "max": "HOME", "min": "HOME" },
#         "29": { "max": "HOME", "min": "HOME" },
#         "30": { "max": "HOME", "min": "HOME" }
#       }
#     },
#     "insight-sleep.wake_prediction_ms": {
#       "title": "Predicted time to wake up",
#       "values": {
#         "17": [31.0, 31.0, 31.0],
#         "18": [29.666666666666668],
#         "19": [30.78333333333333],
#         "20": [30.71666666666667],
#         "21": [31.816666666666666],
#         "22": [30.816666666666666],
#         "23": [31.3],
#         "25": [31.0, 31.0, 31.083333333333332],
#         "27": [31.0, 31.0],
#         "28": [32.53333333333333, 32.53333333333333, 31.166666666666668],
#         "29": [30.666666666666668]
#       },
#       "statistics": {
#         "average": 22.6,
#         "max": { "value": 8.1, "index": 29 },
#         "min": { "value": 5.7, "index": 21 }
#       },
#       "reported": 7.0
#     },
#     "insight-sleep.bedtime_ms": {
#       "title": "Likely asleep",
#       "values": {
#         "17": [24.016666666666666, 22.366666666666667, 23.35, 23.35],
#         "18": [24.633333333333333, 29.383333333333333, 22.416666666666668],
#         "19": [22.816666666666666],
#         "20": [26.983333333333334, 23.916666666666668],
#         "21": [23.783333333333335],
#         "22": [25.266666666666666, 22.9],
#         "23": [23.483333333333334, 23.533333333333335],
#         "25": [24.883333333333333, 23.55],
#         "26": [24.6],
#         "27": [24.033333333333335, 25.133333333333333],
#         "28": [24.033333333333335, 23.833333333333332],
#         "29": [23.733333333333334],
#         "30": [24.95]
#       },
#       "statistics": {
#         "average": 23.5,
#         "max": { "value": 1.5, "index": 19 },
#         "min": { "value": 22.8, "index": 20 }
#       },
#       "reported": 0.2
#     },
#     "trend-trend.wellness_score": {
#       "2024_03": {
#         "value": 94.625,
#         "std": 2.29,
#         "avg": 93.31,
#         "zscore": 0.57,
#         "display": "94%",
#         "updated_ms": 1705896000000,
#         "trend_id": "trend.wellness_score",
#         "trend_category": "category.summary"
#       },
#       "2024_04": {
#         "value": 88.20833333333333,
#         "std": 2.17,
#         "avg": 92.04,
#         "zscore": -1.77,
#         "display": "88%",
#         "updated_ms": 1706500800000,
#         "trend_id": "trend.wellness_score",
#         "trend_category": "category.summary"
#       },
#       "2024_05": {
#         "value": 85.29166666666667,
#         "std": 3.94,
#         "avg": 90.75,
#         "zscore": -1.39,
#         "display": "85%",
#         "updated_ms": 1706673600000,
#         "trend_id": "trend.wellness_score",
#         "trend_category": "category.summary"
#       }
#     },
#     "trend-trend.bedtime": {
#       "2024_03": {
#         "value": 25.616666666666667,
#         "std": 2.23,
#         "avg": 26.03,
#         "zscore": -0.19,
#         "display": "1:37 AM on Sunday",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.bedtime",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 25.78333333333333,
#         "std": 1.46,
#         "avg": 25.63,
#         "zscore": 0.11,
#         "display": "1:47 AM on Sunday",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.bedtime",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 25.233333333333334,
#         "std": 1.37,
#         "avg": 25.53,
#         "zscore": -0.22,
#         "display": "1:14 AM on Tuesday",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.bedtime",
#         "trend_category": "category.sleep"
#       }
#     },
#     "insight-sleep.sleep_score": {
#       "title": "Sleep score",
#       "values": {
#         "17": [0.8579869407740491],
#         "18": [0.6628101869541569],
#         "19": [0.8024332756212817],
#         "20": [0.9676062754347909],
#         "21": [0.8459053063615589],
#         "22": [0.9805015604720321],
#         "23": [0.9155361850892416],
#         "24": [0.999374559508769],
#         "25": [0.9653435433064927],
#         "26": [0.9566524338478068],
#         "27": [0.8287051701067493],
#         "28": [0.7165183435599657],
#         "29": [0.7824581527621255],
#         "30": [0.8612411982259066]
#       },
#       "statistics": {
#         "average": 23.5,
#         "max": { "value": 1.0, "index": 24 },
#         "min": { "value": 0.7, "index": 18 }
#       },
#       "reported": 0.9
#     },
#     "insight-sleep.bedtime_score": {
#       "title": "Bedtime consistency",
#       "values": {
#         "17": [1.0],
#         "18": [1.0],
#         "19": [1.0],
#         "20": [1.0],
#         "21": [1.0],
#         "22": [1.0],
#         "23": [1.0],
#         "24": [1.0],
#         "25": [1.0],
#         "26": [1.0],
#         "27": [1.0],
#         "28": [1.0],
#         "29": [1.0],
#         "30": [1.0]
#       },
#       "statistics": {
#         "average": 23.5,
#         "max": { "value": 1.0, "index": 17 },
#         "min": { "value": 1.0, "index": 17 }
#       },
#       "reported": 1.0
#     },
#     "insight-sleep.wakeup_ms": {
#       "title": "Good morning",
#       "values": {
#         "17": [30.866666666666667],
#         "18": [14.316666666666666],
#         "19": [31.066666666666666],
#         "20": [34.5],
#         "21": [32.53333333333333],
#         "22": [31.15],
#         "23": [30.666666666666668],
#         "24": [30.883333333333333],
#         "25": [30.8],
#         "26": [30.78333333333333],
#         "27": [33.28333333333333],
#         "28": [31.833333333333332],
#         "29": [30.733333333333334],
#         "30": [32.233333333333334]
#       },
#       "statistics": {
#         "average": 23.5,
#         "max": { "value": 10.5, "index": 20 },
#         "min": { "value": 14.3, "index": 18 }
#       },
#       "reported": 6.4
#     },
#     "insight-sleep.duration_ms": {
#       "title": "Sleep Duration",
#       "values": {
#         "17": [6.9],
#         "18": [8.9],
#         "19": [6.9],
#         "20": [7.5],
#         "21": [6.9],
#         "22": [5.6],
#         "23": [6.0],
#         "24": [5.7],
#         "25": [4.4],
#         "26": [6.0],
#         "27": [8.1],
#         "28": [6.1],
#         "29": [6.2],
#         "30": [7.0]
#       },
#       "statistics": {
#         "average": 23.5,
#         "max": { "value": 8.9, "index": 18 },
#         "min": { "value": 4.4, "index": 25 }
#       },
#       "reported": 6.6
#     },
#     "trend-trend.sleep_score": {
#       "2024_03": {
#         "value": 84.0,
#         "std": 10.83,
#         "avg": 82.2,
#         "zscore": 0.17,
#         "display": "84%",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.sleep_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 71.0,
#         "std": 10.83,
#         "avg": 86.92,
#         "zscore": -1.47,
#         "display": "71%",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.sleep_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 86.0,
#         "std": 10.24,
#         "avg": 86.21,
#         "zscore": -0.02,
#         "display": "86%",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.sleep_score",
#         "trend_category": "category.sleep"
#       }
#     },
#     "trend-trend.bedtime_score": {
#       "2024_03": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.bedtime_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.bedtime_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.bedtime_score",
#         "trend_category": "category.sleep"
#       }
#     },
#     "trend-trend.wakeup_score": {
#       "2024_03": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.wakeup_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.wakeup_score",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 100.0,
#         "std": 0.0,
#         "avg": 100.0,
#         "zscore": 0.0,
#         "display": "100%",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.wakeup_score",
#         "trend_category": "category.sleep"
#       }
#     },
#     "trend-trend.sleep_duration": {
#       "2024_03": {
#         "value": 24908706.0,
#         "std": 3173588.02,
#         "avg": 26731398.2,
#         "zscore": -0.57,
#         "display": "6.9 hours",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.sleep_duration",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 21793098.0,
#         "std": 4398678.99,
#         "avg": 23725010.5,
#         "zscore": -0.44,
#         "display": "6.1 hours",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.sleep_duration",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 25180861.0,
#         "std": 4089143.59,
#         "avg": 23717806.86,
#         "zscore": 0.36,
#         "display": "7.0 hours",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.sleep_duration",
#         "trend_category": "category.sleep"
#       }
#     },
#     "trend-trend.wakeup": {
#       "2024_03": {
#         "value": 8.533333333333333,
#         "std": 3.08,
#         "avg": 9.46,
#         "zscore": -0.3,
#         "display": "8:32 AM on Sunday",
#         "updated_ms": 1705843936414,
#         "trend_id": "trend.wakeup",
#         "trend_category": "category.sleep"
#       },
#       "2024_04": {
#         "value": 7.833333333333333,
#         "std": 2.26,
#         "avg": 8.22,
#         "zscore": -0.17,
#         "display": "7:50 AM on Sunday",
#         "updated_ms": 1706446230312,
#         "trend_id": "trend.wakeup",
#         "trend_category": "category.sleep"
#       },
#       "2024_05": {
#         "value": 8.233333333333333,
#         "std": 2.12,
#         "avg": 8.12,
#         "zscore": 0.05,
#         "display": "8:14 AM on Tuesday",
#         "updated_ms": 1706620479482,
#         "trend_id": "trend.wakeup",
#         "trend_category": "category.sleep"
#       }
#     },
#     "trend-trend.absent": {
#       "2024_03": {
#         "value": 8104419.0,
#         "std": 4961286.74,
#         "avg": 4596259.5,
#         "zscore": 0.71,
#         "display": "2 hours",
#         "updated_ms": 1705896768000,
#         "trend_id": "trend.absent",
#         "trend_category": "category.social"
#       },
#       "2024_04": {
#         "value": 312696.0,
#         "std": 2908200.6,
#         "avg": 1555262.14,
#         "zscore": -0.43,
#         "display": "0 hours",
#         "updated_ms": 1706381954847,
#         "trend_id": "trend.absent",
#         "trend_category": "category.social"
#       },
#       "2024_05": {
#         "value": 1910387.0,
#         "std": 2695396.44,
#         "avg": 1599652.75,
#         "zscore": 0.12,
#         "display": "0 hours",
#         "updated_ms": 1706548239275,
#         "trend_id": "trend.absent",
#         "trend_category": "category.social"
#       }
#     },
#     "insight-sleep.underslept": {
#       "title": "Underslept",
#       "values": { "22": [True], "24": [True], "25": [True] },
#       "statistics": {
#         "average": 23.7,
#         "max": { "value": 1, "index": 28 },
#         "min": { "value": 1, "index": 28 }
#       },
#       "reported": 1.0
#     },
#     "insight-sleep.overslept": {
#       "title": "Overslept",
#       "values": { "27": [True] },
#       "statistics": {
#         "average": 27,
#         "max": { "value": 1, "index": 30 },
#         "min": { "value": 1, "index": 30 }
#       },
#       "reported": 1.0
#     }
#   }

# MOCKED DAILY REPORT SAMPLE
REPORT = {
    "title": "JOHN SMITH",
    "subtitle": "Daily Report for January 2024",
    "created_ms": 1706677200000,
    "sections": [
      {
        "id": "wellness",
        "weight": -5,
        "title": "Care Daily Wellness",
        "icon": "heart",
        "color": "F47174",
        "items": [
          {
            "timestamp_ms": 1706677200000,
            "comment": "Stability Score - 100%",
            "comment_raw": "Stability Score - 100%",
            "id": "trend-trend.stability_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Mobility Score - 51%",
            "comment_raw": "Mobility Score - 51%",
            "id": "trend-trend.mobility_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Social Score - 0%",
            "comment_raw": "Social Score - 0%",
            "id": "trend-trend.social_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Wellness Score - 85%",
            "comment_raw": "Wellness Score - 85%",
            "id": "trend-trend.wellness_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Sleep Score - 86%",
            "comment_raw": "Sleep Score - 86%",
            "id": "trend-trend.sleep_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Bedtime Score - 100%",
            "comment_raw": "Bedtime Score - 100%",
            "id": "trend-trend.bedtime_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Wakeup Score - 100%",
            "comment_raw": "Wakeup Score - 100%",
            "id": "trend-trend.wakeup_score"
          }
        ]
      },
      {
        "id": "sleep",
        "weight": 15,
        "title": "Sleep",
        "icon": "moon",
        "color": "946C49",
        "items": [
          {
            "timestamp_ms": 1706677200000,
            "comment": "Predicted Bedtime - 23.8",
            "comment_raw": "Predicted Bedtime - 23.8",
            "id": "insight-sleep.sleep_prediction_ms"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Predicted time to wake up - 7.0",
            "comment_raw": "Predicted time to wake up - 7.0",
            "id": "insight-sleep.wake_prediction_ms"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "On average, you went to sleep at 11:28 PM this month",
            "comment_raw": "On average, you went to sleep at 11:28 PM this month",
            "id": "insight-sleep.bedtime_ms"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "You selpt the best on Wednesday, January 17",
            "comment_raw": "You selpt the best on Wednesday, January 17",
            "id": "insight-sleep.sleep_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Bedtime consistency - 1.0",
            "comment_raw": "Bedtime consistency - 1.0",
            "id": "insight-sleep.bedtime_score"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "You woke up the latest on Thursday, January 18 at 10:30 AM.",
            "comment_raw": "You woke up the latest on Thursday, January 18 at 10:30 AM.",
            "id": "insight-sleep.wakeup_ms"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Your longest sleep was 8.9 hours on Thursday, January 18.",
            "comment_raw": "Your longest sleep was 8.9 hours on Thursday, January 18.",
            "id": "insight-sleep.duration_ms"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Underslept - 1.0",
            "comment_raw": "Underslept - 1.0",
            "id": "insight-sleep.underslept"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Overslept - 1.0",
            "comment_raw": "Overslept - 1.0",
            "id": "insight-sleep.overslept"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Bedtime - 1:14 AM on Tuesday",
            "comment_raw": "Bedtime - 1:14 AM on Tuesday",
            "id": "trend-trend.bedtime"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Sleep Duration - 7.0 hours",
            "comment_raw": "Sleep Duration - 7.0 hours",
            "id": "trend-trend.sleep_duration"
          },
          {
            "timestamp_ms": 1706677200000,
            "comment": "Wake Time - 8:14 AM on Tuesday",
            "comment_raw": "Wake Time - 8:14 AM on Tuesday",
            "id": "trend-trend.wakeup"
          }
        ]
      },
      {
        "id": "activities",
        "weight": 20,
        "title": "Activities",
        "icon": "walking",
        "color": "27195F",
        "items": [
          {
            "timestamp_ms": 1706677200000,
            "comment": "Time spent in motion - 19 minutes",
            "comment_raw": "Time spent in motion - 19 minutes",
            "id": "trend-trend.mobility_duration"
          }
        ]
      },
      {
        "id": "social",
        "weight": 40,
        "title": "Social",
        "icon": "user-friends",
        "color": "B6B038",
        "items": [
          {
            "timestamp_ms": 1706677200000,
            "comment": "Time Away from Home - 0 hours",
            "comment_raw": "Time Away from Home - 0 hours",
            "id": "trend-trend.absent"
          }
        ]
      }
    ],
    "period": "dailyreport"
  }
STATUS = REPORT_STATUS_COMPLETED
METADATA = {}

DELAY_MS = 0 # Send immediately

# Data Stream Content
DATASTREAM_CONTENT = {
    "report": REPORT,
    "status": STATUS,
    "metadata": METADATA,
    "delay_ms": 0
}


# input function behaves differently in Python 2.x and 3.x. And there is no raw_input in 3.x.
if hasattr(__builtins__, 'raw_input'):
    input=raw_input

import requests
import sys
import json
import logging

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

def main(argv=None):

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    
    parser.add_argument("-u", "--username", dest="username", help="Username")
    parser.add_argument("-p", "--password", dest="password", help="Password")
    parser.add_argument("-s", "--server", dest="server", help="Base server URL (app.peoplepowerco.com)")
    parser.add_argument("-l", "--location", dest="location_id", help="Location ID")
    parser.add_argument("-a", "--api_key", dest="apikey", help="User's API key instead of a username/password")
    parser.add_argument("--httpdebug", dest="httpdebug", action="store_true", help="HTTP debug logger output");
    
    # Process arguments
    args, unknown = parser.parse_known_args()
    
    # Extract the arguments
    username = args.username
    password = args.password
    server = args.server
    httpdebug = args.httpdebug
    app_key = args.apikey
    location_id = args.location_id

    if location_id is not None:
        location_id = int(location_id)
        print(Color.BOLD + "Location ID: {}".format(location_id) + Color.END)

    # Define the bot server
    if not server:
        server = "https://app.peoplepowerco.com"
    
    if "http" not in server:
        server = "https://" + server

    # HTTP Debugging
    if httpdebug:
        try:
            import http.client as http_client
                
        except ImportError:
            # Python 2
            import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
                    
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        
    # Login to your user account
    if app_key is None:
        app_key, user_info = _login(server, username, password)

    send_datastream_message(server, app_key, location_id, DATASTREAM_ADDRESS, DATASTREAM_CONTENT)
    print("Done!")
    
    
def send_datastream_message(server, app_key, location_id, address, content):
    http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
    
    params = {
              "address": address,
              "scope": 1,
              "locationId": location_id
              }
    
    body = {
        "feed": content
        }
    
    print("Body: " + json.dumps(body, indent=2, sort_keys=True))
    print("Server: " + server)
    
    r = requests.post(server + "/cloud/appstore/stream", params=params, data=json.dumps(body), headers=http_headers)
    j = json.loads(r.text)
    _check_for_errors(j)
    print(str(r.text))
    
    
def _login(server, username, password):
    """Get an Bot API key and User Info by login with a username and password"""

    if not username:
        username = raw_input('Email address: ')
        
    if not password:
        import getpass
        password = getpass.getpass('Password: ')
    
    try:
        import requests

        # login by username and password
        http_headers = {"PASSWORD": password, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/login", params={"username":username}, headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        app_key = j['key']

        # get user info
        http_headers = {"API_KEY": app_key, "Content-Type": "application/json"}
        r = requests.get(server + "/cloud/json/user", headers=http_headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        return app_key, j

    except BotError as e:
        sys.stderr.write("Error: " + e.msg)
        sys.stderr.write("\nCreate an account on " + server + " and use it to sign in")
        sys.stderr.write("\n\n")
        raise e
    
    

def _check_for_errors(json_response):
    """Check some JSON response for BotEngine errors"""
    if not json_response:
        raise BotError("No response from the server!", -1)
    
    if json_response['resultCode'] > 0:
        msg = "Unknown error!"
        if 'resultCodeMessage' in json_response.keys():
            msg = json_response['resultCodeMessage']
        elif 'resultCodeDesc' in json_response.keys():
            msg = json_response['resultCodeDesc']
        raise BotError(msg, json_response['resultCode'])

    del(json_response['resultCode'])
    
    
    
class BotError(Exception):
    """BotEngine exception to raise and log errors."""
    def __init__(self, msg, code):
        super(BotError).__init__(type(self))
        self.msg = msg
        self.code = code
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg


#===============================================================================
# Color Class for CLI
#===============================================================================
class Color:
    """Color your command line output text with Color.WHATEVER and Color.END"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

if __name__ == "__main__":
    sys.exit(main())




