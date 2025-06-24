"""
Created on February 17, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Parth Agrawal
"""

from devices.device import Device


class AlarmDevice(Device):
    """
    Alarm Device
    """

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

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Alarm Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Alarm")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "alarm"

    def is_alarm_activated(self, botengine):
        """
        Did the alarm get set on?
        :param botengine:
        :return:
        """

        return False

    def is_alarm_deactivated(self, botengine):
        """
        Did the alarm get set on?
        :param botengine:
        :return:
        """

        return False
