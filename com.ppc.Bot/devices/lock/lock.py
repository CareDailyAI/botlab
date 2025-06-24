"""
Created on February 8, 2018

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from enum import IntEnum

from devices.device import Device


# Possible lock states
class LockStatus(IntEnum):
    UNLOCKED = 0
    LOCKED = 1


# Possible lock alarm states
class LockStatusAlarm(IntEnum):
    OK = 0
    JAMMED = 1
    RESET_TO_FACTORY_DEFAULTS = 2
    MODULE_POWER_CYCLED = 3
    WRONG_CODE_ENTRY_LIMIT = 4
    FRONT_ESCUTCHEON_REMOVED = 5
    DOOR_FORCED_OPEN = 6


class LockDevice(Device):
    """Lock Device"""

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9010]

    # Measurement name for the lock status
    MEASUREMENT_NAME_LOCK_STATUS = "lockStatus"
    MEASUREMENT_NAME_LOCK_STATUS_ALARM = "lockStatusAlarm"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_LOCK_STATUS,
        MEASUREMENT_NAME_LOCK_STATUS_ALARM,
    ]

    # Goals
    GOAL_INTELLIGENT_AUTO_LOCK = 101
    GOAL_STATIC_AUTO_LOCK = 102  # Deprecated
    GOAL_UNLOCK_WITH_KEYPADS = 103

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

        # Default behavior
        self.goal_id = LockDevice.GOAL_INTELLIGENT_AUTO_LOCK

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Lock")

    def get_icon(self):
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
        unlocked = False
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.last_updated_params:
            unlocked = self.is_unlocked(botengine)
        botengine.get_logger().debug("lock.did_unlock {}".format(unlocked))
        return unlocked

    def did_lock(self, botengine=None):
        """
        Did the door just lock
        :param botengine:
        :return: True if the door just locked
        """
        locked = False
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.last_updated_params:
            locked = (
                self.is_fully_locked(botengine)
                and self.is_partially_locked(botengine) is None
            )
        botengine.get_logger().debug("lock.did_lock {}".format(locked))
        return locked

    def did_partially_lock(self, botengine=None):
        """
        Did the door just partially lock
        :param botengine:
        :return: True if the door just locked
        """
        partially_locked = False
        if self.MEASUREMENT_NAME_LOCK_STATUS_ALARM in self.last_updated_params:
            partially_locked = self.is_partially_locked(botengine)
        botengine.get_logger().debug(
            "lock.did_partially_lock {}".format(partially_locked)
        )
        return partially_locked

    def is_fully_locked(self, botengine=None):
        """
        Note that just because a door is not fully locked doesn't mean it's actually unlocked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is fully locked; None if the measurement doesn't exist
        """
        fully_locked = None
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            fully_locked = (
                self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0]
                == LockStatus.LOCKED
            )
        botengine.get_logger().debug("lock.is_fully_locked {}".format(fully_locked))
        return fully_locked

    def is_partially_locked(self, botengine=None):
        """
        :param botengine:
        :return: True if the door is partially but not fully locked; None if the measurement doesn't exist
        """
        partially_locked = None
        if self.MEASUREMENT_NAME_LOCK_STATUS_ALARM in self.measurements:
            partially_locked = (
                self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS_ALARM][0][0]
                == LockStatusAlarm.JAMMED
            )
            if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
                if (
                    self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS_ALARM][0][1]
                    < self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][1]
                ):
                    partially_locked = None
        botengine.get_logger().debug(
            "lock.is_partially_locked {}".format(partially_locked)
        )
        return partially_locked

    def is_unlocked(self, botengine=None):
        """
        Note that just because a door is not unlocked doesn't mean it is fully locked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is unlocked; None if the measurement doesn't exist
        """
        unlocked = None
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            unlocked = (
                self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0]
                == LockStatus.UNLOCKED
            )
        botengine.get_logger().debug("lock.is_unlocked {}".format(unlocked))
        return unlocked

    def lock(self, botengine):
        """
        Lock the door
        :param botengine: BotEngine environment
        """
        botengine.send_command(
            self.device_id, self.MEASUREMENT_NAME_LOCK_STATUS, LockStatus.LOCKED
        )

    def unlock(self, botengine):
        """
        Unlock the door
        :param botengine: BotEngine environment
        """
        botengine.send_command(
            self.device_id, self.MEASUREMENT_NAME_LOCK_STATUS, LockStatus.UNLOCKED
        )
