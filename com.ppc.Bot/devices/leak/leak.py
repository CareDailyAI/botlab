'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

# Measurement Names
MEASUREMENT_NAME_STATUS = 'waterLeak'

class LeakDevice(Device):
    """Water Leak Sensor"""
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10017, 10076]
        
    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2450"

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def initialize(self, botengine):
        Device.initialize(self, botengine)
    
    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Leak Sensor")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "water"
    
    
    #===========================================================================
    # Helper methods
    #===========================================================================
    def is_leak_detected(self):
        """
        :return: True if a leak is currently detected
        """
        #=======================================================================
        # import json
        # print("is_leak_detected(" + str(self.device_id) + "): " + json.dumps(self.measurements[MEASUREMENT_NAME_STATUS], indent=2, sort_keys=True))
        #=======================================================================
        
        if MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[MEASUREMENT_NAME_STATUS][0][0]
        
        return False
    