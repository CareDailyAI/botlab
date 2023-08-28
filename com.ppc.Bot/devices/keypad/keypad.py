'''
Created on March 20, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import utilities.utilities as utilities

class KeypadDevice(Device):
    """
    Keypad Device
    """
    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_aa"

    # Type of battery
    BATTERY_TYPE = "AA"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

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

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Keypad")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "keypad-circle"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        As most of the device icons come from the "People Power Regular" icon font, this is currently the default.
        You can override this method in a specific device class.
        :return: The name of the icon font package
        """
        return utilities.ICON_FONT_PEOPLEPOWER_REGULAR

    # Keypad Methods
    def did_disarm(self, botengine):
        """
        Did the keypad authenticate someone into disarm mode
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def did_away(self, botengine):
        """
        Did the keypad authenticate someone into away mode
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def did_stay(self, botengine):
        """
        Did the keypad authenticate someone into stay mode
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def is_silent(self, botengine):
        """
        Did someone select the Silent arming button
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def is_duress(self, botengine):
        """
        Did the user enter a duress code
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def did_authenticate(self, botengine):
        """
        Did someone (location or user ID) authenticate on the keypad
        :param botengine:
        :return:
        """
        raise NotImplementedError

    def get_authenticated_user_id(self, botengine):
        """
        Get the authenticated user ID
        :param botengine:
        :return: User ID if a user authenticated, None if it was a location code/card
        """
        raise NotImplementedError

    def did_code_authenticate(self, botengine):
        """
        Was it a code that authenticated?
        :param botengine:
        :return: True if a code was typed in to authenticate
        """
        raise NotImplementedError

    def did_card_authenticate(self, botengine):
        """
        Was it a card that authenticated?
        :param botengine:
        :return: True if a card was typed in to authenticate
        """
        raise NotImplementedError

    def did_signal_event(self, botengine):
        """
        Did the keypad signal some kind of event, and what was it?

            0 = No event
            1 = Panic
            2 = Fire
            3 = Emergency
            4 = Proprietary

        :param botengine:
        :return: The event type
        """
        raise NotImplementedError

