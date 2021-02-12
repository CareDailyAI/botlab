'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import pytz
import datetime
import utilities.utilities as utilities
import signals.analytics as analytics
from utilities.narrative import Narrative
import intelligence.index
import importlib
import domain

class Location:
    """
    Provide tools and information to manage the Location.
    """

    # Security States
    SECURITY_STATE_DISARMED = 0
    SECURITY_STATE_EXIT_DELAY_FULL = 1
    SECURITY_STATE_EXIT_DELAY_PERIMETER = 2
    SECURITY_STATE_ARMED_FULLY = 3
    SECURITY_STATE_ARMED_PERIMETER = 4
    SECURITY_STATE_ENTRY_DELAY = 5
    SECURITY_STATE_ALARMING_RECENT_CLOSING = 6
    SECURITY_STATE_ALARMING = 7
    SECURITY_STATE_TEST_MODE = 8

    def __init__(self, botengine, location_id):
        """Constructor"""
        self.location_id = int(location_id)

        # Dictionary of all device objects. { 'device_id': <device_object> }
        self.devices = {}
        
        # Born on date
        self.born_on = botengine.get_timestamp()
        
        # Mode of this location (i.e. "HOME", "AWAY", etc.). This is the mode of the security system.
        self.mode = botengine.get_mode(self.location_id)

        # All Location Intelligence modules
        self.intelligence_modules = {}

        # Try to update our current mode
        self.update_mode(botengine)

        # Conversational UI
        self.conversational_ui = None

        # Security state
        self.security_state = Location.SECURITY_STATE_DISARMED

        # Occupancy status as determined by AI occupancy detection algorithms.
        self.occupancy_status = ""

        # Reason for the current occupancy status. For example: "ML.MOTION" or "USER".
        self.occupancy_reason = ""

        # Last time our location properties were sync'd
        self.properties_timestamp_ms = 0

        # Latest copy of our location properties
        self.location_properties = {}

        # Narratives we're tracking from various microservices for your location.  { "unique_id" : narrative_object }.
        self.location_narratives = {}

        # Narratives we're tracking from various microservices for your organization. { "unique_id" : narrative_object }.
        self.org_narratives = {}

        # Latitude
        self.latitude = None

        # Longitude
        self.longitude = None

        # Daylight setting, populated by the 'daylight' microservice package
        self.is_daylight = None

        
    def initialize(self, botengine, initialize_everything=True):
        """
        Initialize
        :param botengine: BotEngine environment
        :param initialize_everything: Default is True. False is used when we're performing advance machine learning edge computing services.
        """
        # Added December 8, 2020
        if not hasattr(self, 'security_state'):
            self.security_state = Location.SECURITY_STATE_DISARMED

        if initialize_everything:
            for d in self.devices:
                self.devices[d].initialize(botengine)

        # for module_name in self.intelligence_modules:
        #     botengine.get_logger().info("{} : {}".format(self.intelligence_modules[module_name].intelligence_id, module_name))

        # Synchronize microservices

        module_names = [x['module'] for x in intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']]

        changed = False
        for m in module_names:
            changed |= m not in self.intelligence_modules

        for m in list(self.intelligence_modules.keys()):
            changed |= m not in module_names

        if changed:
            # Remove microservices that no longer exist
            for module_name in dict(self.intelligence_modules).keys():
                found = False
                for intelligence_info in intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']:
                    if intelligence_info['module'] == module_name:
                        found = True
                        break

                if not found:
                    botengine.get_logger().info("Deleting location microservice: " + str(module_name))
                    self.intelligence_modules[module_name].destroy(botengine)
                    del self.intelligence_modules[module_name]

            # Add more microservices
            for intelligence_info in intelligence.index.MICROSERVICES['LOCATION_MICROSERVICES']:
                if intelligence_info['module'] not in self.intelligence_modules:
                    try:
                        intelligence_module = importlib.import_module(intelligence_info['module'])
                        class_ = getattr(intelligence_module, intelligence_info['class'])
                        botengine.get_logger().info("Adding location microservice: " + str(intelligence_info['module']))
                        intelligence_object = class_(botengine, self)
                        self.intelligence_modules[intelligence_info['module']] = intelligence_object

                    except Exception as e:
                        import traceback
                        botengine.get_logger().error("Could not add location microservice: {}: {}; {}".format(str(intelligence_info), str(e), traceback.format_exc()))
                        
                    

                    
        # Location intelligence execution
        for i in self.intelligence_modules:
            self.intelligence_modules[i].parent = self
            if initialize_everything:
                self.intelligence_modules[i].initialize(botengine)

    def new_version(self, botengine):
        """
        New bot version
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("location: New bot version detected")

        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].new_version(botengine)

        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].new_version(botengine)

    def add_device(self, botengine, device_object):
        """
        Start tracking a new device here.
        Perform any bounds checking, for example with multiple gateways at one location.
        :param device_object: Device object to track
        """
        self.devices[device_object.device_id] = device_object

        if hasattr(device_object, "intelligence_modules"):
            for intelligence_id in device_object.intelligence_modules:
                device_object.intelligence_modules[intelligence_id].device_added(botengine, device_object)

        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_added(botengine, device_object)

    def delete_device(self, botengine, device_id):
        """
        Delete the given device ID
        :param device_id: Device ID to delete
        """
        if device_id in self.devices:
            device_object = self.devices[device_id]

            if hasattr(device_object, "intelligence_modules"):
                for intelligence_id in device_object.intelligence_modules:
                    try:
                        device_object.intelligence_modules[intelligence_id].destroy(botengine)
                    except Exception as e:
                        botengine.get_logger().warning("location.py.delete_device(): microservice.destroy(): {}".format(e))

            try:
                device_object.destroy(botengine)
            except Exception as e:
                botengine.get_logger().warning("location.py.delete_device() device_object.destory(): {}".format(e))

            del self.devices[device_id]

            for intelligence_id in self.intelligence_modules:
                self.intelligence_modules[intelligence_id].device_deleted(botengine, device_object)

    def mode_updated(self, botengine, mode):
        """
        Update this location's mode
        """
        self.mode = mode
        botengine.get_logger().info("location mode_updated(): " + self.mode + " mode.")
        
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].mode_updated(botengine, mode)

        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].mode_updated(botengine, mode)
    
    def device_measurements_updated(self, botengine, device_object):
        """
        Evaluate a device that was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_measurements_updated(botengine, device_object)
    
    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_metadata_updated(botengine, device_object)

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alerts_list: List of alerts
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_alert(botengine, device_object, alert_type, alert_params)

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].question_answered(botengine, question)
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].question_answered(botengine, question)
    
    
    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Updated
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Data Stream content
        """
        for intelligence_id in self.intelligence_modules:
            try:
                self.intelligence_modules[intelligence_id].datastream_updated(botengine, address, content)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering datastream message to location microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    try:
                        self.devices[device_id].intelligence_modules[intelligence_id].datastream_updated(botengine, address, content)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering datastream message to device microservice (continuing execution): " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())
            
    def schedule_fired(self, botengine, schedule_id):
        """
        Schedule Fired.
        It is this location's responsibility to notify all sub-intelligence modules, including both device and location intelligence modules
        :param botengine: BotEngine environment
        """
        # Location intelligence modules
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].schedule_fired(botengine, schedule_id)
        
        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].schedule_fired(botengine, schedule_id)
        
    def timer_fired(self, botengine, argument):
        """
        Timer fired
        :param botengine: BotEngine environment
        :param argument: Optional argument
        """
        return

    def file_uploaded(self, botengine, device_object, file_id, filesize_bytes, content_type, file_extension):
        """
        A device file has been uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file_id: File ID to reference this file at the server
        :param filesize_bytes: The file size in bytes
        :param content_type: The content type, for example 'video/mp4'
        :param file_extension: The file extension, for example 'mp4'
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].file_uploaded(botengine, device_object, file_id, filesize_bytes, content_type, file_extension)

    def user_role_updated(self, botengine, user_id, category, location_access, previous_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param user_id: User ID that changed roles
        :param category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        # Location intelligence modules
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].user_role_updated(botengine, user_id, category, location_access, previous_category, previous_location_access)

        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].user_role_updated(botengine, user_id, category, location_access, previous_category, previous_location_access)

    def call_center_updated(self, botengine, user_id, status):
        """
        Emergency call center status has changed
        :param botengine: BotEngine environment
        :param user_id: User ID that made the change
        :param status: Current call center status
        """
        # Location intelligence modules
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].call_center_updated(botengine, user_id, status)

        # Device intelligence modules
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    self.devices[device_id].intelligence_modules[intelligence_id].call_center_updated(botengine, user_id, status)

    def data_request_ready(self, botengine, reference, device_csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.
        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param device_csv_dict: { 'device_id': 'csv data string' }
        """
        # Location microservices
        for intelligence_id in self.intelligence_modules:
            try:
                self.intelligence_modules[intelligence_id].data_request_ready(botengine, reference, device_csv_dict)
            except Exception as e:
                botengine.get_logger().warning("location.py - Error delivering data_request_ready to location microservice : " + str(e))
                import traceback
                botengine.get_logger().error(traceback.format_exc())


        # Device microservices
        for device_id in self.devices:
            if hasattr(self.devices[device_id], "intelligence_modules"):
                for intelligence_id in self.devices[device_id].intelligence_modules:
                    try:
                        self.devices[device_id].intelligence_modules[intelligence_id].data_request_ready(botengine, reference, device_csv_dict)
                    except Exception as e:
                        botengine.get_logger().warning("location.py - Error delivering data_request_ready to device microservice : " + str(e))
                        import traceback
                        botengine.get_logger().error(traceback.format_exc())

    def update_coordinates(self, botengine, latitude, longitude):
        """
        Attempt to update coordinates
        :param botengine: BotEngine environment
        :param latitude: Current latitude
        :param longitude: Current longitude
        """
        # Added June 26, 2019
        if not hasattr(self, 'latitude'):
            self.latitude = None
            self.longitude = None

        if self.latitude != latitude or self.longitude != longitude:
            self.latitude = latitude
            self.longitude = longitude

            for intelligence_id in self.intelligence_modules:
                try:
                    self.intelligence_modules[intelligence_id].coordinates_updated(botengine, self.latitude, self.longitude)
                except Exception as e:
                    botengine.get_logger().warning("location.py - Error delivering coordinates_updated to location microservice : " + str(e))
                    import traceback
                    botengine.get_logger().error(traceback.format_exc())

    def get_microservice_by_id(self, microservice_id):
        """
        Get a microservice ("intelligence module") by its id ("intelligence_id").
        Sorry we named them 'intelligence modules' at first when they were really microservices.

        :param microservice_id: Microservice ID
        :return: Microservice object, or None if it doesn't exist.
        """
        for microservice in self.intelligence_modules:
            if self.intelligence_modules[microservice].intelligence_id == microservice_id:
                return self.intelligence_modules[microservice]

        for device_id in self.devices:
            for microservice in self.devices[device_id].intelligence_modules:
                if self.devices[device_id].intelligence_modules[microservice].intelligence_id == microservice_id:
                    return self.devices[device_id].intelligence_modules[microservice]

        return None

    #===========================================================================
    # General location information
    #===========================================================================
    def get_location_name(self, botengine):
        """
        Get the nickname of this location
        :param botengine: BotEngine environment
        :return: Nickname
        """
        return botengine.get_location_name()

    #===========================================================================
    # Mode
    #===========================================================================
    def set_mode(self, botengine, mode, comment=None):
        """
        Set the mode for this location
        :param botengine: BotEngine environment
        :param comment: Optional comment about why the mode was set
        """
        botengine.set_mode(self.location_id, mode, comment)
        # Allow the bot to trigger again and set the mode from a single unified action.

    def get_user_facing_mode(self, botengine, mode):
        """
        The modes recognized by most services include "HOME", "AWAY", "STAY", "TEST".

        The user-facing representation of these modes may be different. For example,
        some brands prefer the user to see "OFF" instead of "HOME".

        This method will transform a mode name into the user-facing representation
        for interaction with the user. Use the domain.py file at the root of your bot
        to specify this mapping.

        :param botengine: BotEngine environment
        :param mode: Internal mode name, including "HOME", "AWAY", "STAY", "TEST".
        :return: User-facing text representation of that mode
        """
        if hasattr(domain, 'USER_FACING_MODES'):
            if mode in domain.USER_FACING_MODES:
                return domain.USER_FACING_MODES[mode]
            else:
                botengine.get_logger().warning("location.py: Mode '{}' not found in the domain.USER_FACING_MODES".format(mode))

        return mode

    #===========================================================================
    # Location Properties
    #===========================================================================
    def set_location_property(self, botengine, property_name, property_value, track=True):
        """
        Set a location property
        :param botengine: BotEngine environment
        :param property_name: Property name
        :param property_value: Property value
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True
        """
        self._sync_location_properties(botengine)
        self.location_properties[property_name] = property_value
        botengine.set_ui_content('location_properties', self.location_properties)

        if track:
            import signals.analytics as analytics
            analytics.people_set(botengine, self, {property_name: property_value})

    def update_location_properties(self, botengine, properties_dict, track=True):
        """
        Update multiple location properties simultaneously from a dictionary.
        If the properties don't exist yet, they will be added.

        :param botengine: BotEngine environment
        :param properties_dict: Properties dictionary with key/values to update
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True)
        """
        self._sync_location_properties(botengine)
        self.location_properties.update(properties_dict)
        botengine.set_ui_content('location_properties', self.location_properties)

        if track:
            import signals.analytics as analytics
            analytics.people_set(botengine, self, properties_dict)

    def increment_location_property(self, botengine, property_name, increment_amount=1, track=True):
        """
        Increment a location property integer by the amount given.

        If the property doesn't exist, it will be initialized to 0 and then incremented by the amount given.
        An existing property must be numeric to increment.

        :param botengine: BotEngine environment
        :param property_name: Property name to increment
        :param increment_amount: Incremental amount to add (default is 1)
        :param track: True to automatically copy these properties to the 3rd party analytics (default is True)
        """
        self._sync_location_properties(botengine)
        if property_name not in self.location_properties:
            self.location_properties[property_name] = 0

        self.location_properties[property_name] += increment_amount
        botengine.set_ui_content('location_properties', self.location_properties)

        import signals.analytics as analytics
        analytics.people_increment(botengine, self, {property_name: increment_amount})

    def get_location_property(self, botengine, property_name):
        """
        Retrieve a location property
        :param botengine: BotEngine environment
        :param property_name: Property name to retrieve
        :return: The property value, or None if it doesn't exist
        """
        self._sync_location_properties(botengine)
        if property_name in self.location_properties:
            return self.location_properties[property_name]
        return None
    
    def delete_location_property(self, botengine, property_name):
        """
        Delete a location property
        :param botengine: BotEngine environment
        :param property_name: Property name to delete
        """
        self._sync_location_properties(botengine)
        if property_name in self.location_properties:
            del(self.location_properties[property_name])
            botengine.set_ui_content('location_properties', self.location_properties)

    def set_location_property_separately(self, botengine, additional_property_name, additional_property_json, overwrite=False, timestamp_ms=None):
        """
        Set a large location property. The name is referenced by our 'location_properties' but stored separately
        and referenced in the location_properties as 'additional_properties'.

        You must use botengine.get_ui_content(..) when retrieving the content of this additional property,
        since it is referenced by the 'location_property' but stored separately.

        :param botengine: BotEngine environment
        :param additional_property_name: Property name to store separately and reference in our location_properties
        :param additional_property_json: Property JSON value
        :param overwrite: True to overwrite all existing content, False to update existing server content only with the top-level dictionary keys that are presented leaving others untouched (default)
        :param timestamp_ms: Timestamp for time-series content
        :return:
        """
        if timestamp_ms is None:
            additional_properties = self.get_location_property(botengine, 'additional_properties')
            if additional_properties is None:
                additional_properties = []

            if additional_property_name not in additional_properties:
                additional_properties.append(additional_property_name)
                self.set_location_property(botengine, 'additional_properties', additional_properties)

        else:
            timestamp_ms = int(timestamp_ms / 1000.0) * 1000
            timeseries_properties = self.get_location_property(botengine, 'timeseries_properties')
            if timeseries_properties is None:
                timeseries_properties = {}

            try:
                if timeseries_properties[additional_property_name] != timestamp_ms:
                    raise ValueError
            except:
                timeseries_properties[additional_property_name] = timestamp_ms
                self.set_location_property(botengine, 'timeseries_properties', timeseries_properties)

        botengine.set_ui_content(additional_property_name, additional_property_json, overwrite=overwrite, timestamp_ms=timestamp_ms)

    def _sync_location_properties(self, botengine):
        """
        Internal method to synchornize our local copy of location properties with the server
        :param botengine: BotEngine environment
        """
        if self.properties_timestamp_ms != botengine.get_timestamp():
            properties = botengine.get_ui_content('location_properties')
            if properties is not None:
                self.location_properties = properties

            else:
                self.location_properties = {}

            self.properties_timestamp_ms = botengine.get_timestamp()

    #===========================================================================
    # Data Stream Message delivery
    #===========================================================================
    def distribute_datastream_message(self, botengine, address, content=None, internal=True, external=True):
        """
        Distribute a data stream message both internally to any intelligence module within this bot,
        and externally to any other bots that might be listening.
        :param botengine: BotEngine environment
        :param address: Data stream address
        :param content: Message content
        :param internal: True to deliver this message internally to any intelligence module that's listening (default)
        :param external: True to deliver this message externally to any other bot that's listening (default)
        """
        if internal:
            self.datastream_updated(botengine, address, content)

        if external:
            botengine.send_datastream_message(address, content)


    #===========================================================================
    # Rules
    #===========================================================================
    def set_rule_phrase(self, botengine, phrase_id, phrase_object):
        """
        Declare a rule phrase to be dynamically added (or removed) from our rules engine.
        If the phrase_object is None, then the rule phrase gets removed.

        The phrase_id is a globally unique name for the phrase.

        The phrase_object should contain a dictionary with this type of content:

        {
            # 'type' field can be 0 (trigger), 1 (state), or 2 (action)
            "type": TYPE_TRIGGER,

            # If we evaluate a device: the device type of the device so we could summarize actions for specific types of devices.
            "device_types": self.parent.device_type,

            # Description of the phrase in the user's native language. Fill in the ___:
            # [If my] ____
            # [and my] ____
            # [then] ____
            "description": "'{}' is pressed",

            # Past-tense of the description, for notifications. Fill in the ___:
            # [Your] ____
            # [while your] ___
            "past": "'{}' was pressed",

            # Evaluation function for triggers and states.
            # If dealing with a device, the function is responsible for checking if the device ID is the object that made an update,
            # and then testing to see if that device is in the triggered state.
            # Function arguments are action_function(botengine, rules_engine, location_object, device_object, rule_id)
            # Functions should return a tuple: ( True|False to execute, "past-tense comment describing why" )
            # Any time the function changes, we need to update the rule phrase.
            "eval": evaluation_function,

            # Evaluation function for any timer fires related to this rule / trigger
            # Function arguments are timer_function(botengine, rules_engine, location_object, device_object, rule_id)
            # Functions should return a tuple: ( True|False to execute, "past-tense comment describing why" )
            # Any time the function changes, we need to update the rule phrase.
            "timer_eval": trigger_button_held_timer_fired,

            # Action function for actions.
            # Function arguments are action_function(botengine, rules_engine, location_object, device_object, rule_id)
            # Any time the function changes, we need to update the rule phrase.
            "action": action_function,

            # Icon to apply at the application layer
            "icon": "touch"

            # List of dynamic parameters that need to be captured in the rule
            # Each parameter has a globally unique name.
            # See the "Rule Phrase Parameters" table at https://iotapps.docs.apiary.io/#reference/rules-engine
            "parameters": [

                {
                    # Name of this parameter. The application should save the parameter into the rule data stream message with "unique_rule_phrase_id-parameter_name": "final_value"
                    "name": "unique_rule_phrase_id-parameter_name",

                    # Optional. Know what order to fill out parameters when dealing with multiple parameters.
                    # Higher numbers are filled out later than lower numbers.
                    "order": 0,

                    # Type of input desired
                    #  0 = Device ID
                    #  1 = Text input
                    #  2 = Absolute time-of-day (seconds from the start of the day)
                    #  3 = Day-of-the-week multiple-choice multi-select (0 = Sunday). Remember in Python, Monday = 0 so we have to offset.
                    #  4 = Relative time from when the rule was created (seconds from now) - "Alexa turn off the lights in 5 minutes"
                    #  5 = Multiple-choice single-select (see the list of values below).
                    #  6 = Mode "HOME", "AWAY", "STAY"
                    #  7 = Security system state integer (from the security state enumerator)
                    #  8 = Occupancy status "PRESENT", "ABSENT", "H2A", "A2H", "SLEEP", "H2S", "S2H", "VACATION"
                    "category": parameter_categories_type,

                    "description": "A short user friendly question or brief instruction to display to the user to get them to correctly fill out this parameter.",

                    "values": [
                        "list",
                        "of",
                        "choices",
                        "if",
                        "applicable"
                    ],

                    # Default value of the parameter, if applicable
                    "value": "Default Value",

                    # For UI slider type category
                    "min_value": 0,

                    # For UI slider type category
                    "max_value": 10,

                    # 1=int, 2=float
                    "value_type": 1,

                    # Unit of measurements
                    "unit": "Hours"
                }
            ]
        }

        :param botengine:
        :param phrase_id:
        :param phrase_object:
        :return:
        """
        botengine.save_shared_variable(phrase_id, phrase_object)
        self.distribute_datastream_message(botengine, "set_rule_phrase", { "phrase_id" : phrase_id }, internal=True, external=True)

    def set_behaviors(self, botengine, device_types, behaviors):
        """
        Set behaviors.

        Each behavior dictionary is defined as:

            {
                "id": 123,
                "weight": 0,
                "name": "Protect my home (default)",
                "description": "The motion sensor will recognize movement patterns to help protect your home and reduce energy consumption.",

                # Optional arguments:
                "icon": "home",
                "media_url": "s3://some_url"
                "media_content_type": "image/png"
            }

        :param botengine: BotEngine environment
        :param device_types: List of device types this set of behaviors applies to
        :param behaviors: List of behavior dictionaries
        """
        menu = {}
        for device_type in device_types:
            if behaviors is None:
                menu[device_type] = None
            else:
                menu[device_type] = "behaviors_{}".format(device_type)
            botengine.save_shared_variable("behaviors_{}".format(device_type), behaviors)

        self.distribute_datastream_message(botengine, "set_behaviors", menu, internal=True, external=True)

    #===========================================================================
    # Narration
    #===========================================================================
    def narrate(self, botengine, title=None, description=None, priority=None, icon=None, icon_font=None, timestamp_ms=None, file_ids=None, extra_json_dict=None, update_narrative_id=None, update_narrative_timestamp=None, user_id=None, users=None, device_id=None, devices=None, goal_id=None, question_key=None, comment=None, status=None, microservice_identifier=None, to_user=True, to_admin=False):
        """
        Narrate some activity
        :param botengine: BotEngine environment
        :param title: Title of the event
        :param description: Description of the event
        :param priority: 0=debug; 1=info; 2=warning; 3=critical
        :param icon: Icon name, like 'motion' or 'phone-alert'. See http://peoplepowerco.com/icons and http://fontawesome.com
        :param icon_font: Icon font package. Please see the ICON_FONT_* descriptions in utilities/utilities.py.
        :param timestamp_ms: Optional timestamp for this event. Can be in the future. If not set, the current timestamp is used.
        :param file_ids: List of file ID's (media) to reference and show as part of the record in the UI
        :param extra_json_dict: Any extra JSON dictionary content we want to communicate with the UI
        :param update_narrative_id: Specify a narrative ID to update an existing record.
        :param update_narrative_timestamp: Specify a narrative timestamp to update an existing record. This is a double-check to make sure we're not overwriting the wrong record.
        :param to_admin: True to deliver to an administrator History
        :param to_user: True to deliver to end user History
        :return:  { "user": narrative_object, "admin": narrative_object }. The narrative_object may be None. See com.ppc.Bot/narrative.py
        """
        payload = {}

        if user_id is not None:
            payload['user_id'] = user_id

        if users is not None:
            payload['users'] = users

        if device_id is not None:
            payload['device_id'] = device_id

        if devices is not None:
            payload['devices'] = devices

        if goal_id is not None:
            payload['goal_id'] = goal_id

        if question_key is not None:
            payload['question_key'] = question_key

        if comment is not None:
            payload['comment'] = comment

        if extra_json_dict is None:
            extra_json_dict = payload

        else:
            extra_json_dict.update(payload)

        response_dict = {
            "user": None,
            "admin": None
        }

        if to_admin:
            response = botengine.narrate(title, description, priority, icon, icon_font=icon_font, status=status, timestamp_ms=timestamp_ms, file_ids=file_ids, extra_json_dict=extra_json_dict, update_narrative_id=update_narrative_id, update_narrative_timestamp=update_narrative_timestamp, admin=True)

            if response is not None:
                response_dict['admin'] = Narrative(response['narrativeId'], response['narrativeTime'], admin=True)
                if microservice_identifier is not None:
                    self.org_narratives[microservice_identifier] = response_dict['admin']

        else:
            if microservice_identifier is not None:
                if microservice_identifier in self.org_narratives:
                    del(self.org_narratives[microservice_identifier])

        if to_user:
            response = botengine.narrate(title, description, priority, icon, icon_font=icon_font, status=status, timestamp_ms=timestamp_ms, file_ids=file_ids, extra_json_dict=extra_json_dict, update_narrative_id=update_narrative_id, update_narrative_timestamp=update_narrative_timestamp, admin=False)

            if response is not None:
                response_dict['user'] = Narrative(response['narrativeId'], response['narrativeTime'], admin=False)
                if microservice_identifier is not None:
                    self.location_narratives[microservice_identifier] = response_dict['user']

        else:
            if microservice_identifier is not None:
                if microservice_identifier in self.location_narratives:
                    del(self.location_narratives[microservice_identifier])

        return response_dict

    def resolve_narrative(self, botengine, microservice_identifier):
        """
        Resolve a narrative entry
        :param botengine: BotEngine environment
        :param microservice_identifier: The same microservice identifier used to create the narrative
        :param admin: True to update the admin status on this narrative
        :return:  { "narrativeId": id, "narrativeTime": timestamp_ms } if successful, otherwise None.
        """
        if microservice_identifier in self.org_narratives:
            if self.org_narratives[microservice_identifier] is not None:
                if isinstance(self.org_narratives[microservice_identifier], Narrative):
                    self.org_narratives[microservice_identifier].resolve(botengine)

                del(self.org_narratives[microservice_identifier])

        if microservice_identifier in self.location_narratives:
            if self.location_narratives[microservice_identifier] is not None:
                if isinstance(self.location_narratives[microservice_identifier], Narrative):
                    self.location_narratives[microservice_identifier].resolve(botengine)

                del(self.location_narratives[microservice_identifier])

    def delete_narration(self, botengine, narrative_id, narrative_timestamp):
        """
        Delete a narrative record
        :param botengine: BotEngine environment
        :param narrative_id: ID of the record to delete
        :param narrative_timestamp: Timestamp of the record to delete
        """
        botengine.delete_narration(narrative_id, narrative_timestamp)

    #===========================================================================
    # Mode helper methods
    #===========================================================================
    def is_present(self, botengine=None):
        """
        Is the person likely physically present in the home?
        :return: True if the person is in HOME, STAY, SLEEP, or TEST mode. False for all others.
        """
        return "ABSENT" not in self.occupancy_status \
               and "A2H" not in self.occupancy_status \
               and "H2A" not in self.occupancy_status \
               and "AWAY" not in self.occupancy_status \
               and "VACATION" not in self.occupancy_status

    def is_definitely_absent(self, botengine=None):
        """
        :param botengine:
        :return: True if the occupants are definitely away
        """
        return "ABSENT" in self.occupancy_status \
               or "A2H" in self.occupancy_status \
               or "AWAY" in self.occupancy_status \
               or "VACATION" in self.occupancy_status
    
    def is_present_and_protected(self, botengine=None):
        """
        Is the person at home and wants to be alerted if the perimeter is breached?
        :return: True if the person is in STAY or SLEEP mode
        """
        return utilities.MODE_STAY in self.mode \
               or "SLEEP" in self.occupancy_status \
               or "H2S" in self.occupancy_status \
               or "S2H" in self.occupancy_status

    def is_sleeping(self, botengine=None):
        """
        :return: True if the person is about to go to sleep, or they're sleeping, or about to wake up.
        """
        return "SLEEP" in self.occupancy_status or "S2H" in self.occupancy_status
    
    def update_mode(self, botengine):
        """
        Extract this location's current mode from our botengine environment
        :param botengine: BotEngine environment
        """
        location_block = botengine.get_location_info()
        if location_block is not None:
            if 'event' in location_block['location']:
                self.mode = str(location_block['location']['event'])

    #===========================================================================
    # Time
    #===========================================================================
    def get_local_datetime(self, botengine):
        """
        Get the datetime in the user's local timezone.
        :param botengine: BotEngine environment
        :param timestamp: Unix timestamp in milliseconds
        :returns: datetime
        """
        return self.get_datetime_from_timestamp(botengine, botengine.get_timestamp(), self.get_local_timezone_string(botengine))
    
    def get_local_datetime_from_timestamp(self, botengine, timestamp_ms):
        """
        Get a datetime in the user's local timezone, based on an input timestamp_ms
        :param botengine: BotEngine environment
        :param timestamp_ms: Timestamp in milliseconds to transform into a timezone-aware datetime object
        """
        return self.get_datetime_from_timestamp(botengine, timestamp_ms, self.get_local_timezone_string(botengine))

    def get_datetime_from_timestamp(self, botengine, timestamp_ms=None, timezone=None):
        """
        Get a datetime in the user's local timezone, based on an input timestamp_ms
        :param botengine: BotEngine environment
        :param timestamp_ms: Timestamp in milliseconds to transform into a timezone-aware datetime object
        :param timezone: Optional timezone
        """
        if timestamp_ms is None:
            timestamp_ms = botengine.get_timestamp()

        if timezone is None:
            timezone = self.get_local_timezone_string(botengine)
        return datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, pytz.timezone(timezone))

    def get_local_timezone_string(self, botengine):
        """
        Get the local timezone string
        :param botengine: BotEngine environment
        :return: timezone string
        """
        location_block = botengine.get_location_info()

        # Try to get the user's location's timezone string
        if 'location' in location_block:
            if 'timezone' in location_block['location']:
                return location_block['location']['timezone']['id']

        return domain.DEFAULT_TIMEZONE

    def get_relative_time_of_day(self, botengine, timestamp_ms=None, timezone=None):
        """
        Transform our local datetime into a float hour and minutes
        :param botengine: BotEngine environment
        :param timestamp_ms: Transform this timestamp if given, otherwise transform the current time from botengine.
        :param timezone: Optional timezone
        :return: Relative time of day - hours.minutes where minutes is divided by 60. 10:15 AM = 10.25
        """
        dt = self.get_datetime_from_timestamp(botengine, timestamp_ms, timezone)
        return dt.hour + (dt.minute / 60.0)

    def get_midnight_last_night(self, botengine):
        """
        Get a datetime of midnight last night in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight last night in the local timezone
        """
        return self.get_local_datetime(botengine).replace(hour=0, minute=0, second=0, microsecond=0)

    def get_midnight_tonight(self, botengine):
        """
        Get a datetime of midnight tonight in local time
        :param botengine: BotEngine environment
        :return: Datetime object of midnight tonight in the local timezone
        """
        return self.get_local_datetime(botengine).replace(hour=23, minute=59, second=59, microsecond=999999)

    def local_timestamp_ms_from_relative_hours(self, botengine, weekday, hours, future=True):
        """
        Calculate an absolute timestamp from relative day-of-week and hour
        :param botengine: BotEngine environment
        :param dow: day-of-week (Monday is 0)
        :param hours: Relative hours into the day (i.e. 23.5 = 11:30 PM local time)
        :param future: True to return a timestamp that is always in the future
        :return: Unix epoch timestamp in milliseconds
        """
        from datetime import timedelta
        hours = float(hours)
        weekday = int(weekday)

        reference = self.get_local_datetime(botengine)
        hour, minute = divmod(hours, 1)
        minute = round(minute * 60)
        days = reference.weekday() - weekday
        target_dt = (reference - timedelta(days=days)).replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        timestamp_ms = self.timezone_aware_datetime_to_unix_timestamp(botengine, target_dt)

        if future:
            if timestamp_ms <= botengine.get_timestamp():
                timestamp_ms += utilities.ONE_WEEK_MS

        return timestamp_ms

    def timezone_aware_datetime_to_unix_timestamp(self, botengine, dt):
        """
        Convert a local datetime / timezone-aware datetime to a unix timestamp
        :param botengine: BotEngine environment
        :param dt: Datetime to convert to unix timestamp
        :return: timestamp in milliseconds
        """
        from tzlocal import get_localzone
        return int((dt.astimezone(get_localzone())).strftime("%s")) * 1000

    def get_local_hour_of_day(self, botengine):
        """
        Get the local hour of the day (float), used in machine learning algorithms.

        Examples:
        * Midnight last night = 0.0
        * Noon = 12.0
        * 9:15 PM = 21.25

        :param botengine: BotEngine environment
        :return: hour of the day (float)
        """
        return (botengine.get_timestamp() - self.timezone_aware_datetime_to_unix_timestamp(botengine, self.get_midnight_last_night(botengine))) / 1000 / 60.0 / 60.0

    def get_local_day_of_week(self, botengine):
        """
        Get the local day of the week (0-6)

        :param botengine: BotEngine environment
        :return: local day of the week (0 - 6)
        """
        return self.get_local_datetime(botengine).weekday()

    def day_of_week_to_local_midnight_datetime(self, botengine, dow):
        """
        Get the datetime at midnight of the next relative day of the week.
            0 = Monday
            1 = Tuesday
            2 = Wednesday
            3 = Thursday
            4 = Friday
            5 = Saturday
            6 = Sunday

        :param dow: Python day-of-week (0 = Monday)
        :return: Datetime of midnight on this next day-of-week
        """
        from datetime import timedelta

        midnight_dt = self.get_midnight_last_night(botengine)
        offset = dow - midnight_dt.weekday()
        if offset < 0:
            offset += 7

        return midnight_dt + timedelta(days=offset)

    #===========================================================================
    # Weather
    #===========================================================================
    def get_weather_forecast(self, botengine, units=None, hours=12):
        """
        Get the weather forecast for this location
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :param hours: Forecast depth in hours, default is 12. Available hours are 6, 12.
        :return: Weather JSON data
        """
        return botengine.get_weather_forecast_by_location(self.location_id, units, hours)

    def get_current_weather(self, botengine, units=None):
        """
        Get the current weather by Location ID
        :param units: Default is Metric. 'e'=English; 'm'=Metric; 'h'=Hybrid (UK); 's'=Metric SI units (not available for all APIs)
        :return: Weather JSON data
        """
        return botengine.get_current_weather_by_location(self.location_id, units)


    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        output = "location_id,timestamp_ms,timestamp_iso,event,source_type\n"

        # This number happens to be the oldest timestamp
        if oldest_timestamp_ms < 1262304000000:
            oldest_timestamp_ms = 1262304000000

        try:
            modes = botengine.get_mode_history(self.location_id, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms)
        except Exception as e:
            # This can happen because this bot may not have read permissions for this device.
            botengine.get_logger().error("Could not download modes history for location {}: {}".format(self.location_id, str(e)))
            import traceback
            botengine.get_logger().error(traceback.format_exc())
            return None

        if 'events' not in modes:
            return None

        botengine.get_logger().info("{} mode changes captured".format(len(modes['events'])))

        for event in modes['events']:
            timestamp_ms = event['eventDateMs']
            dt = self.get_local_datetime_from_timestamp(botengine, timestamp_ms)

            event_name = event['event'].replace(",",".")

            output += "{},{},{},{},{}".format(self.location_id, timestamp_ms, utilities.iso_format(dt), event_name, event['sourceType'])
            output += "\n"

        return output
