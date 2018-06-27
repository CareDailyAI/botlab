'''
Created on March 27, 2017

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

# fanModeSequence values
FAN_MODE_SEQUENCE__LOW_MED_HIGH = 0
FAN_MODE_SEQUENCE__LOW_HIGH = 1
FAN_MODE_SEQUENCE__LOW_MED_HIGH_AUTO = 2
FAN_MODE_SEQUENCE__LOW_HIGH_AUTO = 3
FAN_MODE_SEQUENCE__ON_AUTO = 4

# controlSequenceOfOperation values                                         # Possible System Modes
CONTROL_SEQUENCE_OPERATION__COOLING_ONLY = 0                                # OFF/COOL
CONTROL_SEQUENCE_OPERATION__COOLING_WITH_REHEAT = 1                         # OFF/COOL
CONTROL_SEQUENCE_OPERATION__HEATING_ONLY = 2                                # OFF/HEAT
CONTROL_SEQUENCE_OPERATION__HEATING_WITH_REHEAT = 2                         # OFF/COOL/HEAT
CONTROL_SEQUENCE_OPERATION__COOLING_AND_HEATING_4_PIPES = 4                 # OFF/COOL/HEAT
CONTROL_SEQUENCE_OPERATION__COOLING_AND_HEATING_4_PIPES_WITH_REHEAT = 5     # OFF/COOL/HEAT


class ThermostatCentralitePearlDevice(ThermostatDevice):
    """Centralite Pearl Thermostat Device"""
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10037]
    
    # Minimum setpoint in Celsius
    MIN_SETPOINT_C = 7.0
    
    # Maximum setpoint in Celsius
    MAX_SETPOINT_C = 29.0
    
    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_4xAA"
    
    # Battery theshold
    LOW_BATTERY_THRESHOLD = 10
            
    
    def initialize(self, botengine):
        """
        Initialize this object
        
        The correct behavior is to create the object, then initialize() it every time you want to use it in a new bot execution environment
        """
        ThermostatDevice.initialize(self, botengine)
            
    
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Centralite Pearl Thermostat")
    