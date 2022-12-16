'''
Created on April 21, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.keypad.keypad import KeypadDevice
import utilities.utilities as utilities

# Grace period that your code will still work before needing to type it in again
CODE_GRACE_PERIOD_MS = utilities.ONE_SECOND_MS * 20

# Helper enums
VALUE = 0
TIMESTAMP = 1

class DevelcoKeypadDevice(KeypadDevice):
    """
    Keypad Device

    codeType parameter:
        0 - unknown,
        1 - manually entered on the keypad
        2 - scanned card
        3 - combined code+card
        4 - Key was created using the Keypad device itself, but unknown if the user used a numeric code, RFID card, or both.
        8 - registering code and/or card using the keypad
        9 - duress code (9999)
        +100 - location code (101, 102, 103)

    event parameter:
        1 - panic
        2 - fire
        3 - Emergency
        4 - proprietary

    armMode parameter:
        ArmAllZones
        ArmDay_HomeZonesOnly
        ArmNight_SleepZonesOnly
        Disarm
    """
    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_aa"

    # Type of battery
    BATTERY_TYPE = "AA"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9103]

    # Measurement Names
    MEASUREMENT_NAME_ARM_MODE = 'armMode'
    MEASUREMENT_NAME_CODE_TYPE = 'codeType'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_ARM_MODE,
        MEASUREMENT_NAME_CODE_TYPE
    ]

    # Code types
    CODE_TYPE_UNKNOWN = 0
    CODE_TYPE_KEYCODE = 1
    CODE_TYPE_KEYCARD = 2
    CODE_TYPE_COMBO = 3
    CODE_TYPE_COMBO_UNKNOWN = 4
    CODE_TYPE_REGISTERED = 8
    CODE_TYPE_DURESS = 9

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        KeypadDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        KeypadDevice.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Keypad")

    # Keypad Methods
    def did_disarm(self, botengine):
        """
        Did the keypad authenticate someone into disarm mode
        :param botengine:
        :return:
        """
        if self.did_authenticate(botengine):
            if self.MEASUREMENT_NAME_ARM_MODE in self.measurements:
                return self.measurements[self.MEASUREMENT_NAME_ARM_MODE][0][0] == "Disarm"
        return False

    def did_away(self, botengine):
        """
        Did the keypad authenticate someone into away mode
        :param botengine:
        :return:
        """
        if self.did_authenticate(botengine):
            if self.MEASUREMENT_NAME_ARM_MODE in self.measurements:
                return self.measurements[self.MEASUREMENT_NAME_ARM_MODE][0][0] == "ArmAllZones"
        return False

    def did_stay(self, botengine):
        """
        Did the keypad authenticate someone into stay mode
        :param botengine:
        :return:
        """
        if self.did_authenticate(botengine):
            if self.MEASUREMENT_NAME_ARM_MODE in self.measurements:
                return self.measurements[self.MEASUREMENT_NAME_ARM_MODE][0][0] == "ArmDay_HomeZonesOnly"
        return False

    def recent_mode_change_attempts(self, botengine, minutes=5):
        """
        Number of attempts at changing the mode over the past few minutes
        :param botengine:
        :param minutes: Minutes to look back in time for mode change attempts
        :return:
        """
        if botengine.get_timestamp() - self.born_on < utilities.ONE_HOUR_MS * 12:
            return 0

        total = 0
        if self.MEASUREMENT_NAME_ARM_MODE in self.measurements:
            botengine.get_logger().info("\tarmMode parameters = {}".format(self.measurements[self.MEASUREMENT_NAME_ARM_MODE]))
            for m in self.measurements[self.MEASUREMENT_NAME_ARM_MODE]:
                # measurement = (value, timestamp)
                if m[1] >= botengine.get_timestamp() - (utilities.ONE_MINUTE_MS * minutes):
                    # Out of measurements
                    total += 1

                else:
                    break

        return total

    def is_silent(self, botengine):
        """
        Did someone select the Silent arming button
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_ARM_MODE in self.measurements:
            if len(self.measurements[self.MEASUREMENT_NAME_ARM_MODE]) > 1:
                if self.measurements[self.MEASUREMENT_NAME_ARM_MODE][1][VALUE] == "ArmNight_SleepZonesOnly":
                    # Silent button was pressed last before the current button
                    if botengine.get_timestamp() - self.measurements[self.MEASUREMENT_NAME_ARM_MODE][1][TIMESTAMP] < CODE_GRACE_PERIOD_MS:
                        # And it's within the past few seconds
                        return True

        return False

    def is_duress(self, botengine):
        """
        Did the user enter a duress code
        :param botengine:
        :return:
        """
        for p in self.last_updated_params:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                return self.measurements[p][0][VALUE] % 100 == DevelcoKeypadDevice.CODE_TYPE_DURESS

    def get_authenticated_user_id(self, botengine):
        """
        Get the authenticated user ID
        :param botengine:
        :return: User ID if a user authenticated, None if it was a location code/card
        """
        for p in self.last_updated_params:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                if self.measurements[p][0][0]:
                    # Check if there's an index at the end of this parameter name
                    if "." in p:
                        u = p.split(".")
                        return int(u[1])

        return None

    def did_authenticate(self, botengine):
        """
        Did someone (location or user ID) authenticate on the keypad
        :param botengine:
        :return:
        """
        recent_param = None
        recent_ts = 0

        # Find the most recent authenticated codeType.# parameter
        for p in self.measurements:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                if self.measurements[p][0][VALUE] > 0 and self.measurements[p][0][VALUE] % 100 != DevelcoKeypadDevice.CODE_TYPE_REGISTERED:
                    # Authenticated
                    if self.measurements[p][0][TIMESTAMP] > recent_ts:
                        # Recent authentication
                        recent_ts = self.measurements[p][0][TIMESTAMP]
                        recent_param = p

        if botengine.get_timestamp() - recent_ts <= CODE_GRACE_PERIOD_MS:
            code_type = self.measurements[recent_param][0][VALUE]
            return code_type > 0 and code_type != 8

        return False

    def did_code_authenticate(self, botengine):
        """
        Was it a code that authenticated?
        :param botengine:
        :return: True if a code was typed in to authenticate
        """
        recent_param = None
        recent_ts = 0

        # Find the most recent authenticated codeType.# parameter
        for p in self.measurements:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                if self.measurements[p][0][VALUE] > 0 and self.measurements[p][0][VALUE] % 100 != DevelcoKeypadDevice.CODE_TYPE_REGISTERED:
                    # Authenticated
                    if self.measurements[p][0][TIMESTAMP] > recent_ts:
                        # Recent authentication
                        recent_ts = self.measurements[p][0][TIMESTAMP]
                        recent_param = p

        if botengine.get_timestamp() - recent_ts <= CODE_GRACE_PERIOD_MS:
            code_type = self.measurements[recent_param][0][VALUE] % 100
            return code_type == DevelcoKeypadDevice.CODE_TYPE_KEYCODE or code_type == DevelcoKeypadDevice.CODE_TYPE_COMBO

        return False

    def did_card_authenticate(self, botengine):
        """
        Was it a card that authenticated?
        :param botengine:
        :return: True if a card was typed in to authenticate
        """
        recent_param = None
        recent_ts = 0

        # Find the most recent authenticated codeType.# parameter
        for p in self.measurements:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                if self.measurements[p][0][VALUE] > 0:
                    # Authenticated
                    if self.measurements[p][0][TIMESTAMP] > recent_ts:
                        # Recent authentication
                        recent_ts = self.measurements[p][0][TIMESTAMP]
                        recent_param = p

        if botengine.get_timestamp() - recent_ts <= CODE_GRACE_PERIOD_MS:
            code_type = self.measurements[recent_param][0][VALUE] % 100
            return code_type == DevelcoKeypadDevice.CODE_TYPE_KEYCARD or code_type == DevelcoKeypadDevice.CODE_TYPE_COMBO

        return False

    def did_unknown_authenticate(self, botengine):
        """
        User authenticated but the authentication method was unknown
        :param botengine:
        :return: True if the user is authenticated but the method (code or card) is unknown
        """
        recent_param = None
        recent_ts = 0

        # Find the most recent authenticated codeType.# parameter
        for p in self.measurements:
            if self.MEASUREMENT_NAME_CODE_TYPE in p:
                if self.measurements[p][0][VALUE] > 0:
                    # Authenticated
                    if self.measurements[p][0][TIMESTAMP] > recent_ts:
                        # Recent authentication
                        recent_ts = self.measurements[p][0][TIMESTAMP]
                        recent_param = p

        if botengine.get_timestamp() - recent_ts <= CODE_GRACE_PERIOD_MS:
            code_type = self.measurements[recent_param][0][VALUE] % 100
            return code_type == DevelcoKeypadDevice.CODE_TYPE_COMBO_UNKNOWN

        return False

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
        if 'event' in self.last_updated_params:
            return self.measurements['event'][0][VALUE]
