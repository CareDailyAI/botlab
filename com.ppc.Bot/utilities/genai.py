"""
This module contains utility functions for generating Generative AI API requests.
"""

# The maximum number of tokens to generate in the completion.
DEFAULT_MAX_TOKEN = 300

# What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
DEFAULT_TEMPERATURE = 0.2

# An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
DEFAULT_TOP_P = 0.95

# Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
DEFAULT_FREQUENCY_PENALTY = 0.0

# Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
DEFAULT_PRESENCE_PENALTY = 0

# ===========================================================================
# OPEN AI API PARAMETERS
# ===========================================================================

# ID of the model to use. You can use the [List models API](https://platform.openai.com/docs/api-reference/models/list) to see all of your available models, or see our [Model](https://platform.openai.com/docs/models/overview) overview for descriptions of them.
DEFAULT_CHAT_MODEL = "gpt-4-0613"  # Snapshot of gpt-4 from June 13th 2023 with function calling data. Unlike gpt-4, this model will not receive updates, and will be deprecated 3 months after a new version is released.	Supports upt to 8,192 tokens


# How many completions to generate for each prompt.
DEFAULT_N = 1

# Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
STOP_SEQUENCE_INPUT = "USER:"
STOP_SEQUENCE_OUTPUT = "SERVICE:"
STOP_SEQUENCE_NEWLINE = "\n"
DEFAULT_STOP_SEQUENCES = [
    STOP_SEQUENCE_INPUT,
    STOP_SEQUENCE_OUTPUT,
    STOP_SEQUENCE_NEWLINE,
]

# Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message.
DEFAULT_STREAM = False

# Generates best_of completions server-side and returns the "best"
DEFAULT_BEST_OF = 1

# Mode hit a natural stop point or a provided stop sequence.
FINISH_REASON_STOP = "stop"

# Maximum number of tokens specified in the request was reached.
FINISH_REASON_LENGTH = "length"

# Content was omitted due to a flag from our content filters.
FINISH_REASON_CONTENT_FILTER = "content_filter"

# The model called a function
FINISH_REASON_FUNCTION = "function"


def openai_chat_completion_model(
    botengine,
    messages,
    model=DEFAULT_CHAT_MODEL,
    functions=None,
    function_call=None,
    max_tokens=DEFAULT_MAX_TOKEN,
    temperature=DEFAULT_TEMPERATURE,
    top_p=DEFAULT_TOP_P,
    n=DEFAULT_N,
    stream=DEFAULT_STREAM,
    stop=DEFAULT_STOP_SEQUENCES,
    presence_penalty=DEFAULT_PRESENCE_PENALTY,
    frequency_penalty=DEFAULT_FREQUENCY_PENALTY,
    logit_bias={},
    user=None,
):
    """
    Creates an openai chat completion request body for the given parameters.

    For CareDaily Bot OpenAI documentation, see https://iotbots.docs.apiary.io/#/reference/bot-server-ap-is/open-ai

    See https://platform.openai.com/docs/api-reference/chat/create for more information

    :param messages: array (Required) A list of messages comprising the conversation so far.
        See https://cookbook.openai.com/examples/how_to_format_inputs_to_chatgpt_models for more information.

        Message Properties:

        :param role: string (Required) The role of the messages author. One of system, user, assistant, or function.
        :param content: string or null (Required) The contents of the message. content is required for all messages, and may be null for assistant messages with function calls.
        :param name: string (Optional) The name of the author of this message. name is required if role is function, and it should be the name of the function whose response is in the content. May contain a-z, A-Z, 0-9, and underscores, with a maximum length of 64 characters.
        :param function_call: object (Optional) The name and arguments of a function that should be called, as generated by the model.

            Function Call Properties:

            :param name: string (Required) The name of the function to call.
            :param arguments: string (Required) The arguments to call the function with, as generated by the model in JSON format. Note that the model does not always generate valid JSON, and may hallucinate parameters not defined by your function schema. Validate the arguments in your code before calling your function.

    :param model: string (Optional, Default to "gpt-4-0613") ID of the model to use. Use https://platform.openai.com/docs/api-reference/models/list API to see all available models, or see https://platform.openai.com/docs/models/overview for descriptions of them.
    :param functions: array (Optional) A list of functions the model may generate JSON inputs for.
        Function Properties:

        :param name: string (Required) The name of the function to be called. Must be a-z, A-Z, 0-9, or contain underscores and dashes, with a maximum length of 64.
        :param description: string (Optional) A description of what the function does, used by the model to choose when and how to call the function.
        :param parameters: object (Required) The parameters the functions accepts, described as a JSON Schema object. See https://platform.openai.com/docs/guides/gpt/function-calling for examples, and https://json-schema.org/understanding-json-schema/ for documentation about the format.

    :param function_call: string or object (Optional) Controls how the model calls functions. "none" means the model will not call a function and instead generates a message. "auto" means the model can pick between generating a message or calling a function. Specifying a particular function via {"name": "my_function"} forces the model to call that function. "none" is the default when no functions are present. "auto" is the default if functions are present.
        To describe a function that accepts no parameters, provide the value {"type": "object", "properties": {}}.
    :param max_tokens: integer or null (Optional, Defaults to 16) The maximum number of tokens to generate in the completion.
        The token count of your prompt plus max_tokens cannot exceed the model's context length.
        See https://platform.openai.com/tokenizer and https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    :param temperature: number or null (Optional, Defaults to 1) What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        We generally recommend altering this or top_p but not both.
    :param top_p: number or null (Optional, Defaults to 1) An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
        We generally recommend altering this or temperature but not both.
    :param n: integer or null (Optional, Defaults to 1) How many completions to generate for each prompt.
        Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
    :param stream: boolean or null (Optional, Defaults to false) Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message. Example Python code.
    :param stop: string / array / null (Optional, Defaults to null) Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
    :param presence_penalty: number or null (Optional, Defaults to 0) Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
        See more information about frequency and presence penalties.
    :param frequency_penalty: number or null (Optional, Defaults to 0) Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
        See more information about frequency and presence penalties.
    :param logit_bias: map (Optional, Defaults to null) Modify the likelihood of specified tokens appearing in the completion.
        Accepts a json object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this tokenizer tool (which works for both GPT-2 and GPT-3) to convert text to token IDs. Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.
        As an example, you can pass {"50256": -100} to prevent the <|endoftext|> token from being generated.
    :param user: (string, Optional) A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse. Learn more.

    :return: JSON body to send to the CareDaily OpenAI API
    """
    botengine.get_logger(f"{__name__}").debug(
        ">openai_chat_completion_model() messages={} model={} functions={} function_call={} max_tokens={} temperature={} top_p={} n={} stream={} stop={} presence_penalty={} frequency_penalty={} logit_bias={} user={}".format(
            messages,
            model,
            functions,
            function_call,
            max_tokens,
            temperature,
            top_p,
            n,
            stream,
            stop,
            presence_penalty,
            frequency_penalty,
            logit_bias,
            user,
        )
    )
    if messages is None or len(messages) == 0:
        raise "genai.openai_chat_completion_model() No messages provided"

    body = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "n": n,
        "stream": stream,
        "stop": stop,
        "presence_penalty": presence_penalty,
        "frequency_penalty": frequency_penalty,
        "logit_bias": logit_bias,
        "user": user,
    }

    if stream:
        botengine.get_logger(f"{__name__}").warning(
            "|openai_chat_completion_model() Stream is not currently supported by this utility. Setting stream to False."
        )
        body["stream"] = False

    if functions is not None:
        # TODO: Include exeption handling for invalid function schemas
        body["functions"] = functions
        if function_call is not None:
            body["function_call"] = function_call
    import json

    botengine.get_logger(f"{__name__}").debug(
        "<openai_chat_completion_model() body={}".format(json.dumps(body))
    )
    return body


def chat_completion_model(
    botengine,
    messages,
    model=DEFAULT_CHAT_MODEL,
    functions=None,
    function_call=None,
    max_tokens=DEFAULT_MAX_TOKEN,
    temperature=DEFAULT_TEMPERATURE,
    top_p=DEFAULT_TOP_P,
    n=DEFAULT_N,
    stream=DEFAULT_STREAM,
    stop=DEFAULT_STOP_SEQUENCES,
    presence_penalty=DEFAULT_PRESENCE_PENALTY,
    frequency_penalty=DEFAULT_FREQUENCY_PENALTY,
    logit_bias={},
    user=None,
):
    botengine.get_logger(f"{__name__}").warning(
        ">chat_completion_model() This method is deprecated. Please use signals/ai.py:submit_chat_completion_request instead."
    )
    return openai_chat_completion_model(
        botengine,
        messages,
        model,
        functions,
        function_call,
        max_tokens,
        temperature,
        top_p,
        n,
        stream,
        stop,
        presence_penalty,
        frequency_penalty,
        logit_bias,
        user,
    )


def open_ai_response(
    botengine,
    location_object,
    content,
    microservice=None,
    callback_address=None,
    callback_metadata={},
):
    raise "genai.open_ai_response(): This method is deprecated. Please use signals/ai.py:submit_chat_completion_request instead."


# ===================================================================
# Care Daily Parameters
# ===================================================================

# AI Model for Care Daily Llama
CARE_DAILY_AI_MODEL_LLAMA = "llama"

# AI model for Care Daily Set Fit
CARE_DAILY_AI_MODEL_SET_FIT = "setfit"

# Repeat penalty: Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
DEFAULT_REPEAT_PENALTY = 1.1


def care_daily_ai_model(
    botengine,
    text=None,
    chat=None,
    model=CARE_DAILY_AI_MODEL_LLAMA,
    temperature=DEFAULT_TEMPERATURE,
    top_p=DEFAULT_TOP_P,
    min_p=None,
    typical_p=None,
    seed=None,
    max_tokens=DEFAULT_MAX_TOKEN,
    presence_penalty=DEFAULT_PRESENCE_PENALTY,
    frequency_penalty=DEFAULT_FREQUENCY_PENALTY,
    repeat_penalty=DEFAULT_REPEAT_PENALTY,
):
    """
    Creates a Care Daily AI model request body for the given parameters.

    One of "text" or "chat" is required in the request body. If both are provided, "chat" will be used.

    :param botengine: BotEngine environment
    :param model: string (Optional, Default to "llama") The AI model to use

    :param text: string (Required) The message to submit to the AI model
    :param chat: list (Required) The chat object to submit to the AI model (see https://iotbots.docs.apiary.io/#/reference/bot-server-ap-is/open-ai
        For chat completion, enter a list of messages into the "chat" object of the request body.
        Each message must include 2 fields:
        - 'role': The role of the messages author. One of system, user, assistant, or function.
        - 'content': The contents of the message. content is required for all messages, and may be null for assistant messages with function calls.

    :param temperature: float (Optional, Defaults to 0.2) The temperature to use for sampling.
    :param top_p: float (Optional, Defaults to 0.95) The top-p value to use for nucleus sampling. Nucleus sampling described in academic paper "The Curious Case of Neural Text Degeneration" https://arxiv.org/abs/1904.09751
    :param min_p: float (Optional, Defaults to 0.05) The min-p value to use for minimum p sampling. Minimum P sampling as described in https://github.com/ggerganov/llama.cpp/pull/3841
    :param typical_p: float (Optional, Defaults to 1.0) The typical-p value to use for sampling. Locally Typical Sampling implementation described in the paper https://arxiv.org/abs/2202.00666.
    :param seed: int (Optional, Defaults to 0xFFFFFFFF) The seed to use for sampling.
    :param max_tokens: int (Optional, Defaults to 300) The maximum number of tokens to generate. If max_tokens <= 0 or None, the maximum number of tokens to generate is unlimited and depends on n_ctx.
        The token count of your prompt plus max_tokens cannot exceed the model's context length.
        See https://platform.openai.com/tokenizer and https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken
    :param presence_penalty: float (Optional, Defaults to 0.0) The penalty to apply to tokens based on their presence in the prompt.
    :param frequency_penalty: float (Optional, Defaults to 0.0) The penalty to apply to tokens based on their frequency in the prompt.
    :param repeat_penalty: float (Optional, Defaults to 1.1) The penalty to apply to repeated tokens.

    :return: JSON body to send to the CareDaily AI API
    """
    botengine.get_logger(f"{__name__}").info(
        ">care_daily_ai_model() model={}".format(text)
    )

    if model is None:
        botengine.get_logger(f"{__name__}").error(
            "<care_daily_ai_model() No model provided"
        )
        return {}

    if text is None and chat is None:
        botengine.get_logger(f"{__name__}").error(
            "<care_daily_ai_model() No text or chat provided"
        )
        return {}

    body = {"chat": chat} if chat is not None else {"text": text}
    body["model"] = model
    params = {}

    if temperature is not None:
        params["temperature"] = temperature
    if top_p is not None:
        params["top_p"] = top_p
    if min_p is not None:
        params["min_p"] = min_p
    if typical_p is not None:
        params["typical_p"] = typical_p
    if seed is not None:
        params["seed"] = seed
    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    if presence_penalty is not None:
        params["presence_penalty"] = presence_penalty
    if frequency_penalty is not None:
        params["frequency_penalty"] = frequency_penalty
    if repeat_penalty is not None:
        params["repeat_penalty"] = repeat_penalty

    body["params"] = params

    import json

    botengine.get_logger(f"{__name__}").info(
        "|care_daily_ai_model() body={}".format(json.dumps(body))
    )
    botengine.get_logger(f"{__name__}").info("<care_daily_ai_model()")
    return body


def care_daily_ai_message_prioritization(botengine, phrases):
    """
    Creates a Care Daily AI message prioritization request body for the given parameters.

    :param botengine: BotEngine environment
    :param phrases: list (Required) List of phrases to prioritize

    :return: JSON body to send to the CareDaily AI API
    """
    botengine.get_logger(f"{__name__}").info(
        ">care_daily_ai_message_prioritization() phrases={}".format(phrases)
    )

    if phrases is None or len(phrases) == 0:
        botengine.get_logger(f"{__name__}").error(
            "<care_daily_ai_message_prioritization() No phrases provided"
        )
        return {}

    body = {"phrases": phrases}

    import json

    botengine.get_logger(f"{__name__}").info(
        "|care_daily_ai_message_prioritization() body={}".format(json.dumps(body))
    )
    botengine.get_logger(f"{__name__}").info("<care_daily_ai_message_prioritization()")
    return body
