
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities

from intelligence.chat_gpt.location_chatgpt_microservice import *

from unittest.mock import patch, MagicMock

class TestChatGPTMicroservice():

    def test_chatgpt_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        
        # Initialize the location
        location_object = Location(botengine, 0)
        
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.chat_gpt.location_chatgpt_microservice"]

        assert mut is not None