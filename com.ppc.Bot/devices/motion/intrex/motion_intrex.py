'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.motion.motion import MotionDevice


class IntrexMotionDevice(MotionDevice):
    """
    Develco Motion Sensor
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2035]

    # Motion status
    MEASUREMENT_NAME_STATUS = 'occupancy'


    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]

    # Number of seconds that elapses before the motion detector sends a second packet saying motion is no longer detected
    MOTION_AUTO_OFF_SECONDS = 10

    def __init__(self, botengine, location_object, device_id, device_type, device_description,
                 precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        MotionDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                             precache_measurements=precache_measurements)


    # ===========================================================================
    # Measurements
    # ===========================================================================
    def is_detecting_motion(self, botengine=None):
        """
        Are we currently detecting motion
        :param botengine:
        :return:
        """
        if IntrexMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if len(self.measurements[IntrexMotionDevice.MEASUREMENT_NAME_STATUS]) > 0:
                return self.measurements[IntrexMotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def did_start_detecting_motion(self, botengine=None):
        """
        Did we start detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        if IntrexMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if IntrexMotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return self.measurements[IntrexMotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def did_stop_detecting_motion(self, botengine=None):
        """
        Did we stop detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned off in the last execution
        """
        
        if IntrexMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if IntrexMotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                return not self.measurements[IntrexMotionDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def force_stop_detecting_motion(self, botengine=None):
        """
        Force stop detecting motion
        :param botengine: BotEngine environment
        :return:
        """
        self.last_updated_params.append(IntrexMotionDevice.MEASUREMENT_NAME_STATUS)
        self.measurements[IntrexMotionDevice.MEASUREMENT_NAME_STATUS][0] = (False, botengine.get_timestamp())

