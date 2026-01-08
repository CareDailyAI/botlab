'''
Created on June 27, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class. Muscle memory: import it like this.
from intelligence.intelligence import Intelligence

# Import an EntryDevice so we can see if the device that's currently sending a measurement is an instance of this.
from devices.entry.entry import EntryDevice

# Import a MotionDevice so we can see if the device that's currently sending a measurement is an instance of this.
from devices.motion.motion import MotionDevice

# This is your microservice class, which extends the Intelligence class found in com.ppc.Bot/intelligence/intelligence.py
class LocationRealTimeDataMicroservice(Intelligence):
    """
    This is a "location microservice". Location microservices add new services across one or more devices and data sources in your account.
    A location typically represents a physical place, like your home.

    In any index.py file in your project, you declare which location microservices should get added to the project.
    Location microservices are added to any and every location that is being tracked in your account. Most accounts today have only 1 official location,
    but we do support scenarios already where a user has multiple homes, or multiple offices, etc.

    These microservices begin listening to events that happen in the real-world by triggering well defined methods.
    Your job is to react to the events you care about.

    The event-driven methods found in this class are simply copy/pasted from the intelligence.py file.

    In a location microservice, you can get access to the parent Location object at any time by referencing the 'self.parent' class variable.
    Investigating com.ppc.Bot/locations/location.py, you'll see the Location object provides some helper methods, and also maintains
    a dictionary of devices that are associated with that location. You can get access to individual devices dictionary by accessing self.parent.devices[device_id].
    There are other helper methods to explore in the Location object, which we demonstrate in future lessons.

    Here are some Location object variables you might be interested in from the level of a location microservice:

        self.parent.location_id         : The globally unique reference ID of this location.
        self.parent.devices             : Dictionary of devices associated with this location. The key is a globally unique device_id, the value is a device object.
        self.parent.mode                : The user's mode as selected in the UI.


    A location microservices reacts to the following events:
      * __init__()                      : Constructor that is called exactly once at the time the microservice is created.
      * initialize()                    : Initialize method called every single time the bot executes, before any other event
      * destroy()                       : The microservice is disappearing, probably because the device got deleted or the developer removed the microservice from the index.py file.
      * get_html_summary()              : Event-driven method to get HTML content for weekly summaries and test emails to end users. This content typically appears at the top of the email.
      * mode_updated()                  : Event-driven method declaring the user's mode got updated at the UI level.
      * question_answered()             : The user answered a question.
      * datastream_updated()            : A data stream message was received
      * schedule_fired()                : A cron schedule fired
      * timer_fired()                   : A timer or alarm fired

    The following methods whenever ANY device inside the location is updated:
      * device_measurements_updated()   : A device sent a new measurement.
      * device_metadata_updated()       : A device updated some metadata (like the description, goals/scenarios/context, etc.)
      * device_alert()                  : A device sent an alert, typically used in cameras.
      * device_deleted()                : A device got deleted.
      * file_uploaded()                 : A device uploaded a file.
      * coordinates_updated()           : A device's coordinates (lat/long) were updated)

    Note the nomenclature of the filename.  location_***_microservice.py.  This helps you, the developer, realize that this is a microservice
    and it listens to all devices across a location, and its 'self.parent' is a specific Location object.
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
        # botengine.get_logger().info("LOCATION_realtimedata_microservice: initialize()")
        return

    def destroy(self, botengine):
        """
        This device or object is getting permanently deleted - it is no longer in the user's account.
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: destroy()")
        return

    def get_html_summary(self, botengine, oldest_timestamp_ms, newest_timestamp_ms, test_mode=False):
        """
        Return a human-friendly HTML summary of insights or status of this intelligence module to report in weekly and test mode emails
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp in milliseconds to summarize
        :param newest_timestamp_ms: Newest timestamp in milliseconds to summarize
        :param test_mode: True to add or modify details for test mode, instead of a general weekly summary
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: get_html_summary(oldest_timestamp_ms={}, newest_timestamp_ms={})".format(oldest_timestamp_ms, newest_timestamp_ms))
        return ""

    def mode_updated(self, botengine, current_mode):
        """
        Mode was updated
        :param botengine: BotEngine environment
        :param current_mode: Current mode
        :param current_timestamp: Current timestamp
        """
        # You can always access the current mode with "self.parent.mode" when you're inside a location intelligence module, because the parent is the location and the location keeps the current mode.
        botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: mode_updated('{}'){}".format(Color.BOLD + Color.CYAN, self.intelligence_id, current_mode, Color.END))

    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """

        # Because this is a location intelligence module, it listens to all devices in this location.
        # So if we want to do something specific with a particular device, we check out what type of device_object got passed in here.
        # Check out the imports at the top to see how to import device classes.

        # Note that devices send measurements that are heartbeats (keep alives). So just because you got a measurement from a device doesn't mean that the device actually changed state.

        if isinstance(device_object, EntryDevice):
            # This is an entry sensor, so now we can call EntrySensor specific methods.
            if device_object.is_open():
                botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: Your '{}' sent a measurement, and it is currently open.{}".format(Color.BOLD + Color.GREEN, self.intelligence_id, device_object.description, Color.END))
            else:
                botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: Your '{}' sent a measurement, and it is currently closed.{}".format(Color.BOLD + Color.GREEN, self.intelligence_id, device_object.description, Color.END))

        elif isinstance(device_object, MotionDevice):
            # This is a motion sensor so now we can call MotionSensor specific methods.
            if device_object.is_detecting_motion():
                botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: Your '{}' sent a measurement, and it is currently detecting motion.{}".format(Color.BOLD + Color.PURPLE, self.intelligence_id, device_object.description, Color.END))
            else:
                botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: Your '{}' sent a measurement, and it is currently not detecting motion.{}".format(Color.BOLD + Color.PURPLE, self.intelligence_id, device_object.description, Color.END))

        else:
            botengine.get_logger().info("{}LOCATION_realtimedata_microservice {}: Device '{}' measurements were updated!{}".format(Color.BOLD, self.intelligence_id, device_object.description, Color.END))

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
        botengine.get_logger().info("LOCATION_realtimedata_microservice: device_alert from '{}': alert_type={}; alert_params={}".format(device_object.description, str(alert_type), str(alert_params)))
        return

    def device_deleted(self, botengine, device_object):
        """
        Device is getting deleted
        :param botengine: BotEngine environment
        :param device_object: Device object that is getting deleted
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: device_deleted() from '{}'".format(device_object.description))
        return

    def question_answered(self, botengine, question):
        """
        The user answered a question
        :param botengine: BotEngine environment
        :param question: Question object
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: question_answered()")
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: datastream_updated(address={}, content={})".format(address, content))
        return

    def schedule_fired(self, botengine, schedule_id):
        """
        The bot executed on a hard coded schedule specified by our runtime.json file
        :param botengine: BotEngine environment
        :param schedule_id: Schedule ID that is executing from our list of runtime schedules
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: schedule_fired(schedule_id={})".format(schedule_id))
        return

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: timer_fired(argument={})".format(argument))
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
        botengine.get_logger().info("LOCATION_realtimedata_microservice: file_uploaded from device '{}'".format(device_object.description))
        return

    def coordinates_updated(self, botengine, latitude, longitude):
        """
        Approximate coordinates of the parent proxy device object have been updated
        :param latitude: Latitude
        :param longitude: Longitude
        """
        botengine.get_logger().info("LOCATION_realtimedata_microservice: coordinates_updated(latitude={}, longitude={})".format(latitude, longitude))
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

