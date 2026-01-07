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

class RadarNobiDevice(RadarDevice):
    """
    Nobi Lamp Device
    """
    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2003]

    # Parameters
    MEASUREMENT_NAME_TEMPERATURE = "degC"
    MEASUREMENT_NAME_HUMIDITY = "relativeHumidity"
    MEASUREMENT_NAME_VOC = "voc"

    # not published on server side
    MEASUREMENT_NAME_RSSI = "rssi"
    MEASUREMENT_NAME_CO2  = "CO2"
    MEASUREMENT_NAME_WEIGHT  = "weight"
    MEASUREMENT_NAME_SYSTOLIC_PRESSURE = "systolic_pressure"
    MEASUREMENT_NAME_DIASTOLIC_PRESSURE = "diastolic_pressure"
    MEASUREMENT_NAME_MEAN_ARTERIAL_PRESSURE = "mean_arterial_pressure"
    MEASUREMENT_NAME_HEART_RATE = "hr"
    MEASUREMENT_NAME_PRESSURE = "pressure"
    MEASUREMENT_NAME_WIFI_SIGNAL = "wifiSignal"
    MEASUREMENT_NAME_IAQ = "iaq"
    MEASUREMENT_NAME_SIAQ = "siaq"

    # Activity events
    MEASUREMENT_NAME_MOTION_STATUS = "motionStatus"
    MEASUREMENT_NAME_MOTION_OCCUPANCY = "occupancy"
    MEASUREMENT_NAME_MOTION_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_MOTION_SLEEP_STATUS = "sleepStatus"

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_TEMPERATURE,
        MEASUREMENT_NAME_HUMIDITY,
        MEASUREMENT_NAME_VOC,
        RadarDevice.MEASUREMENT_NAME_FALL_STATUS,
        MEASUREMENT_NAME_MOTION_STATUS,
        MEASUREMENT_NAME_MOTION_OCCUPANCY,
        MEASUREMENT_NAME_MOTION_BED_STATUS,
        MEASUREMENT_NAME_MOTION_SLEEP_STATUS,
    ]

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
        return _("Nobi")

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
        return self.get_fall_status(botengine) == RadarNobiDevice.FALL_STATUS_DETECTED

    def did_change_temperature(self, botengine=None):
        """
        :param botengine:
        :return: True if the temperature changed
        """
        return RadarNobiDevice.MEASUREMENT_NAME_TEMPERATURE in self.last_updated_params

    def get_temperature(self, botengine=None):
        """
        :param botengine:
        :return: temperature in celsius. None if it's not available.
        """
        if RadarNobiDevice.MEASUREMENT_NAME_TEMPERATURE in self.measurements:
            return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_TEMPERATURE][0][0]

        return None

    def did_change_relative_humidity(self, botengine=None):
        """
        :param botengine:
        :return: True if the relative humidity changed
        """
        return RadarNobiDevice.MEASUREMENT_NAME_HUMIDITY in self.last_updated_params

    def get_relative_humidity(self, botengine=None):
        """
        :param botengine:
        :return: relative humidity in %. None if it's not available.
        """
        if RadarNobiDevice.MEASUREMENT_NAME_HUMIDITY in self.measurements:
            return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_HUMIDITY][0][0]

        return None

    def did_change_voc(self, botengine=None):
        """
        :param botengine:
        :return: True if the voc changed
        """
        return RadarNobiDevice.MEASUREMENT_NAME_VOC in self.last_updated_params

    def get_voc(self, botengine=None):
        """
        :param botengine:
        :return: voc in ppm. None if it's not available.
        """
        if RadarNobiDevice.MEASUREMENT_NAME_VOC in self.measurements:
            return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_VOC][0][0]

        return None

    def did_change_motion_status(self, botengine=None):
        """
        Did we start detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        return RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS in self.last_updated_params

    def did_start_detecting_motion(self, botengine=None):
        """
        Did we start detecting motion in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        if RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS in self.measurements:
            if RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS in self.last_updated_params:
                return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS][0][0] == 1

        return False
    
    def is_detecting_motion(self, botengine=None):
        """
        Are we currently detecting motion
        :param botengine:
        :return:
        """
        if RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS in self.measurements:
            if len(self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS]) > 0:
                return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_STATUS][0][0] == 1
        return False

    def did_change_occupancy(self, botengine=None):
        """
        Did we start detecting occupancy in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        return RadarNobiDevice.MEASUREMENT_NAME_MOTION_OCCUPANCY in self.last_updated_params

    def is_occupied(self, botengine=None):
        """
        Are we currently detecting occupancy
        :param botengine:
        :return:
        """
        if RadarNobiDevice.MEASUREMENT_NAME_MOTION_OCCUPANCY in self.measurements:
            if len(self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_OCCUPANCY]) > 0:
                return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_OCCUPANCY][0][0] == 1
        return False

    def did_change_bed_status(self, botengine=None):
        """
        Did we start detecting bed status in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        return RadarNobiDevice.MEASUREMENT_NAME_MOTION_BED_STATUS in self.last_updated_params
    
    def is_in_bed(self, botengine=None):
        """
        Are we currently detecting bed status
        :param botengine:
        :return:
        """
        if RadarNobiDevice.MEASUREMENT_NAME_MOTION_BED_STATUS in self.measurements:
            if len(self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_BED_STATUS]) > 0:
                return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_BED_STATUS][0][0] == 1
        return False

    def did_change_sleep_status(self, botengine=None):
        """
        Did we start detecting sleep status in this execution
        :param botengine: BotEngine environment
        :return: True if the light turned on in the last execution
        """
        return RadarNobiDevice.MEASUREMENT_NAME_MOTION_SLEEP_STATUS in self.last_updated_params
    
    def is_sleeping(self, botengine=None):
        """
        Are we currently detecting sleep status
        :param botengine:
        :return:
        """
        if RadarNobiDevice.MEASUREMENT_NAME_MOTION_SLEEP_STATUS in self.measurements:
            if len(self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_SLEEP_STATUS]) > 0:
                return self.measurements[RadarNobiDevice.MEASUREMENT_NAME_MOTION_SLEEP_STATUS][0][0] == 1
        return False



