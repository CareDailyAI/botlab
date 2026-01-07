
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities

from intelligence.chat_gpt.location_chatgpt_microservice import *

from unittest.mock import patch, MagicMock

class TestSetFitMicroservice():

    def test_set_fit_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        
        # Initialize the location
        location_object = Location(botengine, 0)
        
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.set_fit.location_set_fit_microservice"]

        assert mut is not None

    def test_set_fit_message_prioritization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        
        # Initialize the location
        location_object = Location(botengine, 0)
        
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.set_fit.location_set_fit_microservice"]

        assert mut is not None

        phrases = [
            "This is an emergency",
            "I am home",
            "Can we talk?"
        ]

        ai_params = genai.care_daily_ai_message_prioritization(botengine, phrases=phrases)

        ai.submit_message_prioritization_request(
            botengine, 
            location_object, 
            key="set_fit_test",
            ai_params=ai_params)
        
        content = {
            "key": "set_fit_test",
            "ai_params": ai_params
        }
        
        mut.submit_set_fit_message_prioritization(botengine, content)

        assert True