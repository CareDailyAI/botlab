"""
Created on May 21, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

# Chat Completion Providers
CHAT_GPT_PROVIDER_OPENAI = "openai"
CHAT_GPT_PROVIDER_CAREDAILY = "caredaily"

# Text Completion Character Limit
TEXT_COMPLETION_CHARACTER_LIMIT = 500

def submit_chat_completion_request(botengine, location_object, key, ai_params, provider=CHAT_GPT_PROVIDER_CAREDAILY):
    """
    Submit a chat completion request to ChatGPT microservice

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param key: Key to identify this request
    :param ai_params: Content to submit
    """
    body = {
        "key": key,
        "provider": provider,
        "ai_params": ai_params,
    }

    location_object.distribute_datastream_message(botengine, "submit_chatgpt_chat_completion", body, internal=True, external=False)

def form_text_completion_prompt(botengine, location_object, system_message, baked_message, baked_response, user_message, character_limit=TEXT_COMPLETION_CHARACTER_LIMIT):
    """
    Form a text completion prompt.

    Example Output:
    "
    <s>
        [INST]
            <<SYS>>
            You're Arti.
            Stop after my response.
            <</SYS>>
            "Summary for 'Location'\n12:00 AM Friday - Hasn't gone to sleep by midnight." rephrased is:
        [/INST] 
        Arti here! Sleep patterns were off at "Location" last night.
    </s>
    <s>
        [INST]
            "Daily Report Summary for 'PyTest Location'\n10:30 PM Friday - Went to sleep." rephrased is:
        [/INST]
    "

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param system_message: System message
    :param baked_message: Baked message
    :param user_message: User message
    :return: Prompt
    """
    botengine.get_logger(f"{__name__}").info(">form_text_completion_prompt()")
    prompt = [
        '<s>',
        '[INST]',
        '<<SYS>>'
    ]

    if system_message is not None:
        prompt.append(f"{system_message}")
    else:
        import utilities.utilities as utilities
        prompt.append(f"You're {utilities.get_chat_assistant_name(botengine)}.")
        prompt.append("Stop after my response.")
    prompt.append('<</SYS>>')

    if baked_message:
        prompt.append(f"{baked_message}")
    prompt.append("[/INST]\n")

    if baked_response:
        prompt.append(f"{baked_response}")
    prompt.append('</s>')

    prompt.append('<s>')
    if user_message:
        prompt.append(f"{user_message}")

    text = "\n".join(prompt)
    if len(text) > character_limit:
        botengine.get_logger(f"{__name__}").warning("|form_text_completion_prompt() Text exceeds character limit by {} characters. Truncating.".format(len(text) - character_limit))
        text = text[:character_limit]
    botengine.get_logger(f"{__name__}").info("<form_text_completion_prompt() text={}".format(text))
    return text

def submit_message_prioritization_request(botengine, location_object, key, ai_params):
    """
    Submit a message prioritization request to SetFit microservice

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param key: Key to identify this request
    :param ai_params: Content to submit
    """
    botengine.get_logger(f"{__name__}").info(">submit_message_prioritization_request()")
    body = {
        "key": key,
        "ai_params": ai_params,
    }

    # Attempt to use SetFit model for prioritization. If it fails, raise exceptions.
    location_object.distribute_datastream_message(botengine, "submit_set_fit_message_prioritization", body, internal=True, external=False, raise_exceptions=True)
    botengine.get_logger(f"{__name__}").info("<submit_message_prioritization_request()")