'''
Created on June 27, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from intelligence.intelligence import Intelligence

class DeviceEntrySensorMicroservice(Intelligence):
    """
    This is a "device microservice" that extends the capabilities of Entry Sensors only. Each one of your Entry Sensors device types
    will have a unique `DeviceEntrySensorMicroservice` object instantiated and attached to it.

    When any of the device_* event methods are triggered, you can be guaranteed that it is only triggering off of
    a single entry sensor in your account and not triggering off of any other devices other than the one it's attached to.

    To try it out: attach an entry sensor to your account, and then open / close it.  You will see the entry sensor's own
    `DeviceEntrySensorMicroservice` microservice trigger, and you will also see the location_realtimedata_microservice trigger
    because location microservices listen to all devices and data in your account.
    

    ---

    In any index.py file in your project, you declare which device microservices should get added to specific device types.
    As individual devices appear in your account that are of the device type referenced in your index.py files, device microservices
    are dynamically instantiated and applied to those devices. These microservices begin listening to events that happen in the real-world
    by triggering well defined methods inside. Your job is to react to the events you care about.

    The event-driven methods found in this class are simply copy/pasted from the intelligence.py file.

    In a device microservice, you can get access to the parent device object at any time by referencing the 'self.parent' class variable.
    You can explore the Device object inside com.ppc.Bot/devices/device.py. The other directories in that folder contain other Device objects
    that simply extend the Device class to provide some device-specific features for that particular type of device.
    You can access information about a device like this:

        self.parent.description         : The name of the device
        self.parent.device_id           : The globally unique ID of this device
        self.parent.location_object     : The Location object that this device belongs to, so you can interact with other data or devices in the user's home.
        self.parent.is_connected        : True if the device is currently connected
        self.parent.proxy_id            : The device ID of the gateway / proxy that this device connects through, if any.
        self.parent.remote_addr_hash    : The hashed IP address of this device (or the gateway/proxy it connects through), so you can see if 2 devices are at the same physical location.
        self.parent.goal_id             : An ID that represents the context / scenario the user selected when installing the device.
        self.parent.latitude            : The approximate latitude of the device (within about ~5-10 miles)
        self.parent.longitude           : The approximate longitude of the device (within about ~5-10 miles)
        self.parent.measurements        : A dictionary of cached recent measurements from this device, typically from within 1 hour ago.


    A device microservices reacts to the following events:
      * __init__()                      : Constructor that is called exactly once at the time the microservice is created.
      * initialize()                    : Initialize method called every single time the bot executes, before any other event
      * destroy()                       : The microservice is disappearing, probably because the device got deleted or the developer removed the microservice from the index.py file.
      * get_html_summary()              : Event-driven method to get HTML content for weekly summaries and test emails to end users.
      * mode_updated()                  : Event-driven method declaring the user's mode got updated at the UI level.
      * question_answered()             : The user answered a question.
      * datastream_updated()            : A data stream message was received
      * schedule_fired()                : A cron schedule fired
      * timer_fired()                   : A timer or alarm fired

    The following methods only trigger when the 'parent' device is updated (unlike a 'location microservice' which triggers off of every device):
      * device_measurements_updated()   : The parent device sent a new measurement.
      * device_metadata_updated()       : The parent device updated some metadata (like the description, goals/scenarios/context, etc.)
      * device_alert()                  : The parent device sent an alert, typically used in cameras.
      * device_deleted()                : The parent device got deleted.
      * file_uploaded()                 : The parent device uploaded a file.
      * coordinates_updated()           : The parent device's coordinates (lat/long) were updated)

    Note the nomenclature of the filename.  device_***_microservice.py.  This helps you, the developer, realize that this is a microservice
    and it listens to a specific device, and its 'self.parent' is a specific device object.
    """
    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        # Microservices extend the Intelligence class, which can be found in com.ppc.Bot/intelligence/intelligence.py
        # Always initialize your parent Intelligence class at the beginning!
        # This will generate a unique ID for your microservice, and assign your 'self.parent' object.
        # Device microservice's parent object is an actual Device object which will be an extension of the Device class found in com.ppc.Bot/devices/device.py.
        # Location microservice's parent object is the Location object found in com.ppc.Bot/locations/location.py.
        Intelligence.__init__(self, botengine, parent)

    def initialize(self, botengine):
        """
        Initialize
        :param botengine: BotEngine environment
        """
        # Uncomment if you want proof that this initialize() method gets called on every single microservice when the bot is triggered from new data.
        # botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: initialize()")
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: destroy()")
        return

    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: get_html_summary(oldest_timestamp_ms={}, newest_timestamp_ms={})".format(oldest_timestamp_ms, newest_timestamp_ms))
        return ""

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        botengine.get_logger().info("{}DEVICE_realtimedata_microservice {}: mode_updated('{}'){}".format(Color.BOLD + Color.CYAN, self.intelligence_id, current_mode, Color.END))
        return

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # The device_object is guaranteed to be an EntryDevice (see com.ppc.Bot/devices/entry/entry.py) because the index.py says this device microservice
        # should attach to entry sensors only.  So each entry sensor gets a unique instance of this DeviceEntrySensorMicroservice object attached to it.
        # The self.intelligence_id isn't useful here, but I bring it out to show you that each device's microservice is different than the rest.

        # I've added in my handy "Color" class at the bottom of this file to format the text output so you can see it better.
        # As you can see, Microservice files can have multiple class definitions inside, which is why it's important for the index.py to call out exactly
        # which class is the real microservice class inside this Python module.

        # Note that devices send measurements that are heartbeats (keep alives). So just because you got a measurement from a device doesn't mean that the device actually changed state.

        if device_object.did_change_state(botengine):
            if device_object.is_open(botengine):
                botengine.get_logger().info("{}DEVICE_ENTRYSENSOR_microservice {}: Your '{}' opened!{}".format(Color.BOLD + Color.GREEN, self.intelligence_id, device_object.description, Color.END))
            else:
                botengine.get_logger().info("{}DEVICE_ENTRYSENSOR_microservice {}: Your '{}' closed!{}".format(Color.BOLD + Color.GREEN, self.intelligence_id, device_object.description, Color.END))
        else:
            botengine.get_logger().info("{}DEVICE_ENTRYSENSOR_microservice {}: Your '{}' sent a heartbeat but didn't change state.{}".format(Color.BOLD + Color.RED, self.intelligence_id, device_object.description, Color.END))

        return

    def device_metadata_updated(self, botengine, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # Device metadata can get updated multiple times in one execution. Uncomment this line if you'd like to see it.
        #botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: device_metadata_updated from '{}'".format(device_object.description))
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
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice {}: device_alert from '{}': alert_type={}; alert_params={}".format(self.intelligence_id, device_object.description, str(alert_type), str(alert_params)))
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice {}: device_deleted() from '{}'".format(self.intelligence_id, device_object.description))
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: question_answered()")
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: datastream_updated(address={}, content={})".format(address, content))
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: schedule_fired(schedule_id={})".format(schedule_id))
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: timer_fired(argument={})".format(argument))
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
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: file_uploaded from device '{}'".format(device_object.description))
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        botengine.get_logger().info("DEVICE_ENTRYSENSOR_microservice: coordinates_updated(latitude={}, longitude={})".format(latitude, longitude))
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

