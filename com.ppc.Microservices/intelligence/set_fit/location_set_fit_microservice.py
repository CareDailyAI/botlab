"""
Created on June 5, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

import utilities.genai as genai
from intelligence.intelligence import Intelligence


class LocationSetFitMicroservice(Intelligence):
    """
    SetFit Microservice

    This microservice is responsible for handling SetFit requests.
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

    # ===========================================================================
    # Data Stream Message Handlers
    # ===========================================================================

    def submit_set_fit_message_prioritization(self, botengine, content):
        """
        Submit set_fit messages for prioritization
        :param botengine: BotEngine environment
        :param content: JSON object for the chat completion request
        {
            'key': <string> key to identify this request
            'ai_params': <dict> API parameters
                'phrases': <list> list of strings to prioritize
        }

        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">submit_set_fit_message_prioritization()"
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">submit_set_fit_message_prioritization() content={}".format(content)
        )
        if content.get("key") == None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                "<submit_set_fit_message_prioritization() Missing key"
            )
            return
        if content.get("ai_params") == None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                "<submit_set_fit_message_prioritization() Missing phrases"
            )
            return

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|submit_set_fit_message_prioritization() request_key={} params={}".format(
                content["key"], content["ai_params"]
            )
        )
        response = botengine.send_a_request_to_a_model(
            model_name=genai.CARE_DAILY_AI_MODEL_SET_FIT,
            key=content["key"],
            data=content["ai_params"],
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|submit_set_fit_message_prioritization() response={}".format(response)
        )

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<submit_set_fit_message_prioritization()"
        )

    # ==================================================================================================================
    # Care Daily
    # ==================================================================================================================

    def ai(self, botengine, content):
        """
        The input data is a list of phrases (sentences). The response from the AI application contains the scorings of each phrase.

        Data stream message content example:
        ```
        {
            "key": "request key",
            "phrases" : [{
                "text": "Emergency situation",
                "scores": [0.06117, 0.04631, 0.89252]
            }]
        }
        ```

        :param botengine: BotEngine environment
        :param content: Content of the message
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">ai() content={}".format(content)
        )
        try:
            # Track everything but the response and the prompt to limit the amount of data we're storing
            import signals.analytics as analytics

            analytics.track(
                botengine,
                self.parent,
                "genai_completion",
                properties={"key": content.get("key")},
            )
        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                "|ai() Error tracking completion analytics: {}".format(e)
            )
            pass
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ai()")
