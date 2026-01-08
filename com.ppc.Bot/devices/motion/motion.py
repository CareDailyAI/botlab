"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.device import Device


class MotionDevice(Device):
    """Motion Sensor"""

    # Motion status
    MEASUREMENT_NAME_STATUS = "motionStatus"

    MEASUREMENT_PARAMETERS_LIST = [MEASUREMENT_NAME_STATUS]

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10038]

    # Goals
    GOAL_MOTION_PROTECT_HOME = 50
    GOAL_MOTION_ALERT_ON_OCCUPANCY = 51
    GOAL_MOTION_SKIP = 52

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_2xAA"

    # Type of battery
    BATTERY_TYPE = "AA"

    # Number of seconds that elapses before the motion detector sends a second packet saying motion is no longer detected
    MOTION_AUTO_OFF_SECONDS = 15

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

        # Default behavior
        self.goal_id = MotionDevice.GOAL_MOTION_PROTECT_HOME
        
        # Override for bedroom classification from room classification algorithm
        # None = no override, True = force bedroom, False = force not bedroom
        self.is_in_bedroom_override = None

    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        Device.new_version(self, botengine)

        # Added: July 29, 2025
        if not hasattr(self, 'is_in_bedroom_override'):
            self.is_in_bedroom_override = None
        pass

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Motion Sensor")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "motion"

    def is_in_bedroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bedroom
        """
        # Check for override from room classification algorithm
        if hasattr(self, 'is_in_bedroom_override') and self.is_in_bedroom_override is not None:
            return self.is_in_bedroom_override
        
        bedroom_names = [
            _("bed"),
            _("bett"),
            _("bdrm"),
            _("moms room"),
            _("dads room"),
            _("mom's room"),
            _("dad's room"),
        ]

        for name in bedroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, "bedroom")

    def is_in_bathroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bathroom
        """
        bathroom_names = [_("schlaf"), _("bath"), _("toilet"), _("shower"), _("powder")]

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, "bathroom")

    # ===========================================================================
    # Measurements
    # ===========================================================================
    def is_detecting_motion(self, botengine=None):
        """
        Are we currently detecting motion
        :param botengine:
        :return:
        """
        if MotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if len(self.measurements[MotionDevice.MEASUREMENT_NAME_STATUS]) > 0:
                return self.measurements[MotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def did_start_detecting_motion(self, botengine=None):
        """
        Did we start detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        if MotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if MotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[MotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def did_stop_detecting_motion(self, botengine=None):
        """
        Did we stop detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned off in the last execution
        """
        
        if MotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if MotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return not self.measurements[MotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def force_stop_detecting_motion(self, botengine=None):
        """
        Force stop detecting motion
        :param botengine: BotEngine environment
        :return:
        """
        self.last_updated_params.append(MotionDevice.MEASUREMENT_NAME_STATUS)
        self.measurements[MotionDevice.MEASUREMENT_NAME_STATUS][0] = (False, botengine.get_timestamp())

    # ===========================================================================
    # CSV methods for machine learning algorithm integrations
    # ===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a standardized .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        return Device.get_csv(
            self,
            botengine,
            oldest_timestamp_ms=oldest_timestamp_ms,
            newest_timestamp_ms=newest_timestamp_ms,
            params=[MotionDevice.MEASUREMENT_NAME_STATUS],
        )
