'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class GatewayDevice(Device):
    """Abstract gateway device"""
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def initialize(self, botengine):
        Device.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name
        return _("Smart Home Center")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "gateway"

    # Gateway methods
    def did_switch_to_battery_power(self, botengine):
        """
        Did the gateway get unplugged from power and we're running on battery
        :param botengine:
        :return:
        """
        return False

    def did_switch_to_external_power(self, botengine):
        """
        Did the gateway get plugged back into power
        :param botengine:
        :return:
        """
        return False

    def is_on_battery(self, botengine):
        """
        Is the gateway plugged into battery power
        :param botengine:
        :return:
        """
        return False

    def did_connect_cellular(self, botengine):
        """
        Did the gateway's primary network interface switch to a cellular connection
        :param botengine:
        :return:
        """
        return False

    def did_connect_broadband(self, botengine):
        """
        Did the gateway's primary network interface switch to a broadband connection
        :param botengine:
        :return:
        """
        return False

    def is_broadband_connected(self, botengine):
        """
        Is the gateway's primary network interface a broadband connection
        :param botengine:
        :return:
        """
        return self.is_connected

    def is_cellular_connected(self, botengine):
        """
        Is the gateway's primary network interface a cellular connection
        :param botengine:
        :return:
        """
        return False

    def get_battery_level(self, botengine):
        """
        Get the current battery level in units of percentage (i.e. 0 - 100)
        :param botengine:
        :return:
        """
        return 100
