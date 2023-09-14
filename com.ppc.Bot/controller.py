'''
Created on March 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import copy

from locations.location import Location

# Deprecated:
from devices.smartplug.smartplug_centralite_3series import Centralite3SeriesSmartplugDevice
from devices.button.button import ButtonDevice
from devices.button.button_develco import DevelcoButtonDevice
from devices.button.button_linkhigh import LinkHighButtonDevice
from devices.gateway.gateway_peoplepower_xseries import PeoplePowerXSeriesDevice
from devices.movement.touch import TouchDevice

class Controller:
    """
    This is the main class that will coordinate all our sensors and behavior
    """
    
    def __init__(self):
        """
        Constructor
        """
        # A list of our locations, where the key is the location ID.
        self.locations = {}
            
        # A map of device_id : locationId
        self.location_devices = {}

        # Last execution timestamp for debugging support
        self.exec_timestamp = 0

        # Last version of the bot
        self.version = None

    def initialize(self, botengine):
        """
        Initialize the controller.
        This is mandatory to call once for each new execution of the bot
        :param botengine: BotEngine environment
        """
        botengine.get_logger().info("controller: Last execution={}; Current execution={}".format(self.exec_timestamp, botengine.get_timestamp()))
        self.exec_timestamp = botengine.get_timestamp()

        for key in self.locations:
            self.locations[key].initialize(botengine)

    def print_status(self, botengine):
        """
        Print the status of this object
        """
        logger = botengine.get_logger()
        logger.info("Controller Status")
        logger.info("-----")
        logger.info("self.locations: " + str(self.locations))
        logger.info("self.location_devices: " + str(self.location_devices))
        logger.info("-----")

    def get_intelligence_statistics(self, botengine):
        """
        Get the intelligence statistics for all locations
        :param botengine: BotEngine environment
        :return: List of statistics json

        Example:
        [
            {
                "name": "microservice_name",
                "calls": 3,
                "time": 280 # ms
            }   
        ]
        """
        all_intelligence_module_statistics = []
        for location_id in self.locations:
            # Gather location intelligence modules
            for intelligence_module in self.locations[location_id].intelligence_modules.keys():
                all_intelligence_module_statistics.append((intelligence_module, self.locations[location_id].intelligence_modules[intelligence_module].get_statistics(botengine)))
            # Gather device intelligence modules
            for device_id in self.locations[location_id].devices:
                for intelligence_module in self.locations[location_id].devices[device_id].intelligence_modules.keys():
                    all_intelligence_module_statistics.append((intelligence_module, self.locations[location_id].devices[device_id].intelligence_modules[intelligence_module].get_statistics(botengine)))

        stats = []

        for (intelligence_module, intelligence_module_statistics) in all_intelligence_module_statistics:
            # Assign the microservice package name to the "name" field
            if "intelligence" != intelligence_module.split(".")[0] or len(intelligence_module.split(".")) == 1:
                continue
            
            botengine.get_logger().debug("intelligence_module: {} - {}".format(intelligence_module, intelligence_module_statistics))

            intelligence_module_package_name = intelligence_module.split(".")[1]
            # Aggregate intelligence module statistics by package name
            _stats = [stat for stat in stats if stat["name"] == intelligence_module_package_name]
            if len(_stats) == 0:
                stat = {
                    "name": intelligence_module_package_name,
                    "calls": intelligence_module_statistics["calls"],
                    "time": intelligence_module_statistics["time"]
                }
                stats.append(stat)
            else:
                stat = _stats[0]
                stat["calls"] += intelligence_module_statistics["calls"]
                stat["time"] += intelligence_module_statistics["time"]

            # Remove floating point
            stat["time"] = int(stat["time"])
                
        
        return stats

    
    def track_new_and_deleted_devices(self, botengine, precache_measurements=True):
        """
        Track any new or deleted devices
        :param botengine: Execution environment
        :param controller: Controller object managing all locations and devices
        :param precache_measurements: True to pre-cache measurements for each new device
        """
        location_id = botengine.get_location_id()
        if len(self.locations) == 0:
            if location_id not in self.locations:
                # The location isn't being tracked yet, add it
                botengine.get_logger().info("\t=> Now tracking location " + str(location_id))
                self.locations[location_id] = Location(botengine, location_id)

        access = botengine.get_access_block()

        if access is None:
            botengine.get_logger().error("Bot Server error: No 'access' block in our inputs!")
            return

        # Maintenance: Add new devices
        for item in access:
            if item['category'] == botengine.ACCESS_CATEGORY_MODE:
                if 'location' in item:
                    if 'latitude' in item['location'] and 'longitude' in item['location']:
                        self.locations[location_id].update_coordinates(botengine, item['location']['latitude'], item['location']['longitude'])
                
            elif item['category'] == botengine.ACCESS_CATEGORY_DEVICE:
                if 'device' not in item:
                    import json
                    botengine.get_logger().warn("Got a Device Category in our access block, but there was no 'device' element:\n" + json.dumps(access, indent=2, sort_keys=True))
                    continue

                if 'description' in item['device']:
                    device_desc = str(item['device']['description']).strip()
                else:
                    device_desc = ""

                device_id = str(item['device']['deviceId'])
                device_type = int(item['device']['deviceType'])
                location_id = int(item['device']['locationId'])

                if len(self.locations) > 0 and location_id not in self.locations:
                    botengine.get_logger().warning("Device ID {} is being accessed by bot instance {} in location {}, but its location is {}.".format(device_id, botengine.get_bot_instance_id(), list(self.locations.keys()), location_id))
                    continue

                device_object = self.get_device(device_id)
                location_object = self.locations[location_id]

                if device_object is not None:
                    if not hasattr(device_object, 'device_type'):
                        self.delete_device(botengine, device_id)
                        device_object = None
                        continue

                    if device_type != device_object.device_type:
                        # The device type changed. We have to restart this device.
                        # This happens when a device gets registered to our cloud and looks like some device type,
                        # and then starts reporting extra information and features in later that make the cloud realize
                        # it is actually a different device type than what was originally conceived.
                        self.delete_device(botengine, device_id)
                        device_object = None
                        continue
                
                # Load any available device type class within this bundle
                device_type_classes = _extact_available_device_type_classes(botengine)

                if device_object is None:
                    # Instantiate the device object based on the device type
                    for device_type_class in device_type_classes:
                        if device_type in device_type_class.DEVICE_TYPES:
                            device_object = device_type_class(botengine, location_object, device_id, device_type, device_desc, precache_measurements)
                            break
                    if device_object is None:
                        botengine.get_logger().warn("Unsupported device type: " + str(device_type) + " ('" + device_desc + "')")
                        continue

                if 'connected' in item['device']:
                    device_object.is_connected = item['device']['connected']
                else:
                    device_object.is_connected = False

                device_object.can_read = item['read']
                device_object.can_control = item['control']
                device_object.device_id = str(device_id)
                device_object.description = str(device_desc).strip()
                
                if 'remoteAddrHash' in item['device']:
                    device_object.remote_addr_hash = str(item['device']['remoteAddrHash'])
                
                if 'proxyId' in item['device']:
                    device_object.proxy_id = str(item['device']['proxyId'])
                
                if 'goalId' in item['device']:
                    goal_id = int(item['device']['goalId'])
                    if goal_id is None or goal_id >= 0:
                        device_object.is_goal_changed = device_object.goal_id is None or (device_object.goal_id is not None and device_object.goal_id != goal_id)
                        device_object.goal_id = goal_id

                if 'startDate' in item['device']:
                    device_object.born_on = int(item['device']['startDate'])
                elif device_object.born_on is None:
                    device_object.born_on = botengine.get_timestamp()

                self.sync_device(botengine, location_id, device_id, device_object)

                if hasattr(device_object, "latitude") and hasattr(device_object, "longitude"):
                    if 'latitude' in item['device'] and 'longitude' in item['device']:
                        if float(item['device']['latitude']) != device_object.latitude or float(item['device']['longitude']) != device_object.longitude:
                            device_object.update_coordinates(botengine, float(item['device']['latitude']), float(item['device']['longitude']))

        # Maintenance: Prune out old devices
        for device_id in copy.copy(self.location_devices):
            found = False

            for item in access:
                if item['category'] == botengine.ACCESS_CATEGORY_DEVICE:
                    if 'device' in item:
                        if item['device']['deviceId'] == device_id:
                            found = True
                            break
    
            if not found:
                self.delete_device(botengine, device_id)

            else:
                # Delete deprecated objects
                if isinstance(self.locations[self.location_devices[device_id]].devices[device_id], ButtonDevice):
                    self.delete_device(botengine, device_id)

                elif isinstance(self.locations[self.location_devices[device_id]].devices[device_id], LinkHighButtonDevice):
                    self.delete_device(botengine, device_id)

                elif isinstance(self.locations[self.location_devices[device_id]].devices[device_id], DevelcoButtonDevice):
                    self.delete_device(botengine, device_id)

                elif isinstance(self.locations[self.location_devices[device_id]].devices[device_id], Centralite3SeriesSmartplugDevice):
                    self.delete_device(botengine, device_id)

                elif isinstance(self.locations[self.location_devices[device_id]].devices[device_id], PeoplePowerXSeriesDevice):
                    self.delete_device(botengine, device_id)

                elif isinstance(self.locations[self.location_devices[device_id]].devices[device_id], TouchDevice):
                    self.delete_device(botengine, device_id)

    def sync_device(self, botengine, location_id, device_id, device_object):
        """
        Synchronize the device with the tracking system
        + Make sure the device's name is up-to-date
        + Create the location if it doesn't exist
        + Move the device to the correct location if it's in the wrong location
        + Make sure the location is tracking this device object
        + Tell the location to re-evaluate its state based on this new information
        
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param device_id: Device ID
        :param device_object: Device object
        """
        # Make sure the location exists
        if len(self.locations) > 0 and location_id not in self.locations:
            return

        if location_id not in self.locations:
            # The location isn't being tracked yet, add it
            botengine.get_logger().info("\t=> Now tracking location " + str(location_id))
            self.locations[location_id] = Location(botengine, location_id)

        # Make sure the device is being tracked, and it's in the correct location
        if device_id not in self.location_devices:
            # The device isn't being tracked at all - add it
            botengine.get_logger().info("\t=> Now tracking device " + str(device_id))
            self.location_devices[device_id] = location_id
            self.locations[location_id].add_device(botengine, device_object)
            device_object.location_object = self.locations[location_id]

        elif self.location_devices[device_id] != location_id:
            # The device is in the wrong location, move it.
            botengine.get_logger().info("\t=> Moving device " + str(device_id) + " to location " + str(location_id))
            self.locations[self.location_devices[device_id]].delete_device(botengine, device_id)
            self.location_devices[device_id] = location_id
            self.locations[location_id].devices[device_id] = device_object
            device_object.location_object = self.locations[location_id]

    def filter_measurements(self, botengine, location_id, device_object, measurements):
        """
        Optionally filter device measurement data before it reaches the upper layers of the stack.
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param device_object: Device object pending update
        :param measurements: Measurements dictionary we're about to trigger with, which is modified in place.
        """
        self.locations[location_id].filter_measurements(botengine, device_object, measurements)

    def device_measurements_updated(self, botengine, location_id, device_object):
        """
        A device's measurements have been updated
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param device_object: Device object
        """
        self.locations[location_id].device_measurements_updated(botengine, device_object)

    def device_metadata_updated(self, botengine, location_id, device_object):
        """
        Evaluate a device that is new or whose goal/scenario was recently updated
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param device_object: Device object
        """
        self.locations[location_id].device_metadata_updated(botengine, device_object)

    def device_alert(self, botengine, location_id, device_object, alert_type, alert_params):
        """
        Device alerts were updated
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param device_object: Device object that generated the alert
        :param alert_type: Type of alert
        :param alert_params: Dictionary of alert parameters
        :return:
        """
        self.locations[location_id].device_alert(botengine, device_object, alert_type, alert_params)

    def file_uploaded(self, botengine, device_object, file):
        """
        File was uploaded
        :param botengine: BotEngine environment
        :param device_object: Device object that uploaded the file
        :param file: File JSON structure
        """
        location_id = self.location_devices[device_object.device_id]
        content_type = None
        file_extension = None
        file_id = None
        filesize_bytes = None

        if 'contentType' in file:
            content_type = file['contentType']

        if 'extension' in file:
            file_extension = file['extension']

        if 'fileId' in file:
            file_id = file['fileId']

        if 'fileSize' in file:
            filesize_bytes = file['fileSize']

        device_object.file_uploaded(botengine, device_object, file_id, filesize_bytes, content_type, file_extension)
        self.locations[location_id].file_uploaded(botengine, device_object, file_id, filesize_bytes, content_type, file_extension)

    def user_role_updated(self, botengine, location_id, user_id, role, category, location_access, previous_category, previous_location_access):
        """
        A user changed roles
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param user_id: User ID that changed roles
        :param role: Application-layer agreed upon role integer which may auto-configure location_access and alert category
        :param category: User's current alert/communications category (1=resident; 2=supporter)
        :param location_access: User's current access to the location
        :param previous_category: User's previous category, if any
        :param previous_location_access: User's previous access to the location, if any
        :return:
        """
        if location_id not in self.locations:
            # The location isn't being tracked yet, add it
            botengine.get_logger().info("\t=> Now tracking location " + str(location_id))
            self.locations[location_id] = Location(botengine, location_id)

        self.locations[location_id].user_role_updated(botengine, user_id, role, category, location_access, previous_category, previous_location_access)

    def call_center_updated(self, botengine, location_id, user_id, status):
        """
        Emergency call center status has changed
        :param botengine: BotEngine environment
        :param location_id: Location ID
        :param user_id: User ID that made the change
        :param status: Current call center status
        """
        if location_id not in self.locations:
            # The location isn't being tracked yet, add it
            botengine.get_logger().info("\t=> Now tracking location " + str(location_id))
            self.locations[location_id] = Location(botengine, location_id)

        self.locations[location_id].call_center_updated(botengine, user_id, status)

    def data_request_ready(self, botengine, reference, device_csv_dict):
        """
        A botengine.request_data() request is ready
        :param botengine: BotEngine environment
        :param reference: Optional reference passed into botengine.request_data(..)
        :param device_csv_dict: { 'device_id': 'csv data string' }
        """
        for location_id in self.locations:
            self.locations[location_id].data_request_ready(botengine, reference, device_csv_dict)

    def sync_mode(self, botengine, mode, location_id):
        """
        Update the mode.
        
        This notifies the specific location that its mode changed, and it is that location's responsibility to signal the mode_updated to all children device and location intelligence modules.
        
        :param botengine: BotEngine environment
        :param mode: Mode of the home, like "HOME" or "AWAY"
        :param location_id: Location that had its mode changed
        """
        botengine.get_logger().info("Controller: Received mode '{}'".format(mode))
        if location_id not in self.locations:
            self.locations[location_id] = Location(botengine, location_id)

        self.locations[location_id].mode_updated(botengine, mode)
        
    def sync_datastreams(self, botengine, address, content):
        """
        Synchronize the data stream messages across all location objects
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Data Stream content
        """
        for location_id in self.locations:
            self.locations[location_id].datastream_updated(botengine, address, content)
    
    
    def sync_question(self, botengine, question):
        """
        Synchronize an answered question
        :param botengine: BotEngine environment
        :param question: Answered question
        """
        # Sync location intelligence
        for location_id in self.locations:
            self.locations[location_id].question_answered(botengine, question)


    def run_location_intelligence(self, botengine, intelligence_id, argument):
        """
        Because we don't know what location_id owns this intelligence module, we have to own the responsibility of discovering the intelligence module here.
        :param botengine: BotEngine environment
        :param intelligence_id: ID of the intelligence module which needs its timer fired
        :param argument: Argument to pass into the timer_fired() method of the intelligence module
        """
        botengine.get_logger().info("Location Intelligence Timer Fired: " + str(intelligence_id))
        for location_id in self.locations:
            self.locations[location_id].timer_fired(botengine, intelligence_id, argument)
            return

    def run_device_intelligence(self, botengine, intelligence_id, argument):
        """
        Because we don't know what location_id owns this intelligence module, we have to own the responsibility of discovering the intelligence module here.
        :param botengine: BotEngine environment
        :param intelligence_id: ID of the intelligence module which needs its timer fired
        :param argument: Argument to pass into the timer_fired() method of the intelligence module
        """
        botengine.get_logger().info("Device Intelligence Timer Fired: " + str(intelligence_id))
        for location_id in self.locations:
            for device_id in self.locations[location_id].devices:
                for intelligence_module_name in self.locations[location_id].devices[device_id].intelligence_modules:
                    if intelligence_id == self.locations[location_id].devices[device_id].intelligence_modules[intelligence_module_name].intelligence_id:
                        import time
                        t = time.time()
                        self.locations[location_id].devices[device_id].intelligence_modules[intelligence_module_name].timer_fired(botengine, argument)
                        self.locations[location_id].devices[device_id].intelligence_modules[intelligence_module_name].track_statistics(botengine, (time.time() - t) * 1000)
                        return

    def run_intelligence_schedules(self, botengine, schedule_id):
        """
        Notify each location that the schedule fired. 
        The location should be responsible for telling all device and location intelligence modules, 
        and performing periodic tasks like garbage collection.
        :param botengine: BotEngine environment
        """
        for location_id in self.locations:
            self.locations[location_id].schedule_fired(botengine, schedule_id)
        
    def get_device(self, device_id):
        """
        Get the device represented by the device ID, if it exists
        :return: the device object represented by the device ID, or return None if the device does not yet exist
        """
        try:
            if self.location_devices[device_id] in self.locations:
                return self.locations[self.location_devices[device_id]].devices[device_id]
            
        except:
            return None
    
    def delete_device(self, botengine, device_id):
        """
        Delete the given device ID
        :param device_id: Device ID to delete
        """
        botengine.get_logger().info("Deleting device: " + str(device_id))
        if device_id in self.location_devices:
            if self.location_devices[device_id] in self.locations:
                location = self.locations[self.location_devices[device_id]]
                location.delete_device(botengine, device_id)
            del self.location_devices[device_id]
        
    def delete_location(self, botengine, location_id):
        """
        Delete the given location ID
        :param location_id: Location ID to delete
        """
        botengine.get_logger().info("Deleting Location: " + str(location_id))
        if location_id in self.locations.keys():
            for device_id in copy.copy(self.location_devices):
                if self.location_devices[device_id] == location_id:
                    self.delete_device(botengine, device_id)
            
            del self.locations[location_id]

    def new_version(self, botengine):
        """
        New bot version detected
        :param botengine: BotEngine environment
        """
        for location_id in self.locations:
            self.locations[location_id].new_version(botengine)

    def is_version_updated(self, botengine):
        """
        Check if we are indeed running a new version of the bot.
        :param botengine: BotEngine environment
        :return: True if a new version was detected.
        """
        import json
        import os
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "runtime.json")) as f:
            j = json.load(f)
            version = j["version"]["version"]
            if not hasattr(self, "version") or version != self.version:
                botengine.get_logger().info("controller: New version detected")
                return True

        # Are we running locally and this is our very first execution?
        if botengine.local and botengine.local_execution_count == 0:
            return True

        return False

    def update_version(self, botengine):
        """
        Trigger the new_version() if we are indeed running a new version of the bot.
        :param botengine: BotEngine environment
        """
        import json
        import os
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "runtime.json")) as f:
            j = json.load(f)
            version = j["version"]["version"]
            self.version = version
            self.new_version(botengine)


def _extact_available_device_type_classes(botengine):
    """
    Extract all available device type classes from a module
    :return List of device type classes
    """

    device_type_classes = []
    # Walk through our devices directory
    import os
    from os import walk
    mypath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "devices")
    
    for (dirpath, dirnames, filenames) in walk(mypath):
        # Walk through each subdirectory
        for dirname in dirnames:                        
            for (_dirpath, _dirnames, _filenames) in walk(os.path.join(dirpath, dirname)):
                # Walk through each python file in the subdirectory
                for filename in _filenames:
                    if not filename.endswith(".py") and not filename.endswith(".pyc"):
                        continue
                    
                    # Form the module name like "devices.entry.entry"
                    from pathlib import Path
                    module_name = "{}.{}.{}".format(_dirpath.split("/")[-2], _dirpath.split("/")[-1], Path(filename).with_suffix(''))
                    
                    # Import the module
                    import importlib
                    try:
                        module = importlib.import_module(module_name)
                    except Exception as e:
                        continue
                    
                    # Get all the classes in the module
                    from inspect import isclass
                    classes = [x for x in dir(module) if isclass(getattr(module, x))]
                    for class_name in classes:
                        # Extract only classes that conform to the Device class with one or more specified device type
                        class_ = getattr(module, class_name)
                        if hasattr(class_, "DEVICE_TYPES") and class_ not in device_type_classes:
                            device_type_classes.append(class_)

    return device_type_classes