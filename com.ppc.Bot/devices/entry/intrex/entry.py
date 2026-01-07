'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.entry.entry import EntryDevice

class IntrexEntryDevice(EntryDevice):
    """
    Intrex Entry Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2033, 2034, 2037]

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'doorStatus'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        EntryDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                                   precache_measurements=precache_measurements)
