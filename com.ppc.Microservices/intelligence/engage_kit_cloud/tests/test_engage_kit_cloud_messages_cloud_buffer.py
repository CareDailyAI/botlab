
from botengine_pytest import BotEnginePyTest

# import utilities.utilities as utilities


from intelligence.engage_kit_cloud.types.messages_cloud_buffer import MessagesCloudBuffer
from intelligence.engage_kit_cloud.types.messages_priority_calculator import PriorityCalculator
from intelligence.engage_kit_cloud.types.cloud_model import BotMessage
from intelligence.engage_kit_cloud.types.cloud_model import BotUpdatedMessage

CLOUD_SCHEDULE_INTERVAL_S = 60

import heapq
import itertools
import utilities.utilities as utilities

import unittest
from unittest.mock import MagicMock, patch

class TestEngageKitCloudMessagesCloudBuffer(unittest.TestCase):

    def test_engage_kit_cloud_messages_cloud_buffer(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["messages_cloud_buffer"] # Uncomment to see logging
        priority_calculation = PriorityCalculator.custom_priority_calculation
        mut = MessagesCloudBuffer(botengine, priority_calculation)
        assert mut is not None
        mut._buffer == []
        mut.entry_finder == {}
        mut.REMOVED == '<removed-message>'
        mut.counter == itertools.count()
        mut.calculate_priority == priority_calculation

    def test_engage_kit_cloud_messages_cloud_buffer_message_scheduling_future(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["messages_cloud_buffer"] # Uncomment to see logging
        priority_calculation = PriorityCalculator.custom_priority_calculation
        mut = MessagesCloudBuffer(botengine, priority_calculation)
        assert mut is not None

        current_timestamp_ms = 1719420318000 # Wed Jun 26 2024 09:45:18 GMT-0700
        midnight_timestamp_s = 1719385200 # Wed Jun 26 2024 00:00:00 GMT-0700
        
        message_1_delivery_date_s = 35218 # 9:46:58
        message_2_delivery_date_s = 35278 # 9:47:58
        message_3_delivery_date_s = 35338 # 9:48:58
        message_4_delivery_date_s = 35338 # 9:48:58 (same as message 3)

        messages = [
            BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
            BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None), 
            BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
            BotMessage(message_id=4, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_4_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
        ]

        mut.add_messages_with_priority(botengine, messages, [])

        assert mut._buffer == [
            [message_1_delivery_date_s, 1, 0, BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)], 
            [message_2_delivery_date_s, 1, 1, BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
            [message_3_delivery_date_s, 1, 2, BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
            [message_4_delivery_date_s, 1, 3, BotMessage(message_id=4, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_4_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
        ]

        scheduled_messages = mut.get_scheduled_messages_with_adjusted_delivery_times(botengine, CLOUD_SCHEDULE_INTERVAL_S, midnight_timestamp_s, current_timestamp_ms / 1000)

        assert scheduled_messages == [
            BotUpdatedMessage(messageId=1, status=2, delivery_date=f"{(midnight_timestamp_s + message_1_delivery_date_s) * 1000}", schedule=None),
            BotUpdatedMessage(messageId=2, status=2, delivery_date=f"{(midnight_timestamp_s + message_2_delivery_date_s) * 1000}", schedule=None),
            BotUpdatedMessage(messageId=3, status=2, delivery_date=f"{(midnight_timestamp_s + message_3_delivery_date_s) * 1000}", schedule=None),
            BotUpdatedMessage(messageId=4, status=2, delivery_date=f"{(midnight_timestamp_s + message_4_delivery_date_s + CLOUD_SCHEDULE_INTERVAL_S) * 1000}", schedule=None),
        ]

    def test_engage_kit_cloud_messages_cloud_buffer_message_scheduling_past(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["messages_cloud_buffer"] # Uncomment to see logging
        priority_calculation = PriorityCalculator.custom_priority_calculation
        mut = MessagesCloudBuffer(botengine, priority_calculation)
        assert mut is not None

        current_timestamp_ms = 1719420408000 # Wed Jun 26 2024 09:46:48 GMT-0700
        midnight_timestamp_s = 1719385200 # Wed Jun 26 2024 00:00:00 GMT-0700
        
        message_1_delivery_date_s = 35178 # 9:46:18
        message_2_delivery_date_s = 35238 # 9:47:18
        message_3_delivery_date_s = 35298 # 9:48:18

        messages = [
            BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
            BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None), 
            BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
        ]

        mut.add_messages_with_priority(botengine, messages, [])

        assert mut._buffer == [
            [message_1_delivery_date_s, 1, 0, BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)], 
            [message_2_delivery_date_s, 1, 1, BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
            [message_3_delivery_date_s, 1, 2, BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
        ]

        scheduled_messages = mut.get_scheduled_messages_with_adjusted_delivery_times(botengine, CLOUD_SCHEDULE_INTERVAL_S, midnight_timestamp_s, current_timestamp_ms / 1000)

        assert scheduled_messages == [
            BotUpdatedMessage(messageId=1, status=2, delivery_date=f"{int(current_timestamp_ms + (CLOUD_SCHEDULE_INTERVAL_S * 1000))}", schedule=None),
            BotUpdatedMessage(messageId=2, status=2, delivery_date=f"{int(current_timestamp_ms + (CLOUD_SCHEDULE_INTERVAL_S * 2000))}", schedule=None),
            BotUpdatedMessage(messageId=3, status=2, delivery_date=f"{int(current_timestamp_ms + (CLOUD_SCHEDULE_INTERVAL_S * 3000))}", schedule=None),
        ]

    def test_engage_kit_cloud_messages_cloud_buffer_message_scheduling_unordered(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["messages_cloud_buffer"] # Uncomment to see logging
        priority_calculation = PriorityCalculator.custom_priority_calculation
        mut = MessagesCloudBuffer(botengine, priority_calculation)
        assert mut is not None

        current_timestamp_ms = 1719420318000 # Wed Jun 26 2024 09:45:18 GMT-0700
        midnight_timestamp_s = 1719385200 # Wed Jun 26 2024 00:00:00 GMT-0700
        
        message_1_delivery_date_s = 35218 # 9:46:58
        message_2_delivery_date_s = 35338 # 9:48:58
        message_3_delivery_date_s = 35278 # 9:47:58

        messages = [
            BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
            BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None),
            BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None), 
        ]

        mut.add_messages_with_priority(botengine, messages, [])

        assert mut._buffer == [
            [message_1_delivery_date_s, 1, 0, BotMessage(message_id=1, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 1', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_1_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)], 
            [message_3_delivery_date_s, 1, 1, BotMessage(message_id=3, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 3', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_3_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
            [message_2_delivery_date_s, 1, 2, BotMessage(message_id=2, original_message_id=None, schedule_type=0, status=1, topic_id='welcome', app_instance_id=1, content_key='Message 2', content_text=None, creation_time=current_timestamp_ms, max_delivery_time=current_timestamp_ms + utilities.ONE_DAY_MS, delivery_day_time=message_2_delivery_date_s, time_to_live=3600, delivery_time=None, lang=None, schedule=None, delivery_date=None)],
        ]

        scheduled_messages = mut.get_scheduled_messages_with_adjusted_delivery_times(botengine, CLOUD_SCHEDULE_INTERVAL_S, midnight_timestamp_s, current_timestamp_ms / 1000)

        assert scheduled_messages == [
            BotUpdatedMessage(messageId=1, status=2, delivery_date=f"{(midnight_timestamp_s + message_1_delivery_date_s) * 1000}", schedule=None),
            BotUpdatedMessage(messageId=3, status=2, delivery_date=f"{(midnight_timestamp_s + message_3_delivery_date_s) * 1000}", schedule=None),
            BotUpdatedMessage(messageId=2, status=2, delivery_date=f"{(midnight_timestamp_s + message_2_delivery_date_s) * 1000}", schedule=None),
        ]