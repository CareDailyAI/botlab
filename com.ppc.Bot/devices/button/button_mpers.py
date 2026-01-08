"""
Created on September 9, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.button.button import ButtonDevice


class MobileButtonDevice(ButtonDevice):
    """
    Mobile Button Device
    
    Base class for mobile button devices that have cellular connectivity and other mobile-PERS specific features.
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

    # Measurement names for mobile-specific features
    MEASUREMENT_NAME_MOBILE_SIGNAL = 'mobileSignal'

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
        :param location_object:
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
        self.goal_id = MobileButtonDevice.GOAL_BUTTON_CALL_FOR_HELP_MEDICAL

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Mobile Button"
        """
        return _("Mobile PERS Button")

    def did_enter_panic(self, botengine=None):
        """
        Did the button enter panic mode (pressed for some time)
        :param botengine:
        :return:
        """
        return False

    def did_exit_panic(self, botengine=None):
        """
        Did the button exit panic mode (pressed for some time after having entered panic mode)
        :param botengine:
        :return:
        """
        return False

    def is_in_panic(self, botengine=None):
        """
        Is the button currently in panic mode
        :param botengine:
        :return:
        """
        return False

    def does_support_gps_wandering(self):
        """
        Does this device support GPS wandering?
        :return: True if the device supports GPS wandering
        """
        return True

    def did_mobile_signal_change(self, botengine=None):
        """
        Did the mobile signal change?
        :param botengine:
        :return: True if the mobile signal changed
        """
        if self.MEASUREMENT_NAME_MOBILE_SIGNAL in self.measurements:
            if self.MEASUREMENT_NAME_MOBILE_SIGNAL in self.last_updated_params:
                return True

        return False

    def get_mobile_signal(self, botengine=None):
        """
        Get the mobile signal
        :param botengine:
        :return: Mobile signal
        """
        if self.MEASUREMENT_NAME_MOBILE_SIGNAL in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_MOBILE_SIGNAL][0][0]

        return None

    def get_mobile_signal_timestamp(self, botengine=None):
        """
        Get the timestamp of the last mobile signal measurement received
        :param botengine:
        :return: Timestamp of the last mobile signal measurement in ms; None if it doesn't exist
        """
        if self.MEASUREMENT_NAME_MOBILE_SIGNAL in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_MOBILE_SIGNAL][0][1]

        return None
