"""
Created on January 1, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Parth Agrawal
"""

from intelligence.intelligence import Intelligence

import signals.ai as ai
import utilities.genai as genai

class LocationChatGPTMicroservice(Intelligence):
    """
    ChatGPT Microservice

    This microservice is responsible for handling ChatGPT requests.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)
        pass

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        pass

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        pass

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        pass

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    #===========================================================================
    # Data Stream Message Handlers
    #===========================================================================

    def submit_chatgpt_chat_completion(self, botengine, content):
        """
        Submit chatgpt prompt
        :param botengine: BotEngine environment
        :param content: JSON object for the chat completion request
        {
            'key': <string> key to identify this request
            'openai_params': <dict> openai params <Deprecated: Use 'ai_params'>
            'ai_params': <dict> openai params
            'provider': <string> chat completion provider. See signals.openai.CHAT_GPT_PROVIDER_*
        }

        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">submit_chatgpt_chat_completion()")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">submit_chatgpt_chat_completion() content={}".format(content))
        if content.get('key') == None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<submit_chatgpt_chat_completion() Missing key")
            return
        if content.get('openai_params') != None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|submit_chatgpt_chat_completion() Use 'ai_params' instead")
            content['ai_params'] = content['openai_params']
        
        if content.get('ai_params') == None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<submit_chatgpt_chat_completion() Missing ai_params")
            return
        if content.get('provider') == None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<submit_chatgpt_chat_completion() Missing provider")
            return
        
        if content.get('provider') == ai.CHAT_GPT_PROVIDER_OPENAI:
            openai_organization_id = self._get_openai_organzation_id(botengine)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|submit_chatgpt_chat_completion() organization_id={} request_key={} params={}".format(openai_organization_id, content['key'], content['ai_params']))
            response = botengine.send_request_for_chat_completion(key=content['key'], data=content['ai_params'], openai_organization_id=openai_organization_id)
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|submit_chatgpt_chat_completion() response={}".format(response))
        
        elif content.get('provider') == ai.CHAT_GPT_PROVIDER_CAREDAILY:
            model_name = content['ai_params'].get('model', None)
            if model_name is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<submit_chatgpt_chat_completion() Missing model name")
                return
            elif model_name != genai.CARE_DAILY_AI_MODEL_LLAMA:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("<submit_chatgpt_chat_completion() Invalid model name")
                return
            del content['ai_params']['model']
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|submit_chatgpt_chat_completion() request_key={} params={}".format(content['key'], content['ai_params']))
            response = botengine.send_a_request_to_a_model(model_name=model_name, key=content['key'], data=content['ai_params'])
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|submit_chatgpt_chat_completion() response={}".format(response))
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<submit_chatgpt_chat_completion()")
    
    #===========================================================================
    # OpenAI Helpers
    #===========================================================================

    def _get_openai_organzation_id(self, botengine):
        """
        Attempt to return the OpenAI Organization ID.

        :param botengine: BotEngine environment
        :return: Organization ID
        """
        import bundle
        import properties
        organization_id = None
        if properties.get_property(botengine, "OPEN_AI_ORGANIZATIONS", False) is not None:
            for u in properties.get_property(botengine, "OPEN_AI_ORGANIZATIONS", False):
                if u in bundle.CLOUD_ADDRESS:
                    organization_id = properties.get_property(botengine, "OPEN_AI_ORGANIZATIONS", False)[u]

        return organization_id

    def openai(self, botengine, content):
        """
        Bots can interact asynchronously with Open AI ChatGPT using this API. The response from CharGPT is delivered to the bot in a data stream message to the 'openai' address.

        Data stream message content example:
        ```
        {
            "key": "MyRequest",
            "id" : "chatcmpl-86GKbsl3bP5YmmxutIY8aS5c5o5gK",
            "object" : "chat.completion",
            "created" : 1696503437,
            "model" : "gpt-3.5-turbo-0613",
            "choices" : [ {
                "index" : 0,
                "message" : {
                    "role" : "assistant",
                    "content" : "This is a test!"
                },
                "finish_reason" : "stop"
            } ],
            "usage" : {
                "prompt_tokens" : 13,
                "completion_tokens" : 5,
                "total_tokens" : 18
            }
        }
        ```

        :param botengine: BotEngine environment
        :param content: Content of the message
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">openai() content={}".format(content))
        try:
            # Track everything but the response and the prompt to limit the amount of data we're storing
            import signals.analytics as analytics
            analytics.track(botengine, self.parent, "genai_completion", properties={
                "key": content.get("key"),
                "created" : content.get("created"),
                "model" : content.get("model"),
                "object" : content.get("object"),
                "usage" : content.get("usage"),
                "organization": content.get("organization"),
            })
        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|openai() Error tracking completion analytics: {}".format(e))
            pass
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<openai()")

    # ==================================================================================================================
    # Care Daily
    # ==================================================================================================================

    def ai(self, botengine, content):
        """
        Bots can interact asynchronously with Care Daily AI ChatGPT using this API. The response from ChatGPT is delivered to the bot in a data stream message to the 'ai' address.

        Data stream message content example:
        ```
        {
            "key": "request key",
            "text" : "This is a test!"
        }
        ```

        :param botengine: BotEngine environment
        :param content: Content of the message
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">ai() content={}".format(content))
        try:
            # Track everything but the response and the prompt to limit the amount of data we're storing
            import signals.analytics as analytics
            analytics.track(botengine, self.parent, "genai_completion", properties={
                "key": content.get("key")
            })
        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|ai() Error tracking completion analytics: {}".format(e))
            pass
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ai()")