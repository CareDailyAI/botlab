'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class EntryDevice(Device):
    """Entry Sensor"""

    # Goals
    GOAL_PERIMETER_NORMAL = 0
    GOAL_PERIMETER_ALERT_ALWAYS = 1
    GOAL_DEPRECATED_MAKE_MY_OWN_RULES = 2
    GOAL_DEPRECATED_ALERT_OPEN_AND_CLOSE = 3
    GOAL_INSIDE_NORMAL = 4
    GOAL_INSIDE_ALERT_ALWAYS = 5
    GOAL_OUTSIDE_NORMAL = 6
    GOAL_OUTSIDE_ALERT_ALWAYS = 7

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'doorStatus'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10014, 10074]
    
    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)
        
    def initialize(self, botengine):
        Device.initialize(self, botengine)
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Entry Sensor")
    
    
    #===========================================================================
    # Attributes
    #===========================================================================
    def is_open(self, botengine=None):
        """
        :return: True if the door has reported in its last measurement that it is open
        """
        #=======================================================================
        # import json
        # print("is_open(" + str(self.device_id) + "): " + json.dumps(self.measurements[MEASUREMENT_NAME_STATUS], indent=2, sort_keys=True))
        #=======================================================================
        
        if EntryDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[EntryDevice.MEASUREMENT_NAME_STATUS][0][0]
        
        return False

    def did_change_state(self, botengine=None):
        """
        :return: True if this entry sensor's state was updated just now
        """
        return EntryDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params
    
    def get_image_name(self, botengine=None):
        """
        :return: the font icon name of this device type
        """
        return "entry"

    def did_open(self, botengine=None):
        """
        Did the door open right now?
        :param botengine:
        :return: True if the door opened right now
        """
        return self.did_change_state(botengine) and self.is_open(botengine)

    def did_close(self, botengine=None):
        """
        Did the door close right now?
        :param botengine:
        :return: True if the door closed right now
        """
        return self.did_change_state(botengine) and not self.is_open(botengine)

    
    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a standardized .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        return Device.get_csv(self, botengine, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms, params=[EntryDevice.MEASUREMENT_NAME_STATUS])

