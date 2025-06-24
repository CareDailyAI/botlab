"""
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.device import Device


class CarbonMonoxideDevice(Device):
    """Entry Sensor"""

    # Measurement Names
    MEASUREMENT_NAME_TEST = "alarmStatus.1"

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_aaa"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9011]

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

    def initialize(self, botengine):
        Device.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Carbon Monoxide Sensor")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "gas"

    # ===========================================================================
    # Attributes
    # ===========================================================================
    def is_testing(self, botengine=None):
        """
        :return: True if the carbon monoxide sensor is under test
        """
        if CarbonMonoxideDevice.MEASUREMENT_NAME_TEST in self.measurements:
            return self.measurements[CarbonMonoxideDevice.MEASUREMENT_NAME_TEST][0][0]

        return False

    def did_change_state(self, botengine=None):
        """
        :return: True if this entry sensor's state was updated just now
        """
        return CarbonMonoxideDevice.MEASUREMENT_NAME_TEST in self.last_updated_params
