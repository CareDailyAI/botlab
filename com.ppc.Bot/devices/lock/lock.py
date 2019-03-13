'''
Created on February 8, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device


class LockDevice(Device):
    """Lock Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9010]

    # Measurement name for the lock status
    MEASUREMENT_NAME_LOCK_STATUS = 'lockStatus'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_LOCK_STATUS
    ]

    # Possible lock states
    STATUS_PARTIALLY_LOCKED = 0
    STATUS_LOCKED = 1
    STATUS_UNLOCKED = 2

    # Goals
    GOAL_INTELLIGENT_AUTO_LOCK = 101
    GOAL_STATIC_AUTO_LOCK = 102


    def get_device_type_name(self, language):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Lock")
    
    def get_image_name(self, botengine):
        """
        :return: the font icon name of this device type
        """
        return "lock"


    def did_unlock(self, botengine=None):
        """
        Did the door just unlock
        :param botengine:
        :return: True if the door just unlocked
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.last_updated_params:
            return self.is_unlocked(botengine)

        return False

    def did_lock(self, botengine=None):
        """
        Did the door just lock
        :param botengine:
        :return: True if the door just locked
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.last_updated_params:
            return self.is_fully_locked(botengine)

        return False

    def did_partially_lock(self, botengine=None):
        """
        Did the door just partially lock
        :param botengine:
        :return: True if the door just locked
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.last_updated_params:
            return self.is_partially_locked(botengine)

        return False


    def is_fully_locked(self, botengine=None):
        """
        Note that just because a door is not fully locked doesn't mean it's actually unlocked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is fully locked; None if the measurement doesn't exist
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0] == self.STATUS_LOCKED

        return None

    def is_partially_locked(self, botengine=None):
        """
        :param botengine:
        :return: True if the door is partially but not fully locked; None if the measurement doesn't exist
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0] == self.STATUS_PARTIALLY_LOCKED

        return None

    def is_unlocked(self, botengine=None):
        """
        Note that just because a door is not unlocked doesn't mean it is fully locked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is unlocked; None if the measurement doesn't exist
        """
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0] == self.STATUS_UNLOCKED

        return None

    def lock(self, botengine):
        """
        Lock the door
        :param botengine: BotEngine environment
        """
        botengine.send_command(self.device_id, self.MEASUREMENT_NAME_LOCK_STATUS, self.STATUS_LOCKED)

    def unlock(self, botengine):
        """
        Unlock the door
        :param botengine: BotEngine environment
        """
        botengine.send_command(self.device_id, self.MEASUREMENT_NAME_LOCK_STATUS, self.STATUS_UNLOCKED)