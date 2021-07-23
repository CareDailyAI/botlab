'''
Created on December 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.motion.motion import MotionDevice

class DevelcoMotionDevice(MotionDevice):
    """
    Develco Motion Sensor
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9138]


    # Motion status
    MEASUREMENT_NAME_STATUS = 'motionStatus'
    MEASUREMENT_DEG_C = 'degC'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS,
        MEASUREMENT_DEG_C
    ]

    def get_temperature_c(self, botengine=None):
        """
        Get the latest temperature in Celsius
        :param botengine: BotEngine environment
        :return: temperature in Celsius
        """
        if DevelcoMotionDevice.MEASUREMENT_DEG_C in self.measurements:
            return self.measurements[DevelcoMotionDevice.MEASUREMENT_DEG_C][0][0]

        return None

    def did_update_temperature(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if the temperature just got updated on this execution
        """
        return DevelcoMotionDevice.MEASUREMENT_DEG_C in self.last_updated_params
