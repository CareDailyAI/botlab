'''
Created on May 6, 2017
Deprecated on October 27, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class TouchDevice(Device):
    """
    Touch Sensor
    DEPRECATED. Replaced by vibration.linkhigh_vibration.py
    """
    
    # # List of Device Types this class is compatible with
    # DEVICE_TYPES = [10019]
    #
    # # Measurement name for the button status
    # MEASUREMENT_NAME_VIBRATION_STATUS = 'vibrationStatus'
    #
    # MEASUREMENT_PARAMETERS_LIST = [
    #     MEASUREMENT_NAME_VIBRATION_STATUS
    # ]
    #

    # Goals / Behaviors
    GOAL_ALERT_ON_EVERY_TOUCH = 20
    GOAL_ALERT_WHEN_AWAY = 21
    GOAL_TOILET = 22

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = TouchDevice.GOAL_ALERT_WHEN_AWAY

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Touch Sensor")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "touch"
