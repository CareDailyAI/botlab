'''
Created on December 10, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Konstantin Manyankin
'''
from devices.lock.lock import LockDevice
from enum import IntEnum

class IntrexLockStatus(IntEnum):
    LOCKED      = 1
    UNLOCKED    = 2
    PROPPED     = 3
    BREACHED    = 4


class IntrexLockDevice(LockDevice):
    """
    Develco Motion Sensor
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2036]


    def __init__(self, botengine, location_object, device_id, device_type, device_description,
                 precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        LockDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                             precache_measurements=precache_measurements)

    def is_unlocked(self, botengine=None):
        """
        Note that just because a door is not unlocked doesn't mean it is fully locked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is unlocked; None if the measurement doesn't exist
        """
        unlocked= None
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            lock_status = self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0]
            unlocked = lock_status in (IntrexLockStatus.UNLOCKED, IntrexLockStatus.BREACHED, IntrexLockStatus.PROPPED)
        return unlocked

    def is_fully_locked(self, botengine=None):
        """
        Note that just because a door is not fully locked doesn't mean it's actually unlocked. It could be partially locked.
        Test conditions explicitly.
        :param botengine:
        :return: True if the door is fully locked; None if the measurement doesn't exist
        """
        fully_locked = None
        if self.MEASUREMENT_NAME_LOCK_STATUS in self.measurements:
            fully_locked = self.measurements[self.MEASUREMENT_NAME_LOCK_STATUS][0][0] == IntrexLockStatus.LOCKED
        return fully_locked


