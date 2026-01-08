'''
Created on June 30, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class
from intelligence.intelligence import Intelligence

class DeviceEntryNotificationMicroservice(Intelligence):
    """
    This microservice will send a push notification with an alarm sound if your door opens while you are in AWAY mode.
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
        return


    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # The self.parent object is an EntryDevice (com.ppc.Bot/devices/entry/entry.py)
        # The EntryDevice extends Device (com.ppc.Bot/devices/device.py)
        # The Device object contains a reference to its location_object it is a part of.
        # The Location object tracks the current mode of the location.
        if device_object.did_change_state(botengine) and device_object.is_open(botengine) and ("HOME" not in self.parent.location_object.mode):
            botengine.notify(push_content="Your door opened while you were in {} mode!".format(self.parent.location_object.mode), push_sound="alarm.wav")


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

