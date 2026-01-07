"""
Created on September 22, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.button.button_multi import MultiButtonDevice


class DevelcoMultiButtonDevice(MultiButtonDevice):
    """
    Develco Multi Button Device
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9106]

    # Measurement name for the button status
    MEASUREMENT_NAME_BUTTON_STATUS = "buttonStatus"
    MEASUREMENT_NAME_ALARM_STATUS = "alarmStatus"

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2450"

    # Type of battery
    BATTERY_TYPE = "CR2450"

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
        MultiButtonDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )



    def did_enter_panic(self, botengine=None):
        """
        Did the button enter panic mode (pressed for some time)
        :param botengine:
        :return:
        """
        return (
            self.MEASUREMENT_NAME_ALARM_STATUS in self.last_updated_params
            and self.measurements[self.MEASUREMENT_NAME_ALARM_STATUS][0][0]
        )

    def did_exit_panic(self, botengine=None):
        """
        Did the button exit panic mode (pressed for some time after having entered panic mode)
        :param botengine:
        :return:
        """
        return (
            self.MEASUREMENT_NAME_ALARM_STATUS in self.last_updated_params
            and not self.measurements[self.MEASUREMENT_NAME_ALARM_STATUS][0][0]
        )

    def is_in_panic(self, botengine=None):
        """
        Is the button currently in panic mode
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_ALARM_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_ALARM_STATUS][0][0]

        return False