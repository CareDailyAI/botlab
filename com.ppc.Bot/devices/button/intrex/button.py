'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.button.button_mpers import MobileButtonDevice


class IntrexButtonDevice(MobileButtonDevice):
    """
    Intrex Community Wearable Device
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2031]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        MobileButtonDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                                   precache_measurements=precache_measurements)


    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Intrex Community Wearable")  # noqa: F821 # type: ignore