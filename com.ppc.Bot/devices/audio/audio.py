'''
Created on January 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

DEPRECATED

@author: David Moss
'''

from devices.device import Device


class AudioDevice(Device):
    """
    Audio Device
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

    # Measurement names
    MEASUREMENT_NAME_MANUFACTURER = 'manufacturer'
    MEASUREMENT_NAME_MODEL = 'model'

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Audio")
    
    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "microphone"