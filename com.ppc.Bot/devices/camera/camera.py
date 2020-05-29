'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class CameraDevice(Device):
    """Camera Device"""
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doeesn't show up in end user documentation
        return _("Camera")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "camera-ip"
    