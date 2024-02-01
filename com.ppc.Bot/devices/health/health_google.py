'''
Created on October 12, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
'''

from devices.health.health import HealthDevice

class GoogleHealthDevice(HealthDevice):
    """
    Google Health Device
    """

    DEVICE_TYPES = [19]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Google Health")
