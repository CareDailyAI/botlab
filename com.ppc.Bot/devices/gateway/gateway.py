'''
Created on June 28, 2016

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class GatewayDevice(Device):
    """Abstract gateway device"""
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def initialize(self, botengine):
        Device.initialize(self, botengine)

    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name
        return _("Gateway")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "gateway"
    