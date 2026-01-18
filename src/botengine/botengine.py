#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BotEngine

Dependencies:
* Python 3.8+
* requests - use "pip3 install requests" to install
* dateutil - use "pip3 install python-dateutil" to install
* pytz     - use "pip3 install pytz" to install
* dill     - use "pip3 install dill" to install
* lz4      - use "pip3 install lz4" to install
* colorama - use "pip3 install colorama" to install
* ijson    - use "pip3 install ijson" to install

pip install -r requirements.txt

@author:     David Moss, Destry Teeter

@copyright:  2012 - 2025 People Power Company. All rights reserved.

@contact:    dmoss@caredaily.ai, destry@caredaily.ai
"""

import datetime
import importlib
import json
import logging
import os
import sys
import time
import urllib.parse

# Our default server address
DEFAULT_BASE_SERVER_URL = "app.peoplepowerco.com"

__version__ = "9.6.11"
__date__ = "2025-12-29"

DEBUG = 0
TESTRUN = 0
PROFILE = 0

LOGGING_LEVEL_DICT = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARN,
    "error": logging.ERROR,
}

# global variables
_bot_loggers = {}
_bot_logger_config = None
_https_proxy = None

# Maximum integer size, declared because Python 2.7 has a max int concept but Python 3.x does not and we want to remain forward-compatible.
MAXINT = 9223372036854775807

# Name of our core variable
CORE_VARIABLE_NAME = "-core-"

# Name of our internal variable to store Timer information
TIMERS_VARIABLE_NAME = "[t]"

# Minimum gap between timers
TIMER_MIN_MS = 10 * 1000

# Name of our internal variable to store Question/Answer information
QUESTIONS_VARIABLE_NAME = "[q]"

# Name of our internal variable to store the trigger count when running on the server
COUNT_VARIABLE_NAME = "[c]"

# For debugging variables: When variables are flushed to the server, also save them to a local file.
SAVE_VARIABLES_TO_DEBUG_FILE = False

# Keys for state variable properties in cache
STATE_KEY_CONTENT = "c"
STATE_KEY_PUBLISH = "p"
STATE_KEY_UPDATE_LIST = "u"
STATE_KEY_DELETE_LIST = "d"
STATE_KEY_OVERWRITE = "o"
STATE_KEY_SUB_LOCATION = "s"

# .tar or .zip the final bot package
TAR = True

# Default configurable bot start key timeout on the server in seconds
DEFAULT_START_KEY_TIMEOUT_S = 3

# ===============================================================================
# Logger Methods
# ===============================================================================

def _playback_logger_timestamp(self, record, datefmt=None):
    """
    Logger playback timestamp override
    :param record:
    :param datefmt:
    :return:
    """
    global playback_timestamp_ms
    global playback_timezone

    import pytz

    return datetime.datetime.fromtimestamp(
        playback_timestamp_ms / 1000.0, pytz.timezone(playback_timezone)
    )

def _create_logger(
    name, level, console_mode=False, filename=None, playback=False, session_id=None, bundle_id=None, fmt_string=None
):
    """
    Create a logger
    :param name:
    :param level:
    :param console_mode:
    :param filename:
    :param playback:
    :return:
    """
    global _bot_logger_config
    if _bot_logger_config is None or name == "botengine":
        _bot_logger_config = {"level": level, "console_mode": console_mode, "filename": filename, "playback": playback, "session_id": session_id, "bundle_id": bundle_id, "fmt_string": fmt_string}
    # print(f"Creating logger '{name}' level={level} console={console_mode} file={filename} playback={playback} session_id={session_id} bundle_id={bundle_id}")
    if playback:
        logging.Formatter.formatTime = _playback_logger_timestamp
        if session_id is not None:
            filename = "playback_{}_log.txt".format(session_id)
        else:
            filename = "playback_log.txt"

    logger = logging.getLogger(name)

    if _bot_loggers and len(name.split(".")) > 0:
        components = name.split(".")
        for i in range(len(components)):
            # Check if the logger is already configured by referencing prefixes
            if ".".join(components[: i + 1]) in _bot_loggers:
                return logger
    logger.setLevel(level)
    fmt_string = "%(asctime)s %(levelname)-8s %(name)-12s %(message)s"
    if _bot_logger_config.get("fmt_string"):
        fmt_string = _bot_logger_config.get("fmt_string")
    fmt = logging.Formatter(fmt_string)

    if filename is not None:
        if session_id is None:
            try:
                os.remove(filename)
            except Exception as e:
                print(f"Error removing file {filename}: {e}")
                pass

        f = logging.FileHandler(filename, encoding='utf-8')
        f.setFormatter(fmt)
        logger.addHandler(f)

    if console_mode:
        stream = sys.stdout
        try:
            # Python 3.7+ allows reconfiguring stdout encoding
            if hasattr(stream, 'reconfigure'):
                stream.reconfigure(encoding='utf-8')
        except Exception as e:
            # Just in case reconfigure fails, silently fallback
            pass
        console = logging.StreamHandler(stream)
        console.setFormatter(fmt)
        logger.addHandler(console)

    if not console_mode and not filename:
        logger.addHandler(logging.NullHandler())

    return logger

# ===============================================================================
# Run Methods
# ===============================================================================

def _check_for_errors(json_response):
    """
    Check some JSON response for BotEngine errors
    """
    from botengine import BotError
    if not json_response:
        raise BotError("No response from the server!", -1)

    # Not a PPC cloud response
    if "resultCode" not in json_response:
        return

    # Throw errors for results codes greater than 0
    if json_response["resultCode"] > 0:
        # Map message to json response
        msg = "Unknown error!"
        if "resultCodeMessage" in json_response.keys():
            msg = json_response["resultCodeMessage"]
            del json_response["resultCodeMessage"]
        elif "resultCodeDesc" in json_response.keys():
            msg = json_response["resultCodeDesc"]
            del json_response["resultCodeDesc"]

        # Include full json response in bot error message if additional keys provided
        if len(json_response.keys()) > 1:
            msg += " {}".format(json.dumps(json_response))

        raise BotError(msg, json_response["resultCode"])

    # Remove response code for simplicity
    del json_response["resultCode"]

def _run(
    bot,
    inputs,
    logger,
    context=None,
    server_override=None,
    botengine_override=None,
    local=False,
    playback=False,
    local_execution_count=None,
):
    """
    Run the given bot with the given parameters
    :param bot: bot to run
    :param inputs: the input JSON from the bot server
    :param logger: logger object
    :param server_override: Override the server URL with the known server when executing on someone's computer
    :param botengine_override: For playback simulators, override the botengine object
    :return botengine: BotEngine object
    """
    from botengine.color import Color
    global _bot_loggers
    if playback or local:
        if logger is not None and "botengine" not in _bot_loggers:
            _bot_loggers["botengine"] = logger
    else:
        _bot_loggers = {"botengine": logger}
    _bot_loggers["botengine"].info(">_run()")
    # print(f"bot={bot} inputs={inputs} server_override={server_override} botengine_override={botengine_override} local={local} playback={playback} local_execution_count={local_execution_count}")

    import json
    try:
        _bot_loggers["botengine"].debug(
            "|_run() " + Color.RED + "BotEngine Raw Inputs:\n{}\n".format(json.dumps(inputs, indent=2, sort_keys=True)) + Color.END
        )
    except Exception as e:
        import traceback
        # Ingore error. This might happen during bot playback due to data_request csv content being represented in bytes
        _bot_loggers["botengine"].warning(
            "|_run() Failed checking inputs... {};\ninputs={};\ntraceback={}".format(e, inputs, traceback.format_exc())
        )

    next_timer_at_server = None
    if botengine_override is None:
        services = None
        if "services" in inputs:
            services = inputs["services"]

        count = None
        if "count" in inputs:
            count = int(inputs["count"])

        if "timer" in inputs:
            next_timer_at_server = int(inputs["timer"])
            _bot_loggers["botengine"].debug(
                ">_run() Next timer at server: {}".format(next_timer_at_server)
            )

        cloud = None
        if "cloud" in inputs:
            cloud = inputs["cloud"]

        # Determine the primary location of execution: on the edge or in the cloud.
        edge = False
        if "edgeProxyId" in inputs:
            if inputs["edgeProxyId"] is not None:
                edge = True

        if "id" in inputs:
            bot_instance_id = int(inputs["id"])

        botengine = BotEngine(
            inputs,
            server_override=server_override,
            services=services,
            count=count,
            cloud=cloud,
            edge=edge,
            local=local,
            playback=playback,
            context=context,
            bot_instance_id=bot_instance_id,
            local_execution_count=local_execution_count,
        )

    else:
        botengine = botengine_override

    if botengine.playback:
        if "timer" in inputs:
            next_timer_at_server = int(inputs["timer"])
            _bot_loggers["botengine"].debug(
                "|_run() Next timer at server: {}".format(next_timer_at_server)
            )
    botengine.start_time_sec = time.time()
    if not botengine.edge:
        botengine._download_core_variables()

    botengine.load_variables_time_sec = time.time()

    if not botengine.local and not botengine.playback:
        for server in botengine._servers:
            if "sbox" in server:
                botengine._validate_count()
                break

    all_triggers = []
    for i in inputs["inputs"]:
        all_triggers.append(i["trigger"])

    botengine.all_trigger_types = all_triggers
    timers_existed = False
    timers_executed = False

    botengine.triggers_total = len(all_triggers)

    for execution_json in inputs["inputs"]:
        if botengine.playback and "apiKey" in execution_json:
            botengine.set_api_key(execution_json["apiKey"])
            del execution_json["apiKey"]

        botengine.triggers_index += 1
        execution_time = execution_json["time"]
        if hasattr(logger, "log_time"):
            logger.log_time = execution_time
        try:
            botengine.get_logger(f"{'botengine'}").info(
                "|_run() Current time: "
                + str(execution_json["time"])
                + "; Trigger: "
                + str(execution_json["trigger"])
            )
            botengine.get_logger(f"{'botengine'}").debug(
                "|_run() Run Inputs: " + json.dumps(execution_json, sort_keys=True)
            )
        except Exception as e:
            # Ingore error. This might happen during bot playback due to data_request csv content being represented in bytes
            botengine.get_logger(f"{'botengine'}").warning(
                "|_run() Failed checking execution json... {}".format(e)
            )
        trigger = execution_json["trigger"]

        if trigger == 2048 and len(inputs["inputs"]) > 1:
            botengine.get_logger(f"{'botengine'}").error(
                "|_run() Asynchronous Data Request Trigger contained {} bot inputs, should have only contained a single trigger.".format(
                    len(inputs["inputs"])
                )
            )

        botengine.set_inputs(execution_json)

        # print(f"_run() bot={bot}")
        bot.run(botengine)

    # Cannot execute timers during a data request trigger because those triggers execute concurrently with other executions.
    if any(trigger != 2048 for trigger in all_triggers) and not botengine.edge:
        if trigger == 64:
            # The server just executed a timer, the value it provides does not describe the next execution time.
            next_timer_at_server = None

        if next_timer_at_server and next_timer_at_server < botengine.get_timestamp():
            botengine.get_logger(f"{'botengine'}").info(
                "|run() Next timer at server is in the past: {} < {}".format(next_timer_at_server, botengine.get_timestamp())
            )
            next_timer_at_server = None

        botengine._schedule_next_timer(
            next_timer_at_server
        )

    # Non-time-critical outputs to wrap up
    botengine.flush_commands()
    botengine.flush_questions()
    botengine.flush_analytics()
    botengine.flush_states()
    botengine.flush_binary_variables()
    botengine.flush_rules()
    botengine.flush_tags()
    botengine.flush_asynchronous_requests()
    botengine.get_logger(f"{'botengine'}").debug(
        "|_run() Execution Complete: {}".format(
            bot.get_intelligence_statistics(botengine)
            if hasattr(bot, "get_intelligence_statistics")
            else {}
        )
    )
    botengine.get_logger(f"{'botengine'}").info("<_run()")
    return botengine

# ===============================================================================
# BotEngine Class
# ===============================================================================
class BotEngine:
    """This BotEngine class runs your bot and connects to the Bot Server"""

    # Trigger Types
    TRIGGER_UNPAUSED = 0  # 0
    TRIGGER_SCHEDULE = 1 << 0  # 1
    TRIGGER_MODE = 1 << 1  # 2
    TRIGGER_DEVICE_ALERT = 1 << 2  # 4
    TRIGGER_DEVICE_MEASUREMENT = 1 << 3  # 8
    TRIGGER_QUESTION_ANSWER = 1 << 4  # 16
    TRIGGER_DEVICE_FILES = 1 << 5  # 32
    TRIGGER_TIMER = 1 << 6  # 64
    TRIGGER_METADATA = 1 << 7  # 128
    TRIGGER_DATA_STREAM = 1 << 8  # 256
    TRIGGER_SURVEY = 1 << 9  # 512
    TRIGGER_LOCATION_CONFIGURATION = 1 << 10  # 1024
    TRIGGER_DATA_REQUEST = 1 << 11  # 2048
    TRIGGER_MESSAGES = 1 << 12  # 4096
    TRIGGER_DOCUMENTS = 1 << 13  # 8192

    # Access category types
    ACCESS_CATEGORY_MODE = 1
    ACCESS_CATEGORY_FILE = 2
    ACCESS_CATEGORY_PROFESSIONAL_MONITORING = 3
    ACCESS_CATEGORY_DEVICE = 4
    ACCESS_CATEGORY_CHALLENGE = 5
    ACCESS_CATEGORY_RULES = 6

    # Question Responses
    QUESTION_RESPONSE_TYPE_BOOLEAN = 1
    QUESTION_RESPONSE_TYPE_MULTICHOICE_SINGLESELECT = 2
    QUESTION_RESPONSE_TYPE_MULTICHOICE_MULTISELECT = 4
    QUESTION_RESPONSE_TYPE_DAYOFWEEK = 6
    QUESTION_RESPONSE_TYPE_SLIDER = 7
    QUESTION_RESPONSE_TYPE_TIME = 8
    QUESTION_RESPONSE_TYPE_DATETIME = 9
    QUESTION_RESPONSE_TYPE_TEXT = 10

    # Question display types

    # BOOLEAN QUESTIONS
    QUESTION_DISPLAY_BOOLEAN_ONOFF = 0
    QUESTION_DISPLAY_BOOLEAN_YESNO = 1
    QUESTION_DISPLAY_BOOLEAN_BUTTON = 2
    QUESTION_DISPLAY_BOOLEAN_THUMBS = 3

    # MULTIPLE CHOICE - MULTIPLE SELECT QUESTIONS
    QUESTION_DISPLAY_MCMS_CHECKBOX = 0

    # MULTIPLE CHOICE - SINGLE SELECT QUESTIONS
    QUESTION_DISPLAY_MCSS_RADIO_BUTTONS = 0
    QUESTION_DISPLAY_MCSS_PICKER = 1
    QUESTION_DISPLAY_MCSS_SLIDER = 2
    QUESTION_DISPLAY_MCSS_MODAL_BOTTOM_SHEET = 3

    # DAY OF WEEK QUESTIONS
    QUESTION_DISPLAY_DAYOFWEEK_MULTISELECT = 0
    QUESTION_DISPLAY_DAYOFWEEK_SINGLESELECT = 1

    # SLIDER
    QUESTION_DISPLAY_SLIDER_INTEGER = 0
    QUESTION_DISPLAY_SLIDER_FLOAT = 1
    QUESTION_DISPLAY_SLIDER_MINSEC = 2

    # TIME
    QUESTION_DISPLAY_TIME_HOURS_MINUTES_SECONDS_AMPM = 0
    QUESTION_DISPLAY_TIME_HOURS_MINUTES_AMPM = 1

    # DATETIME
    QUESTION_DISPLAY_DATETIME_DATE_AND_TIME = 0
    QUESTION_DISPLAY_DATETIME_DATE = 1

    # Answer Status
    ANSWER_STATUS_NOT_ASKED = -1
    ANSWER_STATUS_DELAYED = 0
    ANSWER_STATUS_QUEUED = 1
    ANSWER_STATUS_AVAILABLE = 2
    ANSWER_STATUS_SKIPPED = 3
    ANSWER_STATUS_ANSWERED = 4
    ANSWER_STATUS_NO_ANSWER = 5

    # Professional Monitoring
    PROFESSIONAL_MONITORING_NEVER_PURCHASED = 0
    PROFESSIONAL_MONITORING_PURCHASED_BUT_NOT_ENOUGH_INFO = 1
    PROFESSIONAL_MONITORING_REGISTRATION_PENDING = 2
    PROFESSIONAL_MONITORING_REGISTERED = 3
    PROFESSIONAL_MONITORING_CANCELLATION_PENDING = 4
    PROFESSIONAL_MONITORING_CANCELLED = 5

    # Professional monitoring alert status
    PROFESSIONAL_MONITORING_ALERT_STATUS_QUIET = 0
    PROFESSIONAL_MONITORING_ALERT_STATUS_RAISED = 1
    PROFESSIONAL_MONITORING_ALERT_STATUS_CANCELLED = 2
    PROFESSIONAL_MONITORING_ALERT_STATUS_REPORTED = 3

    # Rule status
    RULE_STATUS_INCOMPLETE = 0
    RULE_STATUS_ACTIVE = 1
    RULE_STATUS_INACTIVE = 2

    # Data stream destinations
    DATASTREAM_ORGANIZATIONAL_FIELD_TO_INDIVIDUALS = 1
    DATASTREAM_ORGANIZATIONAL_FIELD_TO_ORGANIZATIONS = 2
    DATASTREAM_ORGANIZATIONAL_FIELD_TO_ALL = 3

    # Narrative priority levels
    NARRATIVE_PRIORITY_DEBUG = -2
    NARRATIVE_PRIORITY_ANALYTIC = -1
    NARRATIVE_PRIORITY_DETAIL = 0
    NARRATIVE_PRIORITY_INFO = 1
    NARRATIVE_PRIORITY_WARNING = 2
    NARRATIVE_PRIORITY_CRITICAL = 3

    # Narrative types
    # High-frequency 'observation' entries for explainable AI and accountability
    NARRATIVE_TYPE_OBSERVATION = 0

    # Low-frequency 'journal' entries for SUMMARIZED exec-level communications to humans
    NARRATIVE_TYPE_JOURNAL = 4

    # High-frequency 'insight' entries for real-time CRITICAL exec-level communications to humans
    NARRATIVE_TYPE_INSIGHT = 5

    # Alert Categories
    ALERT_CATAGORY_NONE = 0
    ALERT_CATEGORY_LIVE_HERE = 1
    ALERT_CATEGORY_FAMILY_FRIEND = 2
    ALERT_CATEGORY_SOCIAL_REMINDERS_ONLY = 3

    # Location Access
    LOCATION_ACCESS_NONE = 0
    LOCATION_ACCESS_READONLY = 10
    LOCATION_ACCESS_CONTROL_DEVICES = 20
    LOCATION_ACCESS_CONTROL_EVERYTHING = 30

    # Support Ticket Types
    TICKET_TYPE_PROBLEM = 1
    TICKET_TYPE_INCIDENT = 2
    TICKET_TYPE_QUESTION = 3
    TICKET_TYPE_TASK = 4

    # Support Ticket Priorities
    TICKET_PRIORITY_LOW = 1
    TICKET_PRIORITY_NORMAL = 2
    TICKET_PRIORITY_HIGH = 3
    TICKET_PRIORITY_URGENT = 4

    # Tagging
    TAG_TYPE_USERS = 1
    TAG_TYPE_LOCATIONS = 2
    TAG_TYPE_DEVICES = 3
    TAG_TYPE_FILES = 4

    # Data request types
    DATA_REQUEST_TYPE_PARAMETERS = 1
    DATA_REQUEST_TYPE_ACTIVITIES = 2
    DATA_REQUEST_TYPE_LOCATIONS = 3
    DATA_REQUEST_TYPE_MODES = 4
    DATA_REQUEST_TYPE_NARRATIVES = 5
    DATA_REQUEST_TYPE_DEVICES = 6

    BOT_TYPE_LOCATION = 0
    BOT_TYPE_ORGANIZATION = 1
    BOT_TYPE_ORGANIZATION_RAG = 2

    # Location Sub Types
    LOCATION_SUB_TYPE_ALL = 0
    LOCATION_SUB_TYPE_DEVICE = 1

    def __init__(
        self,
        raw_inputs,
        server_override=None,
        services=None,
        count=None,
        cloud=None,
        edge=False,
        local=False,
        playback=False,
        context=None,
        bot_instance_id=None,
        local_execution_count=None,
        logger=None,
    ):
        """
        Constructor
        :param raw_inputs: The entire input JSON string from the Bot Server
        :param server_override: Option to override the server URL when executing on someone's computer instead of in the cloud
        :param services: List of subscription services in the user's account
        :param count: Each time the bot triggers, the count should increment by 1 when running on the server. The count is always 0 when running locally on a computer.
        :param cloud: Description of the cloud server
        :param edge: True if the edge owns execution of the bot instead of the cloud
        :param bot_instance_id: Instance ID of this bot
        """
        from botengine import BotError
        # if logger is not None:
        #     global _bot_loggers
        #     if _bot_loggers is None:
        #         _bot_loggers = {}
        #     _bot_loggers["botengine"] = logger

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(">__init__()")
        bot_type = self.get_bot_type()

        # User's API key
        if bot_type != BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            if "apiKey" not in raw_inputs:
                raise BotError("No API key provided in the inputs")
            self.__key = raw_inputs["apiKey"]

            # Remove the evidence of the API key and host so they can't be seen by probing externally
            del raw_inputs["apiKey"]

            # Server to connect with
            if server_override is not None:
                self._servers = [server_override]

            elif "apiHosts" in raw_inputs:
                self._servers = raw_inputs["apiHosts"]

            elif "apiHost" in raw_inputs:
                self._servers = [raw_inputs["apiHost"]]

        else:
            # No API Key
            self.__key = None

            # No servers
            self._servers = []

        # Raw inputs for debugging reference
        self._raw_inputs = raw_inputs

        # The current server index used for requests
        self._server_index = 0

        # Lock the server index when we successfully post the start key
        self._server_locked = False

        # Dynamically imported requests module
        self._requests = importlib.import_module("requests")

        # Description of the cloud we are running on
        self._cloud = cloud

        # List of the user's services dictionaries
        self.services = services

        # List of all the trigger types we expect to execute in and around this single execution instance
        self.all_trigger_types = []

        # Trigger count, which is incremented on every trigger when running on the server
        self.count = count

        # Dictionary of variables by name
        self.variables = {}

        # Dictionary of the variables that need to be stored to the cloud, by name
        self.variables_to_flush = {}

        # State content in our cache.  { timestamp_ms : { state_json_dictionary } }
        # This does not include extra STATE_KEY_* fields used in the self.states_to_flush cache, it's just the raw state content
        # Non-time-series states simply have a timestamp_ms of None.
        self.states = {None: {}}

        # State content to flush.
        # Each state to flush will include extra fields beyond the content to declare how to save the state.
        # Non-time-series states will simply have a timestamp_ms of None.
        #     {
        #         timestamp_ms : {
        #             "state_address": {
        #                 STATE_KEY_CONTENT: json_content,
        #                 STATE_KEY_PUBLISH: True or False to publish to a partner,
        #                 STATE_KEY_OVERWRITE: True to overwrite the whole JSON content on the server, or False if we're just providing a few top-level keys to update.
        #                 STATE_KEY_UPDATE_LIST: [optional, list, of, top-level, keys, added, or, updated],
        #                 STATE_KEY_DELETE_LIST: [optional, list, of, top-level, keys, deleted],
        #                 STATE_KEY_SUB_LOCATION: True to also save state to sub location,
        #             }
        #         }
        #     }
        self.states_to_flush = {}

        # Question that was answered as we triggered the bot from an answered question
        self.question_answered = None

        # self.commands_to_flush format: [ << array of devices, with an array of params in each device >> ]
        self.commands_to_flush = []

        # Asynchronous data requests
        self.data_requests = []

        # Tags to create on the server
        self.tags_to_create = []

        # Tags to delete on the server
        self.tags_to_delete = []

        # Dictionary of tags to create by user ID, for admins
        self.tags_to_create_by_user = {}

        # Dictionary of tags to delete by user ID, for admins
        self.tags_to_delete_by_user = {}

        # Dictionary of rules to toggle
        self.rules = {}

        # Dictionary of new questions to ask
        self.questions_to_ask = {}

        # Dictionary of questions to delete
        self.questions_to_delete = {}

        # Organization properties to override local bot default settings
        self.organization_properties = {}

        # We only need to issue an API call to cancel timers once per execution
        self.cancelled_timers = False

        # This is the total number of triggers we'll be handling in this execution. Primarily used for debugging.
        self.triggers_total = 0

        # When we have multiple triggers in one execution, this is which trigger number we're handling now.
        self.triggers_index = 0

        # Cache for location users information so we never call it multiple times
        self._location_users_cache = None

        # User ID executing that caused this trigger
        self.user_id = None

        # Is this bot executing on the edge
        self.edge = edge

        # Is this bot executing locally on a developer laptop
        self.local = local

        # How many times has this bot been run locally
        # Enabling us to know if it's the first run and a new_version() should be triggered, or gather stats if we want.
        self.local_execution_count = local_execution_count

        # True if this bot is being executed with previously recorded data
        self.playback = playback

        # What is this bot's instance ID
        self.bot_instance_id = bot_instance_id

        # Forcefully set to True to declare this bot is currently executing in the cloud.
        # This is set to False inside botclient.py where we execute on the edge.
        self.executing_in_cloud = True

        # Start time set externally from time.time() 
        self.start_time_sec = None

        # HTTP Session
        self.session = self._requests.Session()

        all_triggers = []
        if "inputs" in raw_inputs:
            for i in raw_inputs["inputs"]:
                all_triggers.append(i["trigger"])

        debug_instance_id = 0
        if bot_instance_id is not None:
            debug_instance_id = bot_instance_id
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|__init__() Instance ID: {}; Triggers: {}".format(
                debug_instance_id, all_triggers
            )
        )

        if self.local:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|__init__() Running locally"
            )
            return
        if self.playback:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|__init__() Running in playback mode"
            )
            return
        if bot_type == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|__init__() Running as an organization RAG bot"
            )
            return

        if "startKey" not in raw_inputs:
            raise Exception("No start key in inputs")

        if raw_inputs["startKey"] == 0:
            raise Exception("Start key is 0")

        if not self._start(raw_inputs["startKey"], context=context):
            raise Exception(
                "Failed to start bot with start key: " + str(raw_inputs["startKey"])
            )
        self._server_locked = True

    def _start_core_variables_thread(self):
        if not hasattr(self, "thread_event"):
            import threading

            self.thread_event = threading.Event()
            self.request_thread = threading.Thread(
                target=self._download_core_variables_async, args=(self.thread_event,)
            )

        if not self.thread_event.is_set():
            self.request_thread.start()

    def is_core_variables_downloaded(self):
        return not self.thread_event.is_set()

    # ===========================================================================
    # HTTP Methods
    # ===========================================================================
    def _http_get(self, path, headers={}, params=None, timeout=5, stream=False):
        """
        HTTP GET
        :param path: Path to retrieve
        :param headers: Dictionary of headers, which will override any default headers
        :param params: Dictionary of parameters
        :param timeout: Timeout in seconds, default is 5
        :param stream: True to stream. Default is False.
        :return: Response object from Requests module
        """
        if self.playback:
            return

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return {}

        global _https_proxy
        h = self._build_common_headers()
        h.update(headers)

        while True:
            try:
                r = self.session.get(
                    self._servers[self._server_index] + path,
                    params=params,
                    headers=h,
                    timeout=timeout,
                    proxies=_https_proxy,
                    stream=stream,
                )
                return r
            except Exception as e:
                timeout = self._http_exception_handler("GET", path, timeout, e)

    def _http_post(self, path, headers={}, params=None, data=None, timeout=5):
        """
        HTTP POST
        :param path: Path to retrieve
        :param headers: Dictionary of headers, which will override any default headers
        :param params: Dictionary of parameters
        :param data: Data to POST
        :param timeout: Timeout in seconds, default is 5
        :return: Response object from Requests module
        """
        if self.playback:
            return

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return {}

        global _https_proxy
        h = self._build_common_headers()
        h.update(headers)

        while True:
            try:
                r = self.session.post(
                    self._servers[self._server_index] + path,
                    params=params,
                    headers=h,
                    data=data,
                    timeout=timeout,
                    proxies=_https_proxy,
                )
                return r
            except Exception as e:
                timeout = self._http_exception_handler("POST", path, timeout, e)

    def _http_put(self, path, headers={}, params=None, data=None, timeout=5):
        """
        HTTP PUT
        :param path: Path to retrieve
        :param headers: Dictionary of headers, which will override any default headers
        :param params: Dictionary of parameters
        :param data: Data to PUT
        :param timeout: Timeout in seconds, default is 5
        :return: Response object from Requests module
        """
        if self.playback:
            return

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return {}

        global _https_proxy
        h = self._build_common_headers()
        h.update(headers)

        while True:
            try:
                r = self.session.put(
                    self._servers[self._server_index] + path,
                    params=params,
                    headers=h,
                    data=data,
                    timeout=timeout,
                    proxies=_https_proxy,
                )
                return r
            except Exception as e:
                timeout = self._http_exception_handler("PUT", path, timeout, e)

    def _http_delete(self, path, headers={}, params=None, timeout=5):
        """
        HTTP PUT
        :param path: Path to retrieve
        :param headers: Dictionary of headers, which will override any default headers
        :param params: Dictionary of parameters
        :param data: Data to PUT
        :param timeout: Timeout in seconds, default is 5
        :return: Response object from Requests module
        """
        if self.playback:
            return

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return {}

        global _https_proxy
        h = self._build_common_headers()
        h.update(headers)

        while True:
            try:
                r = self.session.delete(
                    self._servers[self._server_index] + path,
                    params=params,
                    headers=h,
                    timeout=timeout,
                    proxies=_https_proxy,
                )
                return r
            except Exception as e:
                timeout = self._http_exception_handler("DELETE", path, timeout, e)

    def _http_exception_handler(self, request_type, path, timeout, e):
        """
        Handle HTTP exceptions
        :param request_type: Type of request (GET, POST, etc.)
        :param exception: Exception object
        :return: Updated timeout value
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">_http_exception_handler()"
        )
        if isinstance(e, self._requests.HTTPError):
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                f"|_http_exception_handler() Generic HTTP error calling {request_type} "
                + str(self._servers[self._server_index] + path)
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_http_exception_handler() Error:  {}".format(e)
            )

        elif isinstance(e, self._requests.ConnectionError):
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                f"|_http_exception_handler() Connection HTTP error calling {request_type} "
                + str(self._servers[self._server_index] + path)
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_http_exception_handler() Error:  {}".format(e)
            )

        elif isinstance(e, self._requests.Timeout):
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|_http_exception_handler() " 
                + str(timeout)
                + f" second HTTP Timeout calling {request_type} "
                + str(self._servers[self._server_index] + path)
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_http_exception_handler() Error:  {}".format(e)
            )
            timeout += 5
            if timeout >= 25:
                raise self._requests.Timeout()

        elif isinstance(e, self._requests.TooManyRedirects):
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                f"|_http_exception_handler() Too many redirects HTTP error calling {request_type} "
                + str(self._servers[self._server_index] + path)
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_http_exception_handler() Error:  {}".format(e)
            )

        else:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                f"|_http_exception_handler() Generic HTTP exception calling {request_type} "
                + str(self._servers[self._server_index] + path)
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_http_exception_handler() Error:  {}".format(e)
            )
        
        if self._server_locked:
            return timeout
        server = self._servers[self._server_index]
        self._server_index += 1
        self._server_index %= len(self._servers)
        if server != self._servers[self._server_index]:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                f"|_http_exception_handler() Switching server {self._servers[self._server_index]}"
            )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "<_http_exception_handler()"
        )
        return timeout

    # ===========================================================================
    # System Helper Methods
    # ===========================================================================
    def set_inputs(self, inputs):
        """
        Set the inputs for this execution
        :param inputs: Inputs for this next execution
        """
        self.inputs = inputs

        if "userId" in inputs:
            self.user_id = inputs["userId"]

        if self.inputs["trigger"] == BotEngine.TRIGGER_QUESTION_ANSWER:
            question_block = self.inputs["question"]
            self.resynchronize_questions()
            saved_questions = self.load_variable(QUESTIONS_VARIABLE_NAME)
            if saved_questions is not None:
                if question_block["key"] in saved_questions:
                    self.question_answered = saved_questions[question_block["key"]]
                    if "userId" in inputs:
                        self.question_answered.user_id = inputs["userId"]
                    else:
                        self.question_answered.user_id = None

        # Extract custom organization bot properties
        if "access" in inputs:
            for access in inputs["access"]:
                try:
                    properties = access["location"]["organization"]["properties"]
                    # Set each organization property but remove the static bot identifier "bot." from the beginning
                    for key in properties:
                        # Try to normalize the value
                        try:
                            value = eval(properties[key], {}, {})
                        except Exception:
                            if properties[key] in ["true", "True"]:
                                value = True
                            elif properties[key] in ["false", "False"]:
                                value = False
                            else:
                                value = properties[key]

                        self.organization_properties[key.replace("bot.", "")] = value
                    break
                except Exception:
                    pass

    def _enable_debug(self):
        """
        Enable debug logging
        """
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def _build_common_headers(self, content_type="application/json"):
        """
        Build common HTTP headers for API calls
        :param content_type: Content type of the request, default is 'application/json'
        :return: HTTP Header dictionary to inject into HTTP requests
        """
        return {
            "ANALYTIC_API_KEY": self.__key,
            "Content-Type": content_type,
            "User-Agent": "BotEngine/" + str(__version__),
        }

    def _start(self, start_key, context=None):
        """
        Called once at the start of execution to prevent 2 bots of the same instance from executing in parallel.
        The first server to return a success is used for the rest of the execution.
        :param start_key:
        :return: True if the start is successful; False if it's not successful
        """
        from botengine import BotError
        params = {"startKey": start_key}

        if context is not None and self.is_server_version_newer_than(1, 10):
            params["awsRequestId"] = context.aws_request_id
            params["logStreamName"] = context.log_stream_name
        r = self._http_post(
            "/analytic/start",
            params=params,
            timeout=DEFAULT_START_KEY_TIMEOUT_S,
        )

        logger = self.get_logger(f"{'botengine'}.{__class__.__name__}")
        logger.debug(
            "|_start() Notify cloud that the bot is starting: /analytic/start params={}".format(
                params
            )
        )

        try:
            j = json.loads(r.text)
            logger.debug("|_start() Cloud response to /analytic/start: {}".format(j))
            _check_for_errors(j)
            if "resultCode" in j:
                if j["resultCode"] != 0:
                    # This execution is not allowed
                    logger.start_code = j["resultCode"]
                    raise BotError(
                        "Wrong Start API result code. Response={}".format(
                            json.dumps(j)
                        ),
                        j["resultCode"],
                    )
            logger.debug("|_start() Success, the bot has started {}".format(j))
            return True

        except json.decoder.JSONDecodeError as e:
            # Probably because the server is restarting
            logger.warning("|_start() Failure, the bot has not started. {}".format(e))
            return False

        except BotError as e:
            logger.error("|_start() Failure, the bot has not started.. {}".format(e))
            return False

    # ===========================================================================
    # Developer helper methods
    # ===========================================================================
    def get_inputs(self):
        """
        This method will return the inputs, e.g. apiKey, apiHost, trigger type, alerts, measurement blocks
        :return: all inputs in a JSON dictionary format
        """
        return self.inputs

    def get_trigger_type(self):
        """
        This method will return the type of trigger that your bot uses
        * Trigger 1 = Schedule (based off a cron schedule inside the runtime.json file)
        * Trigger 2 = Location Event (switching between home / away / etc.)
        * Trigger 4 = Device Alert
        * Trigger 8 = Device Measurements
        * Trigger 16 = Question Answered
        * Trigger 32 = New device file (like a video or picture)
        * Trigger 64 = Execute Again Countdown Timer
        * Trigger 256 = Data Stream Message

        :return: Trigger type that triggered this bot
        """
        return int(self.inputs["trigger"])

    def get_triggers(self):
        """
        This method will find and return the information about what triggered this bot.

        Location Events (Modes) Example:
          {
            'category':1,
            'control':True,
            'trigger':True,
            'location':{
               'locationId':62,
               'prevEvent':'HOME',
               'event':'AWAY'
            },
            'read':True
          }


        Device Measurements Example:
          {
            'trigger':True,
            'device':{
              'deviceType':10014,
               'updateDate':1465517032000,
               'deviceId':'FFFFFFFF00600a70',
               'description':'Practice\xa0Entry\xa0Sensor',
               'measureDate':1465517031000
            },
            'read':True,
            'control':True,
            'category':4
          }

        :return: JSON structure describing what triggered this bot
        """
        if "access" not in self.inputs:
            return []

        self.trigger_blocks = []

        for block in self.inputs["access"]:
            if "trigger" in block:
                if block["trigger"]:
                    self.trigger_blocks.append(block)

        return self.trigger_blocks

    def get_measures_block(self):
        """
        :return: the measurements block from our inputs, if any
        """
        if "measures" in self.inputs:
            return self.inputs["measures"]

        return None

    def get_alerts_block(self):
        """
        :return: the alerts block from our inputs, if any
        """
        if "alerts" in self.inputs:
            return self.inputs["alerts"]

        return None

    def get_access_block(self):
        """
        :return: the access block from our inputs, if any
        """
        if "access" in self.inputs:
            return self.inputs["access"]

        return None

    def get_device_access_block(self, device_id):
        """
        Return the access block for a specific device
        :param device_id: Device ID to search for
        :return: Access block for a specific device, None if it doesn't exist
        """
        if "access" in self.inputs:
            for a in self.inputs["access"]:
                if a["category"] == BotEngine.ACCESS_CATEGORY_DEVICE:
                    if "device" in a:
                        if a["device"]["deviceId"] == device_id:
                            return a

        return None

    def is_executing_timer(self):
        """
        :return: True if this execution includes a timer fire
        """
        return 64 in self.all_trigger_types

    def get_bundle_id(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the bundle ID.
        This method simply returns the bundle ID from the contents of that file.
        :return: The bundle ID for this bot
        """
        import bundle  # type: ignore

        return bundle.BUNDLE_ID

    def get_cloud_address(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the cloud address we're uploading the bot to.
        This method simply returns the CLOUD_ADDRESS from the contents of the bundle.py file.
        :return: The cloud address for this bot
        """
        import bundle  # type: ignore

        return bundle.CLOUD_ADDRESS

    def get_bot_type(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the bot type.
        This method simply returns the BOT_TYPE from the contents of the bundle.py file.
        :return: The bot type for this bot
        """
        import bundle  # type: ignore

        return int(bundle.BOT_TYPE if hasattr(bundle, "BOT_TYPE") else 0)

    def get_bot_instance_id(self):
        """
        :return: The bot instance ID
        """
        return self.bot_instance_id

    def get_location_id(self, device_id=None):
        """
        :return: The location ID for this bot
        """
        if device_id is not None:
            access_block = self.get_device_access_block(device_id)
            if access_block is not None:
                if "locationId" in access_block.get("device", {}):
                    return access_block["device"]["locationId"]
        return self.inputs["locationId"]

    def get_organization_id(self):
        """
        :return: The organization ID for this bot
        """
        info = self.get_location_info()
        if "location" in info:
            if "organizationId" in info["location"]:
                return int(info["location"]["organizationId"])

        return None

    def get_organization_name(self):
        """
        :return: The name of the organization this location belongs to.
        """
        info = self.get_location_info()
        if "location" in info:
            if "organization" in info["location"]:
                if "organizationName" in info["location"]["organization"]:
                    return info["location"]["organization"]["organizationName"]

        return "Organization ID {}".format(self.get_organization_id())

    def get_organization_signup_code(self):
        """
        :return: The sign-up code (short domain name) of the organization this location belongs to. Or None if we don't have it for some reason.
        """
        info = self.get_location_info()
        if "location" in info:
            if "organization" in info["location"]:
                if "domainName" in info["location"]["organization"]:
                    return info["location"]["organization"]["domainName"]

        return None

    def get_country_code(self):
        """
        :return: The country code of the location.
        """
        info = self.get_location_info()
        if "location" in info:
            if (
                "country" in info["location"]
                and "countryCode" in info["location"]["country"]
            ):
                return info["location"]["country"]["countryCode"]

        return None

    def get_location_info(self, sub_type=LOCATION_SUB_TYPE_ALL):
        """
        Returns this information:
            {
              "category": 1,
              "control": true,
              "location": {
                "event": "STAY",
                "latitude": "47.72328",
                "locationId": 755735,
                "longitude": "-122.17426",
                "name": "Apartment 103",
                "timezone": {
                  "dst": true,
                  "id": "US/Pacific",
                  "name": "Pacific Standard Time",
                  "offset": -480
                },
                "zip": "98034"
              },
              "read": true,
              "trigger": false
            }

        :param location_id: Location ID to extract
        :param sub_type: Location sub type to extract, default is LOCATION_SUB_TYPE_ALL
        :return: location information from the access block
        """
        # Return the first location that matches our sub type
        for access in self.inputs.get("access", []):
            if access.get("category", "") == self.ACCESS_CATEGORY_MODE:
                if (
                    access
                    .get("location", {})
                    .get("subType", 0) == sub_type
                ):
                    return access

        return {}

    def get_locations(self):
        """
        :return: All locations available to this bot
        """
        locations = []
        for access in self.inputs.get("access", []):
            if access.get("category", "") == self.ACCESS_CATEGORY_MODE:
                locations.append(access)

        return locations

    def is_playback(self):
        return self.playback

    def is_test_location(self):
        """
        Determine if this is a test (internal employee) location, possibly to avoid logging analytics.
        :return: True if this is a test location
        """
        info = self.get_location_info()
        if info is not None and "location" in info:
            if "test" in info["location"]:
                return info["location"]["test"]

        return False

    def get_location_name(self):
        """
        :return: Name of this location
        """
        location_info = self.get_location_info()
        if location_info is None:
            return "Home"

        if "location" not in location_info:
            return "Home"

        if "name" not in location_info["location"]:
            return "Home"

        return location_info["location"]["name"]

    def get_location_latitude(self):
        """
        :return: Location latitude, or None if it doesn't exist
        """
        location_info = self.get_location_info()
        if location_info is None:
            return None

        if "location" not in location_info:
            return None

        if "latitude" not in location_info["location"]:
            return None

        return float(location_info["location"]["latitude"])

    def get_location_longitude(self):
        """
        :return: Location longitude, or None if it doesn't exist
        """
        location_info = self.get_location_info()
        if location_info is None:
            return None

        if "location" not in location_info:
            return None

        if "longitude" not in location_info["location"]:
            return None

        return float(location_info["location"]["longitude"])

    def get_answered_question(self):
        """
        :return: the question that has been answered, if any
        """
        return self.question_answered

    def get_datastream_block(self):
        """
        :return: the data stream inputs, if any
        """
        if "dataStream" in self.inputs:
            return self.inputs["dataStream"]

        return None

    def get_input_key(self):
        """
        :return: the key provided by the input, if any
        """
        if "key" in self.inputs:
            return self.inputs["key"]

        return None

    def get_file_block(self):
        """
        :return: the 'file' block for an uploaded file, if any
        """
        if "file" in self.inputs:
            return self.inputs["file"]

        return None

    def get_timestamp(self):
        """
        :return: the Unix timestamp of this execution, in milliseconds
        """
        return self.inputs["time"]

    def set_timestamp(self, timestamp_ms):
        """
        :param: timestamp_ms Time in milliseconds to set the current input time to.
        :return:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"|set_timestamp() timestamp={timestamp_ms}")
        self.inputs["time"] = timestamp_ms
        if hasattr(self.get_logger(f"{'botengine'}"), "log_time"):
            self.get_logger(f"{'botengine'}").log_time = timestamp_ms
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info("|set_timestamp() set lambda log_time")

    def get_data_stream_message(self):
        self.get_datastream_block()

    def get_documents_request_id(self):
        """
        :return: the documents request ID
        """
        return self.inputs.get("requestId", None)

    def get_document_block(self):
        """
        :return: the 'document' block for location configuration triggers
        """
        return self.inputs.get("document", None)

    def get_users_block(self):
        """
        :return: The 'users' block for location configuration triggers
        """
        if "users" in self.inputs:
            return self.inputs["users"]

        return None

    def get_callcenter_block(self):
        """
        :return: The 'callCenter' block for location configuration triggers
        """
        if "callCenter" in self.inputs:
            return self.inputs["callCenter"]

        return None

    def get_data_block(self):
        """
        :return: The 'data' block for asynchronous data request inputs
        """
        if "data" in self.inputs:
            return self.inputs["data"]

        return None

    def get_messages_block(self):
        """
        :return: the messages block from our inputs, if any
        """
        if "messages" in self.inputs:
            return self.inputs["messages"]
        return None

    def get_survey_block(self):
        """
        :return: the survey block from our inputs, if any
        """
        if "survey" in self.inputs:
            return self.inputs["survey"]
        return None

    def get_property(
        self, obj_arr, property_name, property_value, return_property_name
    ):
        """
        This method will locate the specified first object from object array, and then return the specified property value

        :param obj_arr: object array
        :param property_name: the key in searching criteria
        :param property_value: the value in searching criteria
        :param return_property_name: the key in the object indicates which corresponding value will be returned
        """
        response = None
        for item in obj_arr:
            if item[property_name] == property_value:
                response = item[return_property_name]
                break

        return response

    def get_language(self, user_id=None):
        """
        Get the language for the bot associated with this organization, bot domain, location, or user.
        :param user_id: User ID to get the language for.
        :return: language code
        """
        import properties
        language_code = properties.get_property(self, "DEFAULT_LANGUAGE", complain_if_missing=False)

        location_info = self.get_location_info()
        if location_info is not None:
            if "language" in location_info.get("location", {}):
                language_code = location_info["location"]["language"]
        if user_id is not None:
            user = self.get_location_user(user_id)
            if user is not None:
                if "language" in user:
                    language_code = user["language"]
        # Default to English
        return language_code if language_code is not None else "en" 

    def is_server_version_newer_than(self, major, minor=0):
        """
        Compare the server version.
        :param major: Major value
        :param minor: Minor value
        :return: True if the server version is greater than or equal to the input version
        """
        semantic_version = str(self._raw_inputs["version"]).split(".")
        _major = semantic_version[0]
        _minor = 0
        if len(semantic_version) > 1:
            _minor = semantic_version[1]
        is_newer = int(_major) > int(major) or (
            int(_major) == int(major) and int(_minor) >= int(minor)
        )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|is_server_version_newer_than() {}.{} >> {}.{} == {}".format(
                _major, _minor, major, minor, is_newer
            )
        )
        return is_newer

    # ===========================================================================
    # Users
    # ===========================================================================
    def get_location_users(self):
        """
        Get the list of users at this location ID
        https://iotapps.docs.apiary.io/#reference/locations/location-users/get-location-users
        :param location_id: Location ID
        """
        if self.playback:
            self._location_users_cache = [
                {
                    "id": 123,
                    "userName": "john.smith@gmail.com",
                    "altUsername": "1234567890",
                    "firstName": "John",
                    "lastName": "Smith",
                    "nickname": "Johnny",
                    "email": {
                        "email": "john.smith@gmail.com",
                        "verified": True,
                        "status": 0,
                    },
                    "phone": "1234567890",
                    "phoneType": 1,
                    "smsStatus": 1,
                    "locationAccess": 10,
                    "temporary": True,
                    "accessEndDate": "2019-01-29T02:45:30Z",
                    "accessEndDateMs": 1548747995000,
                    "category": 1,
                    "role": 1,
                    "smsPhone": "1234567899",
                    "language": "en",
                    "avatarFileId": 123,
                    "schedules": [
                        {"daysOfWeek": 127, "startTime": 10800, "endTime": 20800}
                    ],
                },
                {
                    "id": 124,
                    "userName": "jane.smith@gmail.com",
                    "altUsername": "1234567891",
                    "firstName": "Jane",
                    "lastName": "Smith",
                    "nickname": "Janey",
                    "email": {
                        "email": "jane.smith@gmail.com",
                        "verified": True,
                        "status": 0,
                    },
                    "phone": "1234567891",
                    "phoneType": 1,
                    "smsStatus": 1,
                    "locationAccess": 40,
                    "temporary": True,
                    "accessEndDate": "2019-01-29T02:45:30Z",
                    "accessEndDateMs": 1548747995000,
                    "category": 1,
                    "role": 4,
                    "smsPhone": "1234567899",
                    "language": "en",
                    "avatarFileId": 123,
                    "schedules": [
                        {"daysOfWeek": 127, "startTime": 10800, "endTime": 20800}
                    ],
                },
            ]

        if self._location_users_cache is not None:
            return self._location_users_cache

        r = self._http_get(
            "/cloud/json/location/{}/users".format(self.get_location_id())
        )
        j = json.loads(r.text)
        _check_for_errors(j)

        if "users" in j:
            self._location_users_cache = j["users"]
            return j["users"]

        else:
            self._location_users_cache = []
            return []

    def get_location_user(self, user_id):
        """
        Retrieve all information about one specific user at this location ID
        :param user_id:
        :return:
        """
        users = self.get_location_users()
        for user in users:
            if user["id"] == user_id:
                return user
        return None

    def set_location_user_alert_category(self, user_id, category):
        """
        Set the alert category of a specific user associated with this location.
        One way to use this is to opt-out users from receiving SMS messages when they reply "STOP"
        :param botengine: BotEngine environment
        :param user_id: User ID
        :param category: Category to move to. 0=No Alerts; 1=I live here; 2=Family/Friend; 3=social reminders only
        """
        body = {"user": {"id": user_id, "category": category}}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|set_location_user_alert_category() \n{}".format(
                json.dumps(body, sort_keys=True)
            )
        )
        r = self._http_put(
            "/cloud/json/location/{}/users".format(self.get_location_id()),
            data=json.dumps(body),
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def set_location_user_access_category(self, user_id, location_access_level):
        """
        Set the location access level for a specific user associated with this location.
        One way to use this is to opt-out users from receiving SMS messages when they reply "STOP"
        :param botengine: BotEngine environment
        :param user_id: User ID
        :param location_access_level: 0 = No Access; 10 = Read all location and device information; 20 = Control location modes and control devices; 30 = Administrate location and manage devices
        """
        body = {"user": {"id": user_id, "locationAccess": location_access_level}}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|set_location_user_access_category() \n{}".format(
                json.dumps(body, sort_keys=True)
            )
        )
        r = self._http_put(
            "/cloud/json/location/{}/users".format(self.get_location_id()),
            data=json.dumps(body),
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def get_resident_last_names(self):
        """
        Return a string that represents the resident's last names.
        If there are no last names, it returns ""
        If there is one last name, that last name is returned.
        If there are two or more last names like Moss and Neufeld then "Moss/Neufeld" is returned.
        :return: String representing location residents' last names.
        """
        last_name = ""
        first = True
        users = self.get_location_users()
        last_names_list = []
        for user in users:
            if user["category"] == 1:
                # This is a resident of the location
                if "lastName" in user:
                    if first:
                        first = False
                        last_name = user["lastName"]
                        last_names_list.append(user["lastName"].lower().strip())

                    else:
                        if (
                            user["lastName"].lower().strip() not in last_names_list
                            and user["lastName"].strip() != ""
                        ):
                            last_name += "/{}".format(user["lastName"])
                            last_names_list.append(user["lastName"].lower().strip())

        return last_name

    def get_location_user_names(
        self, to_residents=True, to_supporters=True, sms_only=True
    ):
        """
        Get a list of users' names associated with the location.

        [
          {
            'firstName': 'David'
            'lastName': 'Moss'
          },
          ...
        ]

        :param residents: Extract residents
        :param supporters: Extract supporters
        :param sms_only: True if we only want to extract users who we can SMS
        :return: List of dictionaries containing first and last names
        """
        names = []

        users = self.get_location_users()
        if len(users) > 0:
            for user in users:
                if (to_residents and user["category"] == 1) or (
                    to_supporters and user["category"] == 2
                ):
                    if sms_only:
                        if "smsStatus" in user:
                            if user["smsStatus"] == 3:
                                continue

                        if "phoneType" in user:
                            if user["phoneType"] != 1:
                                continue
                        if "phoneChannels" in user:
                            if "sms" in user["phoneChannels"]:
                                if not user["phoneChannels"]["sms"]:
                                    continue

                    name = {"firstName": None, "lastName": None}

                    if "firstName" in user:
                        name["firstName"] = user["firstName"]

                    if "lastName" in user:
                        name["lastName"] = user["lastName"]

                    names.append(name)

            return names

        return []

    def get_name_by_user_id(self, user_id):
        """
        Returns a dictionary with 'firstName' and 'lastName' if the user exists, or None if the user doesn't exist
        :param user_id: User ID to extract the name
        :return: { 'firstName': "David", 'lastName': "Moss" }
        """
        users = self.get_location_users()
        for user in users:
            if int(user["id"]) == int(user_id or -1):
                name = {"firstName": "", "lastName": ""}

                if "firstName" in user:
                    name["firstName"] = user["firstName"]

                if "lastName" in user:
                    name["lastName"] = user["lastName"]

                return name

        return None

    def get_formatted_name_by_user_id(self, user_id):
        """
        Returns the name like "David Moss"
        :param user_id:
        :return:
        """
        name = self.get_name_by_user_id(user_id)
        if name is not None:
            return "{} {}".format(name["firstName"], name["lastName"]).strip()

        return None

    def get_organization_locations(self, organization_id):
        """
        Get a list of locations within an organization, as a bot with admin priviledges
        :param organization_id:
        :return:
        """
        params = {"organizationId": organization_id}

        r = self._http_get("/admin/json/locations", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        return j["locations"]

    # ===========================================================================
    # Variables
    # ===========================================================================
    def save_variable(
        self, name, value, required_for_each_execution=False, shared=False, overwrite=False
    ):
        """
        This method will cache a single variable to be saved to the cloud upon flush_variables()
        BotEngine will always flush variables to the cloud at the end of executing the bot.

        We use 'dill' to serialize data. Dill is a form of 'pickle', but can also store things like nested objects
        According to https://docs.python.org/3/library/pickle.html, the following can be pickled:
            * None, True, and False
            * integers, floating point numbers, complex numbers
            * strings, bytes, bytearrays
            * tuples, lists, sets, and dictionaries containing only picklable objects
            * functions defined at the top level of a module (using def, not lambda)
            * built-in functions defined at the top level of a module
            * classes that are defined at the top level of a module
            * instances of such classes whose __dict__ or the result of calling __getstate__() is
              picklable (see section Pickling Class Instances for details).

        There are some machine learning models that have a difficult time inside dill and resule in PyCapsule errors.
        We've had better luck pickling those objects before saving them, and then unpickling them on the way out.
        Do this at the application layer.

        :param name: Custom name of the variable to persist to the cloud
        :param value: Value of the variable to persist to the cloud
        :param required_for_each_execution: Set to True if this variable is required for every execution to increase performance. Setting to True without using this variable on every execution may decrease performance.
        :param shared: True if this variable is shared with other bots within the location. Convenience method that forwards to save_shared_variable().
        :param overwrite: If True, will overwrite an existing variable with new data
        """
        if name == CORE_VARIABLE_NAME and self.edge:
            # This bot is currently executing on the edge, do not attempt to save variables.
            return

        if shared:
            self.save_shared_variable(name, value)
            return

        # Correct a developer mistake, who previously put this variable in the Core Variables and then tried to save outside of the core variables
        if not self.edge:
            if CORE_VARIABLE_NAME in self.variables:
                if name in self.variables[CORE_VARIABLE_NAME]:
                    required_for_each_execution = True

        self.save_variables({name: value}, required_for_each_execution=required_for_each_execution, shared=shared, overwrite=overwrite)

    def save_variables(
        self, variables_dictionary, required_for_each_execution=False, shared=False, overwrite=False
    ):
        """
        This method will cache multiple variables from a dictionary to be saved to the cloud upon flush_variables()
        BotEngine will always flush variables to the cloud at the end of executing the bot.

        :param variables_dictionary: Dictionary of {name:value} variables to persist to the cloud
        :param required_for_each_execution: Set to True if this variable is required for every execution to increase performance. Setting to True without using this variable on every execution may decrease performance.
        :param shared: True if this variable is shared with other bots within the location. Convenience method that forwards to save_shared_variable().
        :param overwrite: If True, will overwrite an existing variable with new data
        """
        if shared:
            for name in variables_dictionary:
                self.save_shared_variable(name, variables_dictionary[name])
            return 
        if required_for_each_execution:
            if overwrite:
                for name in variables_dictionary:
                    self.variables[CORE_VARIABLE_NAME][name] = variables_dictionary[name]
            else:
                self.variables[CORE_VARIABLE_NAME].update(variables_dictionary)
            self.variables_to_flush[CORE_VARIABLE_NAME] = self.variables[
                CORE_VARIABLE_NAME
            ]

        else:
            if overwrite:
                for name in variables_dictionary:
                    self.variables[name] = variables_dictionary[name]
                    self.variables_to_flush[name] = variables_dictionary[name]
            else:
                self.variables.update(variables_dictionary)
                self.variables_to_flush.update(variables_dictionary)

    def load_variable(self, name, shared=False):
        """
        Extract a single variable
        :param name: Name of the variable to load
        :param shared: True if this variable is shared with other bots within the location. Convenience method that forwards to load_shared_variable().
        :return: the value of the given variable name
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">load_variable() name={} shared={}".format(name, shared)
        )
        if shared:
            return self.load_shared_variable(name)

        if CORE_VARIABLE_NAME in self.variables:
            if name in self.variables[CORE_VARIABLE_NAME]:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|load_variable() core value={}".format(
                        self.variables[CORE_VARIABLE_NAME][name]
                    )
                )
                return self.variables[CORE_VARIABLE_NAME][name]

        if name in self.variables:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|load_variable() value={}".format(self.variables.get(name))
            )
            return self.variables.get(name)

        self._download_binary_variable(name)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|load_variable() value={}".format(self.variables.get(name))
        )
        return self.variables.get(name)

    def load_variables(self, names):
        """
        Download and return a list of variables
        :param names: List of variable names to download and return
        :return: Dictionary of variable names and values
        """
        # TODO bring back the chunking mechanism to safely load large (>8MB) variables

        for name in names:
            if self.variables.get(name) is None:
                self._download_binary_variable(name)

        return_values = {}
        for name in names:
            return_values[name] = self.variables.get(name)

        return return_values

    def delete_variable(self, name, shared=False):
        """
        Delete a variable from the cloud
        :param name: Name of the variable to delete at the cloud
        :param shared: True if this variable is shared with other bots within the location. Convenience method that forwards to delete_shared_variable().
        """
        if shared:
            return self.delete_shared_variable(name)

        self._http_delete("/analytic/variables/" + urllib.parse.quote((str(name))))

        try:
            del self.variables[name]
        except KeyError:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"|delete_variable() variable not found: {name}")
            pass

        try:
            del self.variables_to_flush[name]
        except KeyError:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"|delete_variable() variable not found: {name}")
            pass

    def flush_binary_variables(self):
        """
        This method will pickle and save multiple variables from the local variables cache to the cloud.
        It is always automatically called by the BotEngine at the end of bot execution.
        You do not need to call this manually.

        :param variables_dictionary: Dictionary of {name:value} variables to persist to the cloud

        According to https://docs.python.org/3/library/pickle.html, the following can be pickled:
            * None, True, and False
            * integers, floating point numbers, complex numbers
            * strings, bytes, bytearrays
            * tuples, lists, sets, and dictionaries containing only picklable objects
            * functions defined at the top level of a module (using def, not lambda)
            * built-in functions defined at the top level of a module
            * classes that are defined at the top level of a module
            * instances of such classes whose __dict__ or the result of calling __getstate__() is
              picklable (see section Pickling Class Instances for details).
        """
        from .color import Color
        from .bot_error import BotError

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(">flush_binary_variables()")
        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # We don't want to download variables for organization RAG bots
            self.variables_to_flush.clear()
            return

        import dill

        if len(self.variables_to_flush) == 0:
            return

        # New method
        pickles = bytearray()
        params = ""

        # total_length is purely for information/debugging when running locally and has no impact on execution
        total_length = 0

        for name in self.variables_to_flush:
            try:
                # Used for debugging variables stored to the server
                if self.inputs["trigger"] == 2048 and name == CORE_VARIABLE_NAME:
                    raise Exception(
                        "Attempted to store core variable during a data request trigger"
                    )
            except Exception as e:
                import traceback
                self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                    "|flush_binary_variables() Failed to saved core variable during data request trigger: {}; trace: {}".format(
                        str(e), traceback.format_exc()
                    )
                )
                continue


            if SAVE_VARIABLES_TO_DEBUG_FILE:
                # Build sub-directory path
                location_id = str(self.get_location_id())
                bundle_name = self.get_bundle_id()
                bot_instance_id = str(self.get_bot_instance_id())
                dir_path = os.path.join("bot_variables", location_id, bundle_name, bot_instance_id)
                os.makedirs(dir_path, exist_ok=True)
                file_path = os.path.join(dir_path, f"{name}.variable")
                v = dill.dumps(self.variables_to_flush[name])
                with open(file_path, "wb") as f:
                    f.write(v)
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|flush_binary_variables()"
                    + Color.BOLD
                    + f"{file_path}: Saved {len(v)} bytes"
                    + Color.END
                )

            try:
                v = dill.dumps(self.variables_to_flush[name])
            except TypeError as e:
                # https://github.com/uqfoundation/dill/issues/58
                # https://stackoverflow.com/questions/30499341/establishing-why-an-object-cant-be-pickled/30529992#30529992
                # https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-in-python-into-some-sort-of-string-buffer
                # Let's redirect stdout and get the trace from dill
                import traceback
                from io import StringIO

                sys.stdout = my_stdout = StringIO()
                dill.detect.trace(True)
                dill.detect.errors(self.variables_to_flush[name])
                sys.stdout = sys.__stdout__
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|flush_binary_variables() Cannot flush variable {}. \n\ninputs={};\n\ndill.detect.trace stdout={};\n\ndill.detect.baditems()={};\n\ndill.detect.badobjects()={};\n\ndill.detect.badtypes()={};\n\nexception={};\n\ntraceback={}".format(
                        name,
                        self.inputs,
                        my_stdout.getvalue(),
                        dill.detect.baditems(self.variables_to_flush[name]),
                        dill.detect.badobjects(self.variables_to_flush[name]),
                        dill.detect.badtypes(self.variables_to_flush[name]),
                        e,
                        traceback.format_exc(),
                    )
                )
                v = dill.dumps(None)

            pickles += v
            params += "name={}&length={}&".format(name, len(v))

            # These next 2 lines are purely for information/debugging
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_binary_variables() {}: {} bytes".format(name, len(v))
            )
            total_length += len(v)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|flush_binary_variables() Saving {} bytes total...".format(total_length)
        )

        if total_length > 0:
            while True:
                r = None
                try:
                    # self.get_logger(f"{'botengine'}.{__class__.__name__}").info(Color.BOLD + "Flushing: /analytic/variables?{}".format(params) + Color.END)
                    headers = {"Content-Type": "application/octet-stream"}

                    import hashlib

                    md5 = hashlib.md5()
                    md5.update(pickles)
                    headers["Content-MD5"] = md5.digest().hex()

                    r = self._http_post(
                        "/analytic/variables?{}".format(params),
                        data=pickles,
                        headers=headers,
                        timeout=15,
                    )
                    j = json.loads(r.text)
                    _check_for_errors(j)
                    break

                except BotError as e:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|flush_binary_variables() Error [{}]: {}".format(e.code, str(e))
                    )
                    if e.code == 2:
                        # Local run took to long, exit out
                        import sys
                        sys.exit(1)
                    # Wait some time and try again
                    time.sleep(1.0)
                    continue

                except Exception as e:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|flush_binary_variables() error: " + str(e)
                    )
                    if r is not None:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                            "|flush_binary_variables() response from server: " + r.text
                        )

        self.variables_to_flush.clear()
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<flush_binary_variables() Saved.")


    def save_shared_variable(self, name, value):
        """
        A shared variable is one that is accessible by other bots within a Location.

        Examples of shared variables would be rules_engine functions and machine learning models.
        :param name: Name of the shared variable
        :param value: Value to store
        """
        self.variables.update({name: value})
        if self.playback:
            return

        import dill

        data = dill.dumps(value)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|save_shared_variable() {}: Saving {} bytes to shared variable".format(name, len(data))
        )
        params = {"shared": True}

        r = self._http_post(
            "/analytic/variables/{}".format(name),
            params=params,
            data=data,
            headers={"Content-Type": "application/octet-stream"},
            timeout=15,
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def load_shared_variable(self, name):
        """
        Load a variable that has been shared by this bot or some other bot within this Location.
        :param name: Name of the variable to load
        :return: Variable value, or None if it doesn't exist
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">load_shared_variable() name={}".format(name)
        )
        if name in self.variables:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|load_shared_variable() value={}".format(self.variables[name])
            )
            return self.variables[name]

        if self.playback:
            return None

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return None

        import dill

        while True:
            params = {"shared": True}
            r = self._http_get(
                "/analytic/variables/" + urllib.parse.quote(str(name)), params=params
            )

            try:
                return dill.loads(r.content)

            except EOFError:
                # Don't show the error because this error will always happen on new bot instances for every variable
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|load_shared_variable() EOFError in downloading variable {}".format(
                        name
                    )
                )
                return None

            except Exception as e:
                import traceback

                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|load_shared_variable() Unable to unpickle variable: {}. {}; {}".format(
                        name, str(e), traceback.format_exc()
                    )
                )

                # Exit immediately to prevent remote cloud variables from being overwritten and reset
                if self.local:
                    import sys
                    sys.exit(1)

                return None

    def delete_shared_variable(self, name):
        """
        Delete a variable from the cloud
        :param name: Name of the variable to delete at the cloud
        """
        params = {"shared": True}
        self._http_delete(
            "/analytic/variables/" + urllib.parse.quote(str(name)), params=params
        )

    def destroy_core_memory(self):
        """
        Destructive action to forcefully make the bot forget everything and start over from scratch.
        This is primarily used when a bot is unpaused after a long time and we want to just start fresh.
        """
        del self.variables[CORE_VARIABLE_NAME]
        self._reset_core_variable()

    def _download_core_variables_async(self, event):
        event.set()
        self._reset_core_variable()
        self._download_core_variables()
        event.clear()

    def _download_core_variables(self):
        """
        Download and extract the core variables.
        This is to be called exactly once when the BotEngine class begins execution
        """
        self._download_binary_variable(CORE_VARIABLE_NAME)
        self._reset_core_variable()

    def _reset_core_variable(self):
        """
        Reset the core variable
        :return:
        """
        if CORE_VARIABLE_NAME not in self.variables:
            self.variables[CORE_VARIABLE_NAME] = {}

        if self.variables[CORE_VARIABLE_NAME] is None:
            self.variables[CORE_VARIABLE_NAME] = {}

        if not isinstance(self.variables[CORE_VARIABLE_NAME], dict):
            self.variables[CORE_VARIABLE_NAME] = {}

        if TIMERS_VARIABLE_NAME not in self.variables[CORE_VARIABLE_NAME]:
            self.variables[CORE_VARIABLE_NAME][TIMERS_VARIABLE_NAME] = None

        if QUESTIONS_VARIABLE_NAME not in self.variables[CORE_VARIABLE_NAME]:
            self.variables[CORE_VARIABLE_NAME][QUESTIONS_VARIABLE_NAME] = None

        if COUNT_VARIABLE_NAME not in self.variables[CORE_VARIABLE_NAME]:
            self.variables[CORE_VARIABLE_NAME][COUNT_VARIABLE_NAME] = 0

    def _validate_count(self):
        """
        Validate the count and log an error if our count isn't correct
        """
        if self.count is not None:
            if self._needs_resync():
                error_string = (
                    "Expected trigger ID "
                    + str(self.variables[CORE_VARIABLE_NAME][COUNT_VARIABLE_NAME] + 1)
                    + " but got trigger ID "
                    + str(self.count)
                    + ". That's "
                    + str(
                        self.count
                        - (self.variables[CORE_VARIABLE_NAME][COUNT_VARIABLE_NAME] + 1)
                    )
                    + " missed triggers."
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    error_string
                )
                if "sbox" in self._server:
                    self.notify(
                        email_content=error_string,
                        email_subject="[sbox bot debugging] Missed trigger alert",
                    )

            self._save_count()

    def _needs_resync(self):
        """
        :return: True if we need to resynchronize with the server because our trigger count is off
        """
        return (
            self.count > 0
            and self.variables[CORE_VARIABLE_NAME][COUNT_VARIABLE_NAME] > 0
            and (self.variables[CORE_VARIABLE_NAME][COUNT_VARIABLE_NAME] + 1)
            != self.count
        )

    def _save_count(self):
        """
        Save the trigger count
        Called explicitly because it adds computation
        """
        self.save_variable(
            COUNT_VARIABLE_NAME, self.count, required_for_each_execution=True
        )

    def _download_binary_variable(self, name, shared=False):
        """
        Download a single binary variable
        """
        if self.playback:
            self.variables[name] = None
            return
        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # We don't want to download variables for organization RAG bots
            return

        import dill

        while True:
            params = {"shared": shared}

            r = self._http_get(
                "/analytic/variables/" + urllib.parse.quote(str(name)), params=params
            )

            # Used to debug variables loaded from the server, used in conjunction with debug code in the flush.
            # saved_var = None
            # if os.path.isfile('{}.variable'.format(name)):
            #     with open('{}.variable'.format(name), 'rb') as f:
            #         saved_var = f.read()
            #         self.get_logger(f"{'botengine'}.{__class__.__name__}").info(Color.GREEN + "{}: Loaded {} bytes".format('{}.variable'.format(name), len(saved_var)) + Color.END)
            # self.get_logger(f"{'botengine'}.{__class__.__name__}").info(Color.GREEN + "{}: Downloaded {} bytes".format(name, len(r.content)) + Color.END)
            #
            # if saved_var is not None:
            #     self.get_logger(f"{'botengine'}.{__class__.__name__}").info(Color.GREEN + "=> {} bytes difference for variable {}".format(abs(len(saved_var) - len(r.content)), name) + Color.END)
            #     if saved_var == r.content:
            #         self.get_logger(f"{'botengine'}.{__class__.__name__}").info(Color.GREEN + "=> Saved content is the same as downloaded content" + Color.END)
            #     else:
            #         self.get_logger(f"{'botengine'}.{__class__.__name__}").error(Color.RED + "=> Saved content is DIFFERENT than downloaded content" + Color.END)

            try:
                self.variables[name] = dill.loads(r.content)
                return

            except EOFError as e:
                # Don't show the error because this error will always happen on new bot instances for every variable
                self.variables[name] = None
                if r.status_code == 200:
                    # Everything was okay, but our variable was corrupted
                    if name == CORE_VARIABLE_NAME:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                            "|_download_binary_variable() Reset: EOFError {}".format(
                                str(e)
                            )
                        )
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                            "|_download_binary_variable() HTTP status: {}".format(
                                str(r.status_code)
                            )
                        )
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                            "|_download_binary_variable() Variable text: {}".format(
                                str(r.text)
                            )
                        )
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                            "|_download_binary_variable() Variable content: {}".format(
                                str(r.content)
                            )
                        )

                    return

                elif r.status_code == 202:
                    # No variable content on the server
                    if name == CORE_VARIABLE_NAME:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                            "|_download_binary_variable() Core Variable Reset: No variable on the server."
                        )
                    return

                elif r.status_code == 204:
                    # No variable content on the server
                    if name == CORE_VARIABLE_NAME:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                            "|_download_binary_variable() Core Variable Reset: No variable on the server."
                        )
                    return

                else:
                    # Bad status code, try again.
                    time.sleep(0.5)
                    continue

            except Exception as e:
                if r.status_code == 200:
                    import traceback

                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|_download_binary_variable() Unable to unpickle variable: {}. {}; {}".format(
                            name, str(e), traceback.format_exc()
                        )
                    )

                    # Exit immediately to prevent remote cloud variables from being overwritten and reset
                    if self.local:
                        import sys
                        sys.exit(1)

                    return

                elif r.status_code == 202:
                    # No variable content on the server
                    if name == CORE_VARIABLE_NAME:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                            "|_download_binary_variable() Core Variable Reset: No variable on the server."
                        )
                    return

                elif r.status_code == 204:
                    # No variable content on the server
                    if name == CORE_VARIABLE_NAME:
                        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                            "|_download_binary_variable() Core Variable Reset: No variable on the server."
                        )
                    return

                else:
                    # Bad status code, try again
                    time.sleep(0.5)
                    continue

    # ===========================================================================
    # Notifications - push, SMS, email
    # ===========================================================================
    def notify(
        self,
        push_title=None,
        push_subtitle=None,
        push_content=None,
        push_category=None,
        push_sound=None,
        push_sms_fallback_content=None,
        push_template_filename=None,
        push_template_model=None,
        push_info=None,
        email_subject=None,
        email_content=None,
        email_html=False,
        email_attachments=None,
        email_template_filename=None,
        email_template_model=None,
        email_addresses=None,
        sms_content=None,
        sms_template_filename=None,
        sms_template_model=None,
        sms_group_chat=True,
        device_message_device_id=None,
        device_message_title=None,
        device_message_text=None,
        device_message_from=None,
        device_message_duration=None,
        device_message_icon=None,
        device_message_muted=None,
        device_message_imageUrl=None,
        device_message_image=None,
        admin_domain_name=None,
        brand=None,
        language=None,
        user_id=None,
        user_id_list=None,
        to_residents=False,
        to_supporters=False,
        to_admins=False,
        device_message=None,
    ):
        """
        This method sends a push or email notification to the people you selected.

        :param push_title: (optional) Push notification title (limited to the push notification service maximum message size)
        :param push_subtitle: (optional) Push notification subtitle (limited to the push notification service maximum message size) (iOS only)
        :param push_content: (optional) Push notification text (limited to the push notification service maximum message size)
        :param push_category: (optional) Push notification category (limited to the push notification service maximum message size) (iOS only)
        :param push_sound: (optional) Eg: "sound.wav"
        :param push_sms_fallback_content: Message content to deliver over SMS in case the push notification delivery fails
        :param push_template_filename: directoryName/PushTemplateName.vm. If this is used, the 'push_content' field is ignored.
        :param push_template_model: Dictionary of key/value pairs to inject into the push template. Dependent upon what the template itself understands.
        :param push_info: Extra key/value pairs in the push notification

        :param email_subject: (optional) Email subject line
        :param email_content: (optional) Email body
        :param email_html: (optional) True or False; default is False.
        :param email_template_filename: directoryName/EmailTemplateName.vm. If this is used, the 'email_content' and 'email_subject' fields are ignored.
        :param email_template_model: Dictionary of key/value pairs to inject into the email template. Dependent upon what the template itself understands.
        :param email_addresses: List of email addresses to deliver the message to. Your bot must support category 1 ("Specified Emails") email message delivery.

        :param sms_content: Content for an SMS message
        :param sms_template_filename: SMS template filename. If this is used, the 'sms_content' field is ignored
        :param sms_template_model: Dictionary of key/value pairs to inject into the sms template. Dependent upon what the template itself understands.
        :param sms_group_chat: True to send SMS messages as a group chat message instead of one-on-one individual messages.

        :param device_message_device_id: (optional) Device ID",
        :param device_message_title: Message title
        :param device_message_text: Message text
        :param device_message_from: (optional) From name
        :param device_message_duration: (optional) Message duration. default '60'.
        :param device_message_icon: (optional) Icon name
        :param device_message_muted: (optional) Mute the message. default 'false'.
        :param device_message_imageUrl: (optional) Image URL,
        :param device_message_image: (optional) base64 encoded image"

        :param brand: Case-sensitive brand for templates
        :param language: Language, for example 'en'
        :param user_id: (optional) Specific user ID to send to if the bot is running at the organizational level.
        :param user_id_list: (optional) Specific a list of user ID's to send to if the bot is running at the organizational level.
        :param to_residents: True to send the message to residents.
        :param to_supporters: True to send the message to supporters.
        :param to_admins: True to send the message to admins (email).
        :param admin_domain_name: Domain name / "short name" of the organization to send a notification to the admins

        :param debug: True to send a copy of the API call to developers
        """
        from botengine import BotError
        if to_admins:
            import traceback

            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|notify() called with to_admins=True, which is no longer supported. Please update your code: {}".format(
                    traceback.format_exc()
                )
            )

        notifications = {}

        user_declared = False

        if to_residents:
            if "userCategories" not in notifications:
                notifications["userCategories"] = []
            user_declared = True
            notifications["userCategories"].append(1)

        if to_supporters:
            if "userCategories" not in notifications:
                notifications["userCategories"] = []
            user_declared = True
            notifications["userCategories"].append(2)

        if user_id is not None:
            if "users" not in notifications:
                notifications["users"] = []
            user_declared = True
            notifications["users"].append(user_id)

        if user_id_list is not None:
            if "users" not in notifications:
                notifications["users"] = []
            user_declared = True
            notifications["users"] += user_id_list

        if email_addresses is not None:
            if len(email_addresses) > 0:
                user_declared = True

        if not user_declared:
            if "userCategories" not in notifications:
                notifications["userCategories"] = []
            notifications["userCategories"].append(1)

        if brand is not None:
            notifications["brand"] = brand

        if language is not None:
            notifications["language"] = language

        send = False

        # The notification type is included in a push notification to the app to let the app know how to render it.
        # It is also included in the GET Notifications API available to apps, which I don't believe are being used anymore.
        # Type 4 says, "This message came from the bot."
        notifications["type"] = 4

        if sms_content is not None or sms_template_filename is not None:
            send = True
            notifications["smsMessage"] = {}

            notifications["smsMessage"]["individual"] = not sms_group_chat

            if sms_content:
                notifications["smsMessage"]["content"] = sms_content

            if sms_template_filename:
                notifications["smsMessage"]["template"] = sms_template_filename

            if sms_template_model:
                notifications["smsMessage"]["model"] = sms_template_model

        if (
            push_content is not None
            or push_template_filename is not None
            or push_info is not None
        ):
            send = True
            notifications["pushMessage"] = {}

            if push_sms_fallback_content is not None:
                notifications["pushMessage"]["smsContent"] = push_sms_fallback_content

            if push_title is not None:
                notifications["pushMessage"]["title"] = push_title

            if push_subtitle is not None:
                notifications["pushMessage"]["subtitle"] = push_subtitle

            if push_content is not None:
                notifications["pushMessage"]["content"] = push_content

            if push_category is not None:
                notifications["pushMessage"]["category"] = push_category

            if push_sound is not None:
                notifications["pushMessage"]["sound"] = push_sound

            if push_template_filename is not None:
                notifications["pushMessage"]["template"] = push_template_filename

            if push_template_model is not None:
                notifications["pushMessage"]["model"] = push_template_model

            if push_info is not None:
                notifications["pushMessage"]["info"] = push_info

        if email_content is not None or email_template_filename is not None:
            send = True
            notifications["emailMessage"] = {}

            notifications["emailMessage"]["html"] = email_html

            if email_subject is not None:
                notifications["emailMessage"]["subject"] = email_subject

            if email_content is not None:
                notifications["emailMessage"]["content"] = email_content

            if email_template_filename is not None:
                notifications["emailMessage"]["template"] = email_template_filename

            if email_template_model is not None:
                notifications["emailMessage"]["model"] = email_template_model

            if email_attachments is not None:
                notifications["emailMessage"]["attachments"] = email_attachments

            if email_addresses is not None:
                notifications["emailMessage"]["recipients"] = email_addresses

        if device_message_text is not None:
            send = True
            notifications["deviceMessage"] = {}

            notifications["deviceMessage"]["text"] = device_message_text
            notifications["deviceMessage"]["duration"] = device_message_duration or 60

            if device_message_device_id is not None:
                notifications["deviceMessage"]["deviceId"] = device_message_device_id
            if device_message_title is not None:
                notifications["deviceMessage"]["title"] = device_message_title
            if device_message_from is not None:
                notifications["deviceMessage"]["from"] = device_message_from
            if device_message_icon is not None:
                notifications["deviceMessage"]["icon"] = device_message_icon
            if device_message_muted is not None:
                notifications["deviceMessage"]["muted"] = device_message_muted
            if device_message_imageUrl is not None:
                notifications["deviceMessage"]["imageUrl"] = device_message_imageUrl
            if device_message_image is not None:
                notifications["deviceMessage"]["image"] = device_message_image

        if send:
            j = json.dumps(notifications)

            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|notify() content: {}".format(
                    json.dumps(notifications, sort_keys=True)
                )
            )

            location_id = self.get_location_id()
            # Location Notification API
            # https://iotbots.docs.apiary.io/#reference/bot-server-apis/send-notification-to-location-users/send-a-notification
            r = self._http_post(
                "/analytic/location/{}/notifications".format(location_id), data=j
            )
            j = json.loads(r.text)

            # =======================================================================
            # print("Params: " + str(params))
            # print("Data: " + str(j))
            # self.get_logger(f"{'botengine'}.{__class__.__name__}").info("RESPONSE: " + str(r.text))
            # =======================================================================

            # This was barfing on us when sending a push notification to the end user in a bot that requests access to an organization when the user is not part of any organization
            try:
                _check_for_errors(j)
            except BotError:
                # _bot_loggers["botengine"].error("BotEngine SMS notify(): " + e.msg)
                # _bot_loggers["botengine"].error("Notification data: " + str(notifications))
                return

    def send_mms(
        self,
        user_id,
        media_content=None,
        url=None,
        media_type=1,
        ext=None,
        caption=None,
    ):
        """
        Send an image or audio file to the user's phone.
        :param user_id: User ID
        :param media_content: File content
        :param url: Image url
        :param media_type: Media type (1 - image, 2 - audio)
        :param ext: Ext
        :param caption: Additional text to accompany the media file.
        :return:
        """
        headers = {}

        params = {"userId": user_id, "mediaType": media_type}

        if caption is not None:
            params["caption"] = caption

        if ext is not None:
            params["ext"] = ext
        if url is not None:
            content = "application/octet-stream"
            headers = {"Content-Type": content}
            params["url"] = url
            r = self._http_post("/analytic/mms", params=params, headers=headers)
            j = json.loads(r.text)
            _check_for_errors(j)
        else:
            content = ""
            if media_type == 1:
                content = "image/" + ext
            else:
                content = "application/octet-stream"

            headers = {"Content-Type": content}

            r = self._http_post(
                "/analytic/mms", params=params, data=media_content, headers=headers
            )
            j = json.loads(r.text)
            _check_for_errors(j)

    def make_voice_call(self, user_id, voice_model, call_time=None):
        """
        Define the voice call model for specific user.
        :param user_id: User ID
        :param voice_model: Voice call model
        :param call_time: Call start time, in milliseconds since the epoch
        :return:
        """
        body = {"model": voice_model}
        params = {"userId": user_id}

        if call_time is not None:
            params["callTime"] = call_time

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|make_voice_call() params={} body={}".format(
                json.dumps(params), json.dumps(body)
            )
        )
        if self.playback:
            return

        r = self._http_post("/analytic/voiceCall", params=params, data=json.dumps(body))
        j = json.loads(r.text)
        _check_for_errors(j)

    def set_incoming_voicecall(self, user_id, voice_model):
        """
        Define the incoming voice call model for specific users at the bot's location.
        :param user_id:
        :param voice_model: Voice call model
        :return:
        """
        body = {"model": voice_model}
        params = {"userId": user_id}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|set_incoming_voicecall() params={} body={}".format(
                json.dumps(params), json.dumps(body)
            )
        )
        r = self._http_post(
            "/analytic/voiceCallAnswer", params=params, data=json.dumps(body)
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def delete_incoming_voicecall(self, user_id):
        """
        Delete the incoming voice call model for specific users at the bot's location.
        :param user_id:
        :return:
        """
        params = {"userId": user_id}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|delete_incoming_voicecall() params={}".format(
                json.dumps(params)
            )
        )
        r = self._http_delete("/analytic/voiceCallAnswer", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)

    def make_voip_call(self, device_id, location_id=None, sip_address=None, phone=None, address_name=None,
                    audio_device_id=None, speaker_volume=None, mic_volume=None):
        """
        Make a VoIP Call to a device registered on a SIP server.

        If the device is registered on a SIP server, it can make a VoIP call.

        :param device_id: Device ID (string, required)
        :param location_id: Device location ID (integer, required)
        :param sip_address: SIP address to make a call (string, optional)
        :param phone: Phone number to make a call, if SIP address is not provided (string, optional)
        :param address_name: Address name to make a call (string, optional)
        :param audio_device_id: Audio Device ID, if not set, the first available one will be used (string, optional)
        :param speaker_volume: Audio Device speaker volume (integer, optional)
        :param mic_volume: Audio Device microphone volume (integer, optional)
        :return: JSON response from Care Daily API
        """
        params = {
            "locationId": location_id or self.get_location_id(device_id=device_id),
            "sipAddress": sip_address,
            "phone": phone,
            "addressName": address_name,
            "audioDeviceId": audio_device_id,
            "speakerVolume": speaker_volume,
            "micVolume": mic_volume,
        }

        params = {k: v for k, v in params.items() if v is not None}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            f"|make_voip_call() device_id={device_id} location_id={location_id} params={params}"
        )

        r = self._http_put(
            f"/cloud/json/devices/{device_id}/voipCall",
            params=params,
        )
        j = json.loads(r.text)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"|make_voip_call() response={j}")
        _check_for_errors(j)
        pass

    def hang_up_voip_call(self, device_id, location_id=None):
        """
        Hang up a VoIP Call to a device registered on a SIP server.
        :param device_id: Device ID (string, required)
        :param location_id: location ID (integer, required)
        :return:
        """
        params = {"locationId": location_id or self.get_location_id(device_id=device_id)}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            f"|hang_up_voip_call() device_id={device_id} location_id={location_id} params={params}"
        )

        r = self._http_delete(
            f"/cloud/json/devices/{device_id}/voipCall",
            params=params
        )
        j = json.loads(r.text)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            f"|hang_up_voip_call() response={j}"
        )
        _check_for_errors(j)

    def email_admins(
        self,
        email_subject=None,
        email_content=None,
        email_html=False,
        email_attachments=None,
        email_template_filename=None,
        email_template_model=None,
        email_addresses=None,
        brand=None,
        categories=[1, 2],
    ):
        """
        Send an email to administrators
        :param botengine:
        :param email_subject:
        :param email_content:
        :param email_html:
        :param email_attachments:
        :param email_template_filename:
        :param email_template_model:
        :param email_addresses: List of email addresses
        :param categories: List of Organization User Categories; 1 = Manager, 2 = Technician, 3 = Billing
        :return:
        """
        from botengine import BotError
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">email_admins() email_subject={} email_content={} email_html={} email_attachments={} email_template_filename={} email_template_model={} email_addresses={} brand={} categories={}".format(
                email_subject,
                email_content,
                email_html,
                email_attachments,
                email_template_filename,
                email_template_model,
                email_addresses,
                brand,
                categories,
            )
        )
        body = {}
        params = {}

        if brand is not None:
            body["brand"] = brand

        if email_content is not None or email_template_filename is not None:
            body["emailMessage"] = {}

            body["emailMessage"]["html"] = email_html

            if email_subject is not None:
                body["emailMessage"]["subject"] = email_subject

            if email_content is not None:
                body["emailMessage"]["content"] = email_content

            if email_template_filename is not None:
                body["emailMessage"]["template"] = email_template_filename

            if email_template_model is not None:
                body["emailMessage"]["model"] = email_template_model

            if email_attachments is not None:
                body["emailMessage"]["attachments"] = email_attachments

            if email_addresses is not None:
                # Email to selected recipients
                body["emailMessage"]["recipients"] = email_addresses

                # Notify emails directly
                params = {"category": 1}

            else:
                body["userCategories"] = categories

                # Notify Organization Users
                params = {"category": 2}

        else:
            return

        if self.playback:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "<email_admins() params={} body={}".format(
                    json.dumps(params), json.dumps(body)
                )
            )
            return

        r = self._http_post(
            "/analytic/notifications", params=params, data=json.dumps(body)
        )
        j = json.loads(r.text)
        try:
            _check_for_errors(j)
        except BotError as e:
            if e.code == 41:
                if params.get("category") == 2:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                        "|email_admins() This organization has no users to notify for user categories {}.".format(
                            categories
                        )
                    )
                else:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                        "|email_admins() No recipients found with the given email addresses {}.".format(
                            email_addresses
                        )
                    )
            else:
                import traceback

                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|email_admins() Could not send emails: error={} trace={}".format(
                        e, traceback.format_exc()
                    )
                )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("<email_admins()")

    def add_email_attachment_from_camera(
        self, destination_attachment_array, device_file_id, content_id
    ):
        """
        Add an email attachment from a camera with the content being pulled and delivered from the server inside the user's email
        :param destination_attachment_array: Destination array of attachments. Pass in [] if you are starting a new list of attachments.
        :param device_file_id: Device File ID
        :param content_id: Content ID String.  The thumbnail would then cite "cid:<content_id>" to reference this attachment.
        """
        attachment = {"deviceFileId": device_file_id, "contentId": content_id}
        destination_attachment_array.append(attachment)
        return destination_attachment_array

    def add_email_attachment(
        self, destination_attachment_array, filename, content, content_type, content_id
    ):
        """
        This helper method will create an email attachment block and add it to a destination array of existing email attachments

        :param destination_attachment_array: Destination array of attachments. Pass in [] if you are starting a new list of attachments.
        :param filename: Filename of the file, for example, "imageName.jpg"
        :param content: Content to attached, for example base64-encoded binary image content
        :param content_type: Content type of the file, for example "image/jpeg"
        :param content_id: Unique ID for the content, for example "inlineImageId". The email can reference this content with <img src="cid:inlineImageId">.

        :return the destination_attachment_array with the new attachment, ready to pass into the email_attachments argument in the notify() method
        """
        attachment = {
            "name": filename,
            "content": content,
            "contentType": content_type,
            "contentId": content_id,
        }
        destination_attachment_array.append(attachment)
        return destination_attachment_array

    # ===========================================================================
    # Measurements
    # ===========================================================================
    def get_measurements(
        self,
        device_id,
        user_id=None,
        oldest_timestamp_ms=None,
        newest_timestamp_ms=None,
        param_name=None,
        index=None,
        last_rows=None,
    ):
        """
        This method will return measurements from the given device

        * param_name[*] --> getting current measurement
        * start_date, end_date[?], param_name[*], index[?] --> getting historical measurements
        * start_date, end_date[?], param_name[*], index[?], last_count --> getting last n measurements

        :param device_id: Device ID to extract parameters from
        :param user_id: User ID to access devices of specific user by an organization bot
        :param oldest_timestamp_ms: Start time in milliseconds to begin receiving measurements. If not set, only latest measurements will be returned. e.g. 1483246800000
        :param newest_timestamp_ms: End time in milliseconds to stop receiving measurements, default is the current time. e.g. 1483246800000
        :param param_name: Only obtain measurements for given parameter names. Multiple values can be passed, example: "batteryLevel" or ["batteryLevel", "doorStatus"]
        :param index: Only obtain measurements for parameters with this index number.
        :param last_rows: Receive only last N measurements
        """
        if newest_timestamp_ms is None:
            newest_timestamp_ms = self.get_timestamp()

        original_oldest_timestamp_ms = oldest_timestamp_ms

        params = {}

        if user_id:
            params["userId"] = int(user_id)

        if param_name:
            params["paramName"] = param_name

        if index:
            params["index"] = index

        if last_rows:
            params["lastRows"] = last_rows

        if newest_timestamp_ms:
            params["endDate"] = int(newest_timestamp_ms)

        if oldest_timestamp_ms is None:
            r = self._http_get(
                "/analytic/devices/" + device_id + "/parameters",
                params=params,
                timeout=120,
            )
            j = json.loads(r.text)
            _check_for_errors(j)
            return j

        else:
            # Extract the data from the server in calendar month API chunks
            # The parameters history table has monthly partitions.
            # This operation works the fastest when you select data by exactly the first microsecond of the month to the first microsecond of the next month in UTC.
            import dateutil.relativedelta

            # print("get_measurements(): original_oldest_timestamp_ms={}; newest_timestamp_ms={}".format(original_oldest_timestamp_ms, newest_timestamp_ms))
            oldest_dt = datetime.datetime.utcfromtimestamp(
                newest_timestamp_ms / 1000
            ).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

            return_json = {"measures": []}
            while newest_timestamp_ms > original_oldest_timestamp_ms:
                oldest_timestamp_ms = (
                    (oldest_dt - datetime.datetime(1970, 1, 1)).total_seconds()
                ) * 1000
                if oldest_timestamp_ms < original_oldest_timestamp_ms:
                    oldest_timestamp_ms = original_oldest_timestamp_ms

                params["startDate"] = int(oldest_timestamp_ms)
                params["endDate"] = int(newest_timestamp_ms)

                # print("get_measurements(): start={} end={}".format(int(oldest_timestamp_ms), int(newest_timestamp_ms)))
                r = self._http_get(
                    "/analytic/devices/" + device_id + "/parameters",
                    params=params,
                    timeout=240,
                )
                j = json.loads(r.text)
                _check_for_errors(j)

                if "measures" not in j:
                    # Ran out of measurements
                    break

                elif len(j["measures"]) == 0:
                    # Ran out of measurements
                    break

                # Insert the most recently downloaded set of measurements into the front of our total array
                return_json["measures"][0:0] = j["measures"]

                # Inch our way backwards to the previous calendar month
                newest_timestamp_ms = oldest_timestamp_ms
                oldest_dt = oldest_dt + dateutil.relativedelta.relativedelta(months=-1)

            return return_json

    def request_data(
        self,
        type=1,
        device_id=None,
        oldest_timestamp_ms=None,
        newest_timestamp_ms=None,
        param_name_list=None,
        reference=None,
        index=None,
        ordered=1,
    ):
        """
        Selecting a large amount of data from the database can take a significant amount of time and impact server
        performance. To avoid this long waiting period while executing bots, a bot can submit a request for all the
        data it wants from this location asynchronously. The server gathers all the data on its own time, and then
        triggers the bot with trigger 2048. Your bot must include trigger 2048 to receive the trigger.

        Selected data becomes available as a file in CSV format, compressed by LZ4, and stored for one day.
        The bot receives direct access to this file.

        You can call this multiple times to extract data out of multiple devices. The request will be queued up and
        the complete set of requests will be flushed at the end of this bot execution.

        :param type: DATA_REQUEST_TYPE_*, default (1) is key/value device parameters
        :param device_id: Device ID to download historical data from
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds
        :param newest_timestamp_ms: Newest timestamp in milliseconds
        :param param_name_list: List of parameter names to download
        :param reference: Reference so when this returns we know who it's for
        :param index: Index to download when parameters are available with multiple indices
        :param ordered: 1=Ascending (default); -1=Descending.
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|request_data() Requesting data from {} to {} for device {} with param_name_list={}".format(
                oldest_timestamp_ms, newest_timestamp_ms, device_id, param_name_list
            )
        )
        request = {"type": type}

        if device_id is not None:
            request["deviceId"] = device_id

        if oldest_timestamp_ms is not None:
            request["startTime"] = oldest_timestamp_ms
        else:
            # Go back a maximum 1 millisecond less than a year ago.
            request["startTime"] = self.get_timestamp() - 31535999999

        if newest_timestamp_ms is not None:
            request["endTime"] = newest_timestamp_ms

        else:
            request["endTime"] = self.get_timestamp()

        if param_name_list is not None:
            request["paramNames"] = param_name_list

        if reference is not None:
            request["key"] = reference

        if index is not None:
            request["index"] = index

        if ordered is not None:
            request["ordered"] = ordered

        self.data_requests.append(request)

    def flush_asynchronous_requests(self):
        """
        Flush the complete set of asynchronous measurement requests to the server
        """
        from botengine import BotError
        if len(self.data_requests) == 0:
            return

        if self.playback:
            # Data requests are inserted into playback queue as single trigger after to the current execution
            return

        j = json.dumps({"dataRequests": self.data_requests})

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|flush_asynchronous_requests() requests: {}".format(
                json.dumps({"dataRequests": self.data_requests}, sort_keys=True)
            )
        )

        r = self._http_post("/analytic/dataRequests", data=j)
        j = json.loads(r.text)
        try:
            _check_for_errors(j)

        except BotError as e:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").warn(
                "|flush_asynchronous_requests() Error: {} We sent this body: {}".format(
                    e, json.dumps({"dataRequests": self.data_requests}, sort_keys=True)
                )
            )

        self.data_requests = []

    def send_data_request(self, url, timeout, stream=False):
        """
        Flush the complete set of asynchronous measurement requests to the server
        """

        while True:
            try:
                r = self.session.get(url, timeout=timeout, stream=stream)
                return r

            except self._requests.HTTPError as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|send_data_request() Generic HTTP error calling GET " + url
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|send_data_request() Error:  {}".format(e)
                )

            except self._requests.ConnectionError as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|send_data_request() Connection HTTP error calling GET " + url
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|send_data_request() Error:  {}".format(e)
                )

            except self._requests.Timeout as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|send_data_request() " + str(timeout) + " second HTTP Timeout calling POST " + url
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|send_data_request() Error:  {}".format(e)
                )
                timeout += 10
                if timeout >= 30:
                    raise self._requests.Timeout()

            except self._requests.TooManyRedirects as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|send_data_request() Too many redirects HTTP error calling GET " + url
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|send_data_request() Error:  {}".format(e)
                )

            except Exception as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|send_data_request() Generic HTTP exception calling GET " + url
                )
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|send_data_request() Error:  {}".format(e)
                )

    # ===========================================================================
    # Device Properties
    # ===========================================================================
    def set_device_property(self, device_id, name, value, index=None):
        """
        Set a single device property from your location
        https://iotapps.docs.apiary.io/#reference/devices/device-activation-info/set-device-properties

        :param device_id: Device ID
        :param properties: Device properties {"property": [{"name":"size", "value":"10"}, {xxx}]}
        """
        params = {"locationId": self.get_location_id(device_id=device_id)}

        device_property = {"name": name, "value": value}

        if index is not None:
            device_property["index"] = index

        body = {"property": [device_property]}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|set_device_property() Saving device property to {}: \n{}".format(
                device_id, json.dumps(body, sort_keys=True)
            )
        )

        r = self._http_post(
            "/cloud/json/devices/{}/properties".format(device_id),
            params=params,
            data=json.dumps(body),
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def get_device_property(self, device_id, name=None, index=None):
        """
        Get device properties from your location
        https://iotapps.docs.apiary.io/#reference/devices/device-properties/get-device-properties

        :param device_id: Device ID
        :param name: Optional name to search for
        :param index: Optional index to search for
        """
        params = {"locationId": self.get_location_id(device_id=device_id)}

        if name is not None:
            params["name"] = name

        if index is not None:
            params["index"] = index
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|get_device_property() device_id={} params={}".format(device_id, params)
        )
        r = self._http_get(
            "/cloud/json/devices/{}/properties".format(device_id), params=params
        )
        j = json.loads(r.text)
        _check_for_errors(j)

        if "properties" in j:
            return j["properties"]
        return []

    def delete_device_property(self, device_id, name, index=None):
        """
        Delete device properties from your location
        https://iotapps.docs.apiary.io/#reference/devices/device-properties/get-device-properties

        :param device_id: Device ID
        :param property_name: Property name
        """
        # TODO: Delete property on sub type location?
        params = {"locationId": self.get_location_id(device_id=device_id), "name": name}

        if index is not None:
            params["index"] = index

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|delete_device_property() device_id={} params={}".format(device_id, params)
        )
        r = self._http_delete(
            "/cloud/json/devices/{}/properties".format(device_id), params=params
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    def get_system_property(self, name):
        """
        Get a system property for this bot
        https://app.peoplepowerco.com/cloud/apidocs/cloud.html#tag/System-and-User-Properties

        :param name: Property name
        :return: Property value (dict or str) or None
        """
        r = self._http_get(
            "/cloud/json/systemProperty/{}".format(name)
        )
        if len(r.text) == 0:
            return None
        if r.text[0] in ["{", "["]:
            try:
                return json.loads(r.text)
            except Exception as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|get_system_property() Error extracting JSON {}".format(e)
                )
                return None
        return r.text

    # ===========================================================================
    # Commands
    # ===========================================================================
    def send_command(
        self,
        device_id,
        param_name,
        value,
        index=None,
        command_timeout_ms=None,
        comment=None,
    ):
        """
        This method sends a command to the device ID

        :param device_id: The exact device ID to send a command to. This is case-sensitive.
        :param param_name: The name of the parameter to configure.
        :param value: The value to set for this parameter.
        :param index: Optional index number / letters. Default is None.
        :param comment: Reason why this command was sent
        """
        self.send_commands(
            device_id,
            self.form_command(param_name=param_name, index=index, value=value),
            command_timeout_ms=command_timeout_ms,
            comment=comment,
        )

    def form_command(self, param_name, value, index=None):
        """
        This method will form a single command.

        You can pass in parameter name / optional index / value pairs and it will
        generate a dictionary to represent this command. This is a shortcut to send
        multiple commands with the send_commands(device_id, commands) method.

        Append multiple commands into a list and then use send_commands(..) to send them all.

        :param param_name: The name of the parameter to configure.
        :param value: The value to set for this parameter.
        :param index: Optional index number / letters. Default is None.
        """
        response = {"name": param_name, "value": value}

        if index:
            response["index"] = index

        return response

    def send_commands(self, device_id, commands, command_timeout_ms=None, comment=None):
        """
        This method sends one or multiple commands simultaneously to the given device ID
        'index' is optional - if your parameter does not use an index number, do not reference or populate it.

        :param device_id: The exact device ID to send a command to. This is case-sensitive.
        :param commands: Array of dictionaries of the form [{"name":"parameterName", "index":0, "value":"parameterValue"}, ...]
        :param command_timeout_ms: Relative timeout, in ms, to expire the command
        :param comment: Reason why this command was sent
        """
        commands_for_device = {"deviceId": device_id}

        exists = False

        for d in self.commands_to_flush:
            if d["deviceId"] == device_id:
                commands_for_device = d
                exists = True
                break

        if "params" not in commands_for_device:
            commands_for_device["params"] = []

        if command_timeout_ms is not None:
            commands_for_device["commandTimeout"] = command_timeout_ms

        if comment is not None:
            commands_for_device["comment"] = comment

        if not isinstance(commands, list):
            commands = [commands]

        import copy

        for command in commands:
            for param in copy.copy(commands_for_device["params"]):
                if param["name"] == command["name"]:
                    if "index" in param and "index" in command:
                        if param["index"] == command["index"]:
                            # match
                            commands_for_device["params"].remove(param)
                            break

                    else:
                        # match
                        commands_for_device["params"].remove(param)
                        break

            commands_for_device["params"].append(command)

        if not exists:
            self.commands_to_flush.append(commands_for_device)

    def cancel_command(self, device_id, param_name=None):
        """
        Cancel a command to the device with the given parameter names.
        If no parameter name is given, this will cancel all commands to the device.
        :param device_id: Device ID to cancel commands for
        :param param_name: Parameter name to cancel commands for. Leave this None (default) to cancel all commands to the device.
        """
        import copy

        for d in copy.copy(self.commands_to_flush):
            if d["deviceId"] == device_id:
                if param_name is None:
                    # Delete all commands to this device
                    self.commands_to_flush.remove(d)
                    return

                else:
                    if "params" in d:
                        for param in copy.copy(d["params"]):
                            if param["name"] == param_name:
                                d["params"].remove(param)

                        if len(d["params"]) == 0:
                            self.commands_to_flush.remove(d)

    def flush_commands(self):
        """
        https://iotbots.docs.apiary.io/#reference/bot-server-apis/multiple-device-commands/send-set-commands
        Flush all the commands to the server and execute them.
        This is called automatically when the bot exits, you should never have to call this manually.
        """
        if len(self.commands_to_flush) > 0:
            body = {"devices": []}

            for d in self.commands_to_flush:
                body["devices"].append(d)

            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_commands() Sending commands: " + json.dumps(body, sort_keys=True)
            )

            
            r = self._http_put("/analytic/parameters", data=json.dumps(body))
            j = json.loads(r.text)
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_commands() Command responses: " + json.dumps(j, sort_keys=True)
            )
            self.commands_to_flush = []

    # ===========================================================================
    # Modes
    # ===========================================================================
    def set_mode(self, location_id, mode, comment=None):
        """
        Set the mode
        :param location_id: Location ID of which to set the mode
        :param mode: Mode string to set, for example "AWAY" or "AWAY.SILENT"
        :param comment: Optional comment to describe why this mode changed.
        """
        data = None
        if comment is not None:
            data = json.dumps({"comment": comment})

        self._http_post(
            "/cloud/json/location/" + str(location_id) + "/event/" + str(mode),
            data=data,
        )

    def get_mode_history(
        self, location_id, oldest_timestamp_ms=None, newest_timestamp_ms=None
    ):
        """
        This method will return location mode history in backward order (lastest first)
        Including the source of the mode change
        :param location_id: Location ID
        :param oldest_timestamp_ms: Oldest timestamp to start pulling history
        :param newest_timestamp_ms: Newest timestamp to stop pulling history
        """
        params = {}

        if oldest_timestamp_ms is not None:
            params["startDate"] = int(oldest_timestamp_ms)

        if newest_timestamp_ms is not None:
            params["endDate"] = int(newest_timestamp_ms)

        r = self._http_get(
            "/analytic/location/" + str(location_id) + "/events", params=params
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_mode(self, location_id):
        """
        Get the current mode
        :param location_id: Location ID to retrieve the mode for
        :return: The current mode, or "HOME.DEFAULT" by default if the location can't be found
        """
        location = self.get_location_info()
        if location is not None:
            if "location" in location:
                if "event" in location["location"]:
                    return location["location"]["event"]

        return "HOME.DEFAULT"

    # ===========================================================================
    # Files
    # ===========================================================================
    def download_file(self, file_id, local_filename, thumbnail=False):
        """
        Download a file
        :param file_id: File ID to download
        :param local_filename: Local filename to store the file into
        :param thumbnail: True to download the thumbnail for this file
        :return: local_filename
        """
        params = {"thumbnail": thumbnail}

        r = self._http_get(
            "/cloud/json/files/{}".format(file_id), params=params, stream=True
        )
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024):
                # filter out keep-alive new chunks
                if chunk:
                    f.write(chunk)

        return local_filename

    # ===========================================================================
    # Subscription Services
    # ===========================================================================
    def has_subscription(self, name):
        """
        Search for the given name inside our list of available.

        For example if we search for the name "Avantguard" and the location has a subscription "Avantguard.PPC"
        then this will return True.

        :return: True if this location has the given name String found inside any available subscription
        """
        # =====================================================================
        # Example of self.services content:
        # self.services = [
        #   {
        #     "amount": 1,
        #     "endDateMs": 1495174080000,
        #     "serviceName": "ProEnergy",
        #     "startDateMs": 1494569299000
        #   }
        # ]
        # =====================================================================

        if name is not None and self.services is not None:
            for service in self.services:
                if name in service["serviceName"]:
                    return True

        return False

    # ===========================================================================
    # Professional Monitoring Services
    # ===========================================================================
    def has_professional_monitoring(self):
        """
        :return: True if this user has professional monitoring services
        """
        try:
            professional_monitoring = self.professional_monitoring_status()
            return (
                professional_monitoring["callCenter"]["status"]
                == BotEngine.PROFESSIONAL_MONITORING_REGISTERED
            )
        except Exception as e:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|has_professional_monitoring() Error checking professional monitoring status: {}".format(e)
            )
            return False

        return False

    def professional_monitoring_status(self):
        """
        :return: call center service statuses
        """
        if self.playback:
            status = {
                "callCenter": {
                    "alertDateMs": 0,
                    "alertStatus": 0,
                    "alertStatusDateMs": 0,
                    "status": 3,
                }
            }
            return status

        r = self._http_get("/analytic/callCenter")
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def professional_monitoring_alerts(self):
        """
        :return: call center service alerts
        """
        r = self._http_get("/analytic/callCenterAlerts")
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def raise_professional_monitoring_alert(
        self, message, code, device_id=None, latitude=None, longitude=None
    ):
        """
        Raise an alert to the professional monitoring services

        :param message: signal message
        :param code:         E130 - General burglary alarm
                             E131 - Perimeter alarm (door/window entry sensor)
                             E132 - Interior alarm (motion sensor)
                             E134 - Entry/exit alarm (more specific than E131, but I'm not sure we can declare that our door/window sensors will always be used on an entry/exit)
                             E154 - Water leak
                             E111 - Smoke alarm (future)
                             E114 - Heat alarm (future - analytics on temperature sensors above the stove, for example)
                             E158 - Environmental high temperature alarm (temperature sensor)
                             E159 - Environmental low temperature alarm (temperature sensor)
                             E100 - General medical alarm (future - Personal Emergency Reporting System (PERS) button)
                             E108 - Verify contact information

        :param device_id: device ID
        :param latitude: Optional latitude for mobile events
        :param longitude: Optional longitude for mobile events
        """
        return self._signal_professional_monitoring(
            1, message, code, device_id, latitude=latitude, longitude=longitude
        )

    def cancel_professional_monitoring_alert(self, message, code, device_id=None):
        """
        Cancel an alert to the professional monitoring services

        :param message: signal message
        :param code:         E130 - General burglary alarm
                             E131 - Perimeter alarm (door/window entry sensor)
                             E132 - Interior alarm (motion sensor)
                             E134 - Entry/exit alarm (more specific than E131, but I'm not sure we can declare that our door/window sensors will always be used on an entry/exit)
                             E154 - Water leak
                             E111 - Smoke alarm (future)
                             E114 - Heat alarm (future - analytics on temperature sensors above the stove, for example)
                             E158 - Environmental high temperature alarm (temperature sensor)
                             E159 - Environmental low temperature alarm (temperature sensor)
                             E100 - General medical alarm (future - Personal Emergency Reporting System (PERS) button)

        :param device_id: device ID
        """
        return self._signal_professional_monitoring(2, message, code, device_id)

    def _signal_professional_monitoring(
        self, alert_status, message, code, device_id=None, latitude=None, longitude=None
    ):
        """
        This method can change the current alert status to raise or cancel it

        :param alert_status:  0   An alert was never raised
                              1   Raise an alert
                              2   Cancel an alert
                              3   Not available to set - The alert was reported to the professional monitoring services

        :param message: signal message
        :param code:         E130 - General burglary alarm
                             E131 - Perimeter alarm (door/window entry sensor)
                             E132 - Interior alarm (motion sensor)
                             E134 - Entry/exit alarm (more specific than E131, but I'm not sure we can declare that our door/window sensors will always be used on an entry/exit)
                             E154 - Water leak
                             E111 - Smoke alarm (future)
                             E114 - Heat alarm (future - analytics on temperature sensors above the stove, for example)
                             E158 - Environmental high temperature alarm (temperature sensor)
                             E159 - Environmental low temperature alarm (temperature sensor)
                             E100 - General medical alarm (future - Personal Emergency Reporting System (PERS) button)

        :param device_id: device ID
        :param latitude: Optional latitude for mobile events
        :param longitude: Optional longitude for mobile events
        """
        body = {"alertStatus": alert_status, "signalMessage": message}

        if code:
            body["signalType"] = code

        if device_id:
            body["deviceId"] = device_id

        if latitude is not None:
            body["latitude"] = str(latitude)

        if longitude is not None:
            body["longitude"] = str(longitude)

        r = self._http_put(
            "/analytic/callCenter", data=json.dumps({"callCenter": body})
        )
        j = json.loads(r.text)
        return j

    # ===========================================================================
    # Tags
    # ===========================================================================
    def tag_user(self, tag, user_id=None):
        """
        Tag a user
        :param tag: The tag to give the user
        """
        self._tag(1, tag, user_id)

    def tag_location(self, tag, category=None, priority=None):
        """
        Tag a location
        :param tag: The tag to give the location
        :param location_id: The location ID to tag
        :param category: Optional category for this tag
        :param priority: Optional priority for this tag
        """
        self._tag(2, tag, self.get_location_id(), category=category, priority=priority)

    def tag_device(self, tag, device_id, user_id=None):
        """
        Tag a device
        :param tag: The tag to give the device
        :param device_id: The device ID to tag
        """
        self._tag(3, tag, device_id, user_id)

    def tag_file(self, tag, file_id, user_id=None):
        """
        Tag a file
        :param tag: The tag to give the file
        :param file_id: The file ID to tag
        """
        self._tag(4, tag, file_id, user_id)

    def delete_user_tag(self, tag, user_id=None):
        """
        Delete a user tag
        :param tag: Tag to delete
        """
        self._delete_tag(1, tag)

    def delete_location_tag(self, tag):
        """
        Delete a location tag
        :param tag: Tag to delete
        """
        self._delete_tag(2, tag, self.get_location_id())

    def delete_device_tag(self, tag, device_id):
        """
        Delete a location device
        :param tag: Tag to delete
        """
        self._delete_tag(3, tag, device_id)

    def delete_file_tag(self, tag, file_id):
        """
        Delete a location file
        :param tag: Tag to delete
        """
        self._delete_tag(4, tag, file_id)

    def get_location_tags(self):
        """
        Get Location tags
        :return:
        """
        tags = self.get_tags(tag_type=self.TAG_TYPE_LOCATIONS)

        tag_list = []
        for tag_object in tags:
            tag_list.append(tag_object["tag"])

        return tag_list

    def get_tags(self, tag_type=None, tag_id=None, user_id=None):
        """
        Get tags
        :param tag_type: Optional, filter by type:
                1 - Users
                2 - Locations
                3 - Devices
                4 - Files

        :param tag_id: Optional, filter by location ID, device ID, or file ID
        :param user_id: Used with Organizational Apps - confine tags to a specific user
        """
        if self.playback:
            return []

        params = {}

        if user_id is not None:
            params["userId"] = user_id

        if tag_type is not None:
            params["type"] = tag_type

        if tag_id is not None:
            params["id"] = tag_id

        r = self._http_get("/analytic/tags", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)

        if "tags" in j:
            return j["tags"]

        return []

    def _tag(self, tag_type, tag, tag_id=None, user_id=None, category=None, priority=None):
        """Private method to tag users, devices, locations, files

        :param tag_type:   1 - User
                       2 - Location
                       3 - Device
                       4 - Files

        :param tag: Tag to give the object
        :param tag_id: Location ID, Device ID, or File ID
        :param user_id: Used with Organizational Apps - confine tags to a specific user
        :param category: Optional category for this tag
        :param priority: Optional priority for this tag
        """
        if " " in tag:
            return "Error: Tags cannot have any spaces"

        if "#" in tag:
            return "Error: Tags cannot have any # signs"

        if "@" in tag:
            return "Error: Tags cannot have any @ signs"

        tag_block = {"type": tag_type, "tag": tag}

        if tag_id is not None:
            tag_block["id"] = tag_id
        
        if tag_type == 2:  # Location tag
            if category is not None:
                tag_block["category"] = category
            if priority is not None:
                tag_block["priority"] = priority

        if user_id is not None:
            if user_id not in self.tags_to_create_by_user:
                self.tags_to_create_by_user[user_id] = []
            self.tags_to_create_by_user[user_id].append(tag_block)

        else:
            self.tags_to_create.append(tag_block)

    def _delete_tag(self, tag_type, tag, tag_id=None, user_id=None):
        """Delete a tag

        :param tag_type:   1 - User
                       2 - Location
                       3 - Device
                       4 - Files

        :param tag: Tag to delete
        :param tag_id: Location ID, Device ID, or File ID
        """
        tag_block = {"type": tag_type, "tag": tag}

        if tag_id is not None:
            tag_block["id"] = tag_id

        if user_id is not None:
            if user_id not in self.tags_to_delete_by_user:
                self.tags_to_delete_by_user[user_id] = []
            self.tags_to_delete_by_user[user_id].append(tag_block)

        else:
            self.tags_to_delete.append(tag_block)

    def flush_tags(self):
        """
        Flush the new and deleted tags to the server,
        This is called automatically when the bot is finished executing. It should never have to be called manually.
        """
        from botengine import BotError
        # Create tags - single API call
        if len(self.tags_to_create) > 0:
            j = json.dumps({"tags": self.tags_to_create})
            r = self._http_put("/analytic/tags", data=j)
            j = json.loads(r.text)
            try:
                _check_for_errors(j)
            except BotError as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|flush_tags() " + e.msg + "; data=" + str(j)
                )

        # Delete tags - individual API calls
        for params in self.tags_to_delete:
            r = self._http_delete("/analytic/tags", params=params)
            j = json.loads(r.text)

            # Do not check for errors, because most errors are likely the
            # admin manually deleting a tag and we don't want to kill the bot.

        # Organizational tags to create - individual API calls for each user
        for user_id in self.tags_to_create_by_user:
            params = {"userId": user_id}
            j = json.dumps({"tags": self.tags_to_create_by_user[user_id]})
            r = self._http_put("/analytic/tags", params=params, data=j)
            j = json.loads(r.text)
            try:
                _check_for_errors(j)
            except BotError as e:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|flush_tags() " + e.msg + "; user_id=" + str(user_id) + "; data=" + str(j)
                )

        # Organizational tags to delete - individual API calls for each tag
        for user_id in self.tags_to_delete_by_user:
            for params in self.tags_to_delete_by_user[user_id]:
                params["userId"] = user_id
                r = self._http_delete("/analytic/tags", params=params)

    # ===========================================================================
    # Location Settings
    # ===========================================================================
    def set_location_priority(self, category, rank, comment=None):
        """
        Set the prioritized category of human attention needed for this location.

          0 = This location has no devices.
          1 = Everything is running okay
          2 = This location is learning
          3 = Incomplete installation (of devices, people, etc.)
          4 = System problem (offline devices, low battery, abnormal device behaviors, etc.)
          5 = Subjective warning (abnormal trends, sleeping too much, etc.)
          6 = Critical alert (falls, didn't wake up, water leak, etc.)

        :param category: Priority from 0 - 6 where 6 requires the most human attention
        :param rank: Rank from 100% good to 0% good to compare homes within a specific category
        :param comment: Human-understandabld description of why the location has this priority
        :return:
        """
        body = {
            "location": {
                "priorityCategory": int(category),
                "priorityRank": int(rank),
                "priorityComment": comment,
            }
        }

        self._http_put(
            "/analytic/location/{}".format(self.get_location_id()),
            data=json.dumps(body),
        )

    def get_spaces(self):
        """
        Get a list of spaces for this location
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/get-spaces
        :return: List of spaces
        """
        r = self._http_get(
            "/cloud/json/location/{}/spaces".format(self.get_location_id())
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        if "spaces" in j:
            return j["spaces"]
        return []

    def set_space(self, space_type, name, space_id=None):
        """
        Add / Update a space
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/update-space
        :param space_type: Type of space
        :param name: Name of space
        :param space_id: Space ID to update an existing space definition
        """
        params = {}
        if space_id is not None:
            params["spaceId"] = space_id

        body = {"space": {"type": space_type, "name": name}}

        self._http_post(
            "/cloud/json/location/{}/spaces".format(self.get_location_id()),
            params=params,
            data=json.dumps(body),
        )

    def delete_space(self, space_id):
        """
        Delete a space
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/delete-space
        :param space_id: Space ID to delete
        """
        params = {"spaceId": space_id}

        r = self._http_delete(
            "/cloud/json/location/{}/spaces".format(self.get_location_id()),
            params=params,
        )
        _check_for_errors(json.loads(r.text))

    def add_occupancy(self, occupancy):
        """
        Add occupancy
        https://iotapps.docs.apiary.io/#reference/locations/location-occupancy/add-occupancy
        :param occupancy: Bitmask mark that locations is occupied or vacant:
                            0 - none or no data
                            1 - managed
                            2 - measured
        """
        r = self._http_post(
            "/cloud/json/location/{}/occupancy/{}".format(
                self.get_location_id(), occupancy
            )
        )
        _check_for_errors(json.loads(r.text))

    def delete_occupancy(self, occupancy):
        """
        Delete occupancy
        https://iotapps.docs.apiary.io/#reference/locations/location-occupancy/remove-occupancy
        :param occupancy: Bitmask mark that locations is occupied or vacant:
                            0 - none or no data
                            1 - managed
                            2 - measured
        """
        r = self._http_delete(
            "/cloud/json/location/{}/occupancy/{}".format(
                self.get_location_id(), occupancy
            )
        )
        _check_for_errors(json.loads(r.text))

    # ===========================================================================
    # Weather
    # ===========================================================================
    def get_weather_forecast_by_geocode(
        self, latitude, longitude, units=None, hours=12
    ):
        """
        Get the weather forecast by geocode (latitude, longitude)
        :param latitude: Latitude
        :param longitude: Longitude
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :param hours: Forecast depth in hours, default is 12. Available hours are 6, 12.
        :return: Weather JSON data
        """
        params = {}

        if units is not None:
            params["units"] = units

        if hours is not None:
            params["hours"] = hours

        r = self._http_get(
            "/cloud/json/weather/forecast/geocode/"
            + str(latitude)
            + "/"
            + str(longitude),
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_current_weather_by_geocode(self, latitude, longitude, units=None):
        """
        Get the current weather by geocode (latitude, longitude)
        :param latitude: Latitude
        :param longitude: Longitude
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :return: Weather JSON data
        """
        params = {}

        if units is not None:
            params["units"] = units

        r = self._http_get(
            "/cloud/json/weather/current/geocode/"
            + str(latitude)
            + "/"
            + str(longitude),
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_weather_forecast_by_location(self, location_id, units=None, hours=12):
        """
        Get the weather forecast by Location ID
        :param location_id: Location ID for which to retrieve the weather forecast
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :param hours: Forecast depth in hours, default is 12. Available hours are 6, 12.
        :return: Weather JSON data
        """
        params = {}

        if units is not None:
            params["units"] = units

        if hours is not None:
            params["hours"] = hours

        r = self._http_get(
            "/cloud/json/weather/forecast/location/" + str(location_id), params=params
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_current_weather_by_location(self, location_id, units=None):
        """
        Get the current weather by Location ID
        :param location_id: Location ID for which to retrieve the weather forecast
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :return: Weather JSON data
        """
        params = {}

        if units is not None:
            params["units"] = units

        r = self._http_get(
            "/cloud/json/weather/current/location/" + str(location_id), params=params
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===========================================================================
    # Timers
    # ===========================================================================
    def start_timer(self, seconds, function, argument=None, reference=None):
        """
        Start a timer with a relative time in seconds to fire.

        :param seconds: Number of seconds from now to execute.
        :param function: Function to execute when the timer fires. This must be a function, not be a class method.
        :param argument: Optional argument to inject into the fired timer
        :param reference: Optional ID to reference this timer. Useful if you plan on canceling the timer later.
        """
        absolute_time = self.get_timestamp()
        self.set_timer(
            int(absolute_time + (seconds * 1000)), function, argument, reference
        )

    def start_timer_s(self, seconds, function, argument=None, reference=None):
        """
        Start a timer with a relative time in seconds to fire.

        :param seconds: Number of seconds from now to execute.
        :param function: Function to execute when the timer fires. This must be a function, not be a class method.
        :param argument: Optional argument to inject into the fired timer
        :param reference: Optional ID to reference this timer. Useful if you plan on canceling the timer later.
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(">start_timer_s() reference={} ms={} now={} trigger={}".format(reference, seconds * 1000, self.get_timestamp(), int(self.get_timestamp() + (seconds * 1000))))
        self.set_alarm(
            int(self.get_timestamp() + (seconds * 1000)), function, argument, reference
        )

    def start_timer_ms(self, milliseconds, function, argument=None, reference=None):
        """
        Start a timer with a relative time in milliseconds to fire.

        :param milliseconds: Number of milliseconds from now to execute.
        :param function: Function to execute when the timer fires. This must be a function, not be a class method.
        :param argument: Optional argument to inject into the fired timer
        :param reference: Optional ID to reference this timer. Useful if you plan on canceling the timer later.
        """
        absolute_time = self.get_timestamp()
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("|start_timer_ms() reference={} ms={} now={} trigger={}".format(reference, milliseconds, absolute_time, int(absolute_time + milliseconds)))
        self.set_alarm(int(absolute_time + milliseconds), function, argument, reference)

    def set_alarm(self, timestamp_ms, function, argument=None, reference=None):
        """
        Set an alarm with an absolute timestamp
        :param timestamp_ms: Absolute unix epoch time in milliseconds to fire the timer.
        :param function: Function to execute when the timer fires. This must be a function, not be a class method.
        :param argument: Optional argument to inject into the fired timer
        :param reference: Optional ID to reference this timer. Useful if you plan on canceling the timer later.
        """
        from botengine import BotError
        if timestamp_ms < self.get_timestamp() - 31536000000:
            # Set a timer for over a year ago. Did you accidentally set an absolute alarm and think it was a relative timer?
            import traceback

            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|set_alarm() A microservice attempted to set a timer/alarm over a year ago back in time. Did you accidentally set an absolute alarm and think it was a relative timer? Please check your logic. timestamp_ms={}; function={}; argument={}; reference={}; traceback={}".format(
                    timestamp_ms,
                    function,
                    argument,
                    reference,
                    traceback.format_stack(),
                )
            )

        if (
            not self.playback
            and self.get_trigger_type() & self.TRIGGER_DATA_REQUEST != 0
        ):
            # Illegal operation - data request triggers execute concurrently with other bot executions and therefore your core variable cannot get updated.
            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|set_alarm() You cannot start a timer/alarm while executing a data request trigger. Timer/Alarm reference={}".format(
                    reference
                )
            )
            raise BotError(
                "Cannot start a timer/alarm while executing a data request trigger.", -1
            )

        min_countdown_threshold = self.get_system_property("ppc.bot.minCountdownThreshold")
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("|set_alarm() min_countdown_threshold={}".format(min_countdown_threshold))
        try:
            time_variance = int(min_countdown_threshold or TIMER_MIN_MS)
        except Exception:
            time_variance = TIMER_MIN_MS
        system_time = self.get_system_time_ms()
        if timestamp_ms <= system_time + time_variance:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|set_alarm() Timestamp {} before system time {}, setting time to {} ms later.".format(
                    timestamp_ms, system_time, time_variance + 1
                )
            )
            timestamp_ms = system_time + time_variance + 1

        saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)

        if saved_timers is None:
            saved_timers = []

        # Timer tuple is:
        #   (timestamp, function, argument, reference)
        saved_timers = [
            x for x in saved_timers if (x[3] != reference and x[0] != MAXINT)
        ]
        saved_timers.append((int(timestamp_ms), function, argument, reference))

        # Log when the latest change to our timer variable is made
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info("|set_alarm() execution_time={}\tt{} timer={} reference={} system_time={}".format(self.get_timestamp(), system_time - timestamp_ms, timestamp_ms, reference, system_time))

        saved_timers = [x for x in saved_timers if x[0] != MAXINT]
        saved_timers.append((MAXINT, self.get_timestamp(), None, None))
        saved_timers.sort(key=lambda tup: tup[0])

        self.save_variable(TIMERS_VARIABLE_NAME, saved_timers)

        # The end of this bot execution will extract the next timer to execute and set it up
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("<set_alarm()")

    def set_timer(self, timestamp, function, argument=None, reference=None):
        """
        Deprecated. Use set_alarm() instead.

        Set an alarm with an absolute timestamp.
        :param timestamp: Absolute unix epoch time to fire the timer.
        :param function: Function to execute when the timer fires. This must be a function, not be a class method.
        :param argument: Optional argument to inject into the fired timer
        :param reference: Optional ID to reference this timer. Useful if you plan on canceling the timer later.
        """
        self.set_alarm(timestamp, function, argument, reference)

    def is_timer_running(self, reference):
        """
        Find out if at least one instance of a particular timer is running
        :param reference: Search for timers with the given reference. Cannot be None.
        :return: True if there is at least 1 existing timer with this reference running
        """
        saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
        if saved_timers is None:
            return False
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("|is_timer_running() reference={} timers={}".format(reference, saved_timers))
        for ref in [x[3] for x in saved_timers]:
            if ref == reference:
                return True

        return False

    def timer_timestamp_ms(self, reference):
        """
        Get the timer or alarm's timestamp in milliseconds
        :param reference:
        :return:
        """
        saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
        if saved_timers is None:
            return None

        for ref, ts in [(x[3], x[0]) for x in saved_timers]:
            if ref == reference:
                return ts

        return None

    def cancel_timers(self, reference):
        """
        Cancel ALL timers with the given reference.

        :param reference: Search for timers with the given reference and destroy them. Cannot be None.
        """
        saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
        if saved_timers is None:
            saved_timers = []

        saved_timers = [
            x for x in saved_timers if (x[3] != reference and x[0] != MAXINT)
        ]
        saved_timers.append((MAXINT, self.get_timestamp(), None, None))
        saved_timers.sort(key=lambda tup: tup[0])
        self.save_variable(TIMERS_VARIABLE_NAME, saved_timers)

        if not self.cancelled_timers and len(saved_timers) <= 1:
            self._cancel_execution_request()
            self.cancelled_timers = True

    def _inspect_timer_stack(self):
        """
        For running locally
        :return:
        """
        from botengine.color import Color
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">_inspect_timer_stack() "
            + Color.PURPLE 
            + "TIMER STACK:" 
            + Color.END
        )
        saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
        for t in saved_timers:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|_inspect_timer_stack() "
                + Color.PURPLE 
                + "t{}\t{}".format(self.get_timestamp() - t[0], t) 
                + Color.END
            )

    def async_execute_again_in_n_seconds(self, seconds):
        """
        Execute this bot again in N seconds, without an external trigger.
        This is useful for transitioning from an asynchronous back to synchronous execution 
        without waiting for external triggers or dependencies.
        :param seconds:
        """
        return self._execute_again_in_n_seconds(seconds)

    def _execute_again_in_n_seconds(self, seconds):
        """
        Execute this bot again at a relative time, N seconds from now, without an external trigger
        :param seconds
        """

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">_execute_again_in_n_seconds() {} seconds".format(seconds)
        )
        params = {"in": int(seconds)}

        r = self._http_put("/analytic/execute", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        # Extract "timer" field, return as int if present, otherwise return 0 if timer was not set
        timer = int(j.get("timer", 0))
        if timer == 0:
            saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
            self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                "<_execute_again_in_n_seconds() Server did not return a timer value when requesting execution in {} seconds\ntimers={}".format(seconds, saved_timers)
            )
            return timer
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<_execute_again_in_n_seconds() timer={} delta={}".format(timer, timer - seconds * 1000)
        )
        return timer

    def _execute_again_at_timestamp(self, unix_timestamp_ms):
        """Execute this bot again at an absolute time, at the given timestamp, without an external trigger
        :param unix_timestamp_ms:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">_execute_again_at_timestamp() timestamp {} (delta {}ms)".format(unix_timestamp_ms, unix_timestamp_ms - self.get_timestamp())
        )
        params = {"at": int(unix_timestamp_ms)}

        r = self._http_put("/analytic/execute", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        # Extract "timer" field, return as int if present, otherwise return 0 if timer was not set
        timer = int(j.get("timer", 0))
        if timer == 0:
            saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
            self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                "<_execute_again_at_timestamp() Server did not return a timer value when requesting execution at timestamp {}\ntimers={}".format(unix_timestamp_ms, saved_timers)
            )
            return timer
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<_execute_again_at_timestamp() timer={} delta={}".format(timer, timer - unix_timestamp_ms)
        )
        return timer

    def get_system_time_ms(self):
        """
        Get the current system time in milliseconds since epoch
        :return: Current system time in milliseconds since epoch
        """
        return round(time.time() * 1000)

    def _cancel_execution_request(self):
        """
        Cancel any existing requests for delayed executions
        """
        from botengine import BotError
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">_cancel_execution_request()"
        )
        r = self._http_delete("/analytic/execute")
        j = json.loads(r.text)
        try:
            _check_for_errors(j)
        except BotError as e:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|_cancel_execution_request() " + e.msg + "; data=" + str(j)
            )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<_cancel_execution_request()"
        )

    

    def _schedule_next_timer(self, next_timer_at_server):
        from botengine.color import Color
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(">_schedule_next_timer() timer={}".format(next_timer_at_server))
        min_countdown_threshold = self.get_system_property("ppc.bot.minCountdownThreshold")
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug("|_schedule_next_timer() min_countdown_threshold={}".format(min_countdown_threshold))
        while True:
            saved_timers = self.load_variable(TIMERS_VARIABLE_NAME)
            if saved_timers is None:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<_schedule_next_timer() Timers variable not found.")
                return
            for t in saved_timers:
                system_time = self.get_system_time_ms()
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|_schedule_next_timer() " + Color.PURPLE + "t{}\t{}".format(system_time - t[0], t) + Color.END
                )   
            if len(saved_timers) == 0:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<_schedule_next_timer() No timers to schedule.")
                break
            if saved_timers[0][0] == MAXINT:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<_schedule_next_timer() Timers exhausted.")
                break
            # Schedule the first timer in our stack
            current_timer = saved_timers[0]
            if current_timer[0] == next_timer_at_server:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info("_schedule_next_timer() Current timer matches next timer at server, no need to reschedule: t{} {}".format(self.get_timestamp() - current_timer[0], current_timer))
                break

            # Request a new execution no earlier than 1 second from now
            system_time = self.get_system_time_ms()
            try:
                time_variance = int(min_countdown_threshold or TIMER_MIN_MS)
            except Exception:
                time_variance = TIMER_MIN_MS
            
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|_schedule_next_timer() Scheduling first timer: t{} {}".format(system_time - current_timer[0], current_timer)
            )
            next_timer = self._execute_again_at_timestamp(max(system_time + time_variance, current_timer[0]))
            if next_timer == 0:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                    "|_schedule_next_timer() "
                    + Color.PURPLE
                    + "Executing timer during rescheduling. t{} timer={}".format(
                        system_time - current_timer[0], current_timer
                    )
                    + Color.END
                )
                # Remove executed timer from saved_timers
                del saved_timers[0]
                self.save_variable(TIMERS_VARIABLE_NAME, saved_timers, overwrite=True)
                
                # Execute timer callback immediately
                if callable(current_timer[1]):
                    current_timer[1](self, current_timer[2])
                else:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|_schedule_next_timer() Timer callback is not callable: {}".format(current_timer)
                    )
                # Schedule the next timer in the stack
                continue
            if self.is_server_version_newer_than(716):
                saved_timers[0] = (next_timer, current_timer[1], current_timer[2], current_timer[3])
                self.save_variable(TIMERS_VARIABLE_NAME, saved_timers, overwrite=True)
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info("|_schedule_next_timer() Scheduled next timer at server. timer={}".format(next_timer))
            break

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<_schedule_next_timer() next_timer={}".format(saved_timers[0] if saved_timers else None))

    # ===========================================================================
    # Questions
    # ===========================================================================
    def generate_question(
        self,
        key_identifier,
        response_type,
        device_id=None,
        icon=None,
        icon_font=None,
        display_type=None,
        collection=None,
        editable=False,
        default_answer=None,
        correct_answer=None,
        answer_format=None,
        urgent=False,
        front_page=False,
        send_push=False,
        send_sms=False,
        send_email=False,
        ask_timestamp=None,
        section_id=0,
        question_weight=0,
    ):
        """
        Initializer

        :param key_identifier: Your own custom key to recognize this question regardless of the language or framing of the question to the user.
        :param response_type: Type of response we should expect the user to give
            1 = Boolean question
            2 = Multichoice, Single select (requires response options)
            4 = Multichoice, Multi select (requires response options)
            6 = Day of the Week
            7 = Slider (Default minimum is 0, default maximum is 100, default increment is 5)
            8 = Time in seconds since midnight
            9 = Datetime (xsd:dateTime format)
            10 = Open-ended text

        :param device_id: Device ID to ask a question about so the UI can reference its name
        :param icon: Icon to display when asking this question
        :param icon_font: Icon font to render the icon. See the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
        :param display_type: How to render and display the question in the UI. For example, a Boolean question can be an on/off switch, a yes/no question, or just a single button. See the documentation for more details.
        :param collection: Collection Name
        :param editable: True to make this question editable later. This makes the question more like a configuration for the bot that can be adjusted again and again, rather than a one-time question.
        :param default_answer: Default answer for the question
        :param correct_answer: This is a regular expression to determine if the user's answer is "correct" or not
        :param answer_format: Regular expression string that represents what a valid response would look like. All other responses would not be allowed.
        :param urgent: True if this question is urgent enough that it requires a push notification and should be elevated to the top of the stack after any current delivered questions. Use sparingly to avoid end-user burnout.
        :param front_page: True if this question should be delivered to the front page of mobile/web bot, when the user is ready to consume another question from the system.
        :param send_push: True to send this questions as a push notification. Use sparingly to avoid end user burnout.
        :param send_sms: True to send an SMS message. Because this costs money, this is currently disabled.
        :param send_email: True to send the question in an email. Use sparingly to avoid burnout and default to junk mail.
        :param ask_timestamp: Future timestamp to ask this question. If this is not set, the current time will be used.
        :param section_id: ID of a section, which acts as both the element to group by as well as the weight of the section vs. other sections in the UI. (default is 0)
        :param question_weight: Weight of an individual question within a grouped section. The lighter the weight, the more the question rises to the top of the list in the UI. (default is 0)
        """
        # This should mirror exactly what the Question object provides
        from botengine import Question
        return Question(
            key_identifier,
            response_type,
            device_id,
            icon,
            icon_font,
            display_type,
            collection,
            editable,
            default_answer,
            correct_answer,
            answer_format,
            urgent,
            front_page,
            send_push,
            send_sms,
            send_email,
            ask_timestamp,
            section_id,
            question_weight,
        )

    def ask_question(self, question):
        """
        Ask your question

        :param question: Question to ask, created by the generate_question method
        """
        self.questions_to_ask[question.key_identifier] = question

    def delete_question(self, question):
        """
        Delete the question.
        Best practice is to learn what we need to learn from a question and then delete a question after we're done with it.
        This can help free up space and increase execution time if we've already learned what we need to learn from this question.

        :param question: Question to delete
        """
        if question._question_id is None:
            # Then just don't ask the question
            if question.key_identifier in self.questions_to_ask:
                del self.questions_to_ask[question.key_identifier]

        saved_questions = self.load_variable(QUESTIONS_VARIABLE_NAME)
        if saved_questions is not None:
            if question.key_identifier in saved_questions:
                # Delete the question from our saved questions
                del saved_questions[question.key_identifier]
                self.save_variable(QUESTIONS_VARIABLE_NAME, saved_questions)

        self.questions_to_delete[question.key_identifier] = question

    def flush_questions(self):
        """
        Synchronize all deleted and new questions with the server.
        This is called automatically when the bot is finished executing. It should never have to be called manually.
        """

        if self.get_bot_type() == BotEngine.BOT_TYPE_ORGANIZATION_RAG:
            # Organization RAG bots cannot call APIs
            return

        saved_questions = self.load_variable(QUESTIONS_VARIABLE_NAME)
        if saved_questions is None:
            saved_questions = {}

        original_saved_questions = saved_questions.copy()

        # Delete questions
        for q_id in self.questions_to_delete:
            question = self.questions_to_delete[q_id]

            if self.playback:
                if question.key_identifier in saved_questions:
                    # Delete the question from our saved questions
                    del saved_questions[question.key_identifier]
                continue

            params = {"questionId": question._question_id}

            r = self._http_delete("/analytic/questions", params=params)
            j = json.loads(r.text)

            if j["resultCode"] == 0:
                if question.key_identifier in saved_questions:
                    # Delete the question from our saved questions
                    del saved_questions[question.key_identifier]

        # Ask questions
        if self.playback:
            for q_id in self.questions_to_ask:
                question = self.questions_to_ask[q_id]
                question.answer_status = BotEngine.ANSWER_STATUS_QUEUED
                saved_questions[question.key_identifier] = question

            self.save_variable(QUESTIONS_VARIABLE_NAME, saved_questions)
            self.questions_to_delete = {}
            self.questions_to_ask = {}
            return

        if len(self.questions_to_ask) > 0:
            body = {"questions": []}

            for q_id in self.questions_to_ask:
                question = self.questions_to_ask[q_id]
                json_question = question._form_json_question(logger=self.get_logger(f"{'question'}.Question"))

                # 'iconFont' field first appeared in server version 1.16, so delete it for previous versions.
                if not self.is_server_version_newer_than(1, 16):
                    if "iconFont" in json_question:
                        del json_question["iconFont"]

                body["questions"].append(json_question)

            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_questions() questions={}".format(
                    json.dumps(body, sort_keys=True)
                )
            )
            r = self._http_post("/analytic/questions", data=json.dumps(body))
            response = json.loads(r.text)
            self.get_logger(
                f"{'botengine'}.{__class__.__name__}"
            ).info(
                "|flush_questions() | response={}".format(
                    json.dumps(response, sort_keys=True)
                )
            )

            if response["resultCode"] == 0 and "questions" in response:
                for response_block in response["questions"]:
                    question = self.questions_to_ask[response_block["key"]]
                    question._question_id = response_block["id"]
                    question.answer_status = BotEngine.ANSWER_STATUS_QUEUED
                    saved_questions[question.key_identifier] = question

            elif response["resultCode"] == 6:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                    "|flush_questions() Cannot ask questions. {}".format(
                        response["resultCodeMessage"]
                    )
                )

        if original_saved_questions != saved_questions:
            # Only save changes if we actually made changes
            self.save_variable(QUESTIONS_VARIABLE_NAME, saved_questions)

        self.questions_to_delete = {}
        self.questions_to_ask = {}

    def get_asked_questions(self):
        """
        Retrieve a dictionary of previously asked questions that still exist
        Include any pending questions that need to be saved.
        Exclude any pending questions that need to be deleted.

          {
            "question_id_1" : question_object_1,
            "question_id_2" : question_object_2
          }

        :return: a dictionary of questions we've previously asked. The question's ID is the dictionary's key, the question itself is the value.
        """
        saved_questions = self.load_variable(QUESTIONS_VARIABLE_NAME)
        if saved_questions is None:
            saved_questions = {}
        # Include any pending questions that need to be saved.
        for q_id in self.questions_to_ask:
            if q_id not in saved_questions:
                saved_questions[q_id] = self.questions_to_ask[q_id]
        # Exclude any pending questions that need to be deleted.
        for q_id in self.questions_to_delete:
            if q_id in saved_questions:
                del saved_questions[q_id]
        return saved_questions

    def retrieve_question(self, key):
        """
        Retrieve a single previously asked question based on its key
        :param key: Key Identifier generated by the bot developer to track this question
        :return: A Question object if the question was asked and still exists, None if the question wasn't asked or no longer exists because it was deleted
        """
        saved_questions = self.get_asked_questions()

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|retrieve_question() key={}; saved_questions.keys()={}".format(
                key, saved_questions.keys()
            )
        )
        if key not in saved_questions:
            return None

        return saved_questions[key]

    def change_answer(self, question, new_answer):
        """
        Change the answer to a previously asked question.

        One of the best places to use this, for example, is with an Editable question that is being used to configure the bot.
        Let's say you ask an Editable question, the user answered it which configured your bot, and now your bot has to change
        behaviors again. You can update the user's answer to show the user what you're currently running off of, allowing the
        user to adjust the answer again if you want. Sort of a bi-directional back-and-forth "here are what the settings are
        going to be" so the user and bot can continually agree upon it.

        :param question: Question to update the answer for
        :param new_answer: New answer to inject into the question back to the user
        """
        if question._question_id is None:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").warn(
                "|change_answer() Cannot change answer to question: "
                + str(question.key_identifier)
                + " because is has never been asked. Set its default_answer instead, then ask it."
            )
            return

        body = {"answer": new_answer}

        params = {"questionId": question._question_id}

        r = self._http_put("/analytic/questions", params=params, data=json.dumps(body))
        j = json.loads(r.text)
        _check_for_errors(j)

        # Update our saved questions
        question.answer = new_answer
        saved_questions = self.load_variable(QUESTIONS_VARIABLE_NAME)
        if saved_questions is None:
            # If this every happens is due to developer error, not asking the question before modifying the answer.
            saved_questions = {}
        saved_questions[question.key_identifier] = question
        self.save_variable(QUESTIONS_VARIABLE_NAME, saved_questions)

    def resynchronize_questions(self):
        """
        Resynchronize our local cache of Questions with the server.
        :param botengine: BotEngine environment
        """
        from botengine import Question
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">resynchronize_questions()"
        )
        r = self._http_get("/analytic/questions")
        j = json.loads(r.text)
        _check_for_errors(j)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|resynchronize_questions() questions={}".format(
                json.dumps(j, sort_keys=True, indent=4)
            )
        )

        if "questions" in j:
            questions = j["questions"]

            saved_questions = {}

            for question in questions:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|resynchronize_questions() | question={}".format(
                        json.dumps(question, sort_keys=True, indent=4)
                    )
                )
                q = Question(question["key"], question["responseType"])

                q._question_id = question["id"]

                if "deviceId" in question:
                    q.device_id = question["deviceId"]

                if "icon" in question:
                    q.icon = question["icon"]

                if "displayType" in question:
                    q.display_type = question["displayType"]

                if "editable" in question:
                    q.editable = question["editable"]

                if "defaultAnswer" in question:
                    q.default_answer = question["defaultAnswer"]

                if "answer" in question:
                    q.answer = question["answer"]

                if "creationDateMs" in question:
                    q.ask_timestamp = question["creationDateMs"]

                if "answerStatus" in question:
                    q.answer_status = question["answerStatus"]

                if "question" in question:
                    q.question = question["question"]

                if "answerDateMs" in question:
                    q.answer_time = question["answerDateMs"]

                if "questionWeight" in question:
                    q.question_weight = question["questionWeight"]

                if "sectionId" in question:
                    q.section_id = question["sectionId"]

                if "sectionTitle" in question:
                    q.section_title = question["sectionTitle"]

                if "answerModified" in question:
                    q.answer_modified = question["answerModified"]

                if "responseOptions" in question:
                    q.response_options = question["responseOptions"]

                if "placeholder" in question:
                    q.placeholder = question["placeholder"]

                if "slider" in question:
                    if "min" in question["slider"]:
                        q.slider_min = question["slider"]["min"]

                    if "max" in question["slider"]:
                        q.slider_max = question["slider"]["max"]

                    if "inc" in question["slider"]:
                        q.slider_inc = question["slider"]["inc"]

                if "answerFormat" in question:
                    q.answer_format = question["answerFormat"]

                if "collectionName" in question:
                    q.collection = question["collectionName"]

                if question["key"] in saved_questions:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                        "|resynchronize_questions() | overwrite existing question={}".format(
                            json.dumps(
                                vars(saved_questions[question["key"]]),
                                sort_keys=True,
                                indent=4,
                            )
                        )
                    )
                else:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                        "|resynchronize_questions() | new question={}".format(
                            json.dumps(vars(q), sort_keys=True, indent=4)
                        )
                    )
                saved_questions[question["key"]] = q

            self.save_variable(QUESTIONS_VARIABLE_NAME, saved_questions)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "<resynchronize_questions()"
        )

    # ===========================================================================
    # Collections of Questions
    # ===========================================================================
    def set_collection(
        self, name, icon, description, ml_name=None, ml_description=None, weight=0, media=None, media_content_type=None
    ):
        """
        Create or update a Collection
        :param name: Name of the collection
        :param icon: Icon (See fontawesome.com for names)
        :param description: Description of the Collection
        :param ml_name: Multilingual name dict with language code as key and name as value
        :param ml_description: Multilingual description dict with language code as key and description as value
        :param weight: Weight of the collection relative to others. The lower the weight, the higher it floats.
        :param media: Media reference, for example an S3 object.
        :param media_content_type: Content type for the media, for example 'image/jpeg'.
        """
        body = {
            "collection": {
                "name": name,
                "icon": icon,
                "description": description,
                "weight": weight,
            }
        }
        if ml_name is not None and isinstance(ml_name, dict):
            body["collection"]["mlName"] = ml_name

        if ml_description is not None and isinstance(ml_description, dict):
            body["collection"]["mlDescription"] = ml_description

        if media is not None:
            body["collection"]["media"] = media

        if media_content_type is not None:
            body["collection"]["mediaContentType"] = media_content_type

        self._http_put("/analytic/questions/collections", data=json.dumps(body))

    def get_collections(self, name=None):
        """
        Get a list of Collections for Questions.
        :param name: Optional filter by name.
        :return: List of collections
        """
        params = {}
        if name is not None:
            params["name"] = name
        r = self._http_get("/analytic/questions/collections", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)

        if "collections" in j:
            return j["collections"]

        return None

    def delete_collection(self, name):
        """
        Delete a Collection. Any Questions that are part of the collection are not deleted.
        :param name: Name of the collection to delete
        """
        r = self._http_delete("/analytic/questions/collections", params={"name": name})
        _check_for_errors(json.loads(r.text))

    # ===========================================================================
    # Rules
    # ===========================================================================
    # Note that all of these rules APIs are available to administrators too, but I've left out the user_id field
    # because I currently believe only end-user bots should be able to manage end-user rules with permission.
    #
    # Also, there are 2 APIs I haven't implemented:  Create Rule and Update Rule. These are very complex API bodies
    # and as a general strategy I'd like us to move away from Rules and into Bots. Creating new rules goes against
    # that strategy.
    # -moss

    def get_rules(self, device_id=None, details=False):
        """
        Get a list of rules from this user.
        This will raise a BotError if the rules are not accessible.

        Remember: Rule status 0=incomplete; 1=active; 2=inactive

        :param device_id: Only return a list of rules for this device ID
        :param details: True to return details for this rule including all triggers, states, and actions that compose the rule. False to return only the high level information about the rule, including the ID, description text, on/off status, whether this is a default rule, and whether this rule is hidden and not editable.
        :return: List of rules if accessible.
        """
        params = {"details": details}

        if device_id is not None:
            params["deviceId"] = device_id

        r = self._http_get("/cloud/json/rules", params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_rule(self, rule_id, details=False):
        """
        Get a specific rule from this user
        This will raise a BotError if the rules are not accessible.

        :param rule_id: Rule ID to get
        :param details: True to return details for this rule including all triggers, states, and actions that compose the rule. False to return only the high level information about the rule, including the ID, description text, on/off status, whether this is a default rule, and whether this rule is hidden and not editable.
        :return: Complete rule definition
        """
        params = {"details": details}

        r = self._http_get("/cloud/json/rules/" + str(rule_id), params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def delete_rule(self, rule_id):
        """
        Delete a user's rule
        This will raise a BotError if rules are not accessible

        :param rule_id: Rule ID to delete
        """
        r = self._http_delete("/cloud/json/rules/" + str(rule_id))
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_rule_phrases(self):
        """
        Get the rule phrases from which we can compose new rules
        :return: Available rule phrases
        """
        r = self._http_get("/cloud/json/ruleConditions")
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def toggle_rule(self, rule_id, enable):
        """
        Set an attribute for a rule, like changing the name of it or switching it on or off.
        :param rule_id: ID of the rule to update
        :param enable: True to turn the rule on, False to turn it off.
        """
        # Remember rule status 0=incomplete; 1=active; 2=inactive
        status = 1

        if not enable:
            status = 2

        self.rules[rule_id] = status

    def delete_all_rules(
        self,
        status=None,
        rule_id_list=[],
        device_type_list=[],
        device_id_list=[],
        default=None,
        hidden=None,
        user_id=None,
    ):
        """
        Delete all the rules that match the given criteria
        :param status: Specific rule statuses to delete. 0=incomplete; 1=active; 2=inactive
        :param rule_id_list: Optional list of rule ID's to specifically target
        :param device_type_list: Optional list of device types to specifically target
        :param device_id_list: Optional list of device ID's to specifically target
        :param default: If True or False, update only default or non-default rules
        :param hidden: If True or False, update only hidden or non-hidden rules
        :param user_id: Optional user ID to be used by administrative / organizational bots.
        :return: List of rule_id's that were updated
        """
        params = {}

        if status is not None:
            params["status"] = status

        if len(rule_id_list) > 0:
            params["ruleId"] = rule_id_list

        if len(device_type_list) > 0:
            params["deviceType"] = device_type_list

        if len(device_id_list) > 0:
            params["deviceId"] = device_id_list

        if default is not None:
            params["default"] = default

        if hidden is not None:
            params["hidden"] = hidden

        if user_id is not None:
            params["userId"] = user_id

        self._http_delete("/cloud/json/rules", params=params)

    def toggle_all_rules(
        self,
        enable,
        rule_id_list=[],
        device_type_list=[],
        device_id_list=[],
        default=None,
        hidden=None,
        user_id=None,
    ):
        """
        Toggle all rules that match the given criteria
        :param enable: True to enable the rules, False to disable the rules
        :param rule_id_list: Optional list of rule ID's to specifically target
        :param device_type_list: Optional list of device types to specifically target
        :param device_id_list: Optional list of device ID's to specifically target
        :param default: If True or False, update only default or non-default rules
        :param hidden: If True or False, update only hidden or non-hidden rules
        :param user_id: Optional user ID to be used by administrative / organizational bots.
        :return: List of rule_id's that were updated
        """
        if self.playback:
            return []

        # Rule status 0=incomplete; 1=active; 2=inactive
        status = 1
        if not enable:
            status = 2

        params = {}

        if len(rule_id_list) > 0:
            params["ruleId"] = rule_id_list

        if len(device_type_list) > 0:
            params["deviceType"] = device_type_list

        if len(device_id_list) > 0:
            params["deviceId"] = device_id_list

        if default is not None:
            params["default"] = default

        if hidden is not None:
            params["hidden"] = hidden

        if user_id is not None:
            params["userId"] = user_id

        r = self._http_put("/cloud/json/rulesStatus/" + str(status), params=params)
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def flush_rules(self):
        """
        Flush all rule changes to the server. This is performed automatically at the end of execution.
        """
        for rule_id in self.rules:
            body = {"rule": {"status": self.rules[rule_id]}}

            self._http_put(
                "/cloud/json/rules/" + str(rule_id) + "/attrs", data=json.dumps(body)
            )

    # ===========================================================================
    # Bot content delivery to state variables
    # ===========================================================================
    def set_state(
        self,
        address,
        json_content,
        overwrite=True,
        timestamp_ms=None,
        publish_to_partner=True,
        fields_updated=[],
        fields_deleted=[],
        sub_location=False,
    ):
        """
        Set information to be consumed by user interfaces through a known address.

        Application-layer developers first collectively agree upon the data
        that needs to be produced by the bot to be rendered on a UI. Then the UI
        can read the address to extract the JSON information to render natively.

        It is therefore possible for the bot to also produce new addressable content,
        as long as the addresses are retrievable from a well known base address. For example,
        you could save some UI content that includes a list of reports, each report saved under
        a unique address. Then, save UI content for each report under their unique addresses.

        :param address: Address to save information into, in a way that can be recalled by an app.
        :param json_content: Raw JSON content to deliver to an app/UI.
        :param overwrite: True to overwrite all existing content, False to update existing server content only with the top-level dictionary keys that are presented leaving others untouched (default)
        :param timestamp_ms: For time-series state variables, fill in the timestamp in milliseconds.
        :param publish_to_partner: True or False to stream this state update to a partner cloud. Default is True, streaming enabled.
        :param fields_updated: To optimize integrations with 3rd party clouds, this is a list of the fields that were added/updated. Always used in conjunction with overwrite=True.
        :param fields_deleted: List of fields that were removed. Always used in conjunction with overwrite=True
        :param sub_location: True to also save this state variable to the sub-location (if applicable). Default is False.
        """
        if timestamp_ms not in self.states:
            self.states[timestamp_ms] = {}

        # Developer guardrails.
        if fields_updated is None:
            fields_updated = []

        # Developer guardrails
        if fields_deleted is None:
            fields_deleted = []

        try:
            serialized = json.dumps(json_content, sort_keys=True)
            size_bytes = len(serialized)
        except Exception:
            serialized = str(json_content)
            size_bytes = len(serialized)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|set_state() address='{}', overwrite={}, timestamp_ms={}, publish={}, fields_updated={}, fields_deleted={}, sub_location={}, size={} bytes, content={}".format(
                address,
                overwrite,
                timestamp_ms,
                publish_to_partner,
                fields_updated,
                fields_deleted,
                sub_location,
                size_bytes,
                serialized,
            )
        )

        if address not in self.states[timestamp_ms]:
            # We're forcefully updating some content without retrieving it first, let it go through efficiently without requiring a GET.
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|set_state() address='{}' immediate flush because address not cached (timestamp_ms={})".format(
                    address, timestamp_ms
                )
            )
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|set_state() address='{}' immediate flush payload size={} bytes content={}".format(
                    address, size_bytes, serialized
                )
            )
            self._flush_states(
                address,
                json_content,
                overwrite,
                timestamp_ms,
                publish_to_partner=publish_to_partner,
                fields_updated=fields_updated,
                fields_deleted=fields_deleted,
                sub_location=sub_location,
            )
            return

        if not overwrite:
            self.states[timestamp_ms][address].update(json_content)

        else:
            self.states[timestamp_ms][address] = json_content

        if timestamp_ms not in self.states_to_flush:
            self.states_to_flush[timestamp_ms] = {}

        if address in self.states_to_flush[timestamp_ms]:
            if STATE_KEY_UPDATE_LIST in self.states_to_flush[timestamp_ms][address]:
                fields_updated += self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_UPDATE_LIST
                ]

            if STATE_KEY_DELETE_LIST in self.states_to_flush[timestamp_ms][address]:
                fields_deleted += self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_DELETE_LIST
                ]

        # Remove duplicates
        fields_updated = list(set(fields_updated))
        fields_deleted = list(set(fields_deleted))

        if len(fields_updated) > 0 or len(fields_deleted) > 0:
            if not overwrite:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|set_state() address={}, Overwrite is incorrectly set to False. When providing a list of fields to update or remove, you must provide the entire copy of the JSON content and set overwrite=True".format(
                        address
                    )
                )
                overwrite = True

        self.states_to_flush[timestamp_ms][address] = {
            STATE_KEY_CONTENT: self.states[timestamp_ms][address],
            STATE_KEY_OVERWRITE: overwrite,
            STATE_KEY_PUBLISH: publish_to_partner,
            STATE_KEY_UPDATE_LIST: fields_updated,
            STATE_KEY_DELETE_LIST: fields_deleted,
            STATE_KEY_SUB_LOCATION: sub_location,
        }

    def get_state(self, address, timestamp_ms=None):
        """
        Get UI content by address. If a timestamp is provided, time-series states will return exactly 1 value
        at the exact given timestamp_ms.

        :param address: Address to retrieve information from
        :param timestamp_ms: Optional timestamp for time-based state variables
        :return: The JSON value for this address, or None if it doesn't exist
        """
        if timestamp_ms in self.states:
            if address in self.states[timestamp_ms]:
                return self.states[timestamp_ms][address]

        else:
            self.states[timestamp_ms] = {}

        params = {"name": address}

        if timestamp_ms is None:
            # Regular state
            r = self._http_get(
                "/cloud/json/locations/{}/state".format(self.get_location_id()),
                params=params,
            )
            j = json.loads(r.text)
            if "value" in j:
                self.states[timestamp_ms][address] = j["value"]
                return j["value"]

            else:
                return None

        else:
            # Time-based state
            params["startDate"] = timestamp_ms
            r = self._http_get(
                "/cloud/json/locations/{}/timeStates".format(self.get_location_id()),
                params=params,
            )
            j = json.loads(r.text)
            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|get_state() address={}, timestamp_ms={}, result={}".format(
                    address, timestamp_ms, json.dumps(j, sort_keys=True)
                )
            )
            if "states" in j:
                if len(j["states"]) > 0:
                    if "value" in j["states"][0]:
                        return j["states"][0]["value"]

            return None

    def delete_state(
        self,
        address,
        timeseries_property=False,
        overwrite=True,
        publish_to_partner=True,
    ):
        """
        Permanently delete a state variable. Must specify if it is a timeseries_property (default is non-time-series property).

        :param address: State variable address to delete
        :param timeseries_property: Set to True if it is a timeseries property (default is False, non-timeseries state variable)
        :param overwrite: Overwrite entire state property (default is true)
        :param publish_to_partner: True or False to stream this state update to a partner cloud. Default is True, streaming enabled.
        :return:
        """
        body = {"value": None}

        params = {
            "name": address,
            "overwrite": overwrite,
            "publish": publish_to_partner,
        }

        data = json.dumps(body)

        if not timeseries_property:
            # Non-time-series state variable
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|delete_state() Deleting state from state content '{}'".format(address)
            )
            self._http_put(
                "/cloud/json/locations/{}/state".format(self.get_location_id()),
                params=params,
                data=data,
            )

        else:
            # Time-series state variable
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|delete_state() Deleting state from timeState content'{}'".format(address)
            )
            self._http_put(
                "/cloud/json/locations/{}/timeStates".format(self.get_location_id()),
                params=params,
                data=data,
            )

    def get_timeseries_state(self, address, start_timestamp_ms, end_timestamp_ms=None):
        """
        Get a time-series state variable. This loads it from the server every time, and may include multiple time-series records
        ranging from the start_timestamp_ms to the end_timestamp_ms.

        :param address: Time-series state variable address to load
        :param start_timestamp_ms: Required start timestamp
        :param end_timestamp_ms: Optional end timestamp
        :return:
        """
        params = {"name": address, "startDate": start_timestamp_ms}

        if end_timestamp_ms is not None:
            params["endDate"] = end_timestamp_ms
        else:
            # The endDate must be set in order to receive a list of values,
            # otherwise only 1 value for the exact start_timestamp_ms will be returned.
            params["endDate"] = self.get_timestamp()

        r = self._http_get(
            "/cloud/json/locations/{}/timeStates".format(self.get_location_id()),
            params=params,
        )
        j = json.loads(r.text)

        result = {}
        if "states" in j:
            for s in j["states"]:
                result[int(s["stateDateMs"])] = s["value"]

        return result

    def flush_states(self):
        """
        Flush all UI content to the server
        :return:
        """
        if len(self.states_to_flush) == 0:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_states() No pending state variables to flush."
            )
        else:
            pending_summary = {}
            for timestamp_ms in self.states_to_flush:
                pending_summary[
                    timestamp_ms
                ] = list(self.states_to_flush[timestamp_ms].keys())

            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "|flush_states() Pending state variables: {}".format(
                    pending_summary
                )
            )

        for timestamp_ms in self.states_to_flush:
            for address in self.states_to_flush[timestamp_ms]:
                publish = self.states_to_flush[timestamp_ms][address][STATE_KEY_PUBLISH]
                overwrite = self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_OVERWRITE
                ]
                content = self.states_to_flush[timestamp_ms][address][STATE_KEY_CONTENT]
                fields_updated = self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_UPDATE_LIST
                ]
                fields_deleted = self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_DELETE_LIST
                ]
                sub_location = self.states_to_flush[timestamp_ms][address][
                    STATE_KEY_SUB_LOCATION
                ]

                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|flush_states() Flushing state address='{}' timestamp_ms={} overwrite={} publish={} fields_updated={} fields_deleted={}".format(
                        address,
                        timestamp_ms,
                        overwrite,
                        publish,
                        fields_updated,
                        fields_deleted,
                    )
                )

                try:
                    serialized = json.dumps(content, sort_keys=True)
                    size_bytes = len(serialized)
                except Exception:
                    serialized = str(content)
                    size_bytes = len(serialized)

                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|flush_states() Payload for address='{}' size={} bytes content={}".format(
                        address, size_bytes, serialized
                    )
                )
                self._flush_states(
                    address,
                    content,
                    overwrite=overwrite,
                    timestamp_ms=timestamp_ms,
                    publish_to_partner=publish,
                    fields_updated=fields_updated,
                    fields_deleted=fields_deleted,
                    sub_location=sub_location,
                )

        self.states_to_flush.clear()

    def _flush_states(
        self,
        address,
        json_content,
        overwrite=True,
        timestamp_ms=None,
        publish_to_partner=True,
        fields_updated=[],
        fields_deleted=[],
        sub_location=False,
    ):
        """
        Commit state variable content to the cloud
        :param address: Address of this state variable
        :param json_content: JSON content to flush to the cloud
        :param overwrite: True to overwrite all existing content, False to update existing server content only with the top-level dictionary keys that are presented leaving others untouched (default)
        :param timestamp_ms: For time-series state variables, fill in the timestamp in milliseconds.
        :param publish_to_partner: True or False to stream this state update to a partner cloud. Default is True, streaming enabled.
        :param fields_updated: To optimize integrations with 3rd party clouds, this is a list of the fields that were added/updated. Always used in conjunction with overwrite=True.
        :param fields_deleted: List of fields that were removed. Always used in conjunction with overwrite=True
        :param sub_location: True if this state is being saved to a sub-location
        """
        body = {"value": json_content}

        params = {
            "name": address,
            "overwrite": overwrite,
            "publish": publish_to_partner,
        }

        data = json.dumps(body)

        if timestamp_ms is None:
            # Non-time-series State Variable
            params["upd"] = fields_updated
            params["del"] = fields_deleted

            logger = self.get_logger(f"{'botengine'}.{__class__.__name__}")
            message = "|_flush_states() Saving {} bytes to state variable '{}'\n{}".format(
                len(data), address, json.dumps(body, sort_keys=True)
            )
            if isinstance(json_content, dict) and len(json_content) > 0:
                logger.debug(message)
            else:
                logger.debug(message)
            r = self._http_put(
                "/cloud/json/locations/{}/state".format(self.get_location_id()),
                params=params,
                data=data,
            )
            if r is not None:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|_flush_states() HTTP PUT state '{}' status_code={} reason={} payload_bytes={}".format(
                        address, r.status_code, r.reason, len(data)
                    )
                )
                try:
                    j = json.loads(r.text)
                    _check_for_errors(j)
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                        "|_flush_states() Server acknowledged state save '{}' result={}".format(
                            address, j
                        )
                    )
                    if not sub_location:
                        return
                    # Publish states to sub-type locations
                    locations = self.get_locations()
                    for location_access in locations:
                        location = location_access["location"]
                        if location.get("subType", 0) != 0:
                            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                                "|_flush_states() Publishing state '{}' to sub-type location ID {}".format(
                                    address, location["locationId"]
                                )
                            )
                            r = self._http_put(
                                "/cloud/json/locations/{}/state".format(
                                    location["locationId"]
                                ),
                                params=params,
                                data=data,
                            )
                            try:
                                j = json.loads(r.text)
                                _check_for_errors(j)
                                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                                    "|_flush_states() Server at sub-type location ID {} acknowledged state save '{}' result={}".format(
                                        location["locationId"], address, j
                                    )
                                )
                            except Exception as e:
                                self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                                    "|_flush_states() Error saving state content '{}' to sub-type location ID {}: {}".format(
                                        address, location["locationId"], e
                                    )
                                )
                except Exception as e:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|_flush_states() Error saving state content '{}': {}".format(
                            address, e
                        )
                    )

        else:
            # Time-series State Variable
            params["date"] = timestamp_ms

            self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                "|_flush_states() Saving {} bytes to state content '{}' at timestamp {}\n{}".format(
                    len(data), address, timestamp_ms, json.dumps(body, sort_keys=True)
                )
            )
            r = self._http_put(
                "/cloud/json/locations/{}/timeStates".format(self.get_location_id()),
                params=params,
                data=data,
            )
            if r is not None:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|_flush_states() HTTP PUT time-state '{}' timestamp_ms={} status_code={} reason={} payload_bytes={}".format(
                        address, timestamp_ms, r.status_code, r.reason, len(data)
                    )
                )
                try:
                    j = json.loads(r.text)
                    _check_for_errors(j)
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                        "|_flush_states() Server acknowledged time-series state save '{}' timestamp_ms={} result={}".format(
                            address, timestamp_ms, j
                        )
                    )
                except Exception as e:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                        "|_flush_states() Error saving time-series state content '{}': {}".format(
                            address, e
                        )
                    )

    def set_admin_content(self, organization_id, address, json_content, private=True):
        """
        Set administrator content. The content is expected to be JSON content.

        Note there are other API methods to upload images and other content by changing the Content-Type header if we ever need to support that.
        But JSON is expected here.
        https://iotadmins.docs.apiary.io/#reference/organizations/organization-large-objects/upload-large-object

        :param organization_id: Organization ID to save into
        :param address: Object name
        :param json_content: Content to store
        :param content_type: Content-Type header
        :param private: True if this is privately available to the organization. False to make it publicly accessible.
        """
        self._http_put(
            "/admin/json/organizations/{}/objects/{}".format(organization_id, address),
            params={"private": private},
            data=json.dumps(json_content),
        )

    def delete_admin_content(self, organization_id, address):
        """
        Delete administrator content.
        https://iotadmins.docs.apiary.io/#reference/organizations/organization-large-objects/delete-object
        :param organization_id: Organization ID to delete from
        :param address: Object name
        """
        self._http_delete(
            "/admin/json/organizations/{}/objects/{}".format(organization_id, address)
        )

    # ===========================================================================
    # Data Stream Messages
    # ===========================================================================
    def send_datastream_message(
        self,
        address,
        feed_dictionary,
        bot_instance_list=None,
        scope=1,
        location_id_list=None,
    ):
        """
        Send a Data Stream Message
        :param address: Data stream address
        :param feed_dictionary: Dictionary of key/value pairs to send to this data stream address
        :param bot_instance_list: Send data to specific list of bot instances.
        :param scope: Send the data stream message to - 1=Bots at a Location; 2=Bots in an Organization; 4=Bots in a Circle
        :param location_id_list: Send data to bots of the specific list of locations, used by Organizational Bots
        """
        if self.playback:
            return None

        params = {"address": address, "scope": scope}

        body = {"feed": feed_dictionary}

        if bot_instance_list is not None:
            body["bots"] = bot_instance_list

        if location_id_list is not None:
            body["locations"] = location_id_list

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|send_datastream_message() address={}; scope={}; bots={}: \n{}".format(
                address, scope, bot_instance_list, json.dumps(body, sort_keys=True)
            )
        )

        r = self._http_post("/analytic/stream", params=params, data=json.dumps(body))
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===========================================================================
    # Narrative
    # ===========================================================================
    def narrate(
        self,
        title=None,
        description=None,
        priority=None,
        icon=None,
        icon_font=None,
        status=None,
        timestamp_ms=None,
        narrative_type=NARRATIVE_TYPE_OBSERVATION,
        file_ids=None,
        extra_json_dict=None,
        event_type=None,
        update_narrative_id=None,
        update_narrative_timestamp=None,
        admin=False,
        publish_to_partner=None,
    ):
        """
        Narrate some activity
        :param title: Title of the event
        :param description: Description of the event
        :param priority: 0=debug; 1=info; 2=warning; 3=critical
        :param icon: Icon name, like 'motion' or 'phone-alert'. See http://peoplepowerco.com/icons and http://fontawesome.com
        :param icon_font: Icon font type. Please see the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
        :param status: Status of the narrative. 0=initial; 1=deleted; 2=resolved; 3=reopened
        :param timestamp_ms: Optional timestamp for this event. Can be in the future. If not set, the current timestamp is used.
        :param narrative_type: See botengine.NARRATIVE_TYPE_*
        :param file_ids: List of file ID's (media) to reference and show as part of the record in the UI
        :param extra_json_dict: Any extra JSON dictionary content we want to communicate with the UI
        :param event_type: Unique identifier for partner clouds to understand this narrative.
        :param update_narrative_id: Specify a narrative ID to update an existing record.
        :param update_narrative_timestamp: Specify a narrative timestamp to update an existing record. This is a double-check to make sure we're not overwriting the wrong record.
        :param admin: True to alert an administrator; False (default) to deliver to the end user.
        :param publish_to_partner: Set to False to avoid streaming this narrative to partner clouds (default is always True)
        :return: { "narrativeId": id, "narrativeTime": timestamp_ms } if successful, otherwise None.
        """
        if self.playback:
            return None

        narrative = {}

        location_id = self.get_location_id()

        if priority is not None:
            narrative["priority"] = priority

        if icon is not None:
            narrative["icon"] = icon

        if icon_font is not None:
            narrative["iconFont"] = icon_font

        if title is not None:
            narrative["title"] = title

        if description is not None:
            narrative["description"] = description

        if status is not None:
            narrative["status"] = status

        if timestamp_ms is not None:
            narrative["narrativeTime"] = timestamp_ms

        if narrative_type is not None:
            if self.is_server_version_newer_than(1, 29):
                narrative["narrativeType"] = narrative_type

        target = {}

        if file_ids is not None:
            target["fileIDs"] = file_ids

        if extra_json_dict is not None:
            target.update(extra_json_dict)

        if len(target) > 0:
            narrative["target"] = target

        params = {}

        if update_narrative_id is not None:
            params["narrativeId"] = update_narrative_id

        if update_narrative_timestamp is not None:
            params["narrativeTime"] = update_narrative_timestamp

        if admin:
            params["scope"] = 2
        else:
            params["scope"] = 1

        # New server features to stream narratives to partner clouds
        if self.is_server_version_newer_than(1, 22):
            if publish_to_partner is not None:
                params["publish"] = publish_to_partner

            if event_type is not None:
                narrative["eventType"] = event_type

        body = {"narrative": narrative}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|narrate() body: \n{}".format(json.dumps(narrative, sort_keys=True))
        )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|narrate() params: {}".format(json.dumps(params, sort_keys=True))
        )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|narrate() PUT URL: {}".format(
                "/cloud/json/locations/{}/narratives".format(location_id)
            )
        )

        r = self._http_put(
            "/cloud/json/locations/{}/narratives".format(location_id),
            params=params,
            data=json.dumps(body),
        )
        j = json.loads(r.text)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|narrate() response: \n{}".format(json.dumps(j, sort_keys=True))
        )

        if "narrativeTime" in j:
            # Working around an issue with the server where the narrativeId sometimes isn't returned
            if "narrativeId" in j:
                narrativeId = j["narrativeId"]
            else:
                narrativeId = update_narrative_id

            if narrativeId is not None:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                    "|narrate() Narrative {}: title={}; description={}; priority={}".format(
                        narrativeId, title, description, priority
                    )
                )
                return {"narrativeId": narrativeId, "narrativeTime": j["narrativeTime"]}

        return None

    # ===========================================================================
    # Fall Event Feedback
    # ===========================================================================

    def send_fall_event_feedback(
        self, device_id, classification, event_timestamp, comment
    ):
        """
        Send Fall Event Feedback

        :param device_id: Device ID
        :param classification: Classification of the fall event. One of TRUE_POSITIVE, FALSE_POSITIVE, FALSE_NEGATIVE, TEST_FALL
        :param event_timestamp: Timestamp of the fall event
        :param comment: Comment
        :return: JSON response from Care Daily API
        """
        if self.playback:
            return None

        body = {
            "deviceId": device_id,
            "classification": classification,
            "eventTimestamp": event_timestamp,
            "comment": comment,
        }

        r = self._http_post("/analytic/fallFeedback", data=json.dumps(body))
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===========================================================================
    # Open AI
    # ===========================================================================

    def send_request_for_chat_completion(self, key, data, openai_organization_id=None):
        """
        Send asynchronous request to Open AI API to obtain a model response for the given chat conversation.
        :param key: Key to identify this request
        :param data: Parameters to send to the Open AI API
        :param openai_organization_id: Organization ID to use for the Open AI API. Default is None.
        :return: JSON response from Care Daily API
        """
        if self.playback:
            return None
        params = {"key": key}
        if openai_organization_id is not None:
            params["organizationId"] = openai_organization_id
        r = self._http_post("/analytic/openai", params=params, data=json.dumps(data))
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===========================================================================
    # AI
    # ===========================================================================

    def send_a_request_to_a_model(self, model_name, key, data):
        """
        Send asynchronous request to an AI model to obtain a model response for the given data.
        There are 2 types of AI applications:

            - The first type uses the LLama model and provides simple text completion or chat completion.
            - The second type uses the SetFit model and calculates phrase scoring (probabilities of scores 0,1,2).

        The type of AI application is determined automatically by its unique name.
        The response from AI application is delivered to the bot in a data stream message to the address "ai".

        :param model_name: Model ID to use for the AI model
        :param key: Key to identify this request
        :param data: Parameters to send to the AI model
        :return: JSON response from Care Daily API
        """
        if self.playback:
            return None
        params = {
            "name": model_name,
            "key": key,
        }
        r = self._http_post("/analytic/ai", params=params, data=json.dumps(data))
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===========================================================================
    # Narratives
    # ===========================================================================

    def delete_narration(self, narrative_id, narrative_timestamp):
        """
        Delete a narrative record
        :param location_id: Location ID
        :param narrative_id: ID of the record to delete
        :param narrative_timestamp: Timestamp of the record to delete
        :return:
        """
        params = {"narrativeId": narrative_id, "narrativeTime": narrative_timestamp}

        r = self._http_delete(
            "/cloud/json/locations/{}/narratives".format(self.get_location_id()),
            params=params,
        )
        j = json.loads(r.text)
        return j

    def get_narration(self, narrative_id, admin=False):
        """
        Get narrative content for updating or inspection

            {
              "appInstanceId": 3528,
              "creationDate": "2019-09-04T18:45:25-07:00",
              "creationDateMs": 1567647925000,
              "description": "This is a test",
              "icon": "grimace",
              "id": 11247,
              "locationId": 236520,
              "narrativeDate": "2019-09-04T18:45:25-07:00",
              "narrativeDateMs": 1567647925000,
              "priority": 3,
              "status": 0,
              "title": "Testing"
            }

        :param narrative_id: Narrative ID to retrieve
        :return: Narrative content, or None if it doesn't exist.
        """
        params = {"narrativeId": narrative_id}

        if admin:
            params["scope"] = 2
        else:
            params["scope"] = 1

        r = self._http_get(
            "/cloud/json/locations/{}/narratives".format(self.get_location_id()),
            params=params,
        )
        j = json.loads(r.text)

        if "narratives" in j:
            if len(j["narratives"]) > 0:
                return j["narratives"][0]

        return None

    # ===========================================================================
    # Inject Synthetic Device Parameters
    # ===========================================================================
    def form_parameter(self, name, value, index=None):
        """
        This method will form a single parameter.

        You can pass in parameter name / optional index / value pairs and it will
        generate a dictionary to represent this parameter. This is a shortcut to send
        multiple commands with the inject_parameters() method.

        Append multiple commands into a list and then use inject_parameters(..) to send them all.

        All parameters will gain a prefix of "syn." for "synthetic data".

        :param name: The name of the parameter to configure.
        :param value: The value to set for this parameter.
        :param index: Optional index number / letters. Default is None.
        """
        if not name.startswith("syn."):
            name = "syn." + name

        param = {"name": name, "value": value}

        if index:
            param["index"] = index

        return param

    def inject_parameters(self, device_id, parameters_list, timestamp_ms=None):
        """
        Inject a list of synthetic parameters into the device history for this device

        :param device_id: Device ID
        :param parameters_list: List of parameters to inject. You can use the form_parameter() method to create each element in the list.
        :param timestamp_ms: Optional timestamp in milliseconds for these parameters
        """
        body = {"params": parameters_list}

        if timestamp_ms is not None:
            body["timestamp"] = timestamp_ms
        else:
            body["timestamp"] = self.get_timestamp()

        r = self._http_post(
            "/analytic/devices/{}/parameters".format(device_id), data=json.dumps(body)
        )
        j = json.loads(r.text)
        _check_for_errors(j)

    # ===========================================================================
    # Device Models and OOBE's
    # ===========================================================================
    def get_device_models(self, brand, model_id):
        """
        Get device models
        :param brand: Brand name
        :param model_id: Model ID
        :return: JSON or None if it doesn't exist
        """
        params = {"modelId": model_id, "brand": brand}

        r = self._http_get("/cloud/json/devicemodels", params=params)
        j = json.loads(r.text)

        if "categories" in j:
            return j["categories"]

        return None

    # ===========================================================================
    # Organizational Bots
    # ===========================================================================
    def create_challenge_from_template(
        self, challenge_name, start_timestamp_ms, end_timestamp_ms, parent_template_id
    ):
        """
        Create a challenge
        :param challenge_name: Name of this challenge
        :param start_timestamp_ms: Start timestamp in milliseconds
        :param end_timestamp_ms: End timestamp in milliseconds
        :param parent_template_id: Challenge or template ID to copy settings from. When a challenge is created using a template, all the attributes which are not explicitly specified will be copied from the template.
        :return: JSON response dictionary with "challengeId" key of the challenge ID that was created
        """
        if "organization" not in self.inputs:
            return

        params = {"parentId": parent_template_id}

        from dateutil.tz import tzlocal

        challenge = {
            "challenge": {
                "name": challenge_name,
                "startDate": datetime.datetime.fromtimestamp(
                    int(start_timestamp_ms / 1000), tzlocal()
                ).isoformat(),
                "endDate": datetime.datetime.fromtimestamp(
                    int(end_timestamp_ms / 1000), tzlocal()
                ).isoformat(),
            }
        }

        r = self._http_post(
            "/admin/json/organizations/"
            + str(self.inputs["organization"]["organizationId"])
            + "/challenges",
            params=params,
            data=json.dumps(challenge),
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_organization_challenge_participants(
        self,
        challenge_id,
        status=None,
        user_id=None,
        get_devices=None,
        device_category=None,
    ):
        """
        Get information about the participants of the challenge.
        This is accessible to Organizational Bots only.

        :param challenge_id: Challenge ID
        :param status: Participation status filter: 1=Not Responded; 2=Opt-in; 3=Opt-out
        :param user_id: Filter the response by user ID.
        :param get_devices: True or False. Return user devices as well.
        :param device_category: Filter devices by this category.
        """
        if "organization" not in self.inputs:
            return

        params = {}
        if status:
            params["status"] = status

        if user_id:
            params["userId"] = user_id

        if get_devices:
            params["getDevices"] = get_devices

        if device_category:
            params["deviceCategory"] = device_category

        r = self._http_get(
            "/analytic/admin/challenges/" + str(challenge_id) + "/participants",
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_organization_groups(
        self,
        group_id=None,
        group_name=None,
        group_type=None,
        get_user_totals=False,
        get_average_bills=False,
        bill_start_date=None,
    ):
        """
        Get the groups in this organization.
        This is accessible to Organizational Bots only.

        :param group_id: Integer - Search by group ID
        :param group_name: String - Search by the first characters of a group name
        :param group_type: Integer - Search by group type. 0 = Residential; 1 = Business
        :param get_user_totals: Boolean - True to request the total approved, applied, and rejected users in this group
        :param get_average_bills: Boolean - True to request the average monthly energy bill information for a specific group ID.
        :param bill_start_date: Xsd:dateTime string - return monthly bills from the given start date
        :return: Dictionary
        """
        if "organization" not in self.inputs:
            return

        params = {}
        if group_id:
            params["groupId"] = group_id

        if group_name:
            params["name"] = group_name

        if group_type:
            params["type"] = group_type

        if get_user_totals:
            params["userTotals"] = get_user_totals

        if get_average_bills:
            params["averageBills"] = get_average_bills

        if bill_start_date:
            params["billsStartDate"] = bill_start_date

        r = self._http_get(
            "/admin/json/organizations/"
            + str(self.inputs["organization"]["organizationId"])
            + "/groups",
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_organization_users(
        self,
        group_id=None,
        status=None,
        search_by=None,
        search_tag=None,
        search_device_tag=None,
        points_from=None,
        points_to=None,
        limit=None,
        get_tags=False,
    ):
        """
        Get users in this organization.
        This is accessible to Organizational Bots only.

        :param group_id: Search by group ID
        :param status: String - Search for users with a specific status. 0=Applied; 1=Approved; -1=Rejected; -2=Opted Out
        :param search_by: String - Search for matching user login names, first name, last name, and email address. Use * for wildcard.
        :param search_tag: String - Search by user tag
        :param search_device_tag: String - Search by device tag
        :param points_from: Integer - Get users who have more points than this amount
        :param points_to: Integer - Get users who have less points than this amount
        :param limit: Integer - the maximum number of user records to retrieve in this request
        :param get_tags: Boolean - Return user tags
        :return: Dictionary
        """
        if "organization" not in self.inputs:
            return

        params = {}
        if group_id:
            params["groupId"] = group_id

        if status:
            params["organizationStatus"] = status

        if search_by:
            params["searchBy"] = search_by

        if search_tag:
            params["searchTag"] = search_tag

        if search_device_tag:
            params["searchDeviceTag"] = search_device_tag

        if points_from:
            params["pointsFrom"] = points_from

        if points_to:
            params["pointsTo"] = points_to

        if limit:
            params["limit"] = limit

        if get_tags:
            params["getTags"] = get_tags

        r = self._http_get(
            "/admin/json/organizations/"
            + str(self.inputs["organization"]["organizationId"])
            + "/users",
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    def get_organization_devices(
        self,
        linked_to=1,
        group_id=None,
        user_id=None,
        location_id=None,
        tree=None,
        device_types_list=None,
        search_by=None,
        search_tag=None,
        last_update_date_older_than=None,
        last_update_date_newer_than=None,
        param_name=None,
        param_value=None,
        limit=None,
        get_tags=None,
    ):
        """
        Get devices in this organization.
        This is accessible to Organizational Bots only.

        :param linked_to: Integer - Request devices linked to 1=Users; 2=Locations; 3=Users&Locations
        :param group_id: Integer - Group ID to search within
        :param user_id: Integer - Filter by User ID
        :param location_id: Integer - Filter by Location ID
        :param tree: Boolean - True to retrieve devices from sub-locations as well
        :param device_types_list: List of Integers - Filter by these device types
        :param search_by: String - Search by device ID or description
        :param search_tag: String - Search by device tag
        :param last_update_date_older_than: Xsd:dateTime string - Request devices where the last update date is older than this
        :param last_update_date_newer_than: Xsd:dateTime string - Request devices where the last update date is newer than this
        :param param_name: String - Request devices that sent this parameter name to the cloud
        :param param_value: String - Requested parameter value
        :param limit: Integer - Limit the response size by this number
        :param get_tags: Boolean - True to return device tags
        :return: Dictionary
        """
        if "organization" not in self.inputs:
            return

        params = {}

        if linked_to:
            params["linkedTo"] = linked_to

        if group_id:
            params["groupId"] = group_id

        if user_id:
            params["userId"] = user_id

        if location_id:
            params["locationId"] = location_id

        if tree:
            params["tree"] = tree

        if device_types_list:
            params["deviceType"] = device_types_list

        if search_by:
            params["searchBy"] = search_by

        if search_tag:
            params["searchTag"] = search_tag

        if last_update_date_older_than:
            params["lessUpdateDate"] = last_update_date_older_than

        if last_update_date_newer_than:
            params["moreUpdateDate"] = last_update_date_newer_than

        if param_name:
            params["paramName"] = param_name

        if param_value:
            params["paramValue"] = param_value

        if limit:
            params["limit"] = limit

        if get_tags:
            params["getTags"] = get_tags

        r = self._http_get(
            "/admin/json/organizations/"
            + str(self.inputs["organization"]["organizationId"])
            + "/devices",
            params=params,
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        return j

    # ===============================================================================
    # Analytics add-on - include analytics.py in your bot
    # ===============================================================================
    def flush_analytics(self):
        """
        If you have included an analytics.py in the base bot directory, this will attempt
        to call the analytics.flush(botengine) method as the bot is exiting execution.

        You can then connect your analytics to whatever analytics platform you prefer.
        """
        try:
            import analytics  # type: ignore

            analytics.get_analytics(self, must_exist=True).flush(self)

        except ImportError:
            return

    # ===========================================================================
    # Customer Support Tickets
    # ===========================================================================
    def request_customer_support(
        self, ticket_type, ticket_priority, subject, comment, data=None, custom_fields=None, brand="default", user_id=None, template="", language=None, voip_call=None
    ):
        """
        Request customer support via ZenDesk
        :param ticket_type: botengine.TICKET_TYPE_*
        :param ticket_priority: botengine.TICKET_PRIORITY_*
        :param subject: Subject line
        :param comment: Comment to customer support
        :param data: Additional data to send to customer support
        :param custom_fields: Additional custom fields to send to customer support
        :param brand: Brand name
        :param user_id: User ID
        :param template: Velocity template name.  Default is "comment.vm"
        :param language: Language code. Default is "en"
        :param voip_call: Provide a VoIP link in ticket (if service is available)
        :return:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(">request_customer_support()")
        if self.playback:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                "<request_customer_support() ticket_type={}, ticket_priority={}, subject={}, comment={}, data={}, custom_fields={}, brand={}, user_id={}, template={}, language={}, voip_call={}".format(
                    ticket_type, ticket_priority, subject, comment, data, custom_fields, brand, user_id, template, language, voip_call
                )
            )
            return

        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|request_customer_support() ticket_type={}, ticket_priority={}, subject={}, comment={}, data={}, custom_fields={}, brand={}, user_id={}, template={}, language={}, voip_call={}".format(
                ticket_type, ticket_priority, subject, comment, data, custom_fields, brand, user_id, template, language, voip_call
            )
        )

        import properties
        allowed = properties.get_property(self, "ZENDESK_TICKET_CREATION_ALLOWED", complain_if_missing=False)
        if not allowed:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<request_customer_support() Ticket creation not allowed by domain or oganization")
            return

        body = {
            "ticket": {
                "type": ticket_type,
                "priority": ticket_priority,
                "subject": "Location {} - {}".format(self.get_location_id(), subject),
                "comment": comment,
            },
        }
        if data:
            body["ticket"]["data"] = data
        if custom_fields:
            body["ticket"]["customFields"] = custom_fields
        if brand:
            body["brand"] = brand
        if user_id:
            body["userId"] = user_id
        if template:
            body["template"] = template
        if language:
            body["lang"] = language
        if voip_call:
            body["voipCall"] = voip_call

        r = self._http_post("/analytic/ticket", data=json.dumps(body))
        j = json.loads(r.text)
        _check_for_errors(j)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info("<request_customer_support()")
        return

    # ===========================================================================
    # Cloud API for EngageKit
    # ===========================================================================
    def get_cloud_message_topics(self):
        """
        Get a list of message topics
        :return: A list of message topics
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">get_cloud_message_topics()"
        )
        params = {}
        params["appId"] = self.get_bot_instance_id()

        params["lang"] = self.get_language()

        headers = {"Content-Type": "application/json"}

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|get_cloud_message_topics() params={}".format(params)
        )
        r = self._http_get("/cloud/json/messageTopics", params=params, headers=headers)
        j = json.loads(r.text)
        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<get_cloud_message_topics() response={}".format(j)
        )
        return j

    def update_cloud_message_topics(self, topics):
        """
        Create message topics if they don't exist and update the list of topics for the specified bot.
        :param topics: List of topics
        :return:
        """

        params = {}
        params["bundle"] = self.get_bundle_id()

        headers = {"Content-Type": "application/json"}

        j = json.dumps(topics)

        r = self._http_put(
            "/cloud/json/messageTopics", params=params, data=j, headers=headers
        )

        j = json.loads(r.text)

        _check_for_errors(j)
        return j

    def create_cloud_messages(self, messages_json=None, by_user: bool = False):
        """
        Create new cloud messages at a location.
        :param location_id: The location ID if created by user
        :param messages_json: The messages json content
        :return:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">create_cloud_messages()"
        )
        if messages_json is None:
            messages_json = {}
        params = {}
        if by_user is True:
            params["locationId"] = self.get_location_id()

        headers = {"Content-Type": "application/json"}
        j = json.dumps(messages_json)

        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|create_cloud_messages() params={} data={}".format(params, j)
        )

        r = self._http_post(
            "/cloud/json/messages", params=params, data=j, headers=headers
        )
        j = json.loads(r.text)
        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<create_cloud_messages() response={}".format(j)
        )
        return j

    def update_cloud_messages(self, messages_json):
        """
        AI bots can update message statuses and schedule delivery time.
        :param messages_json: The messages json content
        :return:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">update_cloud_messages()"
        )
        headers = {"Content-Type": "application/json"}
        j = json.dumps(messages_json)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|update_cloud_messages() data={}".format(j)
        )
        r = self._http_put("/cloud/json/messages", data=j, headers=headers)
        j = json.loads(r.text)

        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<update_cloud_messages() response={}".format(j)
        )
        return j

    def get_cloud_messages(self, start_date_ms, end_date_ms, topic_id, read_status):
        """
        Get messages from a location
        :param start_date_ms: The start date in milliseconds
        :param end_date_ms: The end date in milliseconds
        :param topic_id: The topic ID
        :param read_status: The read status
        :return: Messages JSON
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">get_cloud_messages()"
        )
        params = {}
        params["locationId"] = self.get_location_id()
        params["startDate"] = start_date_ms
        params["end_date_ms"] = end_date_ms
        params["instance"] = self.get_bot_instance_id()
        params["topic_id"] = topic_id
        params["read_status"] = read_status

        headers = {"Content-Type": "application/json"}
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|get_cloud_messages() params={}".format(params)
        )
        r = self._http_get("/cloud/json/messages", params=params, headers=headers)
        j = json.loads(r.text)

        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<get_cloud_messages() response={}".format(j)
        )
        return j

    def update_cloud_message_read_status(self, message_id, read_status):
        """
        Update message read status
        :param message_id: The message ID
        :param read_status: The read status
        :return:
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            ">update_cloud_message_read_status()"
        )
        params = {}
        params["locationId"] = self.get_location_id()
        params["messageId"] = message_id
        params["readStatus"] = read_status

        headers = {"Content-Type": "application/json"}
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "|update_cloud_message_read_status() params={}".format(params)
        )
        r = self._http_put(
            "/cloud/developer/messageRead", params=params, headers=headers
        )
        j = json.loads(r.text)

        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
            "<update_cloud_message_read_status() response={}".format(j)
        )
        return j

    # ===========================================================================
    # Surveys
    # ===========================================================================
    def send_survey_notification(self, survey_key, location_id, user_id=None, role=None, send_to_user=None, notification_category=None):
        """
        Send a survey notification to a user, role, or notification category.

        :param survey_key: Key of the survey to answer (string)
        :param location_id: Answer a survey for this location (integer)
        :param user_id: Answer a survey for specific user (integer, optional)
        :param role: Answer a survey for users with this role on the location (integer, optional)
        :param send_to_user: Send the email directly to the user (boolean, optional)
        :param notification_category: Send the email to organization notification user with this category (integer, optional)
        :return: Response JSON from server
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(">send_survey_notification()")
        params = {
            "locationId": location_id,
            "surveyKey": survey_key
        }
        if user_id is not None:
            params["userId"] = user_id
        if role is not None:
            params["role"] = role
        if send_to_user is not None:
            params["sendToUser"] = send_to_user
        if notification_category is not None:
            params["notificationCategory"] = notification_category

        headers = {"Content-Type": "application/json"}
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"|send_survey_notification() params={params}")

        r = self._http_post("/cloud/json/surveyNotification", params=params, headers=headers)
        j = json.loads(r.text)

        _check_for_errors(j)
        self.get_logger(f"{'botengine'}.{__class__.__name__}").info(f"<send_survey_notification() response={j}")
        return j

    # ===========================================================================
    # Tools
    # ===========================================================================
    @staticmethod
    def _strftimestamp(ts):
        """This private method will convert the time in seconds to the string of IOS-8601 format, eg: '2014-06-20T12:47:11-07:00

        :param ts: the time in seconds, eg: 1403293631
        """
        t = datetime.datetime.fromtimestamp(ts)
        return t.astimezone().isoformat()

    @staticmethod
    def strftimestamp(ts):
        """This method will convert the time in milliseconds to the string of IOS-8601 format, eg: '2014-06-20T12:47:11-07:00

        :param ts: the time in seconds, eg: 1403293631000
        """
        response = BotEngine._strftimestamp(ts // 1000)
        return response

    @staticmethod
    def strftime(dt):
        """This method will convert the datetime object to the string of IOS-8601 format, eg: '2014-06-20T12:47:11-07:00

        :param dt: the datetime object
        """
        # pattern = "%Y-%m-%dT%H:%M:%S%Z"
        response = BotEngine._strftimestamp(dt.timestamp() // 1)
        return response

    @staticmethod
    def strptime(dt_str):
        """This method will convert the string of IOS-8601 to the datetime object

        :param dt_str: the string of IOS-8601 format (eg: '2014-06-20T12:47:11-07:00)
        """
        from dateutil.parser import parse

        response = parse(dt_str)
        return response

    @staticmethod
    def get_logger(service="botengine"):
        global _bot_loggers
        global _bot_logger_config
        if _bot_logger_config is None:
            print("XXXXXXXXXxxx BotEngine.get_logger(): Logger config is None!")
            # Lambda logging is maintained by a single logging instance
            lambda_logger = _bot_loggers["botengine"]
            # Assign the service to be described in logs
            lambda_logger.service = service
            return lambda_logger
        name = service
        # Logging name is prefixed with bundle ID to support multi-bot playback
        bundle_id = _bot_logger_config.get("bundle_id")
        if bundle_id:
            name = "{}.{}".format(bundle_id, service)
        if name not in _bot_loggers:
            _bot_loggers[name] = _create_logger(name, **_bot_logger_config)
        return _bot_loggers[name]

    def get_secret_value(self, secret_name):
        """
        A bot instance can request a secret value defined by the developers team
        :param secret_name: Name of this secret
        :return: optional string secret.
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            ">get_secret_value() {}".format(secret_name)
        )
        try:
            params = {"secretName": secret_name}
            r = self._http_get("/analytic/secrets", params=params)
            j = json.loads(r.text)
            _check_for_errors(j)
            if "secretValue" in j:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "<get_secret_value() secretValue=***"
                )
                return j["secretValue"]
        except Exception as e:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|get_secret_value() Failed to retrieve secret '{}': {}".format(
                    secret_name, e
                )
            )
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "<get_secret_value() No secret found"
        )
        return None

    # AWS Secrets Manager
    def get_secret(self, secret_name, region_name="us-east-1"):
        """
        Retrieve a secret from AWS Secrets Manager

        :param secret_name: Name of this secret
        :param region_name: AWS region. default "us-east-1"
        :return: optional json secret. i.e., {"appname": "some", "appsecret": "thing"}
        """
        self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
            "|get_secret() {} {}".format(secret_name, region_name)
        )

        secret = None

        try:
            if False:  # Caching
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|get_secret() Prefer caching"
                )
                import botocore
                import botocore.session
                from aws_secretsmanager_caching import SecretCache, SecretCacheConfig

                client = botocore.session.get_session().create_client("secretsmanager")
                cache_config = SecretCacheConfig()
                cache = SecretCache(config=cache_config, client=client)

                secret = cache.get_secret_string("mysecret")

            else:  # No caching
                self.get_logger(f"{'botengine'}.{__class__.__name__}").debug(
                    "|get_secret() Prefer no caching"
                )
                import boto3
                from botocore.exceptions import ClientError

                # Create a Secrets Manager client
                session = boto3.session.Session()
                client = session.client(
                    service_name="secretsmanager", region_name=region_name
                )

                try:
                    self.get_logger(f"{'botengine'}.{__class__.__name__}").info(
                        "|get_secret() Retrieving secret '{}'".format(
                            secret_name
                        )
                    )
                    get_secret_value_response = client.get_secret_value(
                        SecretId=secret_name
                    )
                except ClientError as e:
                    # For a list of exceptions thrown, see
                    # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
                    raise e

                # Decrypts secret using the associated KMS key.
                secret = get_secret_value_response["SecretString"]

            # Your code goes here.
            if secret is None:
                self.get_logger(f"{'botengine'}.{__class__.__name__}").warning(
                    "|get_secret() Missing secret '{}'.".format(secret_name)
                )

        except Exception as e:
            self.get_logger(f"{'botengine'}.{__class__.__name__}").error(
                "|get_secret() Failed to retrieve secret '{}': {}".format(
                    secret_name, e
                )
            )

        return secret