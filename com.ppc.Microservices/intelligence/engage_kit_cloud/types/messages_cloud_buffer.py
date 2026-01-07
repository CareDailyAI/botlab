'''
Created on October 16, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import json
from pydantic import ValidationError
from typing import List
from collections import defaultdict
from datetime import datetime
from intelligence.engage_kit_cloud.types.cloud_model import BotMessage, BotUpdatedMessage, CloudTopicPriority, CloudMessageStatus
from intelligence.engage_kit_cloud.types.messages_counter import MessagesCounter

import heapq
import itertools

class MessagesCloudBuffer:

    def __init__(self, botengine, calculate_priority):
        # list of entries arranged in a heap
        self._buffer = []
        # mapping of messages to entries
        self.entry_finder = {}
        # placeholder for a removed message
        self.REMOVED = '<removed-message>'
        # unique sequence count
        self.counter = MessagesCounter()
        # callback to calculate priority of topics
        self.calculate_priority = calculate_priority

    def add_messages_with_priority(self, botengine, messages: List[BotMessage], phrases: List[dict]):
        """
        Add messages to the buffer with calculated priority.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">add_messages_with_priority()")
        # Filter Messages (not 'DELIVERED') and Group by Topic ID
        topics = defaultdict(list)

        # Sort unprioritized messages by delivery_day_time
        messages.sort(key=lambda x: x.delivery_day_time)

        # Group messages by topic_id
        for msg in messages:
            if msg.status != CloudMessageStatus.DELIVERED.value:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|add_messages_with_priority() appending message_id={}, status={}".format(msg.message_id, msg.status))
                topics[msg.topic_id].append(msg)

        # Concatenate Content and Calculate Priority for each Topic
        topic_priorities = {}
        from statistics import mean
        for topic_id, msgs in topics.items():
            for msg in msgs:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|add_messages_with_priority() message_id={}, topic_id={}, priority_phrase={}, priority={}".format(msg.message_id, msg.topic_id, msg.priority_phrase(), self.calculate_priority(msg.priority_phrase())))

            topic_priorities[topic_id] = CloudTopicPriority(round(mean([self.calculate_priority(msg.priority_phrase(), phrases).value for msg in msgs])))

        # Add Messages to the Buffer
        for topic_id, msgs in topics.items():
            for msg in msgs:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|add_messages_with_priority() adding message_id={}, topic_id={}, priority={}".format(msg.message_id, msg.topic_id, topic_priorities[topic_id]))
                self.add_message(botengine, msg, topic_priorities[topic_id])
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<add_messages_with_priority()")

    def get_scheduled_messages_with_adjusted_delivery_times(self, botengine, time_threshold: int, midnight_timestamp_s: int, current_timestamp_s):
        """
        Adjust the delivery_time of messages in the buffer.
        :param time_threshold: The threshold in milliseconds that determines how close the delivery times can be for messages of the same topic.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_scheduled_messages_with_adjusted_delivery_times()")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() time_threshold={} midnight_timestamp_s={}".format(time_threshold, midnight_timestamp_s))
        # list of updated messages to be scheduled
        list_of_bot_updated_messages = []
        # Temporary storage for the last delivery time per topic
        last_delivery_time_per_topic = {}

        # Iterate through the sorted messages in the buffer
        for _scheduled_time, _priority, _count, message in self._buffer:
            if message is not self.REMOVED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|get_scheduled_messages_with_adjusted_delivery_times() check message buffer...")

                # Set initial delivery_date to delivery_day_time
                delivery_date = message.delivery_day_time

                # Get the last delivery time for the message's topic
                last_delivery_time = last_delivery_time_per_topic.get(message.topic_id)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|get_scheduled_messages_with_adjusted_delivery_times() \tlast_delivery_time={}".format(last_delivery_time))

                # check if message is not scheduled yet

                if message.status == CloudMessageStatus.READY.value:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tScheduling. message={}".format(message))
                    # If the time is in the past then adjust it based on the current time
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tcurrent_timestamp_s={}, midnight_timestamp_s={}, delivery_date={}".format(current_timestamp_s, midnight_timestamp_s, delivery_date))
                    if current_timestamp_s - midnight_timestamp_s + time_threshold > delivery_date:
                        delivery_date = current_timestamp_s - midnight_timestamp_s + time_threshold
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tadjusted delivery time based on current time.")

                    # If there's a previous message for the same topic and the time is close, adjust it
                    if last_delivery_time is not None:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tChecking for adjustments. {} < {}".format(delivery_date - last_delivery_time, time_threshold))
                        if (delivery_date - last_delivery_time) < time_threshold:
                            delivery_date = min(last_delivery_time + time_threshold, (message.max_delivery_time / 1000) - midnight_timestamp_s)
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tadjusted delivery time based on threshold. min({}, {})".format(last_delivery_time + time_threshold, (message.max_delivery_time / 1000) - midnight_timestamp_s))
                    status = CloudMessageStatus.SCHEDULED.value
                    updated_message = BotUpdatedMessage.from_bot_message(message)
                    updated_message.status = status
                    updated_delivery_date_ms = (midnight_timestamp_s + delivery_date) * 1000
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_scheduled_messages_with_adjusted_delivery_times() \tupdated_delivery_date_ms={}".format(updated_delivery_date_ms))
                    updated_message.delivery_date = f"{int(updated_delivery_date_ms)}"

                    list_of_bot_updated_messages.append(updated_message)

                # Update the last delivery time for the topic
                if last_delivery_time_per_topic.get(message.topic_id, 0) < delivery_date:
                    last_delivery_time_per_topic[message.topic_id] = delivery_date

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_scheduled_messages_with_adjusted_delivery_times() list_of_bot_updated_messages={}".format(list_of_bot_updated_messages))
        return list_of_bot_updated_messages

    def clear_buffer(self, botengine):
        """
        Empty the buffer, removing all messages and resetting state.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">clear_buffer()")
        self._buffer.clear()  # Clear the heap
        self.entry_finder.clear()  # Clear the entry finder dictionary

        #  reset the counter.
        self.counter = MessagesCounter()
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<clear_buffer()")

    def add_message(self, botengine, message: BotMessage, priority: CloudTopicPriority):
        """
        Add a new message or update the scheduled_time or priority of an existing message.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">add_message()")
        if message in self.entry_finder:
            self.remove_message(botengine, message)
        count = next(self.counter)
        entry = [message.delivery_day_time, -priority.value, count, message]
        self.entry_finder[message] = entry
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|add_message() _buffer={} entry={}".format(self._buffer, entry))
        heapq.heappush(self._buffer, entry)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<add_message()")
        pass

    def remove_message(self, botengine, message: BotMessage):
        """
        Mark an existing message as REMOVED. Raise KeyError if not found.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">remove_message()")
        entry = self.entry_finder.pop(message)
        entry[-1] = self.REMOVED
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<remove_message()")
        pass

    def get_next_message(self, botengine) -> BotMessage:
        """
        Returns the next message and removes it from the buffer. Returns None if buffer is empty.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_next_message()")
        while self._buffer:
            scheduled_time, priority, count, message = heapq.heappop(self._buffer)
            if message is not self.REMOVED:
                del self.entry_finder[message]
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_next_message() message={}".format(message))
                return message
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_next_message() No message")
        return None

    def get_closest_scheduled_message(self, botengine) -> (int, BotMessage):
        """
        Returns the scheduled time of the next message in the buffer, or None if buffer is empty.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_closest_scheduled_message()")
        for i in range(len(self._buffer)):
            scheduled_time, priority, count, message = self._buffer[i]
            if message is not self.REMOVED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_closest_scheduled_message() scheduled_time={}, message={}".format(scheduled_time, message))
                return scheduled_time, message
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_closest_scheduled_message() No message")
        return (None, None)

    def remove_messages_by_ids(self, botengine, message_ids: list):
        """
        Remove messages by their IDs.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">remove_messages_by_ids()")
        for message_id in message_ids:
            messages_to_remove = [message for _scheduled_time, _priority, _count, message in self._buffer if
                                  message.message_id == message_id and message is not self.REMOVED]
            for message in messages_to_remove:
                self.remove_message(botengine, message)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<remove_messages_by_ids()")
        pass


    def remove_messages_by_topic_ids(self, botengine, topic_ids: list):
        """
        Remove messages by their topic IDs.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">remove_messages_by_topic_ids()")
        if not topic_ids:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<remove_messages_by_topic_ids() No topic IDs")
            return

        for _scheduled_time, _priority, _count, message in self._buffer:
            if message is not self.REMOVED and message.topic_id in topic_ids:
                self.remove_message(botengine, message)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<remove_messages_by_topic_ids()")
        pass

    def find_message_by_id(self, botengine, message_id: str) -> BotMessage:
        """
        Find a message by its ID.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">find_message_by_id()")
        for _scheduled_time, _priority, _count, message in self._buffer:
            if message is not self.REMOVED and message.message_id == message_id:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<find_message_by_id() message={}".format(message))
                return message
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<find_message_by_id() Message not found")
        return None

    def get_priority_of_topic_by_message(self, botengine, message: BotMessage) -> CloudTopicPriority:
        """
        Return the priority of messages that belong to the same topic as the given message.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_priority_of_topic_by_message()")
        entry = self.entry_finder.get(message)
        if entry is not None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_priority_of_topic_by_message() priority={}".format(-entry[1]))
            return CloudTopicPriority(-entry[1])
        else:
            raise ValueError("Message not found in entry_finder")

    def get_priority_of_topic(self, botengine, topic_id: str) -> CloudTopicPriority:
        """
        Return the priority of messages that belong to the same topic ID.
        If no messages with the given topic ID are found, return None.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_priority_of_topic()")
        for _scheduled_time, _priority, _count, message in self._buffer:
            if message is not self.REMOVED and message.topic_id == topic_id:
                entry = self.entry_finder.get(message)
                if entry is not None:
                    scheduled_time, priority, count = entry[:3]
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_priority_of_topic() priority={}".format(-priority))
                    return CloudTopicPriority(-priority)  # convert back to positive priority value
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_priority_of_topic() No message")
        return None

    def update_message(self, botengine, new_message: BotMessage, new_priority: CloudTopicPriority=None):
        """
        Update an existing message with a new message.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">update_message()")
        # Find the old message with the same ID
        old_message = self.find_message_by_id(botengine, new_message.message_id)
        if old_message is None:
            raise ValueError("Message with ID {} not found".format(new_message.message_id))

        if new_priority is None:
            # Get the priority of the old message
            priority = self.get_priority_of_topic_by_message(botengine, old_message)
        else:
            priority = new_priority

        # Remove the old message
        self.remove_message(botengine, old_message)

        # Insert the new message with the old priority
        self.add_message(botengine, new_message, priority)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<update_message()")


