'''
Created on July 12, 2016

@author: David Moss
'''

import logging
import time

# States
STATE_AWAKE = 0
STATE_GOING_TO_SLEEP = 1
STATE_SLEEPING = 2
STATE_WAKING_UP_SOON = 3
DATA_LAST_MOVEMENT_RH = -1
DATA_SLEEP_DURATION_MS = -2

# Logging
LOG_LEVEL=logging.INFO

# Name of our core variable
CORE_VARIABLE_NAME = "-core-"

class BotEnginePyTest:
    # You can override this with your own class to validate access or return responses.

    # Trigger Types
    TRIGGER_UNPAUSED = 0
    TRIGGER_SCHEDULE = 1
    TRIGGER_MODE = 1 << 1
    TRIGGER_DEVICE_ALERT = 1 << 2
    TRIGGER_DEVICE_MEASUREMENT = 1 << 3
    TRIGGER_QUESTION_ANSWER = 1 << 4
    TRIGGER_DEVICE_FILES = 1 << 5
    TRIGGER_TIMER = 1 << 6
    TRIGGER_METADATA = 1 << 7
    TRIGGER_DATA_STREAM = 1 << 8
    TRIGGER_COMMAND_RESPONSE = 1 << 9
    TRIGGER_LOCATION_CONFIGURATION = 1 << 10
    TRIGGER_DATA_REQUEST = 1 << 11

    # Access category types
    ACCESS_CATEGORY_MODE = 1
    ACCESS_CATEGORY_FILE = 2
    ACCESS_CATEGORY_PROFESSIONAL_MONITORING = 3
    ACCESS_CATEGORY_DEVICE = 4
    ACCESS_CATEGORY_CHALLENGE = 5

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
    NARRATIVE_PRIORITY_ANALYTIC = -1
    NARRATIVE_PRIORITY_DEBUG = 0
    NARRATIVE_PRIORITY_DETAIL = 0
    NARRATIVE_PRIORITY_INFO = 1
    NARRATIVE_PRIORITY_WARNING = 2
    NARRATIVE_PRIORITY_CRITICAL = 3

    # Narrative types
    # High-frequency 'observation' entries for explainable AI and accountability
    NARRATIVE_TYPE_OBSERVATION = 0

    # Low-frequency 'journal' entries for SUMMARIZED exec-level communications to humans
    NARRATIVE_TYPE_JOURNAL = 4

    # High-frequency 'journal' entries for real-time CRITICAL exec-level communications to humans
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

    def __init__(self, inputs={}):
        """Constructor"""
        self.inputs = inputs
        self.logger = self.create_logger()
        self.reset()


    def reset(self):
        """Reset all the flags that let us know how this class was accessed during testing"""
        self.notify_called = False
        self.command_sent = False
        self.professional_monitoring_called = False
        self.admin_mail_notified = False
        self.mode = "HOME"
        self.execute_again_seconds = 0
        self.execute_again_timestamp = 0
        self.playback = False
        self.notify_message = None
        self.customer_support_body = None
        self.customer_support_comments = []

        import time
        self.time_ms = int(time.time() * 1000)

        # Created tags
        self.user_tags = []
        self.device_tags = []
        self.location_tags = []
        self.file_tags = []

        # Deleted tags
        self.deleted_user_tags = []
        self.deleted_device_tags = []
        self.deleted_location_tags = []
        self.deleted_file_tags = []

        # Professional monitoring
        self.has_pro_monitoring = True
        self.professional_monitoring_raised = False
        self.professional_monitoring_code = None
        self.professional_monitoring_message = None
        self.professional_monitoring_device_id = None
        self.professional_monitoring_cancelled = False

        # Location settings
        self.location_category = None
        self.location_rank = None
        self.location_comment = None

        # Spaces
        self.spaces = {}

        # States
        self.states = {}

        # Users
        self.users = []

        # Device properties
        self.device_properties = {}

        # Questions
        self.questions = {}

        self.pro_monitoring_status = {
            "callCenter": {
                "status": self.PROFESSIONAL_MONITORING_REGISTERED,
                "alertStatus": 3,
                "alertDate": "2015-09-01T18:00:00Z",
                "alertDateMs": 1441130400000,
                "alertStatusDate": "2015-09-01T18:00:30Z",
                "alertStatusDateMs": 1441130430000
            }
        }

        # Placeholder for users of this location
        self.resident_user_names = [
            {
                'firstName': 'Resident',
                'lastName': 'One'
            },
            {
                'firstName': 'Resident',
                'lastName': 'Two'
            }
        ]

        self.supporter_user_names = [
            {
                'firstName': 'Supporter',
                'lastName': 'One'
            },
            {
                'firstName': 'Supporter',
                'lastName': 'Two'
            }
        ]

        # Last data stream message that was attempted to be sent
        self.datastream = {}

        # Timers dictionary by reference
        self.timers = {}

        # Alarms dictionary by reference
        self.alarms = {}

        self.variables = {}

        self.location_block = self.get_location_block()

        self.status = {
            "callCenter": {
                "alertDateMs": 0,
                "alertStatus": 0,
                "alertStatusDateMs": 0,
                "status": 3
            }
        }

        self.organization_properties = {}
        self.all_trigger_types = []

        # True if this bot is being executed with previously recorded data
        self.playback = True

        # What is this bot's instance ID
        self.bot_instance_id = 0

        # Is this bot executing locally on a developer laptop
        self.local = False

        # How many times has this bot been run locally
        # Enabling us to know if it's the first run and a new_version() should be triggered, or gather stats if we want.
        self.local_execution_count = None

    #============================================================================
    # Loggers
    #============================================================================
    def create_logger(self):
        """Create a logger"""
        logger = logging.getLogger('app')

        if not logger.handlers:
            # Create a console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(LOG_LEVEL)
            console_handler.setFormatter(logging.Formatter(fmt="%(levelname)-8s %(message)s"))

            # Create a blank line handler
            blank_handler = logging.StreamHandler()
            blank_handler.setLevel(LOG_LEVEL)
            blank_handler.setFormatter(logging.Formatter(fmt=''))

            # Configure the logger
            logger.setLevel(LOG_LEVEL)
            logger.addHandler(console_handler)

            # Add handlers
            logger.console_handler = console_handler
            logger.blank_handler = blank_handler

        return logger

    def get_logger(self):
        return self.logger

    def log(self, message, num_of_blank_lines=1):
        """Log with blank lines before the message"""
        logger = self.logger

        # Switch the handler, output blank lines
        logger.removeHandler(logger.console_handler)
        logger.addHandler(logger.blank_handler)
        for _ in range(num_of_blank_lines):
            logger.info('')

        # Switch back
        logger.removeHandler(logger.blank_handler)
        logger.addHandler(logger.console_handler)
        logger.info(message)
        

    #============================================================================
    # Inputs
    #============================================================================
    def get_inputs(self):
        self.logger.debug(">get_inputs()")

        response = self.inputs

        self.logger.debug("<get_inputs() response=" + str(response))
        return response

    def set_inputs(self, inputs):
        self.inputs = inputs
        

    #============================================================================
    # Triggers
    #============================================================================
    def set_trigger_type(self, trigger_type):
        self.inputs['trigger'] = trigger_type

    def get_trigger_type(self):
        """This method will return the type of trigger"""
        if 'trigger' in self.inputs:
            return int(self.inputs['trigger'])

        return BotEnginePyTest.TRIGGER_SCHEDULE

    def get_trigger_info(self):
        """This method will find and return the information about what triggered this app."""
        try:
            accessBlock = self.inputs['access']
        except KeyError:
            self.logger.debug("<get_trigger_info")
            return None

        triggerBlock = None

        for block in accessBlock:
            try:
                if block['trigger']:
                    triggerBlock = block
                    break
            except KeyError:
                pass

        self.logger.debug("<get_trigger_info")
        return triggerBlock
    
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
        if 'access' not in self.inputs:
            return []

        self.trigger_blocks = []

        for block in self.inputs['access']:
            if 'trigger' in block:
                if block['trigger']:
                    self.trigger_blocks.append(block)

        return self.trigger_blocks

    #============================================================================
    # Blocks
    #============================================================================
    def get_measures_block(self):
        """Return the measurements block from our inputs, if any"""
        if 'measures' in self.inputs:
            return self.inputs['measures']

        return None

    def get_alerts_block(self):
        """Return the alerts block from our inputs, if any"""
        if 'alerts' in self.inputs:
            return self.inputs['alerts']

        return None

    def get_access_block(self):
        """Return the access block from our inputs, if any"""
        if 'access' in self.inputs:
            return self.inputs['access']

        return None

    def get_datastream_block(self):
        """
        :return: the data stream inputs, if any
        """
        if 'dataStream' in self.inputs:
            return self.inputs['dataStream']
        
        return None
    
    def get_location_block(self):
        """Return the location access block from our inputs, if any"""
        access_block = self.get_access_block()
        if access_block:
            for block in access_block:
                if 'category' in block and block['category'] == BotEnginePyTest.ACCESS_CATEGORY_MODE:
                    return block

        return {
            'location': {
                'latitude': 0.0,
                'longitude': 0.0
            }
        }

    def get_bundle_id(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the bundle ID.
        This method simply returns the bundle ID from the contents of that file.
        :return: The bundle ID for this bot
        """
        import bundle
        return bundle.BUNDLE_ID

    def get_cloud_address(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the cloud address we're uploading the bot to.
        This method simply returns the CLOUD_ADDRESS from the contents of the bundle.py file.
        :return: The cloud address for this bot
        """
        import bundle
        return bundle.CLOUD_ADDRESS

    def get_bot_instance_id(self):
        """
        :return: The bot instance ID
        """
        return self.bot_instance_id

    def get_location_id(self):
        """
        :return: The location ID for this bot
        """
        location_info = self.get_location_info()
        if location_info is not None:
            if 'locationId' in location_info['location']:
                return location_info['location']['locationId']
        return 0

    def get_name_by_user_id(self, user_id):
        """
        Returns a dictionary with 'firstName' and 'lastName' if the user exists, or None if the user doesn't exist
        :param user_id: User ID to extract the name
        :return: { 'firstName': "David", 'lastName': "Moss" }
        """
        users = self.get_location_users()
        for user in users:
            if int(user['id']) == int(user_id):
                name = {
                    "firstName": "",
                    "lastName": ""
                }

                if 'firstName' in user:
                    name['firstName'] = user['firstName']

                if 'lastName' in user:
                    name['lastName'] = user['lastName']

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
            return "{} {}".format(name['firstName'], name['lastName']).strip()

        return None

    def get_organization_id(self):
        """
        :return: The organization ID for this bot
        """
        return 0

    def get_organization_name(self):
        """
        :return: The name of the organization this location belongs to.
        """
        return "Organization ID {}".format(self.get_organization_id())

    def get_organization_signup_code(self):
        """
        :return: The sign-up code (short domain name) of the organization this location belongs to. Or None if we don't have it for some reason.
        """
        return "pytest"

    def get_country_code(self):
        """
        :return: The country code of the location.
        """
        return "1"


    def get_location_info(self):
        """
        :param location_id: Location ID to extract
        :return: location information from the access block
        """
        return self.location_block

    def get_user_id(self):
        """
        :return: User ID
        """
        return -1

    def get_user_first_name(self):
        return "PyTest"

    def get_user_last_name(self):
        return "Harness"

    def get_user_name(self):
        return "PyTest Harness"

    def get_location_name(self):
        return "PyTest Location"

    #===========================================================================
    # Location Settings
    #===========================================================================
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
        self.location_category = category
        self.location_rank = rank
        self.location_comment = comment

    def get_spaces(self):
        """
        Get a list of spaces for this location
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/get-spaces
        :return: List of spaces
        """
        return self.spaces

    def set_space(self, space_type, name, space_id=None):
        """
        Add / Update a space
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/update-space
        :param space_type: Type of space
        :param name: Name of space
        :param space_id: Space ID to update an existing space definition
        """
        self.spaces[name] = (space_type, space_id)

    def delete_space(self, space_id):
        """
        Delete a space
        https://iotapps.docs.apiary.io/#reference/locations/location-spaces/delete-space
        :param space_id: Space ID to delete
        """
        for name in self.spaces:
            s_type, s_id = self.spaces[name]
            if s_id == space_id:
                del self.spaces[name]
                return

    def add_occupancy(self, occupancy):
        """
        Add occupancy
        https://iotapps.docs.apiary.io/#reference/locations/location-occupancy/add-occupancy
        :param occupancy: Bitmask mark that locations is occupied or vacant:
                            0 - none or no data
                            1 - managed
                            2 - measured
        """
        self.logger.warning("botengine_pytest: Attempting to add_occupancy() but we haven't implemented this yet.")
        return

    def delete_occupancy(self, occupancy):
        """
        Delete occupancy
        https://iotapps.docs.apiary.io/#reference/locations/location-occupancy/remove-occupancy
        :param occupancy: Bitmask mark that locations is occupied or vacant:
                            0 - none or no data
                            1 - managed
                            2 - measured
        """
        self.logger.warning("botengine_pytest: Attempting to delete_occupancy() but we haven't implemented this yet.")
        return

    def get_language(self):
        """
        :return: user's selected language
        """
        location_info = self.get_location_info()
        if location_info is not None:
            if 'language' in location_info['location']:
                return location_info['location']['language']

        return None



    #============================================================================
    # Timestamps
    #============================================================================
    def get_timestamp(self):
        """Return the current botengine time

        :return: time in ms
        """
        if 'time' in self.inputs:
            self.time_ms = self.inputs['time']
        return self.time_ms

    def set_timestamp(self, timestamp):
        """Set the current botengine time

        :param timestamp: time in ms
        """
        if 'time' in self.inputs:
            self.inputs['time'] = timestamp
        self.time_ms = timestamp

    def add_timestamp(self, timestamp):
        """Add the time to the current botengine time

        :param timestamp: time in ms
        """
        if 'time' in self.inputs:
            self.inputs['time'] += timestamp
        self.time_ms += timestamp


    #============================================================================
    # Variables
    #============================================================================
    def save_variable(self, name, value, required_for_each_execution=False, shared=False):
        self.logger.debug("save_variable: {}:{}".format(name, value))
        self.variables[name] = value

    def save_shared_variable(self, name, value):
        self.logger.debug("save_shared_variable: {}:{}".format(name, value))
        self.variables[name] = value

    def save_variables(self, variables_dictionary):
        self.logger.debug("save_variables: {}".format(variables_dictionary))
        pass

    def save_variables(self, variables_dictionary, required_for_each_execution=False, shared=False):
        self.logger.debug("load_variable: {} (required_for_each_execution={}; shared={})".format(variables_dictionary, required_for_each_execution, shared))
        pass

    def load_variable(self, name):
        self.logger.debug("load_variable: {}".format(name))
        if name in self.variables:
            return self.variables[name]
        else:
            return None

    def load_shared_variable(self, name):
        self.logger.debug("load_shared_variable: {}".format(name))
        if name in self.variables:
            return self.variables[name]
        else:
            return None

    def delete_variable(self, name):
        self.logger.debug("delete_variable: {}".format(name))
        if name in self.variables:
            del self.variables[name]

    def delete_all_variables(self):
        self.logger.debug("delete_all_variables")
        self.variables = {}

    def clear_variable(self, name):
        self.logger.debug("clear_variable: {}".format(name))
        pass

    def flush_binary_variables(self):
        self.logger.debug("flush_binary_variables")
        pass

    def flush_variable(self):
        self.logger.debug("flush_variable")
        pass

    
    def destroy_core_memory(self):
        pass

    #============================================================================
    # Notifications
    #============================================================================
    def notify(self, push_title=None, push_subtitle=None, push_content=None, push_category=None, push_sound=None, push_sms_fallback_content=None, push_template_filename=None, push_template_model=None, push_info=None,
               email_subject=None, email_content=None, email_html=False, email_attachments=None, email_template_filename=None, email_template_model=None, email_addresses=None,
               sms_content=None, sms_template_filename=None, sms_template_model=None, sms_group_chat=True, admin_domain_name=None, brand=None, language=None, user_id=None, user_id_list=None, to_residents=False, to_supporters=False, to_admins=False):

        self.logger.info(">notify(): sms_content={}; sms_group_chat={}; push_content={}".format(sms_content, sms_group_chat, push_content))
        self.notify_called = True
        self.notify_message = push_content

    def is_notify_called(self):
        """Reset the notify called variable to be able to check it multiple times"""
        answer = self.notify_called
        self.notify_called = False
        return answer
    


    def make_voice_call(self, user_id, voice_model, call_time=None):
        """
        Define the voice call model for specific user.
        :param user_id: User ID
        :param voice_model: Voice call model
        :param call_time: Call start time, in milliseconds since the epoch
        :return:
        """
        body = {
            "model": voice_model
        }
        params = {
            "userId": user_id
        }

        if call_time is not None:
            params["callTime"] = call_time
        import json
        self.get_logger().debug("botengine: make_voice_call() params={} body={}".format(json.dumps(params, indent=2), json.dumps(body, indent=2)))
        pass

    def set_incoming_voicecall(self, user_id, voice_model):
        """
        Define the incoming voice call model for specific users at the bot's location.
        :param user_id:
        :param voice_model: Voice call model
        :return:
        """
        body = {
            "model": voice_model
        }
        params = {
            "userId": user_id
        }
        
        import json
        self.get_logger().debug("botengine: set_incoming_voicecall() params={} body={}".format(json.dumps(params), json.dumps(body)))
        pass

    def delete_incoming_voicecall(self, user_id):
        """
        Delete the incoming voice call model for specific users at the bot's location.
        :param user_id:
        :return:
        """
        params = {
            "userId": user_id
        }
        import json
        self.get_logger().debug("botengine: delete_incoming_voicecall() params={} body={}".format(json.dumps(params)))
        pass

    def send_mms(self, user_id, media_content=None, url=None, media_type=1, ext=None, caption=None):
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
        self.logger.info(">send_mss(): user_id={}; media_content={}; url={}; media_type={}; ext={}; caption={}".format(user_id, media_content, url, media_type, ext, caption))
        pass

    def email_admins(self, email_subject=None, email_content=None, email_html=False, email_attachments=None, email_template_filename=None, email_template_model=None, email_addresses=None, brand=None, categories=[1,2]):
        self.admin_mail_notified = True
        self.logger.info(">email_admins(): email_subject={}; email_content={} email_html={} email_attachments={} email_template_filename={} email_template_model={} email_addresses={} brand={} categories={}".format(email_subject, email_content, email_html, email_attachments, email_template_filename, email_template_model, email_addresses, brand, categories))
        return

    def get_resident_last_names(self):
        return "Test"

    def get_location_users(self):
        return self.users

    def get_location_user(self, user_id):
        """
        Retrieve all information about one specific user at this location ID
        :param user_id:
        :return:
        """
        users = self.get_location_users()
        for user in users:
            if user['id'] == user_id:
                return user
        return None

    def get_location_user_names(self, to_residents=True, to_supporters=True, sms_only=True):
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
        :return: List of dictionaries containing first and last names
        """
        return_list = []
        if to_residents:
            return_list += self.resident_user_names

        if to_supporters:
            return_list += self.supporter_user_names

        return return_list

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
        property = {
            "name": name,
            "value": value
        }

        if index is not None:
            property['index'] = index

        if device_id not in self.device_properties:
            self.device_properties[device_id] = []

        self.device_properties[device_id].append(property)

    def get_device_property(self, device_id, name=None, index=None):
        """
        Get device properties from your location
        https://iotapps.docs.apiary.io/#reference/devices/device-properties/get-device-properties

        :param device_id: Device ID
        :param name: Optional name to search for
        :param index: Optional index to search for
        """
        if device_id in self.device_properties:
            if name is None:
                return self.device_properties[device_id]
            else:
                for i, p in enumerate(self.device_properties[device_id]):
                    if p["name"] == name:
                        if index is not None:
                            if p["index"] == index:
                                return self.device_properties[device_id][i]
                        else:
                            return self.device_properties[device_id][i]

        return []

    def delete_device_property(self, device_id, name, index=None):
        """
        Delete device properties from your location
        https://iotapps.docs.apiary.io/#reference/devices/device-properties/get-device-properties

        :param device_id: Device ID
        :param property_name: Property name
        """
        if device_id in self.device_properties:
            for i, p in enumerate(self.device_properties[device_id]):
                if p["name"] == name:
                    if index is not None:
                        if p["index"] == index:
                            del self.device_properties[device_id][i]
                    else:
                        del self.device_properties[device_id][i]

    #============================================================================
    # Commands
    #============================================================================
    def form_command(self, param_name, value, index=None):
        """This method will form a command.

        You can pass in parameter name / optional index / value pairs and it will
        generate a dictionary to represent this command. This is a shortcut to send
        multiple commands with the send_commands(device_id, commands) method.

        :params param_name: The name of the parameter to configure
        :params value: The value to set for this parameter
        :params index: Optional index number / letters. Default is None.
        """
        self.logger.debug(
            ">form_command() param_name=" + str(param_name) + ", value=" + str(value) + ", index=" + str(index))

        response = None

        if index is None:
            response = {"name": param_name, "value": value}
        else:
            response = {"name": param_name, "index": index, "value": value}

        self.logger.debug("<form_command() response=" + str(response))
        return response

    def send_command(self, device_id, param_name, value, index=None):
        self.command_sent = True

    def send_commands(self, device_id, commands):
        self.command_sent = True

    def flush_commands(self):
        pass


    #===========================================================================
    # Data Stream Messages
    #===========================================================================
    def send_datastream_message(self, address, feed_dictionary, bot_instance_list=None, scope=1, location_id_list=None):
        self.datastream = {address: feed_dictionary}

    #============================================================================
    # Tags
    #============================================================================
    def tag_user(self, tag):
        """Tag a user
        
        :param tag The tag to give the user
        """
        self.logger.info(">botengine.tag_user(" + str(tag) + ")")
        self.user_tags.append(tag)

    def tag_location(self, tag):
        """Tag a location
        
        :param tag The tag to give the location
        :param location_id The location ID to tag
        """
        self.logger.info(">botengine.tag_location(" + str(tag) + ")")
        self.location_tags.append(tag)

    def tag_device(self, tag, device_id):
        """Tag a device
        
        :param tag The tag to give the device
        :param device_id The device ID to tag
        """
        self.logger.info(">botengine.tag_device(" + str(tag) + ", " + str(device_id) + ")")
        self.device_tags.append(tag)

    def tag_file(self, tag, file_id):
        """Tag a file
        
        :param tag The tag to give the file
        :param file_id The file ID to tag
        """
        self.logger.info(">botengine.tag_File(" + str(tag) + ", " + str(file_id) + ")")
        self.file_tags.append(tag)

    def delete_user_tag(self, tag):
        """Delete a user tag
        
        :param tag Tag to delete
        """
        self.logger.info(">botengine.delete_user_tag(" + str(tag) + ")")
        self.deleted_user_tags.append(tag)

    def delete_location_tag(self, tag):
        """Delete a location tag
        
        :param tag Tag to delete
        """
        self.logger.info(">botengine.delete_location_tag(" + str(tag) + ")")
        self.deleted_location_tags.append(tag)

    def delete_device_tag(self, tag, device_id):
        """Delete a location device

        :param tag Tag to delete
        """
        self.logger.info(">botengine.delete_device_tag(" + str(tag) + ", " + str(device_id) + ")")
        self.deleted_device_tags.append(tag)

    def delete_file_tag(self, tag, file_id):
        """Delete a location file
        
        :param tag Tag to delete
        """
        self.logger.info(">botengine.delete_device_tag(" + str(tag) + ", " + str(file_id) + ")")
        self.deleted_file_tags.append(tag)

    def get_location_tags(self):
        return self.location_tags

    def get_tags(self, type=None, id=None):
        print("\n\nWARNING: get_tags() called, but we can't return anything")
        return None


    #============================================================================
    # Executions
    #============================================================================
    def execute_again_in_n_seconds(self, seconds):
        self.execute_again_seconds = seconds

    def execute_again_at_timestamp(self, unix_timestamp_ms):
        self.execute_again_timestamp = unix_timestamp_ms

    def cancel_execution_request(self):
        self.execute_again_seconds = 0
        self.execute_again_timestamp = 0


    #============================================================================
    # Timers
    #============================================================================
    def set_alarm(self, timestamp_ms, function, argument=None, reference=None):
        self.logger.info(">botengine.set_alarm(timestamp_ms={}, function={}, argument={}, reference={})".format(timestamp_ms, function, argument, reference))
        self.alarms[reference] = (timestamp_ms, argument, function)

    def start_timer_s(self, seconds, function, argument=None, reference=None):
        self.logger.info(">botengine.start_timer_s(s={}, function={}, argument={}, reference={})".format(seconds, function, argument, reference))
        self.timers[reference] = (self.get_timestamp() + seconds * 1000, argument, function)

    def start_timer_ms(self, milliseconds, function, argument=None, reference=None):
        self.logger.info(">botengine.start_timer_ms(ms={}, function={}, argument={}, reference={})".format(milliseconds, function, argument, reference))
        self.timers[reference] = (self.get_timestamp() + milliseconds, argument, function)

    def start_timer(self, seconds, function, argument=None, reference=None):
        self.logger.info(">botengine.start_timer(s={}, function={}, argument={}, reference={})".format(seconds, function, argument, reference))
        self.timers[reference] = (self.get_timestamp() + seconds * 1000, argument, function)

    def cancel_timers(self, reference):
        if reference in self.timers:
            self.get_logger().debug("cancel_timers: {} timers:[{}]".format(reference, len(self.timers[reference])))
            del(self.timers[reference])

        if reference in self.alarms:
            self.get_logger().debug("cancel_timers: {} alarms:[{}]".format(reference, len(self.alarms[reference])))
            del(self.alarms[reference])

    def is_timer_running(self, reference):
        self.get_logger().debug("is_timer_running: {} {}".format(reference, reference in self.timers or reference in self.alarms))
        return reference in self.timers or reference in self.alarms

    def is_executing_timer(self):
        """
        :return: True if this execution includes a timer fire
        """
        return True

    def get_next_timer(self, reference=None):
        """
        :return: Next timer tuple: (absolute timestamp the next timer will fire in milliseconds, argument, reference)
        """
        # Search through timers by timestamp
        for ref, item in sorted(self.timers.items(), key=lambda x: x[1][0]):
            # Skip timers that are not for this reference if specified
            if reference is not None and reference not in ref:
                continue
            # Return the first alarm in our sorted list
            return (item[0], item[1], ref, item[2])

        # No timers found
        return None

    def get_next_alarm(self, reference=None):
        """
        :return: Next alarm tuple: (absolute timestamp the next timer will fire in milliseconds, argument, reference, function)
        """
        # Search through alarms by timestamp
        for ref, item in sorted(self.alarms.items(), key=lambda x: x[1]):
            # Skip alarms that are not for this reference if specified
            if reference is not None and reference not in ref:
                continue
            # Return the first alarm in our sorted list
            return (item[0], item[1], ref, item[2])

        # No alarms found
        return None

    def get_next_alarm_or_timer(self, reference=None):
        next_alarm = self.get_next_alarm(reference)
        next_timer = self.get_next_timer(reference)

        if next_alarm is None:
            return next_timer

        elif next_timer is None:
            return next_alarm

        else:
            if next_timer[0] < next_alarm[0]:
                return next_timer
            else:
                return next_alarm

    def fire_next_timer_or_alarm(self, intelligence_module, reference=None):
        """
        Pick and fire the next timer, removing it from our stack. 
        Advance the local time.

        :param intelligence_module: The module that is firing the timer
        :param reference: The reference to the timer
        :return:
        """
        next_alarm_or_timer = self.get_next_alarm_or_timer(reference)
        self.logger.debug(">botengine.fire_next_timer_or_alarm(): All alarms={}".format(self.alarms))
        self.logger.debug(">botengine.fire_next_timer_or_alarm(): All timers={}".format(self.timers))
        self.logger.debug(">botengine.fire_next_timer_or_alarm(): Next alarm={}".format(next_alarm_or_timer))

        if next_alarm_or_timer is not None:
            function = next_alarm_or_timer[3]
            reference = next_alarm_or_timer[2]
            argument = next_alarm_or_timer[1]
            # Check if this module is the one that should fire the timer
            if intelligence_module.intelligence_id != argument[0]:
                # If not, find the module that should fire the timer
                for module in intelligence_module.parent.intelligence_modules:
                    intelligence_module_lookup = intelligence_module.parent.intelligence_modules[module]
                    self.logger.debug(">botengine.fire_next_timer_or_alarm(): Microservice={} '{}'".format(module, intelligence_module_lookup.intelligence_id))
                    if intelligence_module_lookup.intelligence_id == argument[0]:
                        intelligence_module = intelligence_module_lookup
                        break

            if intelligence_module is not None:

                self.set_timestamp(next_alarm_or_timer[0])
                self.cancel_timers(reference)

                # Note that the microservice's real argument is placed in element 1,
                # and element 0 contains the intelligence_id for the microservice to trigger.
                self.logger.info("\n\n\n>botengine.fire_next_timer_or_alarm(): FIRING TIMER with argument={}".format(argument[1]))
                import datetime
                from dateutil.tz import tzlocal
                self.logger.info(">botengine.fire_next_timer_or_alarm(): ISO time {}".format(datetime.datetime.fromtimestamp(int(self.get_timestamp()/1000), tzlocal()).isoformat()))
                intelligence_module.timer_fired(self, argument[1])

        else:
            self.logger.info("\n\n\n>botengine.fire_next_timer_or_alarm(): NO TIMERS AVAILABLE TO FIRE")


    def get_cloud_address(self):
        """
        When you generate a bot, botengine will automatically generate and add a 'bundle.py' file which contains the cloud address we're uploading the bot to.
        This method simply returns the CLOUD_ADDRESS from the contents of the bundle.py file.
        :return: The cloud address for this bot
        """
        import bundle
        return bundle.CLOUD_ADDRESS

    #===========================================================================
    # Modes
    #===========================================================================
    def set_mode(self, location_id, mode, comment=None):
        """
        Set the mode
        :param location_id: Location ID of which to set the mode
        :param mode: Mode string to set, for example "AWAY" or "AWAY.SILENT"
        """
        self.mode = mode

    def get_mode_history(self, location_id, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        This method will return location mode history in backward order (lastest first)
        Including the source of the mode change
        :param location_id: Location ID
        :param oldest_timestamp_ms: Oldest timestamp to start pulling history
        :param newest_timestamp_ms: Newest timestamp to stop pulling history
        """
        raise NotImplementedError

    def get_mode(self, location_id):
        """
        Get the current mode
        :param location_id: Location ID to retrieve the mode for
        :return: The current mode, None if the location can't be found
        """
        return self.mode


    #============================================================================
    # Subscriptions
    #============================================================================
    def has_subscription(self, name):
        """All subscription are enabled"""
        return True

    def get_sms_subscribers(self, to_residents=False, to_supporters=False):
        """No SMS subscribers"""
        return set()


    #============================================================================
    # Questions
    #============================================================================
    def set_collection(self, name, icon, description, weight=0, media=None, media_content_type=None):
        return

    def ask_question(self, question):
        self.questions[question.key_identifier] = question
        return

    def retrieve_question(self, key):
        """No questions"""
        # if "care.midnightsnack" == key or "care.wandering" == key or "care.latenight" == key or "care.notbackhome" == key:
        #     return Question(None, None, default_answer=True)

        if key in self.questions:
            return self.questions[key]

        return None

    def delete_question(self, question):
        return

    def flush_questions(self):
        return

    def get_asked_questions(self):
        """
        Retrieve a dictionary of previously asked questions that still exist

          {
            "question_id_1" : question_object_1,
            "question_id_2" : question_object_2
          }

        :return: a dictionary of questions we've previously asked. The question's ID is the dictionary's key, the question itself is the value.
        """
        self.logger.debug("botengine_pytest: Attempting to get_asked_questions but we haven't implemented this yet.")
        return {}

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
        self.logger.debug("botengine_pytest: Attempting to change_answer() but we haven't implemented this yet.")
        return

    def resynchronize_questions(self):
        return

    def generate_question(self, key_identifier, response_type, device_id=None, icon=None, icon_font=None, display_type=None, collection=None, editable=False, default_answer=None, correct_answer=None, answer_format=None, urgent=False, front_page=False, send_push=False, send_sms=False, send_email=False, ask_timestamp=None, section_id=0, question_weight=0):
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
        :param display_type: How to render and display the question in the UI. For example, a Boolean question can be an on/off switch, a yes/no question, or just a single button. See the documentation for more details.
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
        return Question(key_identifier, response_type, device_id, icon, icon_font, display_type, collection, editable, default_answer, correct_answer, answer_format, urgent,
                        front_page, send_push, send_sms, send_email, ask_timestamp, section_id, question_weight)

    # ===========================================================================
    # Bot-to-UI content delivery
    # ===========================================================================
    def set_ui_content(self, address, json_content, overwrite=False, timestamp_ms=None):
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
        """
        self.states[address] = json_content
        return None

    def get_ui_content(self, address, timestamp_ms=None):
        """
        Get UI content by address
        :param address: Address to retrieve information from
        :param timestamp_ms: Optional timestamp for time-based state variables
        :return: The JSON value for this address, or None if it doesn't exist
        """
        if address in self.states:
            return self.states[address]

        return None

    #===========================================================================
    # Bot content delivery to state variables
    #===========================================================================
    def set_state(self, address, json_content, overwrite=True, timestamp_ms=None, publish_to_partner=True, fields_updated=[], fields_deleted=[]):
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
        """
        if timestamp_ms is not None:
            if timestamp_ms not in self.states:
                self.states[timestamp_ms] = {}

            if not overwrite:
                if address in self.states[timestamp_ms]:
                    self.states[timestamp_ms][address].update(json_content)
                else:
                    self.states[timestamp_ms][address] = json_content    
            else:
                self.states[timestamp_ms][address] = json_content
        else:
            if not overwrite:
                if address in self.states:
                    self.states[address].update(json_content)
                else:
                    self.states[address] = json_content
            else:
                self.states[address] = json_content

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

        if timestamp_ms is not None:
            if address in self.states[timestamp_ms]:
                return self.states[timestamp_ms][address]
        elif address in self.states:
            return self.states[address]
        return None

    def delete_state(self, address, timeseries_property=False, overwrite=True, publish_to_partner=True):
        """
        Permanently delete a state variable. Must specify if it is a timeseries_property (default is non-time-series property).

        :param address: State variable address to delete
        :param timeseries_property: Set to True if it is a timeseries property (default is False, non-timeseries state variable)
        :param overwrite: Overwrite entire state property (default is true)
        :param publish_to_partner: True or False to stream this state update to a partner cloud. Default is True, streaming enabled.
        :return:
        """
        return

    def get_timeseries_state(self, address, start_timestamp_ms, end_timestamp_ms=None):
        """
        Get a time-series state variable. This loads it from the server every time, and may include multiple time-series records
        ranging from the start_timestamp_ms to the end_timestamp_ms.

        :param address: Time-series state variable address to load
        :param start_timestamp_ms: Required start timestamp
        :param end_timestamp_ms: Optional end timestamp
        :return:
        """
        if start_timestamp_ms in self.states:
            if address in self.states[start_timestamp_ms]:
                return self.states[start_timestamp_ms][address]

        return None

    def flush_states(self):
        """
        Flush all UI content to the server
        :return:
        """
        return

    def _flush_states(self, address, json_content, overwrite=False, timestamp_ms=None):
        """
        Commit UI content to the cloud
        :param address:
        :param json_content:
        :param overwrite:
        :param timestamp_ms: Timestamp for time-based state variables
        :return:
        """
        return

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
        return

    def delete_admin_content(self, organization_id, address):
        """
        Delete administrator content.
        https://iotadmins.docs.apiary.io/#reference/organizations/organization-large-objects/delete-object
        :param organization_id: Organization ID to delete from
        :param address: Object name
        """
        return


    #============================================================================
    # Analytics
    #============================================================================
    def is_playback(self):
        return self.playback
    
    def is_test_location(self):
        """
        Do not log analytics while running tests
        """
        return True

    #============================================================================
    # Rules
    #============================================================================
    def get_rules(self, device_id):
        return {}

    def pause_rules(self):
        pass

    def toggle_all_rules(self, enable, rule_id_list=[], device_type_list=[], device_id_list=[], default=None, hidden=None, user_id=None):
        return []

    def delete_all_rules(self, status=None, rule_id_list=[], device_type_list=[], device_id_list=[], default=None,
                         hidden=None, user_id=None):
        pass

    #============================================================================
    # Narration
    #============================================================================
    def narrate(self, title=None, description=None, priority=None, icon=None, icon_font=None, status=None, timestamp_ms=None, narrative_type=NARRATIVE_TYPE_OBSERVATION, file_ids=None, extra_json_dict=None, event_type=None, update_narrative_id=None, update_narrative_timestamp=None, admin=False, publish_to_partner=None):
        # if self.playback:
        #     return None

        narrative = {}

        location_id = self.get_location_id()

        if priority is not None:
            narrative['priority'] = priority

        if icon is not None:
            narrative['icon'] = icon

        if icon_font is not None:
            narrative['iconFont'] = icon_font

        if title is not None:
            narrative['title'] = title

        if description is not None:
            narrative['description'] = description

        if status is not None:
            narrative['status'] = status

        if timestamp_ms is not None:
            narrative['narrativeTime'] = timestamp_ms

        if narrative_type is not None:
            # if self.is_server_version_newer_than(1, 29):
            narrative['narrativeType'] = narrative_type

        target = {}

        if file_ids is not None:
            target['fileIDs'] = file_ids

        if extra_json_dict is not None:
            target.update(extra_json_dict)

        if len(target) > 0:
            narrative['target'] = target

        params = {}

        if update_narrative_id is not None:
            params['narrativeId'] = update_narrative_id

        if update_narrative_timestamp is not None:
            params['narrativeTime'] = update_narrative_timestamp

        if admin:
            params['scope'] = 2
        else:
            params['scope'] = 1

        # New server features to stream narratives to partner clouds
        # if self.is_server_version_newer_than(1, 22):
        if publish_to_partner is not None:
            params['publish'] = publish_to_partner

        if event_type is not None:
            narrative['eventType'] = event_type

        body = {
                "narrative" : narrative
                }

        import json
        self.logger.info("|narrate() params={}".format(json.dumps(params, sort_keys=True)))
        self.logger.info("|narrate() body={}".format(json.dumps(body, sort_keys=True)))
        if extra_json_dict is not None:
            if "search_timestamp_ms" in extra_json_dict:
                self.save_variable("search_timestamp_ms", extra_json_dict["search_timestamp_ms"])
            elif "expected_wake_ms" in extra_json_dict:
                self.save_variable("expected_wake_ms", extra_json_dict["expected_wake_ms"])
            elif "device_id" in extra_json_dict:
                self.save_variable("device_id", extra_json_dict["device_id"])
            elif "uuid" in extra_json_dict:
                self.save_variable("uuid", extra_json_dict["uuid"])


        if event_type is not None:
            self.save_variable("eventType", event_type)
        
        self.save_variable("body", body)

        return

    def request_customer_support(self, ticket_type, ticket_priority, subject, comment, brand="default"):
        self.customer_support_body = {
            "brand": brand,
            "ticket": {
                "type": ticket_type,
                "priority": ticket_priority,
                "subject": "Location {} - {}".format(self.get_location_id(), subject),
                "comment": comment
            }
        }

        self.customer_support_comments.append(comment)
        
        import json
        self.logger.info("request_customer_support() params={}".format(json.dumps(self.customer_support_body, sort_keys=True)))
        return

    #============================================================================
    # Professional monitoring
    #============================================================================
    def has_professional_monitoring(self):
        """
        :return: True if this user has professional monitoring services
        """
        return self.has_pro_monitoring


    def professional_monitoring_status(self):
        """This method will return call center service statuses"""
        return self.pro_monitoring_status

    def professional_monitoring_alerts(self):
        """This method will return call center service alerts"""
        return None

    def raise_professional_monitoring_alert(self, message, code, device_id=None, latitude=None, longitude=None):
        """Raise an alert to the professional monitoring services

        :param message: signal message
        :param code:        E130 - General burglary alarm
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
        self.professional_monitoring_raised = True
        self.professional_monitoring_code = code
        self.professional_monitoring_message = message
        self.professional_monitoring_device_id = device_id
        self.professional_monitoring_latitude = latitude
        self.professional_monitoring_longitude = longitude

    def cancel_professional_monitoring_alert(self, message, code, device_id=None):
        """Cancel an alert to the professional monitoring services

        :param message: signal message
        :param code:        E130 - General burglary alarm
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
        self.professional_monitoring_cancelled = True
    
    # ===========================================================================
    # Others
    #============================================================================
    def get_property(self, obj_arr, property_name, property_value, return_property_name):
        """This method will locate the specified first object from object array, and then return the specified property value

        :params obj_arr: object array
        :params property_name: the key in searching criteria
        :params property_value: the value in searching criteria
        :params return_property_name: the key in the object indicates which corresponding value will be returned
        """
        self.logger.debug(">get_property() obj_arr=" + str(obj_arr) + ", property_name=" + str(property_name)
                          + ", property_value=" + str(property_value) + ", return_property_name=" + str(
            return_property_name))

        response = None
        for item in obj_arr:
            if item[property_name] == property_value:
                response = item[return_property_name]
                break

        self.logger.debug("<get_property() response=" + str(response))
        return response

    def add_email_attachment(self, destination_attachment_array, filename, base64_content, content_type, content_id):
        """This helper method will create an email attachment block and add it to a destination array of existing email attachments

        :params destination_attachment_array: Destination array of attachments. Pass in [] if you are starting a new list of attachments.
        :params filename: Filename of the file, for example, "imageName.jpg"
        :params base64_content: Base64-encoded binary image content
        :params content_type: Content type of the file, for example "image/jpeg"
        :params content_id: Unique ID for the content, for example "inlineImageId". The email can reference this content with <img src="cid:inlineImageId">.

        :return the destination_attachment_array with the new attachment, ready to pass into the email_attachments argument in the notify() method
        """
        attachment = {
            "name": filename,
            "content": base64_content,
            "contentType": content_type,
            "contentId": content_id
        }
        destination_attachment_array.append(attachment)
        return destination_attachment_array
    
    def get_location_scenes_history(self, location_id):
        """Get location scenes history - can't do much"""
        self.logger.warning("WARNING: get_location_scenes_history() is called, but we can't return anything")
        return {}
    
    def get_measurements(self, device_id, start_date=None, end_date=None, param_name=None, index=None, last_rows=None):
        self.logger.warning("WARNING: get_measurements() called, but we can't return anything")
        return None

    def request_data(self, type=1, device_id=None, oldest_timestamp_ms=None, newest_timestamp_ms=None, param_name_list=None, reference=None, index=None, ordered=1):
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
        self.logger.warning("WARNING: Attempted to request_data(), but we can't do anything here.")

    def get_user_info(self):
        return {
            "user": {
                "firstName": "Firstname",
                "lastName": "Lastname",
                "id": "0"
            }
        }

    # AWS Secrets Manager
    def get_secret(self, secret_name, region_name="us-east-1"):
        """
        Retrieve a secret from AWS Secrets Manager

        :param secret_name: Name of this secret
        :param region_name: AWS region. default "us-east-1"
        :return: optional json secret. i.e., '{"appname": "some", "appsecret": "thing"}'
        """
        return '{"appname": "some", "appsecret": "thing"}'


#===============================================================================
# Question Class
#===============================================================================
class Question:
    """
    Class to hold a question and its answer
    """
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

    def __init__(self, key_identifier, response_type, device_id=None, icon=None, icon_font=None, display_type=None, collection=None, editable=False, default_answer=None, correct_answer=None, answer_format=None, urgent=False, front_page=False, send_push=False, send_sms=False, send_email=False, ask_timestamp=None, section_id=0, question_weight=0):
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
        :param icon: Icon to display when asking this question. See http://peoplepowerco.com/icons or http://fontawesome.com
        :param icon_font: Icon font to render the icon. See the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
        :param display_type: How to render and display the question in the UI. For example, a Boolean question can be an on/off switch, a yes/no question, or just a single button. See the documentation for more details.
        :param collection: Collection name
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
        self._question_id = None
        self.key_identifier = key_identifier
        self.response_type = response_type
        self.device_id = device_id
        self.icon = icon
        self.icon_font = icon_font
        self.display_type = display_type
        self.editable = editable
        self.urgent = urgent
        self.front_page = front_page
        self.send_push = send_push
        self.send_sms = send_sms
        self.send_email = send_email
        self.correct_answer = correct_answer
        self.answer_format = answer_format
        self.default_answer = default_answer
        self.ask_timestamp = ask_timestamp
        self.tags = []
        self.question = {}
        self.placeholder = {}
        self.response_options = []
        self.section_title = {}
        self.section_id = section_id
        self.question_weight = question_weight
        self.answer_status = self.ANSWER_STATUS_NOT_ASKED
        self.answer_time = None
        self.answer = None
        self.answer_correct = False
        self.answer_modified = False
        self.slider_min = 0
        self.collection = collection

        # The user ID who answered this question
        self.user_id = None
        
        if response_type == self.QUESTION_RESPONSE_TYPE_SLIDER:
            if display_type == self.QUESTION_DISPLAY_SLIDER_MINSEC:
                # Minutes:Seconds slider - 60:00 max by default, in increments of 0:15 seconds
                self.slider_max = 3600
                self.slider_inc = 15
                
            else:
                # Float and Integer slider - 100 max by default, in increments of 5
                self.slider_max = 100
                self.slider_inc = 5

    def _boolean_to_str(self, value):
        if type(value) == bool:
            if value:
                return "true"
            else:
                return "false"

        return value

    def _form_json_question(self):
        """
        Private function to form the JSON request to POST this question
        :return: JSON string ready to send to the server
        """
        body = {
             "key": self.key_identifier,
             "urgent": self.urgent,
             "front": self.front_page,
             "push": self.send_push,
             "sms": self.send_sms,
             "email": self.send_email,
             "responseType": self.response_type,
             "editable": self.editable,
             "question": self.question
         }

        if self.device_id is not None:
            body['deviceId'] = self.device_id

        # Added May 27, 2020
        if hasattr(self, 'icon_font'):
            if self.icon_font is not None:
                body['iconFont'] = self.icon_font

        else:
            self.icon_font = None

        if self.icon is not None:
            body['icon'] = self.icon

        if self.display_type is not None:
            body['displayType'] = int(self.display_type)
            
        if len(self.section_title) > 0:
            body['sectionTitle'] = self.section_title
            
        if self.section_id is not None:
            body['sectionId'] = int(self.section_id)
        
        if self.question_weight is not None:
            body['questionWeight'] = int(self.question_weight)
        
        if self.ask_timestamp:
            body['askDateMs'] = self.ask_timestamp

        if len(self.placeholder) > 0:
            body['placeholder'] = self.placeholder

        if self.response_type == self.QUESTION_RESPONSE_TYPE_SLIDER:
            body['sliderMin'] = self.slider_min
            body['sliderMax'] = self.slider_max
            body['sliderInc'] = self.slider_inc
            
            if self.default_answer is None:
                self.default_answer = int((self.slider_max - self.slider_min) / 2)

        if len(self.tags) > 0:
            body['tags'] = self.tags

        if self.answer is not None:
            # We've already gotten an answer to this question and we're asking it again, don't lose the previous answer.
            self.default_answer = self.answer

        if self.default_answer is not None:
            body['defaultAnswer'] = self._boolean_to_str(self.default_answer)

        if self.correct_answer:
            body['validAnswer'] = self.correct_answer

        if self.answer_format:
            body['answerFormat'] = self.answer_format

        if not hasattr(self, 'collection'):
            self.collection = None

        if self.collection:
            body['collectionName'] = self.collection

        if self.response_type == self.QUESTION_RESPONSE_TYPE_MULTICHOICE_MULTISELECT or self.response_type == self.QUESTION_RESPONSE_TYPE_MULTICHOICE_SINGLESELECT:
            body['responseOptions'] = []
            identifier = 0
            for option in self.response_options:
                body['responseOptions'].append(option._get_json_dictionary(identifier))
                identifier += 1
        
        return body

    def get_id(self):
        """
        :return: Server-generated Question ID, or None if this question hasn't been saved to the server yet.
        """
        return self._question_id

    def frame_question(self, question, language="en"):
        """
        Frame question in a specific language

        :param question: The question to ask in that language
        :param language: 'en', 'zh', etc. Default is 'en'
        """
        self.question[language] = question

    def slider_boundaries(self, slider_min=0, slider_max=100, slider_inc=5):
        """
        Set the boundaries of a question that expects a response in the form of a slider
        :param slider_min: Minimum slider boundary, default is 0
        :param slider_max: Maximum slider boundary, default is 100
        :param slider_inc: Incremental slider amount, default is 5
        """
        self.slider_min = slider_min
        self.slider_max = slider_max
        self.slider_inc = slider_inc
        
    def set_placeholder_text(self, placeholder, language="en"):
        """
        A placeholder adds an example to a question that expects a text-based response.
        For example, if the question was "What is your favorite color?" then the placeholder might be "Blue" in English.

        :param placeholder: Open-ended text example to prompt the user to type in their own answer.
        :param language: Language for the placeholder, 'en', 'zh', etc. Default is "en".
        """
        self.placeholder[language] = placeholder

    def set_section_title(self, section_title, language="en"):
        """
        Set the section title. 
        The top most question in the section (lowest weight) sets the title.
        
        :param section_title: Name of the section of questions
        :param language: Language for this section title, default is 'en'
        """
        self.section_title[language] = section_title

    def set_default_answer(self, default_answer):
        """
        Set default answer.

        :param default_answer: Name of the section of questions
        """
        self.default_answer = default_answer

    def set_editable(self, editable):
        """
        Set the question is editable.

        :param editable: Question is editable
        """
        self.editable = editable

    def auto_tag_user(self, tag):
        """
        Auto-tag the user with this tag if they provide is the "correct" response, based on the correct_answer regular expression.
        Cannot be used with any list-type questions.
        Can be called multiple times to add multiple tags:  this simply does a self.tags.append(tag) so you could alternatively
        set it in a more Pythonic way by doing something like:  question.tags = ["tag1","tag2"]

        :param tag: Tag to tag the user's account with if they provide any valid response.
        """
        self.tags.append(tag)

    def generate_response_option(self, text=None, language='en'):
        """
        Get a QuestionResponseOption object
        :param text: Text for this response option
        :param language: Language identifier for that text, i.e. 'en'
        :return: QuestionResponseOption object that has been added to this question, for yours to edit
        """
        option = QuestionResponseOption(len(self.response_options), text, language)
        self.response_options.append(option)
        return option

    def ready_to_ask(self):
        """
        :return: True if this question is ready to ask
        """
        if len(self.question) == 0:
            return False

        if self.response_type == self.QUESTION_RESPONSE_TYPE_RADIO or self.response_type == self.QUESTION_RESPONSE_TYPE_DROPDOWN or self.response_type == self.QUESTION_RESPONSE_TYPE_CHECKBOX or self.response_type == self.QUESTION_RESPONSE_TYPE_MULTISELECT:
            return len(self.response_options) > 0

        return True

class QuestionResponseOption:
    """
    A single response option to a question that is a radio button, drop-down list, checkbox, or multi-select type of question
    """

    def __init__(self, identifier, text=None, language="en"):
        """
        Initialize
        :param identifier: Unique incremental identifier for this response, starting with 0
        :param text: Text for this response option
        :param language: Language identifier for that text, i.e. 'en'
        """
        self.identifier = identifier
        self.text = {}
        self.tags = []
        self.complete = False

        if text is not None:
            self.add_text(text, language)

    def _get_json_dictionary(self, identifier):
        """
        Private method to get a dictionary representing the content that needs to get injected into a JSON API POST
        :param identifier: id of this response option relative to other option, starting with 0
        :return: Dictionary formatted to conform to the POST API
        """
        block = {
            "id": identifier,
            "text": self.text
        }

        if len(self.tags) > 0:
            block["tags"] = self.tags

        return block

    def add_text(self, text, language="en"):
        """
        Add some text to this question's response option, in a specificied language

        :param text: Text for this option
        :param language: Language abbreviation, 'en' by default
        :return: self, so you can keep adding more if you want.
        """
        self.complete = True
        self.text[language] = text
        return self

    def add_tag(self, tag):
        """
        Tag a user with this tag if they answer in this way

        :param tag: Tag to tag the user with if they answer the question in this way
        :return: self, so you can keep adding more if you want.
        """
        self.tags.append(tag)
        return self