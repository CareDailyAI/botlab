
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities


from intelligence.engage_kit_cloud.types.messages_cloud_buffer import MessagesCloudBuffer
from intelligence.engage_kit_cloud.types.messages_priority_calculator import PriorityCalculator
from intelligence.engage_kit_cloud.types.cloud_model import BotMessage
from intelligence.engage_kit_cloud.types.cloud_model import BotUpdatedMessage
from intelligence.engage_kit_cloud.types.cloud_model import CloudMessageStatus

from intelligence.engage_kit_cloud.location_engage_kit_cloud_microservice import *


import unittest
from unittest.mock import MagicMock, patch

class TestEngageKitCloudMicroservice(unittest.TestCase):

    def test_engage_kit_cloud_microservice(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["engage_kit", "set_fit"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        # Start up the bot
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.engage_kit_cloud.location_engage_kit_cloud_microservice"]
        assert mut is not None
        assert mut.messages == []
        assert isinstance(mut.messages_buffer, MessagesCloudBuffer)
        user_id = botengine.get_location_users()[0]['id']
        messages = [
            {
                "messageId": 123,
                "scheduleType": 0,
                "status": 1,
                "topicId": "general",
                "appInstanceId": 456,
                "contentKey": "Message 1 content description",
                "creationTime": 1646537712000,
                "maxDeliveryTime": 1666537712000,
                "deliveryDayTime": 36000,
                "timeToLive": 3600
            },
            {
                "messageId": 124,
                "scheduleType": 0,
                "status": 2,
                "topicId": "general",
                "appInstanceId": 456,
                "contentKey": "Message 2 content description",
                "creationTime": 1646537712000,
                "maxDeliveryTime": 1666537712000,
                "deliveryDayTime": 36000,
                "timeToLive": 3600,
                "deliveryTime": 1666037712000,
            },
            {
                "messageId": 125,
                "scheduleType": 1,
                "status": 1,
                "topicId": "general",
                "appInstanceId": 457,
                "contentKey": "Message 3 content description",
                "creationTime": 1646537712000,
                "maxDeliveryTime": 1666537712000,
                "timeToLive": 3600,
                "schedule": "0 0 10 ? * SUN"
            },
            {
                "messageId": 126,
                "originalMessageId": 123,
                "scheduleType": 0,
                "status": 3,
                "topicId": "general",
                "userId": user_id,
                "contentText": "Reply from a user",
                "lang": "en",
                "creationTime": 1646537712000
            }
        ]
        location_object.messages_updated(botengine, messages)

        assert len(mut.messages) == 2

        phrases = [{"text": message.priority_phrase(), "scores": [0.1, 0.2, 0.3]} for message in mut.messages if message.status == CloudMessageStatus.READY.value]

        # Test the message prioritization
        mut.ai(botengine, {"key": SETFIT_KEY, "phrases": phrases})
