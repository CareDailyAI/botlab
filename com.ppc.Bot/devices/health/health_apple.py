'''
Created on September 10, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.health.health import HealthDevice

class AppleHealthDevice(HealthDevice):
    """
    Apple Health Device
    """

    # Parameters
    MEASUREMENT_NAME_MOVEMENT_STATUS            = "movementStatus"
    MEASUREMENT_NAME_SLEEP_ANALYSIS             = "sleepAnalysis"

    # Movement Status
    MOVEMENT_STATUS_DETECTED = 1
    MOVEMENT_STATUS_EXIT = 0

    MEASUREMENT_PARAMETERS_LIST = [
        HealthDevice.MEASUREMENT_NAME_HEART_RATE,
        HealthDevice.MEASUREMENT_NAME_STEPS,
        MEASUREMENT_NAME_SLEEP_ANALYSIS,
        HealthDevice.MEASUREMENT_NAME_BREATHING_RATE,
        HealthDevice.MEASUREMENT_NAME_BREATHING_RATE_STABILITY,
        HealthDevice.MEASUREMENT_NAME_HEART_RATE_STABILITY,
        HealthDevice.MEASUREMENT_NAME_MOTION_INDEX,
        HealthDevice.MEASUREMENT_NAME_MOTION_STABILITY,
        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC,
        HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC,
        HealthDevice.MEASUREMENT_NAME_HEMATOCRIT,
        HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN,
        HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY,
        HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX,
        HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX,
        HealthDevice.MEASUREMENT_NAME_PROTEIN,
        HealthDevice.MEASUREMENT_NAME_SPO2,
    ]

    # # TRENDS TO MONITOR
    # Alert on falls
    # Detect wandering 
    # alert with gps location
    # monitor sleep quality
    # monitor fitness

    # Device types
    DEVICE_TYPES = [29]

    # Distance in meters used to determine if a person has wandered too far from their home
    MAXIMUM_DISTANCE_MOVED_M = 100

    # Sleep Analysis parameter measurement Indexes
    SLEEP_ANALYSIS_INDEX_IN_BED       = 0 # The user is in bed.
    SLEEP_ANALYSIS_INDEX_ASLEEP       = 1 # The user is asleep, but the specific stage isn’t known.
    SLEEP_ANALYSIS_INDEX_AWAKE        = 2 # The user is awake.
    SLEEP_ANALYSIS_INDEX_ASLEEP_CORE  = 3 # The user is in light or intermediate sleep.
    SLEEP_ANALYSIS_INDEX_ASLEEP_DEEP  = 4 # The user is in deep sleep.
    SLEEP_ANALYSIS_INDEX_ASLEEP_REM   = 5 # The user is in REM sleep.

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        HealthDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # User ID associated with this device.  Used for communications and device association. Left empty for anonymous users.
        self.user_id = self.device_id.split(":")[-1]

        # Distance moved in meters
        # Used to determine if a person has wandered too far from their home
        self.distance_moved = 0

        # True if this device is declared to detect movement.
        self.detect_movements = False

        # Moving information (high frequency / not validated)
        self.information_moving = False

        # Moving knowledge (low frequency / higher reliability)
        self.knowledge_moving = False

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Apple Health")
    
    #---------------------------------------------------------------------------
    # Attributes
    #---------------------------------------------------------------------------
    
    def set_health_user(self, botengine, detect_movements):
        """
        Set the movement detection settings
        :param botengine: BotEngine environment
        :param detect_movements: True if this device should monitor movement status
        """
        self.detect_movements = detect_movements
    
    def set_user_position(self, botengine, latitude, longitude):
        """
        Update position
        :param botengine: BotEngine environment
        :param latitude: Specified latitude of the device
        :param longitude: Specified longitude of the device
        """
        self.latitude = latitude
        self.longitude = longitude


    def did_update_movement_status(self, botengine):
        """
        Determine if we updated the movement status in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the movement status in this execution
        """
        return AppleHealthDevice.MEASUREMENT_NAME_MOVEMENT_STATUS in self.last_updated_params
        
    def get_movement_status(self, botengine):
        """
        Retrieve the most recent movement status value
        :param botengine:
        :return:
        """
        if AppleHealthDevice.MEASUREMENT_NAME_MOVEMENT_STATUS in self.measurements:
            return self.measurements[AppleHealthDevice.MEASUREMENT_NAME_MOVEMENT_STATUS][0][0]
        return None

    def is_detecting_movement(self, botengine):
        """
        Is this Health device detecting any kind of movement
        :param botengine: BotEngine
        :return: True if this Health device is detecting movement
        """
        status = self.get_movement_status(botengine)
        if status is not None:
            return status == AppleHealthDevice.MOVEMENT_STATUS_DETECTED
        return False

    def did_update_sleep(self, botengine):
        """
        Determine if we updated the sleep analysis in this execution
        Examine by seeing if un-indexed parameter is in last_updated_params list
        e.g., Is "sleepAnalysis" in ["sleepAnalysis.0"] should return True.
        :param botengine: BotEngine environment
        :return: True if we updated the sleep analysis in this execution
        """
        return any(AppleHealthDevice.MEASUREMENT_NAME_SLEEP_ANALYSIS in param for param in self.last_updatedparams)

    def get_sleep_analysis(self, botengine, index=SLEEP_ANALYSIS_INDEX_AWAKE):
        """
        Retrieve the most recent sleep analysis value
        :param botengine:
        :return:
        """
        if f"{AppleHealthDevice.MEASUREMENT_NAME_SLEEP_ANALYSIS}.{index}" in self.measurements:
            return self.measurements[f"{AppleHealthDevice.MEASUREMENT_NAME_SLEEP_ANALYSIS}.{index}"][0][0]
        return None

    def get_health_user(self, botengine):
        """
        Return the user settings of this device in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        detect_movements = True
        updated_ms = 0

        for measurement in self.measurements:
            if self.measurements[measurement][0][1] > updated_ms:
                updated_ms = self.measurements[measurement][0][1]

        return {
            "updated_ms": updated_ms,
            "detect_movements": self.detect_movements,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

    def record_moving_information(self, botengine, moving):
        """
        Record information (high-frequency / lower accuracy) that a user is moving
        :param botengine: BotEngine
        :param moving: True if the user is moving
        """
        if moving:
            self.information_moving = True
        else:
            self.information_moving = False

    def record_moving_knowledge(self, botengine, moving):
        """
        Record knowledge (low-frequency / higher accuracy) that a user is moving
        :param botengine: BotEngine
        :param occupied: True if the user is moving
        """
        if moving:
            self.knowledge_moving = True
        else:
            self.knowledge_moving = False

    def information_did_update_user(botengine, location_object, device_object):
        """
        Signal that this user passed through our filters.
        :param botengine: BotEngine
        :param location_object: Location Object
        :param device_object: Device Object
        """
        botengine.get_logger().debug("devices/health.py - Deliver 'information_did_update_user' message to microservices")
        # Location microservices
        for microservice in location_object.intelligence_modules:
            if hasattr(location_object.intelligence_modules[microservice], 'information_did_update_user'):
                try:
                    location_object.intelligence_modules[
                        microservice].information_did_update_user(botengine, device_object)
                except Exception as e:
                    botengine.get_logger().warning("devices/health.py - Error delivering 'information_did_update_user' to location microservice (continuing execution): " + str(e))
                    import traceback
                    botengine.get_logger().error(traceback.format_exc())

        # Device microservices
        for device_id in location_object.devices:
            if hasattr(location_object.devices[device_id], "intelligence_modules"):
                for microservice in location_object.devices[device_id].intelligence_modules:
                    if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'information_did_update_user'):
                        try:
                            location_object.devices[device_id].intelligence_modules[microservice].information_did_update_user(botengine, device_object)
                        except Exception as e:
                            botengine.get_logger().warning("devices/health.py - Error delivering 'information_did_update_user' message to device microservice (continuing execution): " + str(e))
                            import traceback
                            botengine.get_logger().error(traceback.format_exc())

    def health_movement_status_updated(botengine, location_object, device_object, movement_detected, movement_count):
        """
        Updated the movement detection status for the given user

        :param botengine: BotEngine environment
        :param location_object: Location object
        :param device_object: Device object
        :param movement_detected: True if a movement is currently detected on this measurement, False if it's not detected
        :param movement_count: Count of the consecutive number of movement detects based on the targets
        """
        botengine.get_logger().debug("devices/health.py - Deliver 'health_movement_status_updated' message to microservices")
        # Location microservices
        for microservice in location_object.intelligence_modules:
            if hasattr(location_object.intelligence_modules[microservice], 'health_movement_status_updated'):
                try:
                    location_object.intelligence_modules[microservice].health_movement_status_updated(botengine, device_object, movement_detected, movement_count)
                except Exception as e:
                    botengine.get_logger().warning("devices/health.py - Error delivering 'health_movement_status_updated' to location microservice (continuing execution): " + str(e))
                    import traceback
                    botengine.get_logger().error(traceback.format_exc())

        # Device microservices
        for device_id in location_object.devices:
            if hasattr(location_object.devices[device_id], "intelligence_modules"):
                for microservice in location_object.devices[device_id].intelligence_modules:
                    if hasattr(location_object.devices[device_id].intelligence_modules[microservice], 'health_movement_status_updated'):
                        try:
                            location_object.devices[device_id].intelligence_modules[microservice].health_movement_status_updated(botengine, device_object, movement_detected, movement_count)
                        except Exception as e:
                            botengine.get_logger().warning("devices/health.py - Error delivering 'health_movement_status_updated' message to device microservice (continuing execution): " + str(e))
                            import traceback
                            botengine.get_logger().error(traceback.format_exc())