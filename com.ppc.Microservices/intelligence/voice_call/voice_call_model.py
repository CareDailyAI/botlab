'''
Created on April 5th, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

class Settings(object):
    """
    Voice Call Settings

    https://iotbots.docs.apiary.io/#reference/bot-server-apis/outgoing-voice-call/make-voice-call
    Available voices: https://github.com/nexmo-community/vapi-tts-voices
    """

    # Default language is US English
    # Language codes are described by nexmo/vonage. Refer to `voices.json`.
    DEFAULT_LANGUAGE = "en-US"

    # Default voice is 0
    # Each language has a selection of voices. Refer to `voices.json`.
    DEFAULT_VOICE = 0

    # Default timeout is 12 seconds
    DEFAULT_TIMEOUT = 12

    def __init__(self, language=DEFAULT_LANGUAGE, voice=DEFAULT_VOICE, timeout=DEFAULT_TIMEOUT):
        """
        Constructor

        :param language	Text-to-speech language. Default: en-US. Possible values are listed in the Text-To-Speech guide.
        :param voice	Voice style. Default: 0. Possible values are listed in the Text-To-Speech guide.
        :param timeout	The amount of time (in seconds) of inactivity on the called party before the called party hears an alert ("timeout alert") or the call is terminated.
        :return: Settings object
        """
        # Convert language codes to Nexmo language codes
        # TODO: Refer to available codes within `voice.json`
        if language == 'en':
            language = 'en-US'
        if language == 'es':
            language = 'es-US'
        if language == 'sv':
            language = 'sv-SE'
        if language == 'fr':
            language = 'fr-FR'
        
        self.language = language
        self.voice = voice
        self.timeout = timeout

    def __iter__(self):
        """
        Iterator
        """
        yield 'language', self.language
        yield 'voice', self.voice
        yield 'timeout', self.timeout

    

class Step(object):
    """
    Voice Call Step
    """
    
    # Step Identifiers
    STEP_INTRO = 0
    STEP_CONVERSATION_RESOLUTION = 100
    STEP_CONVERSATION_RESOLUTION_OPTION = 110
    STEP_CONVERSATION_RESOLUTION_ACK = 120
    STEP_CONVERSATION_ESCALATION_OPTION = 130
    STEP_CONVERSATION_ESCALATION_ACK = 140
    STEP_CONVERSATION_FEEDBACK = 200
    STEP_CONVERSATION_FEEDBACK_OPTION = 210
    STEP_CONVERSATION_FEEDBACK_ACK = 220

    # Step Answer Keys
    STEP_ANSWER_KEY_RESOLUTION_OPTION = 'RESOLUTION_OPTION'
    STEP_ANSWER_KEY_ESCALATION_OPTION = 'ESCALATION_OPTION'

    def __init__(self, id, text, actions=[], timeout_alerts=[], mis_hit_alerts=[], answer_key=None):
        """
        Constructor

        :param id	The unique ID of the step.
        :param text	The text that will be spoken when the survey moves to this step.
        :param actions	Phone keys that the called party should press in response and how they will be handled.
        :param timeout_alerts	Phrases that the callee will hear at the end of the next idle time interval (specified by the "timeout" parameter in the settings) in this step. The call ends immediately after the last phrase is spoken. If the array is empty, the call will be automatically terminated after the first timeout.
        :param mishit_alerts	The phrases that the callee will hear after the next press of a button that is not associated with any of the actions of the step. The call ends after the last phrase is spoken. If the array is empty, the call will be automatically terminated after the first press of a button that is not associated with any of the step's actions.
        :return: Step object
        """
        self.id = id
        self.text = text
        self.actions = actions
        self.timeout_alerts = timeout_alerts
        self.mis_hit_alerts = mis_hit_alerts
        self.answer_key = answer_key

    def __iter__(self):
        """
        Iterator
        """
        yield 'id', self.id
        yield 'text', self.text
        yield 'actions', [dict(action) for action in self.actions]
        yield 'timeoutAlerts', self.timeout_alerts
        yield 'mishitAlerts', self.mis_hit_alerts
        if self.answer_key is not None:
            yield 'answerKey', self.answer_key

class Action(object):
    """
    Voice Call Action
    """

    def __init__(self, digits, next_step_id):
        """
        Constructor
        
        :param: digits	A string containing the numbers 0 through 9, or the characters "*" or "#". The action will be selected if the called party presses a button with any of these numbers.
        :param: nextStepId	The ID of the step to go to.

        :return: Action object
        """
        self.digits = digits
        self.next_step_id = next_step_id
    
    def __iter__(self):
        """
        Iterator
        """
        yield 'digits', self.digits
        yield 'nextStepId', self.next_step_id

class Model(object):
    """
    Voice Call Model represents a Nexmo Call Control Object (NCCO) and control the flow of inbound and outbound calls.
    """

    def __init__(self, settings=Settings(), phrases=None, start_step_id=0, steps=[]):
        """
        Constructor

        :param settings	The voice parameters and the timeout value.
        :param phrases	A dictionary for common phrases. Optional.
            * Each phrase is a key-value pair. The phrase value can be included in any text element of the steps through a "token" - the phrase key enclosed in curly braces.
        :param steps	Block chain. Each block includes the text to be spoken and options for handling user input.
        :param start_step_id	The ID of the first block to process.
        :return: Model object
        """
        self.settings = settings
        self.phrases = phrases
        self.start_step_id = start_step_id
        self.steps = steps

    def __iter__(self):
        """
        Iterator
        """
        yield 'settings', dict(self.settings)
        if self.phrases is not None:
            yield 'phrases', self.phrases
        yield 'startStepId', self.start_step_id
        yield 'steps', [dict(step) for step in self.steps]