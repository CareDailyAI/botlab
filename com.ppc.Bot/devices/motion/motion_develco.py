"""
Created on December 23, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.motion.motion import MotionDevice


class DevelcoMotionDevice(MotionDevice):
    """
    Develco Motion Sensor
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9138]

    # Motion status
    MEASUREMENT_NAME_STATUS = "motionStatus"
    MEASUREMENT_NAME_ALARM = "alarmStatus"
    MEASUREMENT_DEG_C = "degC"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS,
        MEASUREMENT_NAME_ALARM,
        MEASUREMENT_DEG_C,
    ]

    def get_temperature_c(self, botengine=None):
        """
        Get the latest temperature in Celsius
        :param botengine: BotEngine environment
        :return: temperature in Celsius
        """
        if DevelcoMotionDevice.MEASUREMENT_DEG_C in self.measurements:
            return self.measurements[DevelcoMotionDevice.MEASUREMENT_DEG_C][0][0]

        return None

    def did_update_temperature(self, botengine=None):
        """
        :param botengine: BotEngine environment
        :return: True if the temperature just got updated on this execution
        """
        return DevelcoMotionDevice.MEASUREMENT_DEG_C in self.last_updated_params

    def set_application_light(self, botengine, on=True):
        """
        :param botengine: BotEngine environment
        :param on: True if turn on the application light
        :return:
        """
        value = "0"
        if on:
            value = "1"
        botengine.send_command(self.device_id, "ledAppEnable", value)

    def set_error_light(self, botengine, on=True):
        """
        :param botengine: BotEngine environment
        :param on: True if turn on the error light
        :return:
        """
        value = "0"
        if on:
            value = "1"
        botengine.send_command(self.device_id, "ledErrEnable", value)

    def is_detecting_motion(self, botengine=None):
        """
        Are we currently detecting motion
        :param botengine:
        :return:
        """
        alarm_status = False
        motion_status = False
        if DevelcoMotionDevice.MEASUREMENT_NAME_ALARM in self.measurements:
            if len(self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_ALARM]) > 0:
                if (
                    self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_ALARM][0][0]
                ):
                    alarm_status = True
        elif DevelcoMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if len(self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_STATUS]) > 0:
                if (
                    self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_STATUS][0][0]
                ):
                    motion_status = True

        if botengine is not None:
            botengine.get_logger().info(
                "DevelcoMotionDevice.is_detecting_motion() alarm_status={} motion_status={}".format(
                    alarm_status, motion_status
                )
            )

        return alarm_status or motion_status

    def did_start_detecting_motion(self, botengine=None):
        """
        Did we start detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        alarm_status_updated = False
        motion_status_updated = False
        if DevelcoMotionDevice.MEASUREMENT_NAME_ALARM in self.measurements:
            if DevelcoMotionDevice.MEASUREMENT_NAME_ALARM in self.last_updated_params:
                if (
                    self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_ALARM][0][0]
                ):
                    alarm_status_updated = True

        elif DevelcoMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if DevelcoMotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                if (
                    self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_STATUS][0][0]
                ):
                    motion_status_updated = True

        if botengine is not None:
            botengine.get_logger().debug(
                "DevelcoMotionDevice.did_start_detecting_motion() alarm_status_updated={} motion_status_updated={}".format(
                    alarm_status_updated, motion_status_updated
                )
            )
        return alarm_status_updated or motion_status_updated

    def did_stop_detecting_motion(self, botengine=None):
        """
        Did we stop detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned off in the last execution
        """

        alarm_status_updated = False
        motion_status_updated = False
        if DevelcoMotionDevice.MEASUREMENT_NAME_ALARM in self.measurements:
            if DevelcoMotionDevice.MEASUREMENT_NAME_ALARM in self.last_updated_params:
                if (
                    not self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_ALARM][0][0]
                ):
                    alarm_status_updated = True

        elif DevelcoMotionDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            if DevelcoMotionDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params:
                if (
                    not self.measurements[DevelcoMotionDevice.MEASUREMENT_NAME_STATUS][0][0]
                ):
                    motion_status_updated = True

        if botengine is not None:
            botengine.get_logger().info(
                "DevelcoMotionDevice.did_stop_detecting_motion() alarm_status_updated={} motion_status_updated={}".format(
                    alarm_status_updated, motion_status_updated
                )
            )

        return alarm_status_updated or motion_status_updated
