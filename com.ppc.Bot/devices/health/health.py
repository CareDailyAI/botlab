'''
Created on April 4, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''

from devices.device import Device
import utilities.utilities as utilities

class HealthDevice(Device):
    """
    Health Device
    """
    # Parameters
    MEASUREMENT_NAME_MOVEMENT_STATUS = "movementStatus"
    MEASUREMENT_NAME_HEART_RATE = "hr"
    MEASUREMENT_NAME_STEPS = "steps"
    MEASUREMENT_NAME_IN_BED_SLEEP_ANALYSIS      = "sleepAnalysis.0" # The user is in bed.
    MEASUREMENT_NAME_ASLEEP_SLEEP_ANALYSIS      = "sleepAnalysis.1" # The user is asleep, but the specific stage isn’t known.
    MEASUREMENT_NAME_AWAKE_SLEEP_ANALYSIS       = "sleepAnalysis.2" # The user is awake.
    MEASUREMENT_NAME_ASLEEP_CORE_SLEEP_ANALYSIS = "sleepAnalysis.3" # The user is in light or intermediate sleep.
    MEASUREMENT_NAME_ASLEEP_DEEP_SLEEP_ANALYSIS = "sleepAnalysis.4" # The user is in deep sleep.
    MEASUREMENT_NAME_ASLEEP_REM_SLEEP_ANALYSIS  = "sleepAnalysis.5" # The user is in REM sleep.
    MEASUREMENT_NAME_BREATHING_RATE = "br"
    MEASUREMENT_NAME_BREATHING_RATE_STABILITY = "brStability"
    MEASUREMENT_NAME_HEART_RATE_STABILITY = "hrStability"
    MEASUREMENT_NAME_MOTION_INDEX = "motionIndex"
    MEASUREMENT_NAME_MOTION_STABILITY = "motionStability"
    MEASUREMENT_NAME_OCCUPANCY = "occupancy"
    MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC = 'bloodPressureDiastolic'
    MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC = 'bloodPressureSystolic'
    MEASUREMENT_NAME_HEMATOCRIT = 'hematocrit'
    MEASUREMENT_NAME_HEMOGLOBIN = 'hemoglobin'
    MEASUREMENT_NAME_HEARTRATE = 'hr'
    MEASUREMENT_NAME_HR_VARIABILITY = 'hrVariability'
    MEASUREMENT_NAME_PERFUSION_INDEX = 'perfusionIndex'
    MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX = 'plethVariabilityIndex'
    MEASUREMENT_NAME_PROTEIN = 'protein'
    MEASUREMENT_NAME_SPO2 = 'spo2'

    # Movement Status
    MOVEMENT_STATUS_DETECTED = 1
    MOVEMENT_STATUS_EXIT = 0

    # Device types
    DEVICE_TYPES = []

    # Distance in meters used to determine if a person has wandered too far from their home
    MAXIMUM_DISTANCE_MOVED_M = 100

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Distance moved in meters
        # Used to determine if a person has wandered too far from their home
        self.distance_moved = 0

        # True if this device is declared to detect movement.
        self.detect_movements = False

        # User ID associated with this device.  Used for communications and device association. Left empty for anonymous users.
        self.user_id = self.device_id.split(":")[-1]

        # Moving information (high frequency / not validated)
        self.information_moving = False

        # Moving knowledge (low frequency / higher reliability)
        self.knowledge_moving = False

        # Last known latitude position of the user, optional
        self.latitude = None

        # Last known longitude position of the user, optional
        self.longitude = None
        
    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        Device.new_version(self, botengine)
        return
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Health")
    
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
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "heartbeat"

    def did_update_movement_status(self, botengine):
        """
        Determine if we updated the movement status in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the movement status in this execution
        """
        return "movementStatus" in self.last_updated_params
        
    def get_movement_status(self, botengine):
        """
        Retrieve the most recent movement status value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_MOVEMENT_STATUS in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_MOVEMENT_STATUS][0][0]
        return None

    def is_detecting_movement(self, botengine):
        """
        Is this Health device detecting any kind of movement
        :param botengine: BotEngine
        :return: True if this Health device is detecting movement
        """
        status = self.get_movement_status(botengine)
        if status is not None:
            return status == HealthDevice.MOVEMENT_STATUS_DETECTED
        return False

    def did_update_breathing_rate(self, botengine):
        """
        Determine if we updated the breathing rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the breathing rate in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_BREATHING_RATE in self.last_updated_params

    def get_breathing_rate(self, botengine):
        """
        Retrieve the most recent breathing_rate value
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_BREATHING_RATE in self.measurements:
            return self.measurements[HealthDevice.MEASUREMENT_NAME_BREATHING_RATE][0][0]
        return None

    def did_update_heart_rate(self, botengine):
        """
        Determine if we updated the heart rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate in this execution
        """
        return "hr" in self.last_updated_params
        
    def get_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value with timestamp
        [0][0] = HR and [0][1] = timestamp
        :param botengine:
        :return:
        """
        if HealthDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            botengine.get_logger().info("HR MEASUREMENTS : {}".format(self.measurements))
            return self.measurements[HealthDevice.MEASUREMENT_NAME_HEART_RATE][0][0], self.measurements[HealthDevice.MEASUREMENT_NAME_HEART_RATE][0][1]
        return None

    def did_update_steps(self, botengine):
        """
        Determine if we updated the steps in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the steps in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_STEPS in self.last_updated_params

    def get_steps(self, botengine):
        """
        Retrieve the most recent steps value with timestamp
        [0][0] = steps and [0][1] = timestamp
        :param botengine:
        :return:
        """

        if HealthDevice.MEASUREMENT_NAME_STEPS in self.measurements:
            botengine.get_logger().info("health.py: STEP MEASUREMENTS : {}".format(self.measurements))
            return self.measurements[HealthDevice.MEASUREMENT_NAME_STEPS][0][0], self.measurements[HealthDevice.MEASUREMENT_NAME_STEPS][0][1]
        return None

    def did_update_sleep(self, botengine):
        """
        Determine if we updated the sleep analysis in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate in this execution
        """
        return HealthDevice.MEASUREMENT_NAME_IN_BED_SLEEP_ANALYSIS in self.last_updated_params or HealthDevice.MEASUREMENT_NAME_ASLEEP_SLEEP_ANALYSIS in self.last_updated_params

    def get_sleep_in_bed(self, botengine):
        """
        Retrieve the most recent sleep value of occupant in bed with timestamp
        [0][0] = sleep_analysis and [0][1] = timestamp
        :param botengine:
        :return:
        """

        if HealthDevice.MEASUREMENT_NAME_IN_BED_SLEEP_ANALYSIS in self.measurements:
            botengine.get_logger().info("haelth.py: SLEEP MEASUREMENTS IN BED : {}".format(self.measurements))
            return self.measurements[HealthDevice.MEASUREMENT_NAME_IN_BED_SLEEP_ANALYSIS][0][0], self.measurements[HealthDevice.MEASUREMENT_NAME_IN_BED_SLEEP_ANALYSIS][0][1]
        return None

    def get_sleep_asleep(self, botengine):
        """
        Retrieve the most recent sleep value of occupant asleep with timestamp
        [0][0] = sleep_analysis and [0][1] = timestamp
        :param botengine:
        :return:
        """

        if HealthDevice.MEASUREMENT_NAME_ASLEEP_SLEEP_ANALYSIS in self.measurements:
            botengine.get_logger().info("health.py: SLEEP MEASUREMENTS ASLEEP: {}".format(self.measurements))
            return self.measurements[HealthDevice.MEASUREMENT_NAME_ASLEEP_SLEEP_ANALYSIS][0][0], self.measurements[HealthDevice.MEASUREMENT_NAME_ASLEEP_SLEEP_ANALYSIS][0][1]
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

    def did_change_blood_pressure_diastolic(self, botengine):
        """
        Did the Diastolic blood pressure change? (Bottom number of blood pressure)
        :param botengine:
        :return: True if the diastolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC in self.last_updated_params

    def did_change_blood_pressure_systolic(self, botengine):
        """
        Did the systolic blood pressure change? (Top number of blood pressure)
        :param botengine:
        :return: True if systolic blood pressure changed
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC in self.last_updated_params

    def did_change_hematocrit(self, botengine):
        """
        Did hematocrit change? (Percentage of red blood cells in your blood)
        :param botengine:
        :return: True if hematocrit changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.last_updated_params

    def did_change_hemoglobin(self, botengine):
        """
        Did the hemoglobin change?  (Protein in red blood cell that carries oxygen - low or high oxygenated red blood
        cell count - tells if one is anemic or not)
        :param botengine:
        :return: True if hemoglobin changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.last_updated_params

    def did_change_heartrate(self, botengine):
        """
        Did othe heart rate change? (Pulse Rate per minute)
        :param botengine:
        :return: True if heart rate changed
        """
        if HealthDevice.MEASUREMENT_NAME_HEARTRATE in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HEARTRATE in self.last_updated_params

    def did_change_hr_variability(self, botengine):
        """
        Did the heart rate variability change? (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: True if hr variability changed
        """
        if HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.last_updated_params

    def did_change_perfusion_index(self, botengine):
        """
        Did the perfusion index change? (Oxygen levels in blood)
        :param botengine:
        :return: True if perfusion index change
        """
        if HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX in self.last_updated_params

    def did_change_pleth_variability_index(self, botengine):
        """
        Did the pleth variablity index change?
        :param botengine:
        :return: True if pleth variability index changed
        """
        if HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX in self.last_updated_params

    def did_change_protein(self, botengine):
        """
        Did protein change?
        :param botengine:
        :return: True if protein changed
        """
        if HealthDevice.MEASUREMENT_NAME_PROTEIN in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_PROTEIN in self.last_updated_params

    def did_change_spo2(self, botengine):
        """
        Did spO2 change? (Oxygen Perfusion
        :param botengine:
        :return: True if spo2 changed
        """
        if HealthDevice.MEASUREMENT_NAME_SPO2 in self.measurements:
            return HealthDevice.MEASUREMENT_NAME_SPO2 in self.last_updated_params

    def get_blood_pressure_diastolic(self, botengine):
        """
        Retrieve the Diastolic blood pressure change (Bottom number of blood pressure)
        :param botengine:
        :return: diastolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_DIASTOLIC][0][0]

        return None

    def get_blood_pressure_systolic(self, botengine):
        """
        Retrieve systolic blood pressure (Top number of blood pressure)
        :param botengine:
        :return: systolic blood pressure measurement
        """
        if HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_BLOOD_PRESSURE_SYSTOLIC][0][0]

        return None

    def get_hematocrit(self, botengine):
        """
        Retrieve hematocrit (Percentage of red blood cells in your blood)
        :param botengine:
        :return: hematocrit measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HEMATOCRIT in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HEMATOCRIT]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HEMATOCRIT][0][0]

        return None

    def get_hemoglobin(self, botengine):
        """
        Retrieve hemoglobin  (Protein in red blood cell that carries oxygen - low or high oxygenated red blood
        cell count - tells if one is anemic or not)
        :param botengine:
        :return: hemoglobin measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HEMOGLOBIN][0][0]

        return None

    def get_heartrate(self, botengine):
        """
        Retrieve heart rate (Pulse Rate per minute)
        :param botengine:
        :return: heart rate measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HEARTRATE in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HEARTRATE]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HEARTRATE][0][0]

        return None

    def get_hr_variability(self, botengine):
        """
        Retrieve hr variability (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: hr variability measurement
        """
        if HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY][0][0]

        return None

    def get_perfusion_index(self, botengine):
        """
        Retrieve perfusion index (Oxygen levels in blood)
        :param botengine:
        :return: perfusion index measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_PERFUSION_INDEX][0][0]

        return None

    def get_pleth_variability_index(self, botengine):
        """
        Retrieve pleth variability
        :param botengine:
        :return: pleth variability measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_PLETH_VARIABILITY_INDEX][0][0]

        return None

    def get_protein(self, botengine):
        """
        Retrieve protein
        :param botengine:
        :return: protein measurement
        """
        if HealthDevice.MEASUREMENT_NAME_PROTEIN in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_PROTEIN]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_PROTEIN][0][0]

        return None

    def get_spo2(self, botengine):
        """
        Retrieve sp02 (Oxygen Perfusion)
        :param botengine:
        :return: sp02 measurement
        """
        if HealthDevice.MEASUREMENT_NAME_SPO2 in self.measurements:
            if len(self.measurements[HealthDevice.MEASUREMENT_NAME_SPO2]) > 0:
                return self.measurements[HealthDevice.MEASUREMENT_NAME_SPO2][0][0]

        return None
