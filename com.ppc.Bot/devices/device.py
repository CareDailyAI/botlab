'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import utilities
import intelligence.index
import importlib

# This is the maximum number of elements we'll average over for RSSI and LQI readings
MAXIMUM_AVERAGING_ELEMENTS = 25

# Maximum number of attempts for any one command
MAX_ATTEMPTS = 20

# Time between attempts, in seconds
TIME_BETWEEN_ATTEMPTS_SEC = 30

# Reliability variable name so we prevent typos
RELIABILITY_VARIABLE_NAME = "reliability"

# Total duration of time in which we should cache measurements here locally. Larger = slower to download, faster to execute.
TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS = utilities.ONE_HOUR_MS

# Take a battery reading every 4 hours
BATTERY_MEASUREMENT_PERIODICITY_MS = utilities.ONE_HOUR_MS * 6

# Minimum number of battery readings required to make a decision on the battery life - 3 days worth
MINIMUM_BATTERY_READINGS = 10

# Total number of battery readings to maintain
MAXIMUM_BATTERY_READINGS = MINIMUM_BATTERY_READINGS * 2


class Device:
    """This is a base class for each of our devices"""
        
    # Low battery tag - Override in sub-classes to make it more specific
    LOW_BATTERY_TAG = "lowbattery"
    
    # Low signal strength tag
    LOW_SIGNAL_STRENGTH_TAG = "weaksignal"

    # Low battery threshold - Override in sub-classes
    LOW_BATTERY_THRESHOLD = 10
        
    # Low signal strength threshold - Override in sub-classes
    LOW_RSSI_THRESHOLD = -80
    
    # List of Device Types this class is compatible with - Specify in sub-classes
    DEVICE_TYPES = []
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine: BotEngine environment
        :param device_id: Device ID
        :param device_type: Device Type
        :param device_description: Device description (nickname)
        :param precache_measurements: True (default) to download historical measurements to cache them locally, the length of time of which is defined by device.TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS
        """
        # Device ID
        self.device_id = device_id.encode('utf-8')
        
        # Device type
        self.device_type = int(device_type)
        
        # Device description
        self.description = device_description.encode('utf-8').strip()
        
        # This is set by the controller object after init during synchronization with the location
        self.location_object = None
        
        # Measurements for each parameter, newest measurements at index 0
        self.measurements = {}
        
        # Last parameters that we updated
        self.last_updated_params = []
        
        # Battery level
        self.battery_level = 100

        # List of battery measured battery levels over time
        self.battery_levels = []

        # Last battery update time in ms
        self.last_battery_update_ms = 0

        # True if we have a low battery
        self.low_battery = False

        
        # RSSI averaging elements
        self._rssi_elements = []
        
        # List of arbitrary tags this device has
        self.tags = []
        
        # True if this device is currently connected
        self.is_connected = False
        
        # True if we can control this device
        self.can_control = False
        
        # True if we can read from this device
        self.can_read = False
        
        # Remote IP address hash. Devices connected to the same external IP address will have the same hash.
        self.remote_addr_hash = None
        
        # The proxy ID is the device ID of the gateway this device connects through, if any.
        self.proxy_id = None
        
        # The goal (scenario) ID for this device
        self.goal_id = None

        # Approximate latitude (available on devices that directly connect to the cloud, like gateways)
        self.latitude = None

        # Approximate longitude (available on devices that directly connect to the cloud, like gateways)
        self.longitude = None
        
        # Born on timestamp
        self.born_on = None
        
        # True to enforce the default cache size. This can be reconfigured externally, followed by a call to garbage collect when needed to get rid of excess cache.
        self.enforce_cache_size = precache_measurements
        
        # Total communications odometer (includes measurements and RSSI updates / check-ins)
        self.total_communications_odometer = 0
        
        # Trip communications odometer - see how many communications we received in a shorter period of time, including RSSI check-ins
        self.communications_odometer = 0
        
        # Measurement odometer - how many actual new measurements did we receive
        self.measurement_odometer = 0
        
        # Timestamp of the last time we received a communication from this device
        self.last_communications_timestamp = None
        
        # Every device gets a dictionary of intelligence modules, and can populate these intelligence modules in each device model
        self.intelligence_modules = {}

        if precache_measurements:
            # Download and start this object out with a history of measurements
            self.cache_measurements(botengine, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS, botengine.get_timestamp())

        # initialize(...) gets called in controller.py, after this device is finished syncing with the system.

        
    def initialize(self, botengine):
        """
        Initialize this object
        
        The correct behavior is to create the object, then initialize() it every time you want to use it in a new bot execution environment
        """
        # Added March 28, 2018
        if not hasattr(self, 'battery_levels'):
            # List of battery measured battery levels over time
            self.battery_levels = []

        # Added March 28, 2018
        if not hasattr(self, 'last_battery_update_ms'):
            # Last update time in ms
            self.last_battery_update_ms = 0

        # Added March 28, 2018
        if not hasattr(self, 'low_battery'):
            # True if we have a low battery
            self.low_battery = False

        # Added April 14, 2018
        if not hasattr(self, 'latitude'):
            self.latitude = None

        # Added April 14, 2018
        if not hasattr(self, 'longitude'):
            self.longitude = None

        if str(self.device_type) in intelligence.index.MICROSERVICES['DEVICE_MICROSERVICES']:

            # Synchronize microservice capabilities
            if len(self.intelligence_modules) != len(intelligence.index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]):

                # Add more microservices
                # Example of an element in the DEVICE_MICROSERVICES dictionary:
                # 10014: [{"module": "intelligence.rules.device_entry_microservice", "class": "EntryRulesMicroservice"}],
                for intelligence_info in intelligence.index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]:
                    if intelligence_info['module'] not in self.intelligence_modules:
                        try:
                            intelligence_module = importlib.import_module(intelligence_info['module'])
                            class_ = getattr(intelligence_module, intelligence_info['class'])
                            botengine.get_logger().info("\tAdding device microservice: " + str(intelligence_info['module']))
                            intelligence_object = class_(botengine, self)
                            self.intelligence_modules[intelligence_info['module']] = intelligence_object
                        except:
                            botengine.get_logger().error("\tCould not add device microservice: " + str(intelligence_info))
                            import traceback
                            traceback.print_exc()


                # Remove microservices that no longer exist
                for module_name in self.intelligence_modules.keys():
                    found = False
                    for intelligence_info in intelligence.index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]:
                        if intelligence_info['module'] == module_name:
                            found = True
                            break

                    if not found:
                        botengine.get_logger().info("\tDeleting device microservice: " + str(module_name))
                        del self.intelligence_modules[module_name]


            for i in self.intelligence_modules:
                self.intelligence_modules[i].parent = self
                self.intelligence_modules[i].initialize(botengine)

        elif len(self.intelligence_modules) > 0:
            # There are no intelligence modules for this device type, and yet we have some intelligence modules locally. Delete everything.
            botengine.get_logger().info("\tDeleting all device microservices")
            self.intelligence_modules = {}

    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Super abstract device type name
        return _("Device")
    
    def get_image_name(self, botengine=None):
        """
        :return: the font icon name of this device type
        """
        raise NotImplementedError
    

    #===========================================================================
    # Measurement synchronization and updates
    #===========================================================================
    def synchronize(self, botengine):
        """
        Synchronize with the server
        :param botengine: BotEngine environment
        """
        self.cache_measurements(botengine, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS, botengine.get_timestamp())
        
    def cache_measurements(self, botengine, oldest_timestamp_ms, newest_timestamp_ms):
        """
        Download and cache historical measurements locally
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Oldest timestamp to download history from
        :param newest_timestamp_ms: Newest timestamp to download history to
        """
        try:
            measurements = botengine.get_measurements(self.device_id, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms)

        except:
            # This can happen because this bot may not have read permissions for this device.
            botengine.get_logger().warning("Cannot synchronize measurements for device: " + str(self.description))
            return

        botengine.get_logger().info("Synchronizing measurements for device: " + str(self.description))

        if 'measures' in measurements:
            for measure in measurements['measures']:
                if 'value' not in measure:
                    #botengine.get_logger().error("device.py: Measurement has no value: " + str(measure) + ";\n Measurement was: " + str(measure))
                    continue

                value = utilities.normalize_measurement(measure['value'])
                param_name = measure['name']
                time = measure['time']

                # If there's an index number, we just augment the parameter name with the index number to make it a unique parameter name.  param_name.index
                if 'index' in measure:
                    if measure['index'] is not None:
                        if measure['index'].lower() != "none":
                            param_name = "{}.{}".format(param_name, measure['index'])

                if param_name in self.measurements:
                    if self.measurements[param_name][0][0] == value and self.measurements[param_name][0][1] == time:
                        # Already captured this measurement
                        continue

                self.add_measurement(botengine, param_name, value, time)


    def update(self, botengine):
        """
        Attempt to parse the inputs to update this object
        """
        self.last_updated_params = []
        self.communicated(botengine.get_timestamp())
        botengine.get_logger().info("Updating: " + self.description)

        measures = botengine.get_measures_block()
        
        if measures is not None:
            for measure in measures:
                if measure['deviceId'] == self.device_id:
                    param_name = measure['name']
                    if param_name == 'rssi':
                        if measure['updated']:
                            # Update the RSSI
                            rssi = int(measure['value'])
                            self.update_rssi(botengine, rssi)
                            self.last_updated_params.append('rssi')
                        else:
                            # RSSI didn't change
                            self.rssi_status_quo(botengine)
                    
                    elif param_name == 'batteryLevel' and measure['updated']:
                        # Update the battery_level
                        self.battery_level = int(measure['value'])
                        self.last_updated_params.append('batteryLevel')
                        self.evaluate_battery(botengine)
                        
                    elif param_name not in self.measurements or measure['updated']:
                        if 'value' not in measure:
                            #botengine.get_logger().error("device.py: Measurement has no value: " + str(measure) + ";\n Measures block was: " + str(botengine.get_measures_block()))
                            continue

                        value = utilities.normalize_measurement(measure['value'])

                        # If there's an index number, we just augment the parameter name with the index number to make it a unique parameter name.  param_name.index
                        if 'index' in measure:
                            if measure['index'] is not None:
                                if measure['index'].lower() != "none":
                                    param_name = "{}.{}".format(param_name, measure['index'])

                        self.add_measurement(botengine, param_name, value, measure['time'])
                        self.last_updated_params.append(param_name)

        # List of devices (this one and its proxy) that were updated, to later synchronize with the location outside of this object
        updated_devices = []
        updated_metadata = []

        # Update all device intelligence modules 
        if len(self.last_updated_params) > 0:
            updated_devices.append(self)

            # Measurements were updated
            for intelligence_id in self.intelligence_modules:
                self.intelligence_modules[intelligence_id].device_measurements_updated(botengine, self)
                
        else:
            # Metadata was updated
            updated_metadata.append(self)
            for intelligence_id in self.intelligence_modules:
                self.intelligence_modules[intelligence_id].device_metadata_updated(botengine, self)

        # Make sure our proxy (gateway) gets pinged - it implicitly updated here and needs to trigger microservices
        if self.proxy_id is not None:
            if self.proxy_id in self.location_object.devices:
                d, m = self.location_object.devices[self.proxy_id].update(botengine)
                updated_devices += d
                updated_metadata += m

        return (updated_devices, updated_metadata)

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

    def add_measurement(self, botengine, name, value, timestamp):
        """
        Update the device's status
        :param botengine:
        :param name:
        :param value:
        :param timestamp:
        :return:
        """
        #botengine.get_logger().info("{}: '{}': {}={}".format(self.device_id, self.description, name, value))
        self.measurement_odometer += 1

        if name not in self.measurements:
            # Create the measurement
            self.measurements[name] = []

        self.measurements[name].insert(0, (value, timestamp))

        # Auto garbage-collect
        if self.enforce_cache_size and len(self.measurements[name]) > 1:
            if self.measurements[name][-1][1] <= botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS:
                del(self.measurements[name][-1])


    def garbage_collect(self, botengine):
        """
        Clean up the garbage
        :param current_timestamp: Current timestamp in ms
        """
        current_timestamp = botengine.get_timestamp()
        for name in self.measurements:
            i = 0
            if len(self.measurements[name]) > 1:
                for (value, timestamp) in self.measurements[name]:
                    i += 1
                    if timestamp <= current_timestamp - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS:
                        del self.measurements[name][i:]
                        break

    def communicated(self, timestamp):
        """
        Call this function when the device communicates at all.
        This lets us evaluate how often the device communicates, how many times per day, communications during test mode, etc.
        """
        if self.last_communications_timestamp is not None:
            #self.log("\t=> Last communication was " + str((timestamp - self.last_communications_timestamp) / 1000) + " seconds ago")
            pass

        self.last_communications_timestamp = timestamp
        self.total_communications_odometer += 1
        self.communications_odometer += 1

    def reset_odometers(self):
        """
        Reset all our odometers except the total_communications_odometer
        For example, if we're entering TEST mode and want to keep track of communications
        """
        self.communications_odometer = 0
        self.measurement_odometer = 0


    #===========================================================================
    # Device health
    #===========================================================================
    def evaluate_battery(self, botengine):
        """
        This method is called automatically when we have an update that adjusts the battery level
        :param botengine:
        :return:
        """
        if not 'batteryLevel' in self.last_updated_params:
            return

        if self.last_battery_update_ms < botengine.get_timestamp() - BATTERY_MEASUREMENT_PERIODICITY_MS:
            # Newly replaced battery
            if self.low_battery and self.battery_level > 95:
                botengine.get_logger().info("Newly replaced battery in {}!".format(self.description))
                self.battery_levels = []
                self.low_battery = False
                botengine.delete_device_tag(self.LOW_BATTERY_TAG, self.device_id)

            self.battery_levels.insert(0, self.battery_level)

            # Remove the battery readings that are over our limit
            if len(self.battery_levels) > MAXIMUM_BATTERY_READINGS:
                self.battery_levels = self.battery_levels[:-1]

            if len(self.battery_levels) > MINIMUM_BATTERY_READINGS:
                average = int(sum(self.battery_levels)) / len(self.battery_levels)

                if average <= self.LOW_BATTERY_THRESHOLD and not self.low_battery:
                    # Tag it
                    botengine.tag_device(self.LOW_BATTERY_TAG, self.device_id)
                    self.low_battery = True

                elif average > self.LOW_BATTERY_THRESHOLD and self.low_battery:
                    # Remove the battery tag
                    botengine.delete_device_tag(self.LOW_BATTERY_TAG, self.device_id)
                    self.low_battery = False

    def update_rssi(self, botengine, rssi):
        """
        Update our RSSI readings
        :param rssi
        """
        self._rssi_elements.append(int(rssi))
        
        if len(self._rssi_elements) > MAXIMUM_AVERAGING_ELEMENTS:
            del self._rssi_elements[0]
            
        rssi_average = int(sum(self._rssi_elements) / len(self._rssi_elements))
        
        if rssi_average < self.LOW_RSSI_THRESHOLD:
            # Should be tagged
            if self.LOW_SIGNAL_STRENGTH_TAG not in self.tags:
                # Wasn't tagged before, tag it.
                botengine.tag_device(self.LOW_SIGNAL_STRENGTH_TAG, self.device_id)
                self.tags.append(self.LOW_SIGNAL_STRENGTH_TAG)
                
        else:
            # Shouldn't be tagged
            if self.LOW_SIGNAL_STRENGTH_TAG in self.tags:
                # Was tagged, delete it.
                botengine.delete_device_tag(self.LOW_SIGNAL_STRENGTH_TAG, self.device_id)
                self.tags.remove(self.LOW_SIGNAL_STRENGTH_TAG)
        
    def rssi_status_quo(self, botengine):
        """
        RSSI reading didn't change from last time, duplicate the last reading
        :param botengine:
        :return:
        """
        if len(self._rssi_elements) > 0:
            self.update_rssi(botengine, self._rssi_elements[-1])

    def device_alert(self, botengine, alert_type, alert_params):
        """
        Distribute an alert for this device to its intelligence modules
        :param botengine: BotEngine environment
        :param alert_type: Type of alert
        :param alert_params: Dictionary of alert parameters
        """
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].device_alert(botengine, self, alert_type, alert_params)

    def raw_command(self, name, value):
        """
        Send a command for the given local measurement name
        """
        pass
        
    def is_command(self, measurement_name):
        """
        :param measurement_name: Name of a local measurement name
        :return: True if the given parameter name is a command
        """
        return False

    def get_proxy_object(self, botengine=None):
        """
        :return: Gateway / Proxy object this device connects through.  None if it doesn't exist
        """
        if self.proxy_id is not None:
            if self.proxy_id in self.location_object.devices:
                return self.location_object.devices[self.proxy_id]

        return None

    #===========================================================================
    # Coordinates
    #===========================================================================
    def update_coordinates(self, botengine, latitude, longitude):
        """
        Update the latitude and longitude
        :param botengine: BotEngine environment
        :param latitude: Latitude
        :param longitude: Longitude
        """
        if float(latitude) == self.latitude and float(longitude) == self.longitude:
            return

        self.latitude = float(latitude)
        self.longitude = float(longitude)

        # Notify my microservices
        for intelligence_id in self.intelligence_modules:
            self.intelligence_modules[intelligence_id].coordinates_updated(botengine, latitude, longitude)

        # Notify all children microservices
        for device_id in self.location_object.devices:
            if self.location_object.devices[device_id].proxy_id == self.device_id:
                for intelligence_id in self.location_object.devices[device_id].intelligence_modules:
                    self.location_object.devices[device_id].intelligence_modules[intelligence_id].coordinates_updated(botengine, latitude, longitude)


    #===========================================================================
    # Daylight
    #===========================================================================
    def is_daylight(self, botengine):
        """
        REQUIRES THE 'daylight' MICROSERVICE.

        This is a convenience method that requires you to attach the 'daylight' microservice.
        It will then seek out this microservice for your device and ask it whether it's daylight outside or not.

        :param botengine:
        :return: True/False if daylight information can be accessed from the 'daylight' microservice; None if there is no information.
        """
        proxy_object = self.get_proxy_object(botengine)
        if proxy_object is not None:
            for intelligence_id in proxy_object.intelligence_modules:
                try:
                    daylight = proxy_object.intelligence_modules[intelligence_id].is_daylight(botengine)
                    if daylight:
                        botengine.get_logger().info("It is day time")
                    else:
                        botengine.get_logger().info("It is night time")

                    return daylight
                except:
                    pass

        return None


    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None, params=[]):
        """
        Get a .csv string of all the data

        This is useful when you're using .csv data from a user's account outside of the bot microservices environment to construct machine learning algorithms,
        and then want to drag-and-drop those same algorithms into a bot environment and watch it run the same way without having to transform data.

        Mimics the type of .csv output you'd obtain with the following CLI commands:

            botengine --download_device <device_id>
            botengine --download_type <device_type>

        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :param params: List of parameters
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        if len(self.measurements) == 0:
            botengine.get_logger().info("{}: get_csv() - This device has no measurements")
            return None

        if params:
            titles = sorted(params)
        else:
            titles = sorted(self.measurements.keys())

        last_measurements = {}

        for title in titles:
            try:
                last_measurements[title] = self.measurements[title][0][0]
            except:
                pass

        # Check to see that all the parameters we're requesting have valid measurements in this device object
        # Remember that an index number will modify the name of the parameter to make it unique, and we need to match against the unique name of each parameter
        if not set(params).issubset(last_measurements.keys()):
            botengine.get_logger().info("{}: get_csv() - Not all of the requested parameters exist for this device")
            return None

        output = "device_type,device_id,description,timestamp_ms,timestamp_iso,"

        for t in titles:
            output = "{}{},".format(output, t)

        output += "\n"

        try:
            measurements = botengine.get_measurements(self.device_id, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms, param_name=params)

        except:
            # This can happen because this bot may not have read permissions for this device.
            botengine.get_logger().warning("Cannot synchronize measurements for device: " + str(self.description))
            return None

        processed_readings = {}
        if 'measures' in measurements:
            for measure in measurements['measures']:
                if 'value' not in measure:
                    continue

                value = utilities.normalize_measurement(measure['value'])
                param_name = measure['name']
                time = int(measure['time'])

                # If there's an index number, we just augment the parameter name with the index number to make it a unique parameter name.  param_name.index
                if 'index' in measure:
                    if measure['index'] is not None:
                        if measure['index'].lower() != "none":
                            param_name = "{}.{}".format(param_name, measure['index'])

                processed_readings[time] = (param_name, value)

        measurements = None
        import gc
        gc.collect()

        botengine.get_logger().info("{}: get_csv() - Processing {} measurements ...".format(self.description, str(len(processed_readings))))

        for timestamp_ms in sorted(processed_readings.keys()):
            dt = self.location_object.get_local_datetime_from_timestamp(botengine, timestamp_ms)
            output += "{},{},{},{},{},".format(self.device_type, self.device_id, self.description, timestamp_ms, dt.isoformat())

            for t in titles:
                if t == processed_readings[timestamp_ms][0]:
                    output += "{},".format(processed_readings[timestamp_ms][1])
                else:
                    output += "{},".format(last_measurements[t])

            output += "\n"

        return output


#===============================================================================
# These functions are outside the Device class above.
#===============================================================================

def send_command_reliably(botengine, device_id, param_name, param_value):
    """
    Send a command reliably
    :param botengine: BotEngine
    :param device_id: Device ID to send the command to
    :param param_name: Parameter name
    :param param_value: Parameter value
    """
    botengine.get_logger().info("{}: Send command reliably".format(device_id))
    queue = botengine.load_variable(RELIABILITY_VARIABLE_NAME)
    if queue is None:
        queue = {}
        
    if device_id not in queue:
        queue[device_id] = {}
    
    botengine.send_commands(device_id, [botengine.form_command(param_name, param_value)])
    botengine.cancel_timers(device_id)
    botengine.start_timer(TIME_BETWEEN_ATTEMPTS_SEC, _attempt_reliable_delivery, None, "reliability")
    
    # queue[device_id] = {'param_name': ('param_value', attempts, timestamp)}
    if param_name in queue[device_id]:
        if queue[device_id][param_name][0] == param_value:
            # No need to update the timestamp
            return
    
    queue[device_id][param_name] = (param_value, 0, botengine.get_timestamp())
    botengine.save_variable(RELIABILITY_VARIABLE_NAME, queue)
    
def cancel_reliable_command(botengine, device_id, param_name):
    """
    Stop trying to send a command reliably
    :param botengine:
    :param device_id: Device ID
    :param param_name: Parameter name to cancel.
    :return:
    """
    queue = botengine.load_variable(RELIABILITY_VARIABLE_NAME)
    if queue is None:
        return

    if device_id in queue:
        if param_name in queue[device_id]:
            del(queue[device_id][param_name])

        if len(queue[device_id]) == 0:
            del(queue[device_id])

    botengine.save_variable(RELIABILITY_VARIABLE_NAME, queue)

def queued_commands_for_device(botengine, device_id):
    """
    Get the queued commands for the current device in a dictionary of the form:   { 'paramName': ('value', attempts, send_timestamp) , ... }
    Basically if this response isn't empty, then there are commands in the queue that haven't been verified yet.
    :return: Dictionary of commands in the queue, or a blank dictionary {} if there are no commands or the device isn't found
    """
    queue = botengine.load_variable(RELIABILITY_VARIABLE_NAME)
    
    if queue is not None:
        if device_id in queue:
            return queue[device_id]
    
    return {}

def _attempt_reliable_delivery(botengine, args):
    """
    Attempt reliable delivery of everything in our queue
    This is executed by a timer.
    """
    botengine.get_logger().info(">reliability")
    queue = botengine.load_variable(RELIABILITY_VARIABLE_NAME)
    if queue is None:
        return
    
    logger = botengine.get_logger()
    
    logger.debug("RELIABILITY: Queue looks like " + str(queue))

    import copy
    for device_id in copy.copy(queue):
        # Prune out all our successfully delivered commands, and commands that have timed out
        params_to_remove = []
        
        for param_name in queue[device_id]:
            (param_value, attempts, timestamp) = queue[device_id][param_name]

            if attempts < MAX_ATTEMPTS:
                # Check to see if the last attempt went through
                measures = None
                try:
                    measures = botengine.get_measurements(device_id, param_name=param_name, oldest_timestamp_ms=timestamp)
                except:
                    # No longer have access to the device
                    params_to_remove.append(param_name)

                logger.debug("RELIABILITY: measurements since " + str(timestamp) + ": " + str(measures))

                if measures is not None:
                    if 'measures' in measures:
                        for m in measures['measures']:
                            if m['name'] == param_name and m['value'] == param_value:
                                # Command had been delivered reliably
                                logger.debug("RELIABILITY: COMMAND HAS BEEN DELIVERED RELIABLY")
                                params_to_remove.append(param_name)
                                break
                
            else:
                # TODO log this error somewhere
                logger.debug("RELIABILITY: MAXIMUM ATTEMPTS REACHED FOR DEVICE " + str(device_id) + "; PARAM_NAME=" + str(param_name) + "; PARAM_VALUE=" + str(param_value))
                params_to_remove.append(param_name)
                
        for param in params_to_remove:
            if param in queue[device_id]:
                del(queue[device_id][param])
                
        if len(queue[device_id]) > 0:
            botengine.cancel_timers("reliability")
            botengine.start_timer(TIME_BETWEEN_ATTEMPTS_SEC, _attempt_reliable_delivery, None, "reliability")
            
            for param_name in queue[device_id]:
                # Increment our attempts
                (param_value, attempts, timestamp) = queue[device_id][param_name]
                attempts += 1
                queue[device_id][param_name] = (param_value, attempts, timestamp)
                logger.debug("RELIABILITY: Re-sending command to " + device_id + ": " + str(param_name) + " = " + str(param_value))
                botengine.send_command(device_id, param_name, param_value)

        else:
            del(queue[device_id])
                
    logger.debug("RELIABILITY: Cleaned queue looks like " + str(queue))
        
    botengine.save_variable(RELIABILITY_VARIABLE_NAME, queue)
    
         
