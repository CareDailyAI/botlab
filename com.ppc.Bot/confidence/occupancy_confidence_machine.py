'''
Created on August 16, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
'''

from confidence.confidence_state import CONFIDENCE_OFFLINE
from confidence.confidence_state import CONFIDENCE_LOW
from confidence.confidence_state import CONFIDENCE_MEDIUM
from confidence.confidence_state import CONFIDENCE_HIGH

from devices.motion.motion import MotionDevice
from devices.entry.entry import EntryDevice
from devices.vayyar.vayyar import VayyarDevice
from devices.lock.lock import LockDevice

import utilities.utilities as utilities


class OccupancyConfidenceStateMachine:

    def __init__(self):
        """
        Instantiate this object
        """
        # Away confidence state
        self.away_confidence_state = None

        # Home confidence state
        self.home_confidence_state = None

        self.away_reason = None

        self.home_reason = None

    def update_away_confidence_state(self, botengine, location_object):
        """
        Update the confidence state based on the devices we installed.
        param: botengine
        param: location_object
        """
        confidence_motion_points = 0
        confidence_entry_points = 0

        for device_id in location_object.devices:
            device = location_object.devices[device_id]
            if not device.is_connected:
                continue

            if isinstance(device, MotionDevice):
                if device.is_goal_id(MotionDevice.GOAL_MOTION_PROTECT_HOME):
                    confidence_motion_points += 1

            elif isinstance(device, VayyarDevice):
                confidence_motion_points += 1

            elif isinstance(device, EntryDevice):
                if device.is_goal_id(EntryDevice.GOAL_PERIMETER_NORMAL):
                    confidence_entry_points += 1

            elif isinstance(device, LockDevice):
                confidence_entry_points += 1

        if confidence_motion_points == 0 and confidence_entry_points == 0:
            state = CONFIDENCE_OFFLINE
            self.away_reason = _("We don't have enough Motion or Vayyar devices for occupancy away service to work.")

        elif confidence_motion_points > 1 and confidence_entry_points > 0:
            state = CONFIDENCE_HIGH
            self.away_reason = _("We have high confidence on the occupancy away service.")

        elif confidence_motion_points > 0 and confidence_entry_points > 0:
            state = CONFIDENCE_MEDIUM
            self.away_reason = _("Add 1 more Motion or Vayyar device to improve the confidence.")

        elif confidence_motion_points > 1:
            state = CONFIDENCE_MEDIUM
            self.away_reason = _("Add 1 more entry device to improve the confidence.")

        else:
            state = CONFIDENCE_LOW
            if confidence_motion_points > 0:
                self.away_reason = _("Add 1 Entry device to improve the confidence.")

            else:
                self.away_reason = _("Add 1 Motion or Vayyar device to improve the confidence.")

        if self.away_confidence_state is None or self.away_confidence_state != state:
            self.away_confidence_state = state

    def update_home_confidence_state(self, botengine, location_object):
        """
        Update the confidence state based on the devices we installed.
        param: botengine
        param: location_object
        """
        confidence_motion_points = 0
        confidence_entry_points = 0

        for device_id in location_object.devices:
            device = location_object.devices[device_id]
            if not device.is_connected:
                continue

            if isinstance(device, MotionDevice):
                if not device.is_goal_id(MotionDevice.GOAL_MOTION_PROTECT_HOME):
                    continue
                confidence_motion_points += 1

            elif isinstance(device, VayyarDevice):
                confidence_motion_points += 1

            elif isinstance(device, EntryDevice):
                confidence_entry_points += 1

            elif isinstance(device, LockDevice):
                confidence_entry_points += 1

        if confidence_motion_points == 0 and confidence_entry_points == 0:
            state = CONFIDENCE_OFFLINE
            self.home_reason = _("We don't have Motion or Vayyar or Entry device for occupancy home service to work.")

        elif confidence_motion_points > 1 and confidence_entry_points > 0:
            state = CONFIDENCE_HIGH
            self.home_reason = _("We have high confidence on the occupancy home service.")

        elif confidence_motion_points > 0 and confidence_entry_points > 0:
            state = CONFIDENCE_MEDIUM
            self.home_reason = _("Add 1 Motion or Vayyar device to improve the confidence.")

        elif confidence_motion_points > 1:
            state = CONFIDENCE_MEDIUM
            self.home_reason = _("Add 1 Entry device to improve the confidence.")

        else:
            state = CONFIDENCE_LOW
            if confidence_motion_points > 0:
                self.home_reason = _("Add 1 Entry device to improve the confidence.")

            else:
                self.home_reason = _("Add 1 Motion or Vayyar device to improve the confidence.")

        if self.home_confidence_state is None or self.home_confidence_state != state:
            self.home_confidence_state = state

    def current_away_confidence(self):
        return self.away_confidence_state, self.away_reason

    def current_home_confidence(self):
        return self.home_confidence_state, self.home_reason
    
    def is_away_confidence_good(self):
        return self.away_confidence_state > CONFIDENCE_LOW

