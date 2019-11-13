'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import utilities


class TemperatureHumidityDevice(Device):
    """
    Temperature & Humidity Sensor
    """
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [10034]

    # Goals
    GOAL_MONITOR_HOUSE = 30
    GOAL_WINE_TEMP = 31
    GOAL_REFRIGERATOR = 32
    GOAL_FREEZER = 33
    GOAL_DEPRECATED_FREEZER_DOOR_CRACKED_OPEN = 34
    GOAL_INSTRUMENT_TEMP = 35
    GOAL_COOL_AND_DRY_MEDICATION = 36
    GOAL_STOVETOP_MONITORING = 37
    GOAL_HVAC_MONITORING = 38
    GOAL_SKIP_TEMP = 39

    GOAL_MOLD_MILDEW = 40
    GOAL_HUMIDOR = 41
    GOAL_SKIP_HUM = 44

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr2032"

    # Degrees C measurement parameter
    MEASUREMENT_DEG_C = "degC"

    # Humidity measurement parameter
    MEASUREMENT_HUMIDITY = "relativeHumidity"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_DEG_C,
        MEASUREMENT_HUMIDITY
    ]
    
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Temperature and Humidity Sensor")
    
    def get_image_name(self):
        """
        :return: the font icon name of this device type
        """
        return "temp-humidity"


    def get_temperature_c(self, botengine=None):
        """
        Get the latest temperature in Celsius
        :param botengine:
        :return: temperature in Celsius
        """
        if TemperatureHumidityDevice.MEASUREMENT_DEG_C in self.measurements:
            return self.measurements[TemperatureHumidityDevice.MEASUREMENT_DEG_C][0][0]

        return None

    def get_relative_humidity(self, botengine=None):
        """
        Get the latest relative humidity in percent
        :param botengine:
        :return: relative humidity %
        """
        if TemperatureHumidityDevice.MEASUREMENT_HUMIDITY in self.measurements:
            return self.measurements[TemperatureHumidityDevice.MEASUREMENT_HUMIDITY][0][0]

        return None

    def get_heat_index(self, botengine=None):
        """
        Get the heat index in Celsius.
        :param botengine: BotEngine environment
        :return: Heat index in degrees Celsius
        """
        degrees_c = self.get_temperature_c(botengine)
        if degrees_c is None:
            return None

        humidity = self.get_relative_humidity(botengine)
        if humidity is None:
            return None

        return utilities.calculate_heat_index(degrees_c, humidity)

    def did_change_state(self, botengine=None):
        """
        :return: True if this sensor's state was updated just now
        """
        return (TemperatureHumidityDevice.MEASUREMENT_DEG_C in self.last_updated_params) or (TemperatureHumidityDevice.MEASUREMENT_HUMIDITY in self.last_updated_params)