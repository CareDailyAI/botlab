"""
Created on December 3, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.motion.motion import MotionDevice


class AxendMotionDevice(MotionDevice):
    """
    Axend Motion Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2138]

    # Motion status
    MEASUREMENT_NAME_STATUS = "motionStatus"

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        MotionDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )
