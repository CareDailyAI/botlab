"""
Created on October 27, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.vibration.vibration import VibrationDevice


class DevelcoVibrationDevice(VibrationDevice):
    """
    Develco Vibration Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9119]

    # ===========================================================================
    # Sensor-specific Methods
    # ===========================================================================
    def set_sensitivity_percent(self, botengine, percent):
        """
        Set the sensitivity based on percentage
        :param percent: 0-100%
        """
        range = self.SENSITIVITY_MAXIMUM - self.SENSITIVITY_MINIMUM
        value = int(round(range * (percent / 100.0), 0)) + self.SENSITIVITY_MINIMUM
        botengine.send_command(
            self.device_id, VibrationDevice.MEASUREMENT_NAME_SENSITIVITY, value
        )

    def get_sensitivity_percent(self, botengine):
        """
        Retrieve the current sensitivity percentage
        :param botengine:
        :return: Sensitivity percent
        """
        value = self.get_sensitivity_value(botengine)
        range = self.SENSITIVITY_MAXIMUM - self.SENSITIVITY_MINIMUM
        return int(((value - self.SENSITIVITY_MINIMUM) / range) * 100)

    def set_sensitivity_value(self, botengine, value):
        """
        Set the sensitivity value directly.
        Use the VibrationSensor.SENSITIVITY_MINIMUM and VibrationSensor.SENSITIVITY_MAXIMUM for reference
        :param value: Value to set for sensitivity
        """
        if value < self.SENSITIVITY_MINIMUM:
            value = self.SENSITIVITY_MINIMUM

        if value > self.SENSITIVITY_MAXIMUM:
            value = self.SENSITIVITY_MAXIMUM

        botengine.send_command(
            self.device_id, VibrationDevice.MEASUREMENT_NAME_SENSITIVITY, value
        )

    def get_sensitivity_value(self, botengine):
        """
        Retrieve the current sensitivity value
        :param botengine:
        :return: Sensitivity value
        """
        if self.MEASUREMENT_NAME_SENSITIVITY in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_SENSITIVITY][0][0]

        return self.SENSITIVITY_MINIMUM

    def did_start_touch(self, botengine):
        """
        Is the sensor touched, even momentarily?
        :param botengine:
        :return: True if the sensor is touched
        """
        if self.MEASUREMENT_NAME_MOVEMENT_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_MOVEMENT_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_MOVEMENT_STATUS][0][0]

        return False

    def did_stop_touch(self, botengine):
        """
        Did the sensor stop getting touched?
        :param botengine:
        :return: True if the sensor is touched
        """
        if self.MEASUREMENT_NAME_MOVEMENT_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_MOVEMENT_STATUS in self.last_updated_params:
                return not self.measurements[self.MEASUREMENT_NAME_MOVEMENT_STATUS][0][
                    0
                ]

        return False

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
