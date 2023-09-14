'''
Created on April 5th, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

from intelligence.intelligence import Intelligence
from intelligence.voice_call.voice_call_model import Settings, Step, Model, Action

from utilities import utilities

class LocationVoiceCallMicroservice(Intelligence):
    """
    Base Intelligence Module Class / Interface
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

    def update_conversation(self, botengine, conversation_object, message=None, resolved=False):
        """
        Update a conversation
        :param botengine: BotEngine environment
        :param conversation_object: Conversation object to update
        :param message: Message to send out to either homeowners or supporters
        :param resolved: True to resolve and end the conversation (default is False)
        :return conversation_object for reference in update_conversation(..). Or None if this conversation will no longer be active.
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
            return getattr(self, address)(botengine, content)

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        pass

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        pass

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        pass

    def SMS(self, botengine, content):
        """
        SMS Message received
        :param botengine:
        :param content:
        :return:
        """
        pass

    def VOICE(self, botengine, content):
        """
        VOICE Message received

        **Answers**
        
        Each key pressed by the callee for the current step is recorded in the format answerKey:digit or stepId:digit to the database. 
        The entire sequence of keys pressed sent to the calling bot as a comma-separated string answerKey1:digit1,stepId2:digit2,....
        
        **Call Statuses**

        | Status | Description |
        | 0	     | Created     |
        | 1	     | Started     |
        | 2	     | Completed   |
        | 3	     | Failed      |

        :param botengine:
        :param content: {
            "answers": "de4f281d-0221-4b58-a7fc-797532790e6e:1,RESOLUTION_OPTIONS:1",
            "callUuid": "CON-ca298d06-db01-49b4-b995-5f17d5fbff84",
            "endTime": 1680904126000,
            "startTime": 1680904100000,
            "status": 2,
            "userId": 82129
        }
        :return:
        """
        import json
        botengine.get_logger().info(utilities.Color.RED + "location_voice_call_microservice: Voice call updated: content={}.".format(json.dumps(content)) + utilities.Color.END)

        import signals.analytics as analytics
        properties = {}
        if "endTime" in content:
            properties["end_time"] = content["endTime"]
        if "startTime" in content:
            properties["start_time"] = content["startTime"]
        if "status" in content:
            properties["status"] = content["status"]
        if "userId" in content:
            properties["user_id"] = content["userId"]

        analytics.track(botengine, self.parent, 'voice_call_completed', properties=properties)
        pass

    def conversation_resolved(self, botengine, content):
        """
        Conversation resolution from the UI
        Data stream message that a conversation has been resolved
        Even if we don't have this conversation active anymore, we should tell the microservice to reset and wrap up.

        {
            # Microservice ID should always be here
            "microservice_id": callback_microservice.intelligence_id,

            # Conversation ID might not be here if this wasn't officially generated from a conversation
            "conversation_id": self.conversation_id,

            # Answer 0=Resolved; 1=False Alarm (in general - could have been overridden by the application layer)
            "answer": 0
        }

        :param botengine:
        :param content:
        :return:
        """
        pass
