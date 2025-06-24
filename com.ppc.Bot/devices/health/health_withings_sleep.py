"""
Created on January 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.health.health import HealthDevice


class WithingsSleepHealthDevice(HealthDevice):
    """
    Withings Sleep Pad Device
    """

    # Goals
    GOAL_BED = 0
    GOAL_LATE_NIGHT_ALERTS = 1
    GOAL_SLEEP_ANALYSIS = 2
    GOAL_ALWAYS_ALERT = 3

    # Parameters
    MEASUREMENT_NAME_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_SLEEP_AWAKE = "sleepAwake"
    MEASUREMENT_NAME_SLEEP_DEEP = "sleepDeep"
    MEASUREMENT_NAME_SLEEP_LIGHT = "sleepLight"
    MEASUREMENT_NAME_SLEEP_REM = "sleepRem"
    MEASUREMENT_NAME_SLEEP_TOTAL = "sleepTotal"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_BED_STATUS,
        HealthDevice.MEASUREMENT_NAME_HEART_RATE,
        HealthDevice.MEASUREMENT_NAME_HEART_RATE_RESTING,
        HealthDevice.MEASUREMENT_NAME_BREATHING_RATE,
        HealthDevice.MEASUREMENT_NAME_HR_VARIABILITY,
        MEASUREMENT_NAME_SLEEP_AWAKE,
        MEASUREMENT_NAME_SLEEP_DEEP,
        MEASUREMENT_NAME_SLEEP_LIGHT,
        MEASUREMENT_NAME_SLEEP_REM,
        MEASUREMENT_NAME_SLEEP_TOTAL,
    ]

    # Device type
    DEVICE_TYPES = [4302]

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        HealthDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

        # Default behavior
        self.goal_id = WithingsSleepHealthDevice.GOAL_BED

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Withings Sleep")

    # ===========================================================================
    # Attributes
    # ===========================================================================

    def is_pressure_applied(self, botengine=None):
        """
        :return: True if pressure is applied
        """
        if WithingsSleepHealthDevice.MEASUREMENT_NAME_BED_STATUS in self.measurements:
            return self.measurements[
                WithingsSleepHealthDevice.MEASUREMENT_NAME_BED_STATUS
            ][0][0]

        return False

    def did_change_state(self, botengine=None):
        """
        :return: True if this entry sensor's state was updated just now
        """
        return (
            WithingsSleepHealthDevice.MEASUREMENT_NAME_BED_STATUS
            in self.last_updated_params
        )

    def did_apply_pressure(self, botengine=None):
        """
        Did you get on the pressure pad?
        :param botengine:
        :return: True if the door opened right now
        """
        return self.did_change_state(botengine) and self.is_pressure_applied(botengine)

    def did_release_pressure(self, botengine=None):
        """
        Did you get off the pressure pad?
        :param botengine:
        :return: True if the door closed right now
        """
        return self.did_change_state(botengine) and not self.is_pressure_applied(
            botengine
        )
