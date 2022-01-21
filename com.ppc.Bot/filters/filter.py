'''
Created on October 21, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import bot
import utilities.utilities as utilities


class Filter:
    """
    Override this class with your own filter, then add it to the 'data_filters' in your index.py.

    As data flows in, this will trigger methods in the following order:
        * new_version() - only when we've updated the bot version
        * initialize() - on every execution

        EITHER/OR
        * filter_measurements() - edit the measurements_dict in place
        * data_request_ready() - edit the data request results in place

    Filters can receive data stream messages to enable filter configurations and communications.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        import uuid
        self.filter_id = str(uuid.uuid4())
        self.parent = parent

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        return

    def initialize(self, botengine):
        """
        Initialize on every bot execution.
        :param botengine: BotEngine environment
        """
        return
    
    def destroy(self, botengine):
        """
        This object is getting permanently deleted. Clean up.
        :param botengine: BotEngine environment
        """
        return

    def filter_measurements(self, botengine, device_object, measurements):
        """
        Optionally filter device measurement data before it reaches the upper layers of the stack.

        The device_object is only passed in as a reference so we can determine what type of device this is,
        and identifiers / configuration around it. DO NOT interact with the device object functionally or
        attempt to pull information out of the device object about this current trigger, because this
        filter_measurements() event gets triggered before the device object is updated with the filtered data.

        Use self.get_parameter(measurements, name, index=None) to extract a specific parameter, then
        edit the measurements_dict directly in place.

        Example measurements:
            [
                {
                    "deviceId": "63a5f00e006f0d00",
                    "name": "power",
                    "time": 1608748576694,
                    "updated": true,
                    "value": "0.2"
                },
                {
                    "deviceId": "63a5f00e006f0d00",
                    "name": "energy",
                    "time": 1634866106490,
                    "updated": false,
                    "value": "34.8459829801"
                }
            ]

        :param botengine: BotEngine environment
        :param device_object: Device object pending update
        :param measurements: Measurements we're about to trigger, which is modified in place.
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

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        return

    def question_answered(self, botengine, question_object):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question_object: Question object
        """
        return

    def data_request_ready(self, botengine, reference, csv_dict):
        """
        Edit the data request results directly in place.

        A botengine.request_data() asynchronous request for CSV data is ready.

        This is part of a very scalable method to extract large amounts of data from the server for the purpose of
        machine learning services. If a service needs to extract a large amount of data for one or multiple devices,
        the developer should call botengine.request_data(..) and also allow the bot to trigger off of trigger type 2048.
        The bot can exit its current execution. The server will independently gather all the necessary data and
        capture it into a LZ4-compressed CSV file on the server which is available for one day and accessible only by
        the bot through a public HTTPS URL identified by a cryptographic token. The bot then gets triggered and
        downloads the CSV data, passing the data throughout the environment with this data_request_ready()
        event-driven method.

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

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)


    #===============================================================================
    # Built-in Timer and Alarm methods.
    #===============================================================================
    def start_timer_ms(self, botengine, milliseconds, argument=None, reference=""):
        """
        Start a relative timer in milliseconds
        :param botengine: BotEngine environment
        :param seconds: Time in milliseconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        bot.start_location_intelligence_timer_ms(botengine, milliseconds, self.filter_id, argument, self.filter_id + str(reference))

    def start_timer_s(self, botengine, seconds, argument=None, reference=""):
        """
        Helper function with an explicit "_s" at the end, to start a timer in seconds
        :param botengine: BotEngine environment
        :param seconds: Time in seconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        self.start_timer(botengine, seconds, argument, str(reference))

    def start_timer(self, botengine, seconds, argument=None, reference=""):
        """
        Start a relative timer in seconds
        :param botengine: BotEngine environment
        :param seconds: Time in seconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        bot.start_location_intelligence_timer(botengine, seconds, self.filter_id, argument, self.filter_id + str(reference))

    def is_timer_running(self, botengine, reference=""):
        """
        Check if a timer or alarm with the given reference is running
        :param botengine: BotEngine environment
        :param reference: Reference
        :return: True if timers or alarms with the given reference are running.
        """
        return botengine.is_timer_running(self.filter_id + str(reference))

    def cancel_timers(self, botengine, reference=""):
        """
        Cancel timers with the given reference
        :param botengine: BotEngine environment
        :param reference: Cancel all timers with the given reference
        """
        botengine.cancel_timers(self.filter_id + str(reference))

    def set_alarm(self, botengine, timestamp_ms, argument=None, reference=""):
        """
        Set an absolute alarm
        :param botengine: BotEngine environment
        :param timestamp_ms: Absolute time in milliseconds for the timer to fire
        :param argument: Optional argument to provide when the timer fires.
        :param reference: Optional reference to use to manage this timer.
        """
        # We seed the reference with this intelligence ID to make it unique against all other intelligence modules.
        bot.set_location_intelligence_alarm(botengine, timestamp_ms, self.filter_id, argument, self.filter_id + str(reference))
        
    def is_alarm_running(self, botengine, reference=""):
        """
        Check if a timer or alarm with the given reference is running
        :param botengine: BotEngine environment
        :param reference: Reference
        :return: True if timers or alarms with the given reference are running.
        """
        return botengine.is_timer_running(self.filter_id + str(reference))

    def cancel_alarms(self, botengine, reference=""):
        """
        Cancel alarms with the given reference
        :param botengine: BotEngine environment
        :param reference: Cancel all alarms with the given reference
        """
        # It's not a mistake that this is forwarding to `cancel_timers`.
        # They're all the same thing underneath, and this is a convenience method help to avoid confusion and questions.
        botengine.cancel_timers(self.filter_id + str(reference))

    #===============================================================================
    # Helper methods for data manipulation
    #===============================================================================
    def get_parameter(self, measurements, name, index=None):
        """
        Attempt to retrieve the parameter's dictionary object from the given measurements.

        This will automatically normalize the value on the way out, converting strings into
        integers, floats, and booleans whenever possible.

        For example:

            {
                "deviceId": "63a5f00e006f0d00",
                "name": "rssi",
                "time": 1634879938089,
                "updated": true,
                "value": "-80"   # This turns into the integer -80
            }

        :param measurements: Measurements
        :param name: Name of the parameter to search for
        :param index: Optional index to search for
        :return: The dictionary representing the parameter, if found.
        """
        for m in measurements:
            if m['name'] == name:
                if index is not None:
                    if 'index' in m:
                        if utilities.normalize_measurement(m['index']) == index:
                            m['value'] = utilities.normalize_measurement(m['value'])
                            return m
                else:
                    m['value'] = utilities.normalize_measurement(m['value'])
                    return m

        return None

    def generate_synthetic_parameter(self, botengine, device_object, parameter_name, value, index=None, timestamp_ms=None):
        """
        Generate a synthetic parameter.
        Inject it into our representative model and local cache, and trigger microservices to execute from this generated parameter.
        This will trigger the rest of the bot immediately before the filter gets done executing.

        :param botengine: BotEngine environment
        :param device_object: Device object to generate a synthetic parameter for
        :param parameter_name: Name of the parameter
        :param value: Value for the parameter
        :param index: Optional index identifier
        :param timestamp_ms: The default timestamp is the local time now. You can override this with the timestamp in milliseconds.
        """
        measurement = {
            "deviceId": device_object.device_id,
            "name": parameter_name,
            "value": value,
            "updated": True
        }

        if timestamp_ms is not None:
            measurement["time"] = timestamp_ms
        else:
            measurement["time"] = botengine.get_timestamp()

        if index is not None:
            measurement["index"] = index

        device_object.update(botengine, [measurement])
        self.parent.device_measurements_updated(botengine, device_object)