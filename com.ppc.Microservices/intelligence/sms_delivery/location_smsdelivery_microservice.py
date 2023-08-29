'''
Created on August 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

import properties
import signals.analytics as analytics

# How fast can Presence Family type?
CHARACTERS_PER_MINUTE = 600

# Timer reference
TIMER_REFERENCE = "sms"

class LocationSmsDeliveryMicroservice(Intelligence):
    """
    Listen for data stream messages that contain SMS message content
    and add delays between a series of messages to encourage them to arrive in the correct order.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # SMS buffer
        self.sms_buffer = []

    def send_sms(self, botengine, content):
        """
        Data stream message: Send an SMS message in order with delays between messages.
        https://presence.atlassian.net/wiki/spaces/BOTS/pages/732790794/send+sms+Send+an+SMS+message+intelligently+Data+Stream+Message

        The first message, by default, will be sent with no delay and future messages in the series will be sent with a
        delay proportional to the number of characters in the message.

        You can encourage the first message to be sent with a delay by default by specifying "add_delay": True

        content =
            {
              "sms_content": sms_content,           # Required
              "to_residents": to_residents,         # Required
              "to_supporters": to_supporters,       # Required
              "sms_group_chat": True,               # Required
              "user_id": user_id,                   # Optional
              "add_delay": True                     # Optional - add a delay to the very first message (default is False)
            }

        :param botengine:
        :param content:
        :return:
        """
        if 'sms_content' not in content:
            botengine.get_logger().warning("location_smsdelivery_microservice: Missing 'sms_content' from the send_sms data stream content: {}".format(content))
            return

        add_delay = False

        if 'add_delay' in content:
            add_delay = content['add_delay']

        self.sms_buffer.insert(0, content)

        if self.is_timer_running(botengine, reference=TIMER_REFERENCE):
            return

        else:
            if add_delay:
                characters = len(content['sms_content'])
                seconds = characters / (CHARACTERS_PER_MINUTE / 60.0)
                if seconds > 10:
                    seconds = 10
                self.start_timer_s(botengine, seconds, reference=TIMER_REFERENCE)

            else:
                self.start_timer_ms(botengine, 0, reference=TIMER_REFERENCE)


    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        user_id = None
        sms_content = None
        to_residents = False
        to_supporters = False
        sms_group_chat = False

        try:
            content = self.sms_buffer.pop()
        except:
            return

        if 'sms_content' in content:
            sms_content = content['sms_content']

        if 'user_id' in content:
            user_id = content['user_id']

        if 'to_residents' in content:
            to_residents = content['to_residents']

        if 'to_supporters' in content:
            to_supporters = content['to_supporters']

        if 'sms_group_chat' in content:
            sms_group_chat = content['sms_group_chat']

        try:

            analytics.track_and_notify(botengine, self.parent, "sms_sent", properties={
                "sms_content": sms_content,
                "user_id": user_id,
                "to_residents": to_residents,
                "to_supporters": to_supporters,
                "sms_group_chat": sms_group_chat
            }, sms_content=sms_content, user_id=user_id, to_residents=to_residents, to_supporters=to_supporters, sms_group_chat=sms_group_chat)

        except Exception as e:
            botengine.get_logger().warning("location_smsdelivery_microservice: Error sending SMS message: {}".format(e))

        if len(self.sms_buffer) > 0:
            characters = len(self.sms_buffer[-1]['sms_content'])
            seconds = characters / (CHARACTERS_PER_MINUTE / 60.0)
            if seconds > 10:
                seconds = 10
            self.start_timer_s(botengine, seconds, reference=TIMER_REFERENCE)