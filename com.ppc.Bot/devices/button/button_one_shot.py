"""
Created on December 3, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.button.button import ButtonDevice


class OneShotButtonDevice(ButtonDevice):
    """
    One Shot Button Device - Base Class
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery"

    # Type of battery
    BATTERY_TYPE = ""

    # Goals
    GOAL_BUTTON_SIGNAL_PEOPLE_WHO_LIVE_HERE = 100
    GOAL_BUTTON_SIGNAL_FAMILY_FRIENDS = 105
    GOAL_BUTTON_TOOK_MEDICINE = 109
    GOAL_BUTTON_ARM_DISARM = 110
    GOAL_BUTTON_CALL_FOR_HELP_MEDICAL = 111
    GOAL_BUTTON_CALL_FOR_HELP_SECURITY = 112
    GOAL_BUTTON_CALL_FOR_HELP_PANIC = 113
    GOAL_BUTTON_DOORBELL = 115
    GOAL_BUTTON_STAY_DISARM = 116
    GOAL_BUTTON_SKIP = 300

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
        ButtonDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

        # Default behavior
        self.goal_id = OneShotButtonDevice.GOAL_BUTTON_CALL_FOR_HELP_MEDICAL

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Assist Button")  # noqa: F821 # type: ignore