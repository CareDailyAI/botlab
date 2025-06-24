"""
Created on January 17, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.smartplug.smartplug import SmartplugDevice


class SmartenitLargeLoadControllerDevice(SmartplugDevice):
    """
    Large load controller from Smartenit
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9017]

    # Large load controller goals
    GOAL_LLC_HOT_WATER_HEATER = 120
    GOAL_LLC_POOL_PUMP_TIMER = 121
    GOAL_LLC_ELECTRIC_VEHICLE = 122
    GOAL_LLC_DRYER = 123

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name - Smartenit Large Load Controller
        return _("Large Load Controller")
