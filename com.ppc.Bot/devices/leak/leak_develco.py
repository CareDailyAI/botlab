'''
Created on April 14, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.leak.leak import LeakDevice

class DevelcoLeakDevice(LeakDevice):
    """
    Develco Water Leak Detector
    """

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9117]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_li"

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'waterLeak'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        LeakDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        LeakDevice.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("Leak Sensor")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "water"

    # ===========================================================================
    # Helper methods
    # ===========================================================================
    def did_change_state(self, botengine=None):
        """
        :return: True if this entry sensor's state was updated just now
        """
        return LeakDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params

    def is_leak_detected(self):
        """
        :return: True if a leak is currently detected
        """
        if LeakDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[LeakDevice.MEASUREMENT_NAME_STATUS][0][0]

        return False

    def did_start_leak(self, botengine=None):
        """
        :param botengine:
        :return: True if a leak just started
        """
        return self.did_change_state(botengine) and self.is_leak_detected()

    def did_stop_leak(self, botengine=None):
        """
        :param botengine:
        :return: True if a leak just stopped
        """
        return self.did_change_state(botengine) and not self.is_leak_detected()