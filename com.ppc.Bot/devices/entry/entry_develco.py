"""
Created on December 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.entry.entry import EntryDevice


class DevelcoEntryDevice(EntryDevice):
    """
    Develco Entry Sensor
    """

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_aaa"

    # Type of battery
    BATTERY_TYPE = "AAA"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9114]

    # Measurement Names
    MEASUREMENT_NAME_STATUS = "doorStatus"
    MEASUREMENT_DEG_C = "degC"

    MEASUREMENT_PARAMETERS_LIST = [MEASUREMENT_NAME_STATUS]

    def get_temperature_c(self, botengine=None):
        """
        Get the latest temperature in Celsius
        :param botengine:
        :return: temperature in Celsius
        """
        if DevelcoEntryDevice.MEASUREMENT_DEG_C in self.measurements:
            return self.measurements[DevelcoEntryDevice.MEASUREMENT_DEG_C][0][0]

        return None

    def set_application_light(self, botengine, on=True):
        """
        :param botengine: BotEngine environment
        :param on: True if turn on the application light
        :return:
        """
        value = "0"
        if on:
            value = "1"
        botengine.send_command(self.device_id, "ledAppEnable", value)

    def set_error_light(self, botengine, on=True):
        """
        :param botengine: BotEngine environment
        :param on: True if turn on the error light
        :return:
        """
        value = "0"
        if on:
            value = "1"
        botengine.send_command(self.device_id, "ledErrEnable", value)
