'''
Created on October 30, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class TemperatureDevice(Device):
    """
    Temperature Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10033]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"

    # Degrees C measurement parameter
    MEASUREMENT_DEG_C = "degC"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_DEG_C
    ]

    
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Temperature Sensor")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "temp-humidity"


    def get_temperature_c(self, botengine=None):
        """
        Get the latest temperature in Celsius
        :param botengine:
        :return: temperature in Celsius
        """
        if TemperatureDevice.MEASUREMENT_DEG_C in self.measurements:
            return self.measurements[TemperatureDevice.MEASUREMENT_DEG_C][0][0]

        return None

    def did_change_state(self, botengine=None):
        """
        :return: True if this sensor's state was updated just now
        """
        return TemperatureDevice.MEASUREMENT_DEG_C in self.last_updated_params