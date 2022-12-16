'''
Created on January 28, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class PressurePadDevice(Device):
    """
    Pressure Pad Device - Bed Sensor
    """

    # Goals
    GOAL_PRESSUREPAD_BED = 0
    GOAL_PRESSUREPAD_CHAIR = 1
    GOAL_PRESSUREPAD_FLOORMAT = 2

    # Measurement Names
    MEASUREMENT_NAME_STATUS = 'pressureStatus'

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS
    ]

    # Low battery tag
    LOW_BATTERY_TAG = "lowbattery_cr123a"

    # Type of battery
    BATTERY_TYPE = "CR123A"
    
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9039]
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = PressurePadDevice.GOAL_PRESSUREPAD_BED

    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Pressure Pad"
        """
        return _("Pressure Pad")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "bed"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def is_goal_id(self, target_goal_id):
        """
        This is the proper way to check for whether or not this device matches the given target goal ID,
        because goal IDs can change by an order of 1000 for each different brand.
        :param botengine: BotEngine environment
        :return: True if the goal ID matches for this device
        """
        # Since pressure pads can appear as motion sensors that protect the home,
        # if we're ever asked if we're protecting the home as a motion sensor, the answer is yes.
        from devices.motion.motion import MotionDevice
        if target_goal_id == MotionDevice.GOAL_MOTION_PROTECT_HOME:
            return True

        return Device.is_goal_id(self, target_goal_id)

    def is_on_bed(self, botengine=None):
        """
        Is this pressure pad on the bed?
        :return:
        """
        return self.is_goal_id(PressurePadDevice.GOAL_PRESSUREPAD_BED)

    #===========================================================================
    # Attributes
    #===========================================================================
    def is_pressure_applied(self, botengine=None):
        """
        :return: True if pressure is applied
        """
        if PressurePadDevice.MEASUREMENT_NAME_STATUS in self.measurements:
            return self.measurements[PressurePadDevice.MEASUREMENT_NAME_STATUS][0][0]
        
        return False

    def did_change_state(self, botengine=None):
        """
        :return: True if this entry sensor's state was updated just now
        """
        return PressurePadDevice.MEASUREMENT_NAME_STATUS in self.last_updated_params

    def did_apply_pressure(self, botengine=None):
        """
        Did you get on the pressure pad?
        :param botengine:
        :return: True if the door opened right now
        """
        return self.did_change_state(botengine) and self.is_pressure_applied(botengine)

    def did_release_pressure(self, botengine=None):
        """
        Did you get off the pressure pad?
        :param botengine:
        :return: True if the door closed right now
        """
        return self.did_change_state(botengine) and not self.is_pressure_applied(botengine)

    #===========================================================================
    # CSV methods for machine learning algorithm integrations
    #===========================================================================
    def get_csv(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get a standardized .csv string of all the data
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: oldest timestamp in milliseconds
        :param newest_timestamp_ms: newest timestamp in milliseconds
        :return: .csv string, largely matching the .csv data you would receive from the "botengine --download_device [device_id]" command line interface. Or None if this device doesn't have data.
        """
        return Device.get_csv(self, botengine, oldest_timestamp_ms=oldest_timestamp_ms, newest_timestamp_ms=newest_timestamp_ms, params=[PressurePadDevice.MEASUREMENT_NAME_STATUS])

