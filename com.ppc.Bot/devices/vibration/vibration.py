'''
Created on October 27, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class VibrationDevice(Device):
    """
    Vibration Sensor
    """

    # Goals / Behaviors
    GOAL_VIBRATION_BED = 1
    GOAL_VIBRATION_CHAIR = 2
    GOAL_VIBRATION_WATERPIPE = 3
    GOAL_VIBRATION_WASHERDRYER = 4
    GOAL_VIBRATION_GLASSBREAK = 5
    GOAL_MEDICINE_CONTAINER = 6
    GOAL_REFIGERATOR = 7
    GOAL_ALERT_ON_EVERY_TOUCH = 20
    GOAL_ALERT_WHEN_AWAY = 21
    GOAL_VIBRATION_TOILET = 22

    # Sensitivity bounds
    SENSITIVITY_MINIMUM = 1
    SENSITIVITY_MAXIMUM = 15

    # Measurement Names
    # Vibration is continuous movement over time
    MEASUREMENT_NAME_VIBRATION_STATUS = 'vibrationStatus'

    # Movement is more instantaneous movement, like getting touched
    MEASUREMENT_NAME_MOVEMENT_STATUS = 'movementStatus'

    # Sensitivity
    MEASUREMENT_NAME_SENSITIVITY = 'vibrationSensitivity'

    # For machine learning algorithms
    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_VIBRATION_STATUS,
        MEASUREMENT_NAME_MOVEMENT_STATUS
    ]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_aaa"

    # Type of battery
    BATTERY_TYPE = "AAA"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = VibrationDevice.GOAL_ALERT_ON_EVERY_TOUCH

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
        return _("Vibration Sensor")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "touch"

    # ===========================================================================
    # Sensor-specific Methods
    # ===========================================================================
    def set_sensitivity_percent(self, botengine, percent):
        """
        Set the sensitivity based on percentage
        :param percent: 0-100%
        """
        raise NotImplementedError

    def get_sensitivity_percent(self, botengine):
        """
        Retrieve the current sensitivity percentage
        :param botengine:
        :return: Sensitivity percent
        """
        raise NotImplementedError

    def set_sensitivity_value(self, botengine, value):
        """
        Set the sensitivity value directly.
        Use the VibrationSensor.SENSITIVITY_MINIMUM and VibrationSensor.SENSITIVITY_MAXIMUM for reference
        :param value: Value to set for sensitivity
        """
        raise NotImplementedError

    def get_sensitivity_value(self, botengine):
        """
        Retrieve the current sensitivity value
        :param botengine:
        :return: Sensitivity value
        """
        raise NotImplementedError

    def did_start_touch(self, botengine):
        """
        Is the sensor touched, even momentarily?
        :param botengine:
        :return: True if the sensor is touched
        """
        raise NotImplementedError

    def did_stop_touch(self, botengine):
        """
        Did the sensor stop getting touched?
        :param botengine:
        :return: True if the sensor stopped getting touched
        """
        raise NotImplementedError

    def is_moving(self, botengine):
        """
        Is the sensor currently moving
        :param botengine: BotEngine
        :return: True if the sensor is currently moving
        """
        raise NotImplementedError

    def did_start_moving(self, botengine):
        """
        Did the sensor start continually moving, based on the current sensitivity value?
        :param botengine:
        :return: True if the sensor started moving
        """
        raise NotImplementedError

    def did_stop_moving(self, botengine):
        """
        Did the sensor stop continually moving?
        :param botengine:
        :return: True if the sensor stopped moving
        """
        raise NotImplementedError
