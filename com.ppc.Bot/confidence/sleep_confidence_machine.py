"""
Created on August 15, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Edward Liu
"""

import utilities.utilities as utilities
from confidence.confidence_state import (
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    CONFIDENCE_OFFLINE,
)
from devices.motion.motion import MotionDevice
from devices.radar.radar import RadarDevice


class SleepConfidenceStateMachine:
    def __init__(self):
        """
        Instantiate this object
        """
        # Confidence State
        self.state = None

        # Reason for the confidence state
        self.reason = None

    def update_confidence_state(self, botengine, location_object):
        """
        Update the confidence state based on the devices we installed.
        param: botengine
        param: location_object
        """
        confidence_normal_points = 0
        confidence_timeout_exceeded = True  # No Motion in last 12 hours
        confidence_in_bedroom_points = 0
        confidence_out_bedroom_points = 0

        for device_id in location_object.devices:
            device = location_object.devices[device_id]
            if not device.is_connected:
                continue

            if isinstance(device, MotionDevice):
                if not device.is_goal_id(MotionDevice.GOAL_MOTION_PROTECT_HOME):
                    continue

                confidence_normal_points += 1

                if MotionDevice.MEASUREMENT_NAME_STATUS in device.measurements:
                    if botengine.get_timestamp() - device.measurements[
                        MotionDevice.MEASUREMENT_NAME_STATUS
                    ][0][1] >= (utilities.ONE_HOUR_MS * 12):
                        confidence_timeout_exceeded = True
                    else:
                        confidence_timeout_exceeded = False
                else:
                    confidence_timeout_exceeded = True

                if device.is_in_bedroom(botengine):
                    confidence_in_bedroom_points += 1

                else:
                    confidence_out_bedroom_points += 1

            elif isinstance(device, RadarDevice):
                confidence_normal_points += 1

                if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in device.measurements:
                    if botengine.get_timestamp() - device.measurements[
                        RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET
                    ][0][1] >= (utilities.ONE_HOUR_MS * 12):
                        confidence_timeout_exceeded = True
                    else:
                        confidence_timeout_exceeded = False
                else:
                    confidence_timeout_exceeded = True

                if device.is_in_bedroom(botengine):
                    confidence_in_bedroom_points += 1

                else:
                    confidence_out_bedroom_points += 1

        if confidence_normal_points == 0:
            state = CONFIDENCE_OFFLINE
            self.reason = _("We don't have enough devices for sleep service to work.")

        else:
            if confidence_in_bedroom_points > 0 and confidence_out_bedroom_points > 1:
                if confidence_timeout_exceeded:
                    state = CONFIDENCE_MEDIUM
                    self.reason = _(
                        "We have medium confidence on the sleep service due to lack of recent measurements."
                    )
                else:
                    state = CONFIDENCE_HIGH
                    self.reason = _("We have high confidence on the sleep service.")

            elif confidence_in_bedroom_points > 0 and confidence_out_bedroom_points > 0:
                if confidence_timeout_exceeded:
                    state = CONFIDENCE_LOW
                    self.reason = _(
                        "We have low confidence on the sleep service due to lack of recent measurements."
                    )
                else:
                    state = CONFIDENCE_MEDIUM
                    self.reason = _(
                        "Add 1 more Motion or Radar device to improve the confidence."
                    )

            else:
                state = CONFIDENCE_LOW
                if confidence_in_bedroom_points > 0:
                    self.reason = _(
                        "Add more Motion or Radar devices installed outside bedroom to improve the confidence."
                    )

                else:
                    self.reason = _(
                        "Add more Motion or Radar devices installed inside bedroom to improve the confidence."
                    )

        if self.state is None or self.state != state:
            self.state = state

    def current_state(self):
        return self.state

    def current_confidence(self):
        return self.state, self.reason
