'''
Created on 05/10/2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''
from intelligence.intelligence import Intelligence

import utilities.utilities as utilities
import signals.analytics as analytics
import signals.engage_kit_cloud as engage_kit_cloud
import properties
import json
from pydantic import TypeAdapter
from typing import List
from datetime import datetime
import signals.ai as ai
import utilities.genai as genai

from intelligence.engage_kit_cloud.types.messages_cloud_buffer import MessagesCloudBuffer
from intelligence.engage_kit_cloud.types.messages_priority_calculator import PriorityCalculator
from intelligence.engage_kit_cloud.types.cloud_model import BotMessage, CloudMessageStatus

# Seconds between each cloud message delivery check
CLOUD_SCHEDULE_INTERVAL_S = 60

# SetFit Key
SETFIT_KEY = "engage_kit_cloud"

class LocationEngageKitCloudMicroservice(Intelligence):
    """
    Primary role is to understand the best way to talk to each person.
    One-way communications (push notifications, TV, Alexa, etc.) and two-way communications (SMS, phone, in-app messaging).
    References the role, category, and accessibility preferences of the users at the location.
    The class is responsible for logging narratives and analytics, understanding services for the location,
    coordinate the APIs between multiple engagement bots.
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

        # BotMessages that are currently active and pending prioritization
        self.messages = []

        # buffer for active messages priorities based on time to start and priority of topic
        self.messages_buffer = MessagesCloudBuffer(botengine, PriorityCalculator.custom_priority_calculation)

        pass

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        return

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """

        # Added: 6/27/2024
        if not hasattr(self, 'messages'):
            self.messages = []
        return

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        return

    def occupancy_status_updated(self, botengine, status, reason, last_status, last_reason):
        """
        AI Occupancy Status updated
        :param botengine: BotEngine
        :param status: Current occupancy status
        :param reason: Current occupancy reason
        :param last_status: Last occupancy status
        :param last_reason: Last occupancy reason
        """
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        return

    def device_alert(self, botengine, device_object, alert_type, alert_params):
        """
        Device sent an alert.
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
        :param alert_params: Alert parameters as key/value dictionary
        """
        return

    def device_added(self, botengine, device_object):
        """
        A new Device was added to this Location
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting added
        """
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question_object):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question_object: Question object
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
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
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        return

    def user_role_updated(self, botengine, user_id, role, alert_category, location_access, previous_alert_category,
                          previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param user_id: User ID that changed roles
        :param alert_category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's access to the location and devices. (0=None; 10=read location/device data; 20=control devices and modes; 30=update location info and manage devices)
        :param previous_alert_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        """
        return

    def call_center_updated(self, botengine, user_id, status):
        """
        Emergency call center status has changed.

            0 = Unavailable
            1 = Available, but the user does not have enough information to activate
            2 = Registration pending
            3 = Registered and activated
            4 = Cancellation pending
            5 = Cancelled

        :param botengine: BotEngine environment
        :param user_id: User ID that made the change
        :param status: Current call center status
        """
        return

    def async_data_request_ready(self, botengine, reference, csv_dict):
        """
        A botengine.request_data() asynchronous request for CSV data is ready.

        This is part of a very scalable method to extract large amounts of data from the server for the purpose of
        machine learning services. If a service needs to extract a large amount of data for one or multiple devices,
        the developer should call botengine.request_data(..) and also allow the bot to trigger off of trigger type 2048.
        The bot can exit its current execution. The server will independently gather all the necessary data and
        capture it into a LZ4-compressed CSV file on the server which is available for one day and accessible only by
        the bot through a public HTTPS URL identified by a cryptographic token. The bot then gets triggered and
        downloads the CSV data, passing the data throughout the environment with this async_data_request_ready()
        event-driven method.


        IMPORTANT: This method executes in an asynchronous environment where you are NOT allowed to:
        - Set timers or alarms
        - Manage class variables that persist across executions
        - Perform other stateful operations

        To return to a synchronous environment where you can use timers and manage state, call:
        botengine.async_execute_again_in_n_seconds(seconds)

                Developers are encouraged to use the 'reference' argument inside calls to botengine.request_data(..). The
        reference is passed back out at the completion of the request, allowing the developer to ensure the
        data request that is now available was truly destined for their microservice.

        Your bots will need to include the following configuration for data requests to operate:
        * runtime.json should include trigger 2048
        * structure.json should include inside 'pip_install_remotely' a reference to the "lz4" Python package

        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param csv_dict: { device_object: 'csv data string' }
        """
        return
    
    def messages_updated(self, botengine, messages):
        """
        List of Messages were updated
        :param botengine: BotEngine environment
        :param messages: Message objects
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">messages_updated()")
        
        # empty buffer
        self.messages_buffer.clear_buffer(botengine)

        # TODO: Handle schedule type 1 (recurring).  Remove for now.
        messages = [message for message in messages if message['scheduleType'] == 0 and not message.get('userId')]

        # Validate the messages
        ta = TypeAdapter(List[BotMessage])
        self.messages = ta.validate_python(messages)
    
        # Submit the messages for prioritization
        ai_params = genai.care_daily_ai_message_prioritization(botengine, phrases=[message.priority_phrase() for message in self.messages if message.status == CloudMessageStatus.READY.value])
        try:
            ai.submit_message_prioritization_request(
                botengine, 
                self.parent, 
                key=SETFIT_KEY,
                ai_params=ai_params)
        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("|messages_updated() Error submitting message prioritization request: {}".format(e))
            
            # Proceed with the messages without AI prioritization
            self._process_set_fit_phrase_prioritization(botengine, [])
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<messages_updated()")

    
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
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">ai() content={}".format(content))
        if content.get('key', '') != SETFIT_KEY:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ai() Missing or non-matching key '{}'".format(content.get('key', 'NONE')))
            return
        
        # Process the AI prioritization of the phrases
        self._process_set_fit_phrase_prioritization(botengine, content.get('phrases', []))

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<ai()")
        
    def _process_set_fit_phrase_prioritization(self, botengine, phrases):
        """
        Process the AI prioritization of the phrases
        :param botengine: BotEngine environment
        :param phrases: List of phrases to prioritize
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_process_set_fit_phrase_prioritization()")
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_process_set_fit_phrase_prioritization() messages={}".format(self.messages))

        # Update the messages with the AI scores
        self.messages_buffer.add_messages_with_priority(botengine, self.messages, phrases)

        # Update the cloud with the message delivery schedule based on the AI prioritization
        midnight_timestamp_s = int(self.parent.get_midnight_last_night(botengine).timestamp())
        current_timestamp_s = int(self.parent.get_local_datetime(botengine).timestamp())
        scheduled_messages = self.messages_buffer.get_scheduled_messages_with_adjusted_delivery_times(botengine, CLOUD_SCHEDULE_INTERVAL_S, midnight_timestamp_s, current_timestamp_s)
        scheduled_messages_list = [json.loads(message.model_dump_json(by_alias=True, indent=4, exclude_none=True)) for
                              message in scheduled_messages]
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|_process_set_fit_phrase_prioritization() scheduled_messages_list={}".format(scheduled_messages_list))

        engage_kit_cloud.update_cloud_messages(botengine, scheduled_messages_list)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_process_set_fit_phrase_prioritization()")
        return
