'''
Created on June 30, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# All microservices must extend the Intelligence class
from intelligence.intelligence import Intelligence

# Import an EntryDevice so we can see if the device that's currently sending a measurement is an instance of this.
from devices.entry.entry import EntryDevice


class LocationDoorsAndLightingMicroservice(Intelligence):
    """
    This class will turn on() all lights and smart plugs when the door opens, and turn off() all lights and smart plugs when the door closes.

    When you switch to a mode where the user is not home, the state of your lights and smart plugs will be saved, and then they'll turn off.
    When you switch back to HOME mode, the lights and smart plugs will be restored to how they were before the user left HOME mode.

    Now that you should be familiar with the workings of a microservice, we'll remove all the excess comments and logger methods, and
    build this more like a professionally written microservice.

    Explore com.ppc.Bot/devices/... directories to see what control methods are provided by various devices.

    I recommend checking out the following devices to explore what can be controlled and how:

        * com.ppc.Bot/devices/camera/camera_peoplepower_presence.py     - Provides control methods for all cameras provided by your smartphone app (use your spare smartphone as a security camera).
        * com.ppc.Bot/devices/light/light.py                            - Base class for lighting controls (on / off / save / restore / hue / saturation / brightness)
        * com.ppc.Bot/devices/lock/lock.py                              - Control smart locks (i.e. Kwikset 916 Smart Lock) (lock / unlock)
        * com.ppc.Bot/devices/siren/siren_linkhigh.py                   - Controls MyPlace / People Power sirens (play sounds, blink lights)
        * com.ppc.Bot/smartplug/smartplug.py                            - Base class for smart plug devices (on / off / save / restore)
        * com.ppc.Bot/thermostat/thermostat.py                          - Base class for thermostat devices (control modes, set points, energy efficiency and demand response policies)
        * com.ppc.Bot/touchpad/touchpad_peoplepower.py                  - Touchpad (play sounds, send notifications to the touchpad)

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
        # Remember this is a location microservice, so self.parent refers to a Location object found at com.ppc.Bot/location/location.py.

        # We could explicitly check the mode, but our parent Location object provides some helper methods to generally know if people are home or not.

        if not self.parent.is_present(botengine):
            # People are away from home - save states and turn off all lights and smart plugs

            # Below is a style of Python coding called 'duck-typing'.
            # Our objective here is to save and turn off all lights and smart plugs that are in this user's location.
            # So we iterate through each device in the location, and try to call save() and off(), wrapped in a try-catch block.
            # If the object does not provide the save() or off() methods, then an exception is thrown. We don't care. Just keep going.
            # This saves a step of checking to see what type of device this is before we attempt to turn it off.
            for device_id in self.parent.devices:
                try:
                    self.parent.devices[device_id].save(botengine)
                    self.parent.devices[device_id].off(botengine)

                except:
                    # This isn't a light bulb or smart plug device, ignore it and keep going.
                    pass

        else:
            # People are home - restore all lights and smart plugs back to where they were before the user left home

            # Again, duck-type our way through restoring everything back to where it was before the user left home.
            # Since the device objects have some memory, if save() was never called then restore() will do nothing.
            for device_id in self.parent.devices:
                try:
                    self.parent.devices[device_id].restore(botengine)

                except:
                    # This isn't a light bulb or smart plug device, ignore it and keep going.
                    pass


    def device_measurements_updated(self, botengine, device_object):
        """
        Device was updated
        :param botengine: BotEngine environment
        :param device_object: Device object that was updated
        """
        # Location intelligence modules are used to coordinate activities of multiple devices within a single location,
        # instead of trying to add new features to a single device.

        # Here we want to implement the behavior that when a door opens, the lights and smart plugs will turn on.
        # And when the door closes, lights and smart plugs will turn off.

        # CHALLENGE: Try editing this file to switch the input from doors to motion sensors.
        # If motion is detected, turn on lights and smart plugs. When motion stops being detected, turn off lights and smart plugs.

        if isinstance(device_object, EntryDevice):
            # An entry sensor sent us a measurement.

            if device_object.did_change_state(botengine):
                # This entry sensor opened or closed right now.

                if device_object.is_open(botengine):
                    # It just opened. Duck-type our way through turning all the lights and smart plugs on.
                    # See the comments in the mode_updated() method for more info.
                    for device_id in self.parent.devices:
                        try:
                            self.parent.devices[device_id].on(botengine)
                        except:
                            # This isn't a light bulb or smart plug device, ignore it and keep going.
                            pass

                else:
                    # It just closed. Again, duck-type our way through turning all the lights and smart plugs off.
                    for device_id in self.parent.devices:
                        try:
                            self.parent.devices[device_id].off(botengine)
                        except:
                            # This isn't a light bulb or smart plug device, ignore it and keep going.
                            pass


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

