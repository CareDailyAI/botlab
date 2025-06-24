"""
Created on October 27, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.vibration.vibration import VibrationDevice


class LinkHighVibrationDevice(VibrationDevice):
    """
    LinkHigh Touch Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10019]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"

    # Type of battery
    BATTERY_TYPE = "CR2032"

    # ===========================================================================
    # Sensor-specific Methods
    # ===========================================================================
    def set_sensitivity_percent(self, botengine, percent):
        """
        Set the sensitivity based on percentage
        :param percent: 0-100%
        """
        return None

    def get_sensitivity_percent(self, botengine):
        """
        Retrieve the current sensitivity percentage
        :param botengine:
        :return: Sensitivity percent
        """
        return None

    def set_sensitivity_value(self, botengine, value):
        """
        Set the sensitivity value directly.
        Use the VibrationSensor.SENSITIVITY_MINIMUM and VibrationSensor.SENSITIVITY_MAXIMUM for reference
        :param value: Value to set for sensitivity
        """
        return None

    def get_sensitivity_value(self, botengine):
        """
        Retrieve the current sensitivity value
        :param botengine:
        :return: Sensitivity value
        """
        return None

    def did_get_touched(self, botengine):
        """
        Is the sensor touched, even momentarily?
        :param botengine:
        :return: True if the sensor is touched
        """
        return self.did_start_moving(botengine)

    def is_moving(self, botengine):
        """
        Is the sensor currently moving
        :param botengine: BotEngine
        :return: True if the sensor is currently moving
        """
        if self.MEASUREMENT_NAME_VIBRATION_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_VIBRATION_STATUS][0][0]

        return False

    def did_start_moving(self, botengine):
        """
        Did the sensor start continually moving, based on the current sensitivity value?
        :param botengine:
        :return: True if the sensor started moving
        """
        if self.MEASUREMENT_NAME_VIBRATION_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_VIBRATION_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_VIBRATION_STATUS][0][0]

        return False

    def did_stop_moving(self, botengine):
        """
        Did the sensor stop continually moving?
        :param botengine:
        :return: True if the sensor stopped moving
        """
        if self.MEASUREMENT_NAME_VIBRATION_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_VIBRATION_STATUS in self.last_updated_params:
                return not self.measurements[self.MEASUREMENT_NAME_VIBRATION_STATUS][0][
                    0
                ]

        return False
