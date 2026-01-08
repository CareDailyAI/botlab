'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.alarm.alarm import AlarmDevice


class IntrexPullCordDevice(AlarmDevice):
    """
    Intrex Pull Cord Alarm
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2032]

    # Measurement name for the pull status
    MEASUREMENT_NAME_PULL_STATUS = 'pullStatus'

    def is_alarm_activated(self, botengine):
        """
        Did the alarm get set on?
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_PULL_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_PULL_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_PULL_STATUS][0][0]

    def is_alarm_deactivated(self, botengine):
        """
        Is the alarm off?
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_PULL_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_PULL_STATUS in self.last_updated_params:
                return not self.measurements[self.MEASUREMENT_NAME_PULL_STATUS][0][0]

