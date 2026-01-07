"""
Created on June 17, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from gc import is_finalized
import utilities.utilities as utilities
from devices.device import Device, MINIMUM_MEASUREMENTS_TO_CACHE


class BedDevice(Device):
    
    # Goals
    GOAL_PRESSUREPAD_BED = 0
    GOAL_PRESSUREPAD_CHAIR = 1

    # Behavior identifiers shared across all bed devices
    BEHAVIOR_TYPE_BED = 0
    BEHAVIOR_TYPE_CHAIR = 1
    
    # Parameters
    MEASUREMENT_NAME_HEART_RATE = "hr"
    MEASUREMENT_NAME_BREATHING_RATE = "br"
    MEASUREMENT_NAME_ROOM_TYPE = "roomType"
    MEASUREMENT_NAME_SLEEP_OUT_OF_BED = "sleepOut"
    MEASUREMENT_NAME_SLEEP_TOTAL = "sleepTotal"
    MEASUREMENT_NAME_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_SLEEP_AWAKE = "sleepAwake"
    MEASUREMENT_NAME_SLEEP_DEEP = "sleepDeep"
    MEASUREMENT_NAME_SLEEP_LIGHT = "sleepLight"
    MEASUREMENT_NAME_SLEEP_REM = "sleepRem"
    MEASUREMENT_NAME_SLEEP_TOTAL = "sleepTotal"
    MEASUREMENT_NAME_HEART_RATE_RESTING = "hrResting"
    MEASUREMENT_NAME_HR_VARIABILITY = "hrVariability"
    MEASUREMENT_NAME_OCCUPANCY = "occupancy"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_OCCUPANCY,
        MEASUREMENT_NAME_BED_STATUS,
        MEASUREMENT_NAME_HEART_RATE,
        MEASUREMENT_NAME_HEART_RATE_RESTING,
        MEASUREMENT_NAME_BREATHING_RATE,
        MEASUREMENT_NAME_HR_VARIABILITY,
        MEASUREMENT_NAME_SLEEP_AWAKE,
        MEASUREMENT_NAME_SLEEP_DEEP,
        MEASUREMENT_NAME_SLEEP_LIGHT,
        MEASUREMENT_NAME_SLEEP_REM,
        MEASUREMENT_NAME_SLEEP_TOTAL,
    ]


    # Device types
    DEVICE_TYPES = []

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )
        
        # Set goal_id to be recognized as a pressure pad bed device
        self.goal_id = BedDevice.GOAL_PRESSUREPAD_BED

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
        return _("Bed")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        occupied = bool(self.is_in_bed(None))

        if self.is_behavior_chair(None):
            return "couch"

        # Default to bed behavior/icon
        return "bed" if occupied else "bed-empty"


    def is_in_bed(self, botengine):
        """
        Is this Health device detecting someone in bed
        :param botengine: BotEngine
        :return: True if this Health device is detecting someone in bed
        """
        return None

    def is_in_bedroom(self, botengine):
        """
        Is this bed device in a bedroom?
        Bed devices are typically placed in bedrooms, so this generally returns True.
        :param botengine: BotEngine
        :return: True if this bed device is in a bedroom
        """
        return True

    def did_update_bed_status(self, botengine):
        """
        Determine if we updated the bed status in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the bed status in this execution
        """
        return (BedDevice.MEASUREMENT_NAME_BED_STATUS in self.last_updated_params or 
                BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params)

    def is_behavior_bed(self, botengine):
        """
        :return: True if the device is configured for bed behavior.
        """
        return self.is_goal_id(BedDevice.BEHAVIOR_TYPE_BED)

    def is_behavior_chair(self, botengine):
        """
        :return: True if the device is configured for chair behavior.
        """
        return self.is_goal_id(BedDevice.BEHAVIOR_TYPE_CHAIR)

    def did_get_in_bed(self, botengine):
        """
        Did the person get in bed?
        :param botengine: BotEngine environment
        :return: True if the person got in bed
        """
        if self.did_update_bed_status(botengine):
            if self.is_in_bed(botengine):
                return True
        return False

    def did_get_out_of_bed(self, botengine):
        """
        Did the person get out of bed?
        :param botengine: BotEngine environment
        :return: True if the person got out of bed
        """
        
        if self.did_update_bed_status(botengine):
            if not self.is_in_bed(botengine):
                return True
        return False

    def last_out_of_bed_timestamp_ms(self, botengine):
        """
        Get the last timestamp when this BedDevice reported being out of bed (bed status = 0).
        :param botengine: BotEngine environment
        :return: Timestamp in milliseconds when someone last got out of bed, or None if no bed exit found
        """
        if BedDevice.MEASUREMENT_NAME_BED_STATUS not in self.measurements:
            return None
        
        if len(self.measurements[BedDevice.MEASUREMENT_NAME_BED_STATUS]) == 0:
            return None
        
        last_out_of_bed_timestamp = None
        
        for measurement in self.measurements[BedDevice.MEASUREMENT_NAME_BED_STATUS]:
            value, timestamp = measurement[0], measurement[1]
            # Check if this measurement shows out of bed (value = 0)
            if value == 0:
                if last_out_of_bed_timestamp is None or timestamp > last_out_of_bed_timestamp:
                    last_out_of_bed_timestamp = timestamp
        
        return last_out_of_bed_timestamp

    
    def did_update_breathing_rate(self, botengine):
        """
        Determine if we updated the breathing rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the breathing rate in this execution
        """
        return BedDevice.MEASUREMENT_NAME_BREATHING_RATE in self.last_updated_params

    def get_breathing_rate(self, botengine):
        """
        Retrieve the most recent breathing_rate value
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_BREATHING_RATE in self.measurements:
            return self.measurements[BedDevice.MEASUREMENT_NAME_BREATHING_RATE][0][0]
        return None


    def did_update_heart_rate(self, botengine):
        """
        Determine if we updated the heart rate in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate in this execution
        """
        return BedDevice.MEASUREMENT_NAME_HEART_RATE in self.last_updated_params

    def get_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            return self.measurements[BedDevice.MEASUREMENT_NAME_HEART_RATE][0][0]
        return None

    def get_average_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[BedDevice.MEASUREMENT_NAME_HEART_RATE]
                ]
            )
        return None

    def did_update_heart_rate_resting(self, botengine):
        """
        Determine if we updated the heart rate resting in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the heart rate resting in this execution
        """
        return (
            BedDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.last_updated_params
        )

    def get_heart_rate_resting(self, botengine):
        """
        Retrieve the most recent heart rate resting value
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.measurements:
            return self.measurements[BedDevice.MEASUREMENT_NAME_HEART_RATE_RESTING][
                0
            ][0]
        return None

    def get_average_heart_rate_resting(self, botengine):
        """
        Retrieve the most recent heart rate resting value
        :param botengine:
        :return:
        """
        if BedDevice.MEASUREMENT_NAME_HEART_RATE_RESTING in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[
                        BedDevice.MEASUREMENT_NAME_HEART_RATE_RESTING
                    ]
                ]
            )
        return None


    def did_change_heart_rate(self, botengine):
        """
        Did the heart rate change? (Pulse Rate per minute)
        :param botengine:
        :return: True if heart rate changed
        """
        if BedDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            return BedDevice.MEASUREMENT_NAME_HEART_RATE in self.last_updated_params

    def did_change_hr_variability(self, botengine):
        """
        Did the heart rate variability change? (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: True if hr variability changed
        """
        if BedDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            return (
                BedDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.last_updated_params
            )


    def get_hr_variability(self, botengine):
        """
        Retrieve hr variability (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: hr variability measurement
        """
        if BedDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            if len(self.measurements[BedDevice.MEASUREMENT_NAME_HR_VARIABILITY]) > 0:
                return self.measurements[BedDevice.MEASUREMENT_NAME_HR_VARIABILITY][
                    0
                ][0]

        return None

    def get_average_hr_variability(self, botengine):
        """
        Retrieve hr variability (The variance in time between the beats of your heart. If 60 beats
        per minute, it's not beating once per second, there may be .9 seconds between two beats and
         1.15 seconds between two beats. The greater the variability, the healthier a patient is )
        :param botengine:
        :return: hr variability measurement
        """
        if BedDevice.MEASUREMENT_NAME_HR_VARIABILITY in self.measurements:
            if len(self.measurements[BedDevice.MEASUREMENT_NAME_HR_VARIABILITY]) > 0:
                from statistics import mean

                return mean(
                    [
                        x[0]
                        for x in self.measurements[
                            BedDevice.MEASUREMENT_NAME_HR_VARIABILITY
                        ]
                    ]
                )

        return None

    def update(self, botengine, measures):
        """
        Intercept the parent Device.update() method to add occupancy correction logic.
        If heartrate or breathing is detected but occupancy is 0, force occupancy to 1.
        :param botengine: BotEngine environment
        :param measures: Full or partial measurement block from bot inputs
        :return: Tuple of (updated_devices, updated_metadata) from parent update
        """
        # Call parent Device.update() and capture the return value
        result = Device.update(self, botengine, measures)
        
        # Check if we need to correct occupancy
        # Only proceed if we have heartrate or breathing measurements in this execution
        heartrate_updated = self.did_update_heart_rate(botengine)
        breathing_updated = self.did_update_breathing_rate(botengine)
        
        if heartrate_updated or breathing_updated:
            # Check current occupancy status
            current_occupancy = None
            
            # Check both bedStatus and occupancy measurements
            if BedDevice.MEASUREMENT_NAME_BED_STATUS in self.measurements:
                if len(self.measurements[BedDevice.MEASUREMENT_NAME_BED_STATUS]) > 0:
                    current_occupancy = self.measurements[BedDevice.MEASUREMENT_NAME_BED_STATUS][0][0]
            
            if current_occupancy is None and BedDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
                if len(self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    current_occupancy = self.measurements[BedDevice.MEASUREMENT_NAME_OCCUPANCY][0][0]
            
            # If occupancy is 0 (unoccupied) but we have heartrate or breathing, force occupancy to 1
            if current_occupancy == 0:
                current_timestamp = botengine.get_timestamp()
                
                # Add occupancy measurement with value 1
                self.add_measurement(botengine, BedDevice.MEASUREMENT_NAME_OCCUPANCY, 1, current_timestamp)
                
                # Add to last_updated_params so did_update_bed_status() will return True
                if BedDevice.MEASUREMENT_NAME_OCCUPANCY not in self.last_updated_params:
                    self.last_updated_params.append(BedDevice.MEASUREMENT_NAME_OCCUPANCY)
                
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "Corrected occupancy to 1 for device '{}' due to heartrate/breathing detection".format(
                        self.description
                    )
                )
        
        return result
