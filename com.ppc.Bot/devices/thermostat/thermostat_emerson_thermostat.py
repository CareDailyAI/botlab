'''
Created on March 20, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Device Model
# https://presence.atlassian.net/wiki/display/devices/Thermostat

from devices.thermostat.thermostat import ThermostatDevice

# Set the default rounding to 3 numbers.
from decimal import *
getcontext().prec = 1


class ThermostatEmersonDevice(ThermostatDevice):
    """Emerson Thermostat Device"""
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4260]
    
    # Minimum setpoint in Celsius
    MIN_SETPOINT_C = 7.0
    
    # Maximum setpoint in Celsius
    MAX_SETPOINT_C = 29.0
    
    
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Emerson Thermostat")

    def set_system_mode(self, botengine, system_mode, reliably=False):
        """
        Set the system mode
        :param botengine:
        :param system_mode:
        :param reliably: True to keep retrying to get the command through
        :return:
        """
        ThermostatDevice.set_system_mode(self, botengine, system_mode, reliably=False)

    def set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the cooling setpoint
        :param botengine: BotEngine environment
        :param setpoint_celsius: Absolute setpoint in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        ThermostatDevice.set_cooling_setpoint(self, botengine, setpoint_celsius, reliably=False)

    def set_heating_setpoint(self, botengine, setpoint_celsius, reliably=False):
        """
        Set the heating set-point
        :param botengine: BotEngine environmnet
        :param setpoint_celsius: Temperature in Celsius
        :param reliably: True to keep retrying to get the command through
        """
        ThermostatDevice.set_heating_setpoint(self, botengine, setpoint_celsius, reliably=False)
