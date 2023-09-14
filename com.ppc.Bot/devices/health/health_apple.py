'''
Created on September 10, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.health.health import HealthDevice

class AppleHealthDevice(HealthDevice):
    """
    Apple Health Device
    """

    DEVICE_TYPES = [29]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        HealthDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # User ID associated with this device.  Used for communications and device association. Left empty for anonymous users.
        self.user_id = self.device_id.split(":")[-1]

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Apple Health")
