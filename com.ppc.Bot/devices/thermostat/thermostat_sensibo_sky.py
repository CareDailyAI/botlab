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


class ThermostatSensiboSkyDevice(ThermostatDevice):
    """Sensibo Sky Thermostat Device"""

    MEASUREMENT_NAME_POWER_STATUS = 'powerStatus'

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [4220]
    
    # Minimum setpoint in Celsius
    MIN_SETPOINT_C = 7.0
    
    # Maximum setpoint in Celsius
    MAX_SETPOINT_C = 30.0


    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        ThermostatDevice.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # The boolean on/off state of this device that was saved
        self.saved_state = None

    def initialize(self, botengine):
        """
        Initialization
        :param botengine:
        :return:
        """
        ThermostatDevice.initialize(self, botengine)

        if not hasattr(self, 'saved_state'):
            self.saved_state = None

    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Sensibo Sky Thermostat")

    def is_on(self, botengine=None):
        """
        :param botengine:
        :return: True if the unit is on
        """
        if ThermostatSensiboSkyDevice.MEASUREMENT_NAME_POWER_STATUS in self.measurements:
            return self.measurements[ThermostatSensiboSkyDevice.MEASUREMENT_NAME_POWER_STATUS][0][0]

        return False

    def on(self, botengine):
        """
        Turn the A/C on
        :param botengine:
        :return:
        """
        botengine.get_logger().info("Sensibo: on()")
        botengine.send_command(self.device_id, ThermostatSensiboSkyDevice.MEASUREMENT_NAME_POWER_STATUS, "1")

    def off(self, botengine):
        """
        Turn the A/C off
        :param botengine:
        :return:
        """
        botengine.get_logger().info("Sensibo: off()")
        botengine.send_command(self.device_id, ThermostatSensiboSkyDevice.MEASUREMENT_NAME_POWER_STATUS, "0")

    def save(self, botengine=None):
        """
        Save the current state
        :param botengine:
        :return:
        """
        botengine.get_logger().info("Sensibo: save()")
        self.saved_state = self.is_on(botengine)

    def restore(self, botengine):
        """
        Restore any previously saved state
        :param botengine:
        :return:
        """
        if self.saved_state is not None:
            botengine.get_logger().info("Sensibo: restore()")
            botengine.send_command(self.device_id, ThermostatSensiboSkyDevice.MEASUREMENT_NAME_POWER_STATUS, str(self.saved_state))

        self.saved_state = None

    def is_saved(self, botengine=None):
        """
        :param botengine:
        :return: True if this device's state is already saved
        """
        if self.saved_state is None:
            return False

        return self.saved_state