'''
Created on November 26, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''
from devices.device import Device
from devices.radar.radar import RadarDevice
import signals.radar as radar
import utilities.utilities as utilities

class RadarWavveDevice(RadarDevice):
    """
    AeroSense Wavve Device
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2021]

    # Parameters
    MEASUREMENT_NAME_HEART_RATE = "hr"
    MEASUREMENT_NAME_BREATHING_RATE = "br"
    MEASUREMENT_NAME_ROOM_TYPE = "roomType"
    MEASUREMENT_NAME_SLEEP_AWAKE = "sleepAwake"
    MEASUREMENT_NAME_SLEEP_LIGHT = "sleepLight"
    MEASUREMENT_NAME_SLEEP_DEEP = "sleepDeep"
    MEASUREMENT_NAME_SLEEP_REM = "sleepRem"
    MEASUREMENT_NAME_SLEEP_AWAKE = "sleepAwake"
    MEASUREMENT_NAME_SLEEP_OUT_OF_BED = "sleepOut"
    MEASUREMENT_NAME_SLEEP_TOTAL = "sleepTotal"

    MEASUREMENT_PARAMETERS_LIST = [
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY,
        MEASUREMENT_NAME_HEART_RATE,
        MEASUREMENT_NAME_BREATHING_RATE,
        MEASUREMENT_NAME_SLEEP_AWAKE,
        MEASUREMENT_NAME_SLEEP_LIGHT,
        MEASUREMENT_NAME_SLEEP_DEEP,
        MEASUREMENT_NAME_SLEEP_REM,
    ]

    # Room Types
    ROOM_TYPE_BEDROOM = 2

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        RadarDevice.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default Behavior
        self.goal_id = RadarDevice.BEHAVIOR_TYPE_BEDROOM


    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        RadarDevice.new_version(self, botengine)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("AeroSense Wavve")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "bed"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        As most of the device icons come from the "People Power Regular" icon font, this is currently the default.
        You can override this method in a specific device class.
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def did_change_heart_rate(self, botengine=None):
        """
        :param botengine:
        :return: True if the heart rate changed
        """
        return RadarWavveDevice.MEASUREMENT_NAME_HEART_RATE in self.last_updated_params

    def get_heart_rate(self, botengine=None):
        """
        :param botengine:
        :return: heart rate in bpm. None if it's not available.
        """
        if RadarWavveDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            return self.measurements[RadarWavveDevice.MEASUREMENT_NAME_HEART_RATE][0][0]

        return None

    def get_average_heart_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if RadarWavveDevice.MEASUREMENT_NAME_HEART_RATE in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[RadarWavveDevice.MEASUREMENT_NAME_HEART_RATE]
                ]
            )
        return None

    def did_change_breathing_rate(self, botengine=None):
        """
        :param botengine:
        :return: True if the breathing rate changed
        """
        return RadarWavveDevice.MEASUREMENT_NAME_BREATHING_RATE in self.last_updated_params
    
    def get_breathing_rate(self, botengine=None):
        """
        :param botengine:
        :return: breathing rate in bpm. None if it's not available.
        """
        if RadarWavveDevice.MEASUREMENT_NAME_BREATHING_RATE in self.measurements:
            return self.measurements[RadarWavveDevice.MEASUREMENT_NAME_BREATHING_RATE][0][0]

        return None

    def get_average_breathing_rate(self, botengine):
        """
        Retrieve the most recent heart_rate value
        :param botengine:
        :return:
        """
        if RadarWavveDevice.MEASUREMENT_NAME_BREATHING_RATE in self.measurements:
            from statistics import mean

            return mean(
                [
                    x[0]
                    for x in self.measurements[RadarWavveDevice.MEASUREMENT_NAME_BREATHING_RATE]
                ]
            )
        return None
    
    def did_change_room_type(self, botengine=None):
        """
        :param botengine:
        :return: True if the room type changed
        """
        return RadarWavveDevice.MEASUREMENT_NAME_ROOM_TYPE in self.last_updated_params
    
    def get_room_type(self, botengine=None):
        """
        :param botengine:
        :return: room type. None if it's not available.
        """
        if RadarWavveDevice.MEASUREMENT_NAME_ROOM_TYPE in self.measurements:
            return self.measurements[RadarWavveDevice.MEASUREMENT_NAME_ROOM_TYPE][0][0]

        return None
    
    def set_room_type(self, botengine, room_type):
        """
        :param botengine:
        :param room_type: Room Type 
        """
        pass