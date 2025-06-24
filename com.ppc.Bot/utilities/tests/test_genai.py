import unittest

import pytest
from utilities.genai import (
    care_daily_ai_model,
    CARE_DAILY_AI_MODEL_LLAMA,
    chat_completion_model,
    DEFAULT_CHAT_MODEL,
    DEFAULT_FREQUENCY_PENALTY,
    DEFAULT_MAX_TOKEN,
    DEFAULT_N,
    DEFAULT_PRESENCE_PENALTY,
    DEFAULT_REPEAT_PENALTY,
    DEFAULT_STOP_SEQUENCES,
    DEFAULT_STREAM,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    open_ai_response,
    openai_chat_completion_model,
)

from botengine_pytest import BotEnginePyTest


class TestGenAI(unittest.TestCase):
    def test_genai_openai_chat_completion_model(self):
        # Initial setup
        botengine = BotEnginePyTest({})

        messages = [{"role": "user", "content": "tell me a joke"}]
        mut = openai_chat_completion_model(botengine, messages=messages)

        assert mut is not None
        assert mut.get("model") == DEFAULT_CHAT_MODEL
        assert mut.get("messages") == messages
        assert mut.get("functions") is None
        assert mut.get("function_call") is None
        assert mut.get("max_tokens") == DEFAULT_MAX_TOKEN
        assert mut.get("temperature") == DEFAULT_TEMPERATURE
        assert mut.get("top_p") == DEFAULT_TOP_P
        assert mut.get("n") == DEFAULT_N
        assert mut.get("stream") == DEFAULT_STREAM
        assert mut.get("stop") == DEFAULT_STOP_SEQUENCES
        assert mut.get("presence_penalty") == DEFAULT_PRESENCE_PENALTY
        assert mut.get("frequency_penalty") == DEFAULT_FREQUENCY_PENALTY
        assert mut.get("logit_bias") == {}
        assert mut.get("user") is None

    def test_genai_openai_chat_completion_model_exception(self):
        # Initial setup
        botengine = BotEnginePyTest({})

        with pytest.raises(Exception):
            chat_completion_model(botengine, messages=None)

    def test_genai_open_ai_completion(self):
        # Initial setup
        botengine = BotEnginePyTest({})

        with pytest.raises(Exception):
            open_ai_response(botengine, None, None)

    def test_genai_care_daily_ai_model(self):
        # Initial setup
        botengine = BotEnginePyTest({})

        text = "tell me a joke"
        mut = care_daily_ai_model(botengine, text=text)

        assert mut is not None
        assert mut.get("text") == text
        assert mut.get("params") is not None
        assert mut["model"] == CARE_DAILY_AI_MODEL_LLAMA
        assert mut["params"].get("temperature") == DEFAULT_TEMPERATURE
        assert mut["params"].get("top_p") == DEFAULT_TOP_P
        assert mut["params"].get("max_tokens") == DEFAULT_MAX_TOKEN
        assert mut["params"].get("presence_penalty") == DEFAULT_PRESENCE_PENALTY
        assert mut["params"].get("frequency_penalty") == DEFAULT_FREQUENCY_PENALTY
        assert mut["params"].get("repeat_penalty") == DEFAULT_REPEAT_PENALTY

        chat = [{"role": "user", "content": "tell me a joke"}]
        mut = care_daily_ai_model(botengine, chat=chat)

        assert mut is not None
        assert mut.get("text") is None
        assert mut.get("params") is not None
        assert mut["model"] == CARE_DAILY_AI_MODEL_LLAMA
        assert mut["params"].get("temperature") == DEFAULT_TEMPERATURE
        assert mut["params"].get("top_p") == DEFAULT_TOP_P
        assert mut["params"].get("max_tokens") == DEFAULT_MAX_TOKEN
        assert mut["params"].get("presence_penalty") == DEFAULT_PRESENCE_PENALTY
        assert mut["params"].get("frequency_penalty") == DEFAULT_FREQUENCY_PENALTY
        assert mut["params"].get("repeat_penalty") == DEFAULT_REPEAT_PENALTY
