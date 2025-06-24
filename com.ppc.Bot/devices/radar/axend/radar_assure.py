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

class RadarAssureDevice(RadarDevice):
    """
    AeroSense Assure Device
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2020]

    MEASUREMENT_NAME_ROOM_TYPE = "roomType"
    MEASUREMENT_NAME_TIME_SITTING = "timeSit"
    MEASUREMENT_NAME_TIME_ACTIVE = "timeActive"
    MEASUREMENT_NAME_TIME_OUT_OF_ROOM = "timeOut"
    MEASUREMENT_NAME_TIME_IN_BATHROOM = "timeBathroom"
    MEASUREMENT_NAME_TIME_IN_BEDROOM = "timeBed"

    MEASUREMENT_PARAMETERS_LIST = [
        RadarDevice.MEASUREMENT_NAME_FALL_STATUS,
        MEASUREMENT_NAME_TIME_SITTING,
        MEASUREMENT_NAME_TIME_ACTIVE,
        MEASUREMENT_NAME_TIME_OUT_OF_ROOM,
        MEASUREMENT_NAME_TIME_IN_BATHROOM,
        MEASUREMENT_NAME_TIME_IN_BEDROOM,
    ]

    # Room Types
    ROOM_TYPE_LIVING_ROOM = 1
    ROOM_TYPE_BEDROOM = 2
    ROOM_TYPE_BATHROOM = 3
    ROOM_TYPE_KITCHEN = 4
    ROOM_TYPE_OFFICE = 5
    ROOM_TYPE_OTHERS = 6

    # Fall Status
    FALL_STATUS_DETECTED    = 1
    FALL_STATUS_FINISHED    = 0

    # TBD others

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
        return _("AeroSense Assure")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "radar"

    def get_icon_font(self):
        """
        Get the icon font package from which to render an icon
        As most of the device icons come from the "People Power Regular" icon font, this is currently the default.
        You can override this method in a specific device class.
        :return: The name of the icon font package
        """
        import utilities.utilities as utilities
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    def is_detecting_fall(self, botengine):
        """
        True if this device is detecting fall
        :param botengine:
        :return:
        """
        return self.get_fall_status(botengine) == RadarAssureDevice.FALL_STATUS_DETECTED

    def did_change_room_type(self, botengine=None):
        """
        :param botengine:
        :return: True if the room type changed
        """
        return RadarAssureDevice.MEASUREMENT_NAME_ROOM_TYPE in self.last_updated_params
    
    def get_room_type(self, botengine=None):
        """
        :param botengine:
        :return: room type. None if it's not available.
        """
        if RadarAssureDevice.MEASUREMENT_NAME_ROOM_TYPE in self.measurements:
            return self.measurements[RadarAssureDevice.MEASUREMENT_NAME_ROOM_TYPE][0][0]

        return None
    
    def set_room_type(self, botengine, room_type):
        """
        :param botengine:
        :param room_type: Room Type 
        """
        botengine.send_command(
            self.device_id,
            RadarAssureDevice.MEASUREMENT_NAME_ROOM_TYPE,
            room_type,
        )