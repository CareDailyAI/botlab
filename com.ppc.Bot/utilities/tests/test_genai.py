import unittest
from unittest.mock import MagicMock, patch
import logging

from botengine_pytest import BotEnginePyTest
from locations.location import Location
import properties

from utilities.genai import *

import pytest

class TestGenAI(unittest.TestCase):

    def test_genai_chat_completion_model(self):
        # Initial setup
        botengine = BotEnginePyTest({})

        messages = [{ "role": "user", "content": "tell me a joke" }]
        mut = chat_completion_model(
            botengine,
            messages=messages
        )

        assert mut is not None
        assert mut.get("model") == DEFAULT_CHAT_MODEL
        assert mut.get("messages") == messages
        assert mut.get("functions") == None
        assert mut.get("function_call") == None
        assert mut.get("max_tokens") == DEFAULT_MAX_TOKEN
        assert mut.get("temperature") == DEFAULT_TEMPERATURE
        assert mut.get("top_p") == DEFAULT_TOP_P
        assert mut.get("n") == DEFAULT_N
        assert mut.get("stream") == DEFAULT_STREAM
        assert mut.get("stop") == DEFAULT_STOP_SEQUENCES
        assert mut.get("presence_penalty") == DEFAULT_PRESENCE_PENALTY
        assert mut.get("frequency_penalty") == DEFAULT_FREQUENCY_PENALTY
        assert mut.get("logit_bias") == {}
        assert mut.get("user") == None

    def test_genai_chat_completion_model_exception(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        
        with pytest.raises(Exception):
            chat_completion_model(
                botengine,
                messages=None
            )

    def test_genai_open_ai_completion(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        
        with pytest.raises(Exception):
            open_ai_response(botengine, None, None)
