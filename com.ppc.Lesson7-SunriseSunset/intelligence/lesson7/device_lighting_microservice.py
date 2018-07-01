'''
Created on July 1, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class
from intelligence.intelligence import Intelligence

class DeviceLightingMicroservice(Intelligence):
    """
    This microservice will listen for 'sunset_fired' and 'sunrise_fired' data stream messages which are distributed from the 'daylight' microservice.
    It will turn on the lights at sunset and turn them back off again at sunrise to show an example of how sunrise and sunset work.
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
        When a device disconnects, it will send an alert like this:  [{u'alertType': u'status', u'params': [{u'name': u'deviceStatus', u'value': u'2'}], u'deviceId': u'eb10e80a006f0d00'}]
        When a device reconnects, it will send an alert like this:  [{u'alertType': u'on', u'deviceId': u'eb10e80a006f0d00'}]
        :param botengine: BotEngine environment
        :param device_object: Device object that sent the alert
        :param alert_type: Type of alert
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
        # Forward 'sunrise_fired' and 'sunset_fired' data stream messages to the appropriate methods in this class
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

    #===============================================================================
    # The sunrise_fired() and sunset_fired() data stream messages require your bot to include the 'daylight' microservice.
    #===============================================================================
    def sunrise_fired(self, botengine, content=None):
        """
        Data stream message from the internal 'daylight' microservice indicating it is now sunrise.
        :param botengine: BotEngine environment
        :param content: Data stream message content - a dictionary containing "proxy_id"
        """

        # The 'sunset_fired' data stream message should always contain a 'proxy_id' in its content dictionary.
        # Sunrise and Sunset is relative to the approximate physical location of each gateway.
        # Because you can technically have gateways in different parts of the world, it's important to verify
        # that any device you're intending to react to sunrise or sunset events goes through that gateway as its proxy.
        # The Device object maintains a "proxy_id" class variable which tracks who its gateway is, and this proxy_id
        # should be compared to the content['proxy_id'] to make sure that sunset or sunrise data stream messages
        # apply to each device that may react.

        # It's always good practice to write defensive code like this.
        if 'proxy_id' not in content:
            # Malformed data stream message.
            return

        # If this light is connected through the gateway where it is sunrise, then turn this light off.
        if self.parent.proxy_id == content['proxy_id']:
            self.parent.off()


    def sunset_fired(self, botengine, content=None):
        """
        Data stream message from the internal 'daylight' microservice indicating it is now sunset.
        :param botengine: BotEngine environment
        :param content: Data stream message content - a dictionary containing "proxy_id"
        """

        # The 'sunset_fired' data stream message should always contain a 'proxy_id' in its content dictionary.
        # Sunrise and Sunset is relative to the approximate physical location of each gateway.
        # Because you can technically have gateways in different parts of the world, it's important to verify
        # that any device you're intending to react to sunrise or sunset events goes through that gateway as its proxy.
        # The Device object maintains a "proxy_id" class variable which tracks who its gateway is, and this proxy_id
        # should be compared to the content['proxy_id'] to make sure that sunset or sunrise data stream messages
        # apply to each device that may react.

        # It's always good practice to write defensive code like this.
        if 'proxy_id' not in content:
            # Malformed data stream message.
            return

        # If this light is connected through the gateway where it is sunrise, then turn this light on.
        if self.parent.proxy_id == content['proxy_id']:
            self.parent.on()



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


