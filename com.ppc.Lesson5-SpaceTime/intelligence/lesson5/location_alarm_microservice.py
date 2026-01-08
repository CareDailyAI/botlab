'''
Created on June 30, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class
from intelligence.intelligence import Intelligence


# It's always good practice to define states and strings as local variables to avoid typos

# When our timer/alarm fires, this argument will pop out and let us it fired because it's midnight
ARGUMENT_STATE_MIDNIGHT = "MIDNIGHT"

# Example of a unique reference so we can cancel the alarm or check if it's running. We could just use the argument shown above in most cases, but this works too.
REFERENCE_MIDNIGHT = "midnight_alarm"



class LocationAlarmMicroservice(Intelligence):
    """
    This microservice will set an alarm for midnight tonight when you change modes.
    If running locally, you'll see the output from helper methods provided by this location microservice's parent Location object.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        # Always initialize your parent Intelligence class at the beginning
        Intelligence.__init__(self, botengine, parent)


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

    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        return ""

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        # Set a new alarm for midnight tonight.
        # Typically in a situation this simple, I'll simply use the unique state argument as the reference. But just for this example I'll keep them separate.
        midnight_dt = self.parent.get_midnight_tonight(botengine)
        midnight_timestamp_ms = self.parent.timezone_aware_datetime_to_unix_timestamp(botengine, midnight_dt)

        self.set_alarm(botengine, midnight_timestamp_ms, reference=REFERENCE_MIDNIGHT)
        botengine.get_logger().info("{}device_entrysensor_microservice : Mode changed and an alarm has been set for the absolute unix timestamp {} [ms]{}".format(Color.BOLD, midnight_timestamp_ms, Color.END))
        botengine.get_logger().info("{}device_entrysensor_microservice : Here's some extra info from our Location object:{}".format(Color.BOLD, Color.END))
        botengine.get_logger().info("\tget_local_datetime() = {}".format(self.parent.get_local_datetime(botengine)))
        botengine.get_logger().info("\tget_local_timezone_string() = {}".format(self.parent.get_local_timezone_string(botengine)))
        botengine.get_logger().info("\tget_relative_time_of_day() = {}".format(self.parent.get_relative_time_of_day(botengine)))
        botengine.get_logger().info("\tget_midnight_last_night() = {}".format(self.parent.get_midnight_last_night(botengine)))
        botengine.get_logger().info("\tget_midnight_tonight() = {}".format(self.parent.get_midnight_tonight(botengine)))
        botengine.get_logger().info("\tget_local_hour_of_day() = {}".format(self.parent.get_local_hour_of_day(botengine)))
        botengine.get_logger().info("\tget_local_day_of_week() = {}".format(self.parent.get_local_day_of_week(botengine)))

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
        # Device metadata can get updated multiple times in one execution. Uncomment this line if you'd like to see it.
        #botengine.get_logger().info("LOCATION_realtimedata_microservice: device_metadata_updated from '{}'".format(device_object.description))
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

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        return

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
        botengine.get_logger().info("{}It's midnight!{}".format(Color.BOLD + Color.GREEN, Color.END))
        botengine.notify(push_content="It's midnight!")

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


class Color:
    """Color your command line output text with Color.WHATEVER and Color.END"""
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


