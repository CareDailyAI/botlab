'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class TemperatureHumidityDevice(Device):
    """Temperature & Humidity Sensor"""
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10034]
    
    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"
    
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Temperature and Humidity Sensor")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "temp-humidity"
    