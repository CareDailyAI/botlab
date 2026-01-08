'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.button.button_multi import MultiButtonDevice


class IntrexButtonDevice(MultiButtonDevice):
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
        MultiButtonDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                                   precache_measurements=precache_measurements)

