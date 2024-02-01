'''
Created on July 22, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

DEPRECATED SEPTEMBER 22, 2020
REPLACED WITH button_panic_develco.py

@author: David Moss
'''

from devices.device import Device


class DevelcoButtonDevice(Device):
    """
    Develco Button Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [] # [9101] < Deprecated, see button_panic_develco.py >

    # Measurement name for the button status
    MEASUREMENT_NAME_BUTTON_STATUS = 'buttonStatus'

    # Goals
    GOAL_BUTTON_SIGNAL_PEOPLE_WHO_LIVE_HERE = 100
    GOAL_BUTTON_SIGNAL_FAMILY_FRIENDS = 105
    GOAL_BUTTON_CALL_FOR_HELP_MEDICAL = 111

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

        # Default behavior
        self.goal_id = DevelcoButtonDevice.GOAL_BUTTON_CALL_FOR_HELP_MEDICAL

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Button")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "push-button"

    def did_enter_panic(self, botengine=None):
        """
        Did the button enter panic mode (pressed and released)
        :param botengine:
        :return:
        """
        return self.MEASUREMENT_NAME_BUTTON_STATUS in self.last_updated_params and self.measurements[self.MEASUREMENT_NAME_BUTTON_STATUS][0][0]

    def did_exit_panic(self, botengine=None):
        """
        Did the button exit panic mode (held for >3 seconds)
        :param botengine:
        :return:
        """
        return self.MEASUREMENT_NAME_BUTTON_STATUS in self.last_updated_params and not self.measurements[self.MEASUREMENT_NAME_BUTTON_STATUS][0][0]

    def is_in_panic(self, botengine=None):
        """
        Is the button currently in panic mode
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_BUTTON_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_BUTTON_STATUS][0][0]

        return False
