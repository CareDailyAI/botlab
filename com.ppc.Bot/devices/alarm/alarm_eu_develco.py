'''
Created on February 17, 2022

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Parth Agrawal
'''

from devices.alarm.alarm import AlarmDevice


class DevelcoEuDevice(AlarmDevice):
    """
    Alarm Device
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9112]
    # Fire alarm bool
    MEASUREMENT_NAME_ALARM_STATUS = "smokeAlarm"
    # Temperature in Celsius
    MEASUREMENT_NAME_TEMPERATURE = "degC"
    # Battery Voltage
    MEASUREMENT_NAME_VOLTAGE = "batteryVoltage"
    # Signal Strength
    MEASUREMENT_NAME_RSSI = "rssi"


    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Alarm Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Alarm")

    def is_alarm_activated(self, botengine):
        """
        Did the alarm get set on?
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_ALARM_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_ALARM_STATUS in self.last_updated_params:
                return self.measurements[self.MEASUREMENT_NAME_ALARM_STATUS][0][0]

    def is_alarm_deactivated(self, botengine):
        """
        Is the alarm off?
        :param botengine:
        :return:
        """
        if self.MEASUREMENT_NAME_ALARM_STATUS in self.measurements:
            if self.MEASUREMENT_NAME_ALARM_STATUS in self.last_updated_params:
                return not self.measurements[self.MEASUREMENT_NAME_ALARM_STATUS][0][0]

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "alarm-ip"

    def is_smoke_detected(self, botengine):
        """
        :param botengine:
        :return: True if smoke is detected
        """
        return self.is_alarm_activated(botengine)