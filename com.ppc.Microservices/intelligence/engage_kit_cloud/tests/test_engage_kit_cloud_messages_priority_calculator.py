
from botengine_pytest import BotEnginePyTest


from intelligence.engage_kit_cloud.types.messages_priority_calculator import *


import unittest
from unittest.mock import MagicMock, patch

class TestEngageKitCloudMessagesPriorityCalculator(unittest.TestCase):

    def test_engage_kit_cloud_messages_priority_calculator(self):
        botengine = BotEnginePyTest({})

        botengine.reset()

        # botengine.logging_service_names = ["messages_priority_calculator"] # Uncomment to see logging
        mut = PriorityCalculator.custom_priority_calculation
        assert mut is not None

        content_1 = "This is an emergency"
        content_2 = "I am home"
        content_3 = "Can we talk?"
        phrases = [
            {
                "text": content_1,
                "scores": [0.1, 0.2, 0.3]
            },
            {
                "text": content_2,
                "scores": [0.1, 0.2, 0.15]
            }
        ]

        assert mut(content_1) == CloudTopicPriority.UNSET
        assert mut(content_1, phrases) == CloudTopicPriority.HIGH
        assert mut(content_2, phrases) == CloudTopicPriority.MEDIUM
        assert mut(content_3, phrases) == CloudTopicPriority.UNSET
