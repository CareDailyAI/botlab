'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class DisplayDevice(Device):
    """Display"""

    # Goals
    GOAL_DEFAULT = 0

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = DisplayDevice.GOAL_DEFAULT
        
    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Display")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "tv"

