'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import utilities.utilities as utilities
import index
import importlib

# Maximum number of attempts for any one command
MAX_ATTEMPTS = 20

# Time between attempts, in seconds
TIME_BETWEEN_ATTEMPTS_SEC = 30

# Reliability variable name so we prevent typos
RELIABILITY_VARIABLE_NAME = "reliability"

# Total duration of time in which we should cache measurements here locally.
TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS = utilities.ONE_HOUR_MS

# Take a battery reading every 4 hours
BATTERY_MEASUREMENT_PERIODICITY_MS = utilities.ONE_HOUR_MS * 6

# Minimum number of battery readings required to make a decision on the battery life - 3 days worth
MINIMUM_BATTERY_READINGS = 10

# Total number of battery readings to maintain
MAXIMUM_BATTERY_READINGS = MINIMUM_BATTERY_READINGS * 2

# Space type language-neutral constants
# Internal docs: https://presence.atlassian.net/wiki/spaces/BOTS/pages/656638178/Space+Constants+and+Definitions
SPACE_TYPE = {
    "kitchen": 1,
    "bedroom": 2,
    "bathroom": 3,
    "hallway": 4,
    "livingroom": 5,
    "diningroom": 6,
    "familyroom": 7,
    "laundryroom": 8,
    "office": 9,
    "stairs": 10,
    "garage": 11,
    "basement": 12,
    "other": 13
}

# Helper enums
NEWEST_MEASUREMENT = 0
VALUE = 0
TIMESTAMP = 1

class Device:
    """
    This is a base class for each of our devices
    """
    # Parameter names
    MEASUREMENT_NAME_FIRMWARE = "firmware"

    # Low battery threshold - Override in sub-classes
    LOW_BATTERY_THRESHOLD = 10
        
    # Low signal strength threshold - Override in sub-classes
    LOW_RSSI_THRESHOLD = -87
    
    # List of Device Types this class is compatible with - Specify in sub-classes
    DEVICE_TYPES = []

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine: BotEngine environment
        :param location_object: Parent location object
        :param device_id: Device ID
        :param device_type: Device Type
        :param device_description: Device description (nickname)
        :param precache_measurements: True (default) to download historical measurements to cache them locally, the length of time of which is defined by device.TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS
        """
        # Parent location object
        self.location_object = location_object

        # Device ID
        self.device_id = device_id
        
        # Device type
        self.device_type = int(device_type)
        
        # Device description
        self.description = device_description.strip()
        
        # Measurements for each parameter, newest measurements at index 0
        # self.measurements["parameterName"] = [ ( newest_value, newest_timestamp ), ( value, timestamp ), ... ]
        self.measurements = {}

        # Last alert received { "alert_type": { "parameter_one" : "value_one", "timestamp_ms": timestamp_ms_set_locally } }
        self.last_alert = {}

        # Spaces this device is associated with. For example:
        # "spaces": [
        #               {
        #                   "name": "Kitchen",
        #                   "spaceId": 152,
        #                   "spaceType": 1
        #               },
        #               {
        #                   "name": "Hallway",
        #                   "spaceId": 154,
        #                   "spaceType": 4
        #               },
        #               {
        #                   "name": "Living Room",
        #                   "spaceId": 157,
        #                   "spaceType": 5
        #               }
        #           ]
        self.spaces = []
        
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

        # If the goal (scenario) ID changed
        self.is_goal_changed = False

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

        # User ID associated with this device.  Used for communications and device association. Left empty for anonymous users.
        self.user_id = None

        # If the user ID has changed keep reference to the old user ID
        self.last_user_id = None

        if precache_measurements:
            # Download and start this object out with a history of measurements
            self.cache_measurements(botengine, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS, botengine.get_timestamp())

        self.new_version(botengine)

    def new_version(self, botengine):
        """
        New version

        NOTE: YOU CANNOT CHANGE THE CLASS NAME OF A MICROSERVICE AT THIS TIME.
        Microservice changes will be identified through different 'module' names only. If you change the class name, it is currently ignored.
        This can be revisited in future architecture changes, noted below.

        The correct behavior is to create the object, then initialize() it every time you want to use it in a new bot execution environment

        :param botengine: BotEngine environment
        """
        # Added April 7, 2022
        if not hasattr(self, "is_goal_changed"):
            self.is_goal_changed = False

        # Added March 20, 2024
        if not hasattr(self, "user_id"):
            self.user_id = None

        # Added March 27, 2024
        if not hasattr(self, "last_user_id"):
            self.last_user_id = None
            
        # Fixed March 27, 2024: User ID may have been set to the device ID in the past
        if self.user_id == self.device_id:
            self.user_id = None

        # Synchronize device microservices
        if str(self.device_type) in index.MICROSERVICES.get('DEVICE_MICROSERVICES', {}):
            # Synchronize microservices
            changed = False

            module_names = [x['module'] for x in index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]]

            for m in module_names:
                changed |= m not in self.intelligence_modules

            for m in list(self.intelligence_modules.keys()):
                changed |= m not in module_names

            if changed:
                # Remove microservices that no longer exist
                delete = []
                for module_name in self.intelligence_modules.keys():
                    found = False
                    for intelligence_info in index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]:
                        if intelligence_info['module'] == module_name:
                            found = True
                            break

                    if not found:
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("\tDeleting device microservice: " + str(module_name))
                        delete.append(module_name)

                for d in delete:
                    del self.intelligence_modules[d]

                # Add more microservices
                for intelligence_info in index.MICROSERVICES['DEVICE_MICROSERVICES'][str(self.device_type)]:
                    if intelligence_info['module'] not in self.intelligence_modules:
                        try:
                            intelligence_module = importlib.import_module(intelligence_info['module'])
                            class_ = getattr(intelligence_module, intelligence_info['class'])
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("\tAdding device microservice: " + str(intelligence_info['module']))
                            intelligence_object = class_(botengine, self)
                            self.intelligence_modules[intelligence_info['module']] = intelligence_object
                        except Exception as e:
                            import traceback
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").error("Could not add device microservice: {}: {}; {}".format(str(intelligence_info), str(e), traceback.format_exc()))
                            if botengine.playback:
                                import time
                                time.sleep(10)

        elif len(self.intelligence_modules) > 0:
            # There are no intelligence modules for this device type, and yet we have some intelligence modules locally. Delete everything.
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("\tDeleting all device microservices")
            self.intelligence_modules = {}

        # Tell all device microservices we're running a new version
        for microservice_object in self.sorted_intelligence_modules().values():
            try:
                import time
                t = time.time()
                microservice_object.new_version(botengine)
                microservice_object.track_statistics(botengine, (time.time() - t) * 1000)
            except Exception as e:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("location.py - Error delivering new_version to device microservice (continuing execution): " + str(e))
                import traceback
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error(traceback.format_exc())

    def initialize(self, botengine):
        """
        Initialize this object
        :param botengine: BotEngine environment
        """
        # Initialize all device microservices
        for microservice_object in self.sorted_intelligence_modules().values():
            
            # Reset device microservice statistics
            microservice_object.reset_statistics(botengine)

            import time
            t = time.time()
            microservice_object.initialize(botengine)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

    def destroy(self, botengine):
        """
        Destroy this device
        :param botengine: BotEngine environment
        """
        return

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Super abstract device type name
        return _("Device")
    
    def get_icon(self):
        """
        Get the name of an icon
        :return: the font icon name of this device type
        """
        raise NotImplementedError

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        As most of the device icons come from the "People Power Regular" icon font, this is currently the default.
        You can override this method in a specific device class.
        :return: The name of the icon font package
        """
        return utilities.ICON_FONT_PEOPLEPOWER_REGULAR

    def is_goal_id(self, target_goal_id):
        """
        This is the proper way to check for whether or not this device matches the given target goal ID,
        because goal IDs can change by an order of 1000 for each different brand.
        :param botengine: BotEngine environment
        :return: True if the goal ID matches for this device
        """
        if self.goal_id is not None:
            return self.goal_id % 1000 == int(target_goal_id)
        return False
    
    def did_update_firmware(self, botengine):
        """
        Did the device firmware get updated?
        :param botengine:
        :return:
        """
        if Device.MEASUREMENT_NAME_FIRMWARE in self.measurements:
            if Device.MEASUREMENT_NAME_FIRMWARE in self.last_updated_params:
                return True
        return False
    
    def get_firmware_version(self, botengine):
        """
        Get the firmware version
        :param botengine:
        :return:
        """
        if Device.MEASUREMENT_NAME_FIRMWARE in self.measurements:
            return self.measurements[Device.MEASUREMENT_NAME_FIRMWARE][0][0]
        return None

    #===========================================================================
    # Microservice notification distribution methods
    #===========================================================================
    def device_measurements_updated(self, botengine):
        """
        Distribute notifications to all microservices that your measurements have been updated
        :param botengine:
        :return:
        """
        for microservice_object in self.sorted_intelligence_modules().values():
            import time
            t = time.time()
            microservice_object.device_measurements_updated(botengine, self)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

    def device_metadata_updated(self, botengine):
        """
        Distribute notifications to all microservices that your metadata has been updated
        :param botengine:
        :return:
        """
        for microservice_object in self.sorted_intelligence_modules().values():
            import time
            t = time.time()
            microservice_object.device_metadata_updated(botengine, self)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

    def device_alert(self, botengine, alert_type, alert_params):
        """
        Distribute notifications to all microservices that an alert has been generated from this device
        :param botengine: BotEngine environment
        :param alert_type: Type of alert
        :param alert_params: Dictionary of alert parameters
        """
        # Added May 4, 2021
        if not hasattr(self, "last_alert"):
            self.last_alert = {}

        alert_params['timestamp_ms'] = botengine.get_timestamp()

        self.last_alert = {
            alert_type : alert_params
        }

        for microservice_object in self.sorted_intelligence_modules().values():
            import time
            t = time.time()
            microservice_object.device_alert(botengine, self, alert_type, alert_params)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

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

        except Exception as e:
            # This can happen because this bot may not have read permissions for this device.
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Cannot synchronize measurements for device {} '{}': {}".format(self.description, self.device_id, e))
            return

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Synchronizing measurements for device: " + str(self.description))
        if 'measures' in measurements:
            for measure in measurements['measures']:
                if 'value' not in measure:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("device.py: Measurement has no value: " + str(measure))
                    continue

                value = utilities.normalize_measurement(measure['value'])
                param_name = measure['name']
                time = measure['time']

                # If there's an index number, we just augment the parameter name with the index number to make it a unique parameter name.  param_name.index
                if 'index' in measure:
                    if measure['index'] is not None:
                        if str(measure['index']).lower() != "none":
                            param_name = "{}.{}".format(param_name, measure['index'])
                
                if param_name in self.measurements:
                    if self.measurements[param_name][0][0] == value and self.measurements[param_name][0][1] == time:
                        # Already captured this measurement
                        continue
                
                # Add the measurement to the cache
                self.add_measurement(botengine, param_name, value, time)

    def update(self, botengine, measures):
        """
        Attempt to parse the inputs to update this object
        :param measures: Full or partial measurement block from bot inputs
        """
        self.last_updated_params = []
        self.communicated(botengine.get_timestamp())

        # # Handy debug tool.
        # if measures is not None:
        #     for measure in measures:
        #         if measure['deviceId'] == self.device_id and 'value' in measure:
        #             param_name = measure['name']
        #             if 'index' in measure:
        #                 if measure['index'] is not None:
        #                     param_name = "{}.{}".format(measure['name'], measure['index'])
        
        #             if param_name in self.measurements:
        #                 if len(self.measurements[param_name]) > 0:
        #                     if 'time' in measure:
        #                         if not measure['updated'] and measure['time'] == self.measurements[param_name][NEWEST_MEASUREMENT][TIMESTAMP]:
        #                             # Nothing to update
        #                             botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.GREEN + "\tSAME:      {} @ {} = {}".format(param_name, measure['time'], measure['value']) + utilities.Color.END)
        #                             continue
        
        #             if measure['updated']:
        #                 botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.GREEN + "\tUPDATED:   {} @ {} = {}".format(param_name, measure['time'], measure['value']) + utilities.Color.END)
        #             else:
        #                 botengine.get_logger(f"{__name__}.{__class__.__name__}").info(utilities.Color.GREEN + "\tTIME DIFF: {} @ {} = {}".format(param_name, measure['time'], measure['value']) + utilities.Color.END)

        if measures is not None:
            for measure in measures:
                if measure['deviceId'] == self.device_id:
                    param_name = measure['name']
                    if param_name == 'batteryLevel' and measure['updated']:
                        if 'value' not in measure or measure['value'] == "":
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("device.py: Updated parameter provided no updated value: {}".format(measure))
                            continue
                        # Update the battery_level
                        self.battery_level = int(measure['value'])
                        self.last_updated_params.append('batteryLevel')
                        
                    elif param_name not in self.measurements or measure['updated']:
                        if 'value' not in measure:
                            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("device.py: Updated parameter provided no updated value: {}".format(measure))
                            continue
                            
                        value = utilities.normalize_measurement(measure['value'])

                        # If there's an index number, we just augment the parameter name with the index number to make it a unique parameter name.  param_name.index
                        if 'index' in measure:
                            if measure['index'] is not None:
                                if str(measure['index']).lower() != "none":
                                    param_name = "{}.{}".format(param_name, measure['index'])
                        is_param_get_new_value = self.add_measurement(botengine, param_name, value, measure['time'])
                        if is_param_get_new_value and not param_name in self.last_updated_params:
                            self.last_updated_params.append(param_name)

        # List of devices (this one and its proxy) that were updated, to later synchronize with the location outside of this object
        updated_devices = []
        updated_metadata = []

        # Update all device intelligence modules 
        if len(self.last_updated_params) > 0:
            updated_devices.append(self)
                
        else:
            # Metadata was updated
            updated_metadata.append(self)

        # Make sure our proxy (gateway) gets pinged - it implicitly updated here and needs to trigger microservices
        if self.proxy_id is not None:
            if self.proxy_id in self.location_object.devices:
                d, m = self.location_object.devices[self.proxy_id].update(botengine, measures)
                updated_devices += d
                updated_metadata += m

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("Updated '{}' with params: {}".format(self.description, [(param, self.measurements.get(param,[])[:1]) for param in self.last_updated_params]))
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
        for microservice_object in self.sorted_intelligence_modules().values():
            import time
            t = time.time()
            microservice_object.file_uploaded(botengine, device_object, file_id, filesize_bytes, content_type, file_extension)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

    def last_measurement_timestamp_ms(self, botengine):
        """
        Timestamp of the last measurement received
        :param botengine: BotEngine
        :return: Timestamp in milliseconds or None if no measurements received
        """
        newest_timestamp_ms = None
        for name in self.measurements:
            if len(self.measurements[name]) > 0:
                value, timestamp_ms = self.measurements[name][0]
                if newest_timestamp_ms is None:
                    newest_timestamp_ms = timestamp_ms
                elif timestamp_ms > newest_timestamp_ms:
                    newest_timestamp_ms = timestamp_ms

        return newest_timestamp_ms

    def add_measurement(self, botengine, name, value, timestamp):
        """
        Update the device's status
        :param botengine: BotEngine environment
        :param name: Parameter name
        :param value: Parameter value
        :param timestamp: Timestamp in milliseconds
        :return:
        """
        measurement_updated = False
        if name not in self.measurements:
            # Create the measurement
            self.measurements[name] = []

            measurement_updated = True
            self.measurement_odometer += 1
            self.measurements[name].insert(0, (value, timestamp))
        else:
            is_new_measurement = True
            for i in range(len(self.measurements[name])):
                if value == self.measurements[name][i][0] and timestamp == self.measurements[name][i][1]:
                    is_new_measurement = False
                    break

            if is_new_measurement:
                measurement_updated = True
                self.measurement_odometer += 1
                self.measurements[name].insert(0, (value, timestamp))

        # Auto garbage-collect
        if self.enforce_cache_size:
            while (len(self.measurements[name]) > 1) and self.measurements[name][-1][1] <= botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS:
                del(self.measurements[name][-1])

        return measurement_updated

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

    def get_measurement_history(self, botengine, param_name):
        """
        Get the measurement history for this parameter, newest measurements first
        [ ( value, timestamp), (value, timestamp) ]
        :param botengine: BotEngine environment
        :param param_name: Parameter name
        :return: List of measurements history tuples, or None if the measurement doesn't exist
        """
        if param_name in self.measurements:
            return self.measurements[param_name]
        return None

    #===========================================================================
    # Device health
    #===========================================================================
    def did_update_rssi(self, botengine=None):
        """
        :return: True if we updated the RSSI for this device on this execution
        """
        return 'rssi' in self.last_updated_params

    def get_rssi(self, botengine=None):
        """
        :return: The most recent RSSI value, or None if it doesn't exist
        """
        if 'rssi' in self.measurements:
            return self.measurements['rssi'][0][0]

    def low_signal_strength(self, botengine=None):
        """
        :return: True if this device currently has a low signal strength
        """
        rssi = self.get_rssi(botengine)
        if rssi is not None:
            return rssi < self.LOW_RSSI_THRESHOLD
        return False

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

    def did_tamper(self, botengine):
        """
        Did someone tamper with this device
        :param botengine:
        :return:
        """
        if 'tamper' in self.last_updated_params:
            if 'tamper' in self.measurements:
                if len(self.measurements['tamper']) > 0:
                    return self.measurements['tamper'][0][0]

        return False

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
        for microservice_object in self.sorted_intelligence_modules().values():
            import time
            t = time.time()
            microservice_object.coordinates_updated(botengine, latitude, longitude)
            microservice_object.track_statistics(botengine, (time.time() - t) * 1000)

        # Notify all children microservices
        for device_id in self.location_object.devices:
            if self.location_object.devices[device_id].proxy_id == self.device_id:
                for intelligence_id in self.location_object.devices[device_id].intelligence_modules:
                    import time
                    t = time.time()
                    self.location_object.devices[device_id].intelligence_modules[intelligence_id].coordinates_updated(botengine, latitude, longitude)
                    self.location_object.devices[device_id].intelligence_modules[intelligence_id].track_statistics(botengine, (time.time() - t) * 1000)

    #===========================================================================
    # Spaces
    #===========================================================================
    def is_in_space(self, botengine, space_description_or_type):
        """
        Determine if this device is associated with the given space description.
        The description must be a word inside our SPACE_TYPE dictionary.
        :param botengine: BotEngine environment
        :param space_description_or_type: Space type number or description from our SPACE_TYPE dictionary
        :return: True if the device is in the given space
        """
        space_type = None

        if space_description_or_type.lower() in SPACE_TYPE:
            space_type = SPACE_TYPE[space_description_or_type.lower()]

        else:
            try:
                space_type = int(space_description_or_type)
            except:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").error("device.is_in_space(): Couldn't identify what space type you're talking about - {}".format(space_description_or_type))
                return False

        for space in self.spaces:
            if space['spaceType'] == space_type:
                return True

        return False

    def is_in_spaces(self, botengine, space_descriptions_or_types_list):
        """
        Determine if this device is associated with any of the given spaces in the list.
        If the list contains descriptive strings, the strings must be words inside of our SPACE_TYPE dictionary.
        :param botengine: BotEngine environment
        :param space_descriptions_or_types_list: List of space type numbers, or list of strings from our SPACE_TYPE dictionary
        :return: True if the device is in any of the given spaces
        """
        space_types = []

        for s in space_descriptions_or_types_list:
            if s.lower() in SPACE_TYPE:
                space_types.append(SPACE_TYPE[s.lower()])

            else:
                try:
                    space_type = int(s)
                    space_types.append(space_type)

                except:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error("device.is_in_spaces(): Couldn't identify what space type you're talking about - {}".format(s))
                    continue

        comparison_types = []
        for space in self.spaces:
            comparison_types.append(space['spaceType'])

        for t in space_types:
            if t in comparison_types:
                return True

        return False

    #===========================================================================
    # Data request
    #===========================================================================
    def request_data(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None, param_name_list=None, reference=None, index=None, ordered=1):
        """
        Selecting a large amount of data from the database can take a significant amount of time and impact server
        performance. To avoid this long waiting period while executing bots, a bot can submit a request for all the
        data it wants from this location asynchronously. The server gathers all the data on its own time, and then
        triggers the bot with trigger 2048. Your bot must include trigger 2048 to receive the trigger.

        Selected data becomes available as a file in CSV format, compressed by LZ4, and stored for one day.
        The bot receives direct access to this file.

        You can call this multiple times to extract data out of multiple devices. The request will be queued up and
        the complete set of requests will be flushed at the end of this bot execution.

        :param botengine:
        :param oldest_timestamp_ms:
        :param newest_timestamp_ms:
        :param param_name_list:
        :param reference:
        :param index:
        :param ordered:
        :return:
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("{}: request_data() - Requesting data from {} to {} for parameters {}".format(self.description, oldest_timestamp_ms, newest_timestamp_ms, param_name_list))
        if oldest_timestamp_ms is None:
            oldest_timestamp_ms = botengine.get_timestamp() - utilities.ONE_MONTH_MS * 6
        
        botengine.request_data(type=botengine.DATA_REQUEST_TYPE_PARAMETERS,
                               device_id=self.device_id,
                               oldest_timestamp_ms=oldest_timestamp_ms,
                               newest_timestamp_ms=newest_timestamp_ms,
                               param_name_list=param_name_list,
                               reference=reference,
                               index=index,
                               ordered=ordered)

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
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("{}: get_csv() - This device has no measurements")
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
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("{}: get_csv() - Not all of the requested parameters exist for this device")
            return None

        output = "device_type,device_id,description,timestamp_ms,timestamp_iso,"

        for t in titles:
            output = "{}{},".format(output, t)

        output += "\n"

        try:
            measurements = botengine.get_measurements(self.device_id, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms, param_name=params)

        except:
            # This can happen because this bot may not have read permissions for this device.
            # botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("Cannot synchronize measurements for device: " + str(self.description))
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
                        if str(measure['index']).lower() != "none":
                            param_name = "{}.{}".format(param_name, measure['index'])

                processed_readings[time] = (param_name, value)

        measurements = None
        import gc
        gc.collect()

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("{}: get_csv() - Processing {} measurements ...".format(self.description, str(len(processed_readings))))

        for timestamp_ms in sorted(processed_readings.keys()):
            dt = self.location_object.get_local_datetime_from_timestamp(botengine, timestamp_ms)
            output += "{},{},{},{},{},".format(self.device_type, self.device_id.replace(",","_"), self.description.replace(",","_"), timestamp_ms, utilities.iso_format(dt))

            for t in titles:
                if t == processed_readings[timestamp_ms][0]:
                    output += "{},".format(processed_readings[timestamp_ms][1])
                else:
                    output += "{},".format(last_measurements[t])

            output += "\n"

        return output
    
    def sorted_intelligence_modules(self):
        """
        Order intelligence modules alphabetically then by execution priority
        :return: List of intelligence modules sorted by execution priority
        """
        modules = dict(sorted(self.intelligence_modules.items(), key=lambda module: module[0]))
        execution_priorities = {}
        for intelligence_info in index.MICROSERVICES.get('DEVICE_MICROSERVICES', {}).get(str(self.device_type), []):
            execution_priorities[intelligence_info['module']] = intelligence_info.get('execution_priority', 0)
        
        return dict(sorted(modules.items(), key=lambda module: execution_priorities.get(module[0], 0), reverse=True))


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
    botengine.get_logger(f"{__name__}").info("{}: Send command reliably".format(device_id))
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
    botengine.get_logger(f"{__name__}").info(">reliability")
    queue = botengine.load_variable(RELIABILITY_VARIABLE_NAME)
    if queue is None:
        return
    
    logger = botengine.get_logger(f"{__name__}")
    
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
    
         
