"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.light.light import LightDevice


class SmartDimmerDevice(LightDevice):
    """Smart Dimmer Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9019]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Smart Dimmer")
