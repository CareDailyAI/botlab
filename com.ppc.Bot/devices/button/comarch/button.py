"""
Created on January 3rd, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

from devices.button.button_mpers import MobileButtonDevice
import utilities.utilities as utilities
from enum import Enum


class ButtonIndex(Enum):
    SOS = 1
    CALL = 2


class PhoneIndex(Enum):
    SOS = 0
    CONTACT_1 = 1
    CONTACT_2 = 2
    CONTACT_3 = 3


class ChargingStatus(Enum):
    NOT_CHARGING = 0
    CHARGING = 1


class PutOnStatus(Enum):
    OFF = 0
    ON = 1


class FallStatus(Enum):
    CANCELED = 0
    DETECTED = 1


class Immobility(Enum):
    CANCELED = 0
    DETECTED = 1


class CyclicPeriod(Enum):
    MINIMUM = 1
    MAXIMUM = 1440


class TwinPeriod(Enum):
    MINUTES_15 = 15
    MINUTES_60 = 60
    MINUTES_120 = 120
    MINUTES_240 = 240
    MINUTES_480 = 480
    MINUTES_720 = 720


class LocationPeriod(Enum):
    MINIMUM = 1
    MAXIMUM = 1440


class GPSSwitch(Enum):
    OFF = 0
    ON = 1


class GPSMode(Enum):
    CONTINUOUSLY = 0
    ON_DEMAND = 1


class FallSwitch(Enum):
    OFF = 0
    ON = 1

class FallLevel(Enum):
    LOW = 0
    HIGH = 1

class HRSwitch(Enum):
    OFF = 0
    ON = 1

class Volume(Enum):
    MINIMUM = 0
    MAXIMUM = 11

class WhitelistSwitch(Enum):
    OFF = 0
    ON = 1

class SequentialCalls(Enum):
    OFF = 0
    ON = 1

class EventType(Enum):
    DEVICE_ON = "DEVICE_ON"
    DEVICE_OFF = "DEVICE_OFF"

class ComarchButtonDevice(MobileButtonDevice):
    """
    Comarch WristBand Button Device
    """

    # DeviceBatteryIntelligence Overrides
    BATTERY_MEASUREMENT_PERIODICITY_MS = utilities.ONE_MINUTE_MS * 3
    LOW_BATTERY_THRESHOLD = 20

    # DeviceRTLSMicroservice Overrides
    MINIMUM_RTLS_READINGS = 1
    MAXIMUM_RTLS_READINGS = 1
    RTLS_THRESHOLD_METERS = 50
    RTLS_THRESHOLD_UPPER_METERS = 100

    # Parameters
    MEASUREMENT_NAME_BATTERY_LEVEL = "batteryLevel"
    MEASUREMENT_NAME_MOBILE_SIGNAL = "mobileSignal"
    MEASUREMENT_NAME_BUTTON_STATUS = "buttonStatus"
    MEASUREMENT_NAME_FIRMWARE = "firmware"
    MEASUREMENT_NAME_CHARGING = "charging"
    MEASUREMENT_NAME_PUT_ON = "putOn"
    MEASUREMENT_NAME_FALL_STATUS = "fallStatus"
    MEASUREMENT_NAME_EVENT_TYPE = "eventType"
    MEASUREMENT_NAME_HR = "hr"
    MEASUREMENT_NAME_STEPS = "steps"
    MEASUREMENT_NAME_LONGITUDE = "longitude"
    MEASUREMENT_NAME_LATIDUDE = "latitude"
    MEASUREMENT_NAME_CYCLIC_PERIOD = "cmr.cyclicPeriod"
    MEASUREMENT_NAME_TWIN_PERIOD = "cmr.twinPeriod"
    MEASUREMENT_NAME_GPS_MODE = "cmr.gpsMode"
    MEASUREMENT_NAME_GPS_SWITCH = "cmr.gpsSwitch"
    MEASUREMENT_NAME_FALL_SWITCH = "cmr.fallSwitch"
    MEASUREMENT_NAME_FALL_LEVEL = "cmr.fallLevel"
    MEASUREMENT_NAME_HR_SWITCH = "cmr.hrSwitch"
    MEASUREMENT_NAME_LOCATION_PERIOD = "cmr.locationPeriod"
    MEASUREMENT_NAME_PHONE = "cmr.phone"
    MEASUREMENT_NAME_TIMEZONE = "cmr.timezone"
    MEASUREMENT_NAME_VOLUME = "cmr.volume"
    MEASUREMENT_NAME_IMMOBILITY = "immobility"
    MEASUREMENT_NAME_TIMEZONE_ID = "timeZoneId"
    MEASUREMENT_NAME_WHITELIST = "cmr.whitelist"
    MEASUREMENT_NAME_WHITELIST_SWITCH = "cmr.whitelistSwitch"
    MEASUREMENT_NAME_SEQUENTIAL_CALLS = "cmr.sequentialCalls"

    # Measurement parameters list for machine learning data extraction
    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_BUTTON_STATUS,
        MEASUREMENT_NAME_FALL_STATUS,
        MEASUREMENT_NAME_HR,
        MEASUREMENT_NAME_STEPS,
    ]

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2006]

    def __init__(
        self,
        botengine,
        location_object,
        device_id,
        device_type,
        device_description,
        precache_measurements=True,
    ):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        MobileButtonDevice.__init__(
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
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Comarch Wearable")

    # MutliButtonDevice Overrides
    def is_currently_pressed(self, botengine, index=None):
        """
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: True if the button is currently being pressed (from the perspective of the server)
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.SOS.value}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.CALL.value}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        # botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
        #     f"|is_currently_pressed() param_names={param_names} measurements={self.measurements}"
        # )
        params = [
            self.measurements[param_name][0][0]
            for param_name in param_names
            if param_name in self.measurements
        ]
        return any(params)

    def is_single_button_pressed(self, botengine, index=None):
        """
        Find out if a single button is pressed on this device
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: True if the button is currently pressed
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.SOS.value}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.CALL.value}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        for param_name in param_names:
            if (
                param_name in self.last_updated_params
                and self.measurements[param_name][0][0]
            ):
                return True
        return False

    def is_single_button_released(self, botengine, index=None):
        """
        Find out if a single button is pressed on this device
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: True if the button is currently pressed
        """
        return False

    def get_timestamp(self, botengine=None, index=None):
        """
        Get the timestamp of the last buttonStatus measurement received
        :param botengine:
        :return: Timestamp of the last buttonStatus measurement in ms; None if it doesn't exist
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.SOS.value}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{ButtonIndex.CALL.value}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        # Sort the param names by timestamp
        params = [
            self.measurements[param_name][0]
            for param_name in param_names
            if param_name in self.measurements
        ]
        params.sort(key=lambda x: x[1], reverse=True)
        return params[0][1] if params else None

    def does_support_gps_wandering(self):
        """
        Does this device support GPS wandering?
        :return: True if the device supports GPS wandering
        """
        gps_switch = self.get_gps_switch()
        return gps_switch is not None and gps_switch == GPSSwitch.ON.value

    # ComarchButtonDevice Attributes

    def did_mobile_signal_change(self, botengine=None):
        """
        Did the mobile signal change?
        :param botengine:
        :return: True if the mobile signal changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_MOBILE_SIGNAL in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_MOBILE_SIGNAL
                in self.last_updated_params
            ):
                return True

        return False

    def get_mobile_signal(self, botengine=None):
        """
        Get the mobile signal
        :param botengine:
        :return: Mobile signal
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_MOBILE_SIGNAL in self.measurements:
            return self.measurements[
                ComarchButtonDevice.MEASUREMENT_NAME_MOBILE_SIGNAL
            ][0][0]

        return None

    def did_charging_change(self, botengine=None):
        """
        Did the charging status change?
        :param botengine:
        :return: True if the charging status changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_CHARGING in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_CHARGING
                in self.last_updated_params
            ):
                return True

        return False

    def is_charging(self, botengine=None):
        """
        Is the device currently charging?
        :param botengine:
        :return: True if the device is currently charging
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_CHARGING in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_CHARGING][0][
                0
            ]

        return False

    def did_put_on_change(self, botengine=None):
        """
        Did the putOn status change?
        :param botengine:
        :return: True if the putOn status changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_PUT_ON in self.measurements:
            if ComarchButtonDevice.MEASUREMENT_NAME_PUT_ON in self.last_updated_params:
                return True

        return False

    def is_put_on(self, botengine=None):
        """
        Is the device currently being worn?
        :param botengine:
        :return: True if the device is currently being worn
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_PUT_ON in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_PUT_ON][0][0]

        return False

    def did_fall_status_change(self, botengine=None):
        """
        Did the fall status change?
        :param botengine:
        :return: True if the fall status changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_FALL_STATUS
                in self.last_updated_params
            ):
                return True

        return False

    def get_fall_status(self, botengine=None):
        """
        Get the fall status
        :param botengine:
        :return: Fall status
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_FALL_STATUS][
                0
            ][0]

        return None

    def did_event_type_change(self, botengine=None):
        """
        Did the event type change?
        :param botengine:
        :return: True if the event type changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_EVENT_TYPE
                in self.last_updated_params
            ):
                return True

        return False

    def get_event_type(self, botengine=None):
        """
        Get the event type
        :param botengine:
        :return: Event type
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_EVENT_TYPE in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_EVENT_TYPE][
                0
            ][0]

        return None

    def did_hr_change(self, botengine=None):
        """
        Did the heart rate change?
        :param botengine:
        :return: True if the heart rate changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_HR in self.measurements:
            if ComarchButtonDevice.MEASUREMENT_NAME_HR in self.last_updated_params:
                return True

        return False

    def get_hr(self, botengine=None):
        """
        Get the heart rate
        :param botengine:
        :return: Heart rate
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_HR in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_HR][0][0]

        return None

    def did_steps_change(self, botengine=None):
        """
        Did the steps change?
        :param botengine:
        :return: True if the steps changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_STEPS in self.measurements:
            if ComarchButtonDevice.MEASUREMENT_NAME_STEPS in self.last_updated_params:
                return True

        return False

    def get_steps(self, botengine=None):
        """
        Get the steps
        :param botengine:
        :return: Steps
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_STEPS in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_STEPS][0][0]

        return None

    def did_longitude_change(self, botengine=None):
        """
        Did the longitude change?
        :param botengine:
        :return: True if the longitude changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LONGITUDE in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_LONGITUDE
                in self.last_updated_params
            ):
                return True

        return False

    def get_longitude(self, botengine=None):
        """
        Get the longitude
        :param botengine:
        :return: Longitude
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LONGITUDE in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_LONGITUDE][0][
                0
            ]

        return None

    def did_latitude_change(self, botengine=None):
        """
        Did the latitude change?
        :param botengine:
        :return: True if the latitude changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LATIDUDE in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_LATIDUDE
                in self.last_updated_params
            ):
                return True

        return False

    def get_latitude(self, botengine=None):
        """
        Get the latitude
        :param botengine:
        :return: Latitude
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LATIDUDE in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_LATIDUDE][0][
                0
            ]

        return None

    def did_cyclic_period_change(self, botengine=None):
        """
        Did the cyclic period change?
        :param botengine:
        :return: True if the cyclic period changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_CYCLIC_PERIOD in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_CYCLIC_PERIOD
                in self.last_updated_params
            ):
                return True

        return False

    def get_cyclic_period(self, botengine=None):
        """
        Get the cyclic period
        :param botengine:
        :return: Cyclic period
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_CYCLIC_PERIOD in self.measurements:
            return self.measurements[
                ComarchButtonDevice.MEASUREMENT_NAME_CYCLIC_PERIOD
            ][0][0]

        return None

    def set_cyclic_period(self, botengine=None, cyclic_period=None):
        """
        Set the cyclic period
        :param botengine:
        :param cyclic_period: Cyclic period
        """
        if cyclic_period is None:
            raise ValueError("Cyclic period must be set")
        if cyclic_period < CyclicPeriod.MINIMUM.value:
            raise ValueError(
                f"Cyclic period must be at least {CyclicPeriod.MINIMUM.value}"
            )
        if cyclic_period > CyclicPeriod.MAXIMUM.value:
            raise ValueError(
                f"Cyclic period must be at most {CyclicPeriod.MAXIMUM.value}"
            )
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_CYCLIC_PERIOD,
                "value": int(cyclic_period),
            },
        )

    def did_twin_period_change(self, botengine=None):
        """
        Did the twin period change?
        :param botengine:
        :return: True if the twin period changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TWIN_PERIOD in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_TWIN_PERIOD
                in self.last_updated_params
            ):
                return True

        return False

    def get_twin_period(self, botengine=None):
        """
        Get the twin period
        :param botengine:
        :return: Twin period
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TWIN_PERIOD in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_TWIN_PERIOD][
                0
            ][0]

        return None

    def set_twin_period(self, botengine=None, twin_period=None):
        """
        Set the twin period
        :param botengine:
        :param twin_period: Twin period
        """
        if twin_period is None:
            raise ValueError("Twin period must be set")
        if twin_period not in [
            TwinPeriod.MINUTES_15.value,
            TwinPeriod.MINUTES_60.value,
            TwinPeriod.MINUTES_120.value,
            TwinPeriod.MINUTES_240.value,
            TwinPeriod.MINUTES_480.value,
            TwinPeriod.MINUTES_720.value,
        ]:
            raise ValueError(
                f"Twin period must be one of {TwinPeriod.MINUTES_15.value}, {TwinPeriod.MINUTES_60.value}, {TwinPeriod.MINUTES_120.value}, {TwinPeriod.MINUTES_240.value}, {TwinPeriod.MINUTES_480.value}, {TwinPeriod.MINUTES_720.value}"
            )
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_TWIN_PERIOD,
                "value": int(twin_period),
            },
        )

    def did_gps_mode_change(self, botengine=None):
        """
        Did the gps mode change?
        :param botengine:
        :return: True if the gps mode changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_GPS_MODE in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_GPS_MODE
                in self.last_updated_params
            ):
                return True

        return False

    def get_gps_mode(self, botengine=None):
        """
        Get the gps mode
        :param botengine:
        :return: Gps mode
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_GPS_MODE in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_GPS_MODE][0][
                0
            ]

        return None
    
    def set_gps_mode(self, botengine=None, gps_mode=None):
        """
        Set the gps mode
        :param botengine:
        """
        if gps_mode is None:
            raise ValueError("GPS mode must be set")
        if gps_mode not in [GPSMode.CONTINUOUSLY.value, GPSMode.ON_DEMAND.value]:
            raise ValueError(f"GPS mode must be one of {GPSMode.CONTINUOUSLY.value} or {GPSMode.ON_DEMAND.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_GPS_MODE,
                "value": int(gps_mode),
            },
        )

    def did_gps_switch_change(self, botengine=None):
        """
        Did the gps switch change?
        :param botengine:
        :return: True if the gps switch changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_GPS_SWITCH in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_GPS_SWITCH
                in self.last_updated_params
            ):
                return True

        return False

    def get_gps_switch(self, botengine=None):
        """
        Get the gps switch
        :param botengine:
        :return: Gps switch
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_GPS_SWITCH in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_GPS_SWITCH][
                0
            ][0]

        return None

    def set_gps_switch(self, botengine=None, gps_switch=None):
        """
        Set the gps switch
        :param botengine:
        """
        if gps_switch is None:
            raise ValueError("GPS switch must be set")
        if gps_switch not in [GPSSwitch.OFF.value, GPSSwitch.ON.value]:
            raise ValueError(f"GPS switch must be one of {GPSSwitch.OFF.value} or {GPSSwitch.ON.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_GPS_SWITCH,
                "value": int(gps_switch),
            },
        )

    def did_fall_switch_change(self, botengine=None):
        """
        Did the fall switch change?
        :param botengine:
        :return: True if the fall switch changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_SWITCH in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_FALL_SWITCH
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_fall_switch(self, botengine=None):
        """
        Get the fall switch
        :param botengine:
        :return: Fall switch
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_SWITCH in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_FALL_SWITCH][0][0]

        return None
    
    def set_fall_switch(self, botengine=None, fall_switch=None):
        """
        Set the fall switch
        :param botengine:
        """
        if fall_switch is None:
            raise ValueError("Fall switch must be set")
        if fall_switch not in [FallSwitch.OFF.value, FallSwitch.ON.value]:
            raise ValueError(f"Fall switch must be one of {FallSwitch.OFF.value} or {FallSwitch.ON.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_FALL_SWITCH,
                "value": int(fall_switch),
            },
        )

    def did_fall_level(self, botengine=None):
        """
        Did the fall level change?
        :param botengine:
        :return: True if the fall level changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_LEVEL in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_FALL_LEVEL
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_fall_level(self, botengine=None):
        """
        Get the fall level
        :param botengine:
        :return: Fall level
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_FALL_LEVEL in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_FALL_LEVEL][0][0]

        return None
    
    def set_fall_level(self, botengine=None, fall_level=None):
        """
        Set the fall level
        :param botengine:
        """
        if fall_level is None:
            raise ValueError("Fall level must be set")
        if fall_level not in [FallLevel.LOW.value, FallLevel.HIGH.value]:
            raise ValueError(f"Fall level must be one of {FallLevel.LOW.value} or {FallLevel.HIGH.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_FALL_LEVEL,
                "value": int(fall_level),
            },
        )

    def did_hr_switch_change(self, botengine=None):
        """
        Did the hr switch change?
        :param botengine:
        :return: True if the hr switch changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_HR_SWITCH in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_HR_SWITCH
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_hr_switch(self, botengine=None):
        """
        Get the hr switch
        :param botengine:
        :return: Hr switch
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_HR_SWITCH in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_HR_SWITCH][0][0]

        return None
    
    def set_hr_switch(self, botengine=None, hr_switch=None):
        """
        Set the hr switch
        :param botengine:
        """
        if hr_switch is None:
            raise ValueError("HR switch must be set")
        if hr_switch not in [HRSwitch.OFF.value, HRSwitch.ON.value]:
            raise ValueError(f"HR switch must be one of {HRSwitch.OFF.value} or {HRSwitch.ON.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_HR_SWITCH,
                "value": int(hr_switch),
            },
        )

    def did_location_period_change(self, botengine=None):
        """
        Did the location period change?
        :param botengine:
        :return: True if the location period changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LOCATION_PERIOD in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_LOCATION_PERIOD
                in self.last_updated_params
            ):
                return True

        return False

    def get_location_period(self, botengine=None):
        """
        Get the location period
        :param botengine:
        :return: Location period
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_LOCATION_PERIOD in self.measurements:
            return self.measurements[
                ComarchButtonDevice.MEASUREMENT_NAME_LOCATION_PERIOD
            ][0][0]

        return None
    
    def set_location_period(self, botengine=None, location_period=None):
        """
        Set the location period
        :param botengine:
        """
        if location_period is None:
            raise ValueError("Location period must be set")
        if location_period < LocationPeriod.MINIMUM.value:
            raise ValueError(f"Location period must be at least {LocationPeriod.MINIMUM.value}")
        if location_period > LocationPeriod.MAXIMUM.value:
            raise ValueError(f"Location period must be at most {LocationPeriod.MAXIMUM.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_LOCATION_PERIOD,
                "value": int(location_period),
            },
        )

    def did_phone_change(self, botengine=None, index=None):
        """
        Did the phone change?
        :param botengine:
        :param index: Phone index
        :return: True if the phone changed
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.SOS.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_1.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_2.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_2.value}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_PHONE}.{index}"]

        return any([param in self.last_updated_params for param in param_names])

    def get_phone(self, botengine=None, index=None):
        """
        Get the phone
        :param botengine:
        :param index: Phone index
        :return: Phone
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.SOS.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_1.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_2.value}",
                f"{self.MEASUREMENT_NAME_PHONE}.{PhoneIndex.CONTACT_2.value}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_PHONE}.{index}"]

        # botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
        #     f"|is_currently_pressed() param_names={param_names} measurements={self.measurements}"
        # )
        params = [
            self.measurements[param_name][0][0]
            for param_name in param_names
            if param_name in self.measurements
        ]
        return params[0] if params else None
    
    def set_phone(self, botengine=None, index=None, phone=None):
        """
        Set the phone
        :param botengine:
        :param index: Phone index
        :param phone: Phone
        """
        if index is None:
            raise ValueError("Phone index must be set")
        if index not in [PhoneIndex.SOS.value, PhoneIndex.CONTACT_1.value, PhoneIndex.CONTACT_2.value, PhoneIndex.CONTACT_3.value]:
            raise ValueError(f"Phone index must be one of {PhoneIndex.SOS.value}, {PhoneIndex.CONTACT_1.value}, {PhoneIndex.CONTACT_2.value}, {PhoneIndex.CONTACT_3.value}")
        if phone is None:
            raise ValueError("Phone must be set")
        # TODO: Validate phone number?
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_PHONE,
                "value": phone,
                "index": f"{index}",
            },
        )

    def did_timezone_change(self, botengine=None):
        """
        Did the timezone change?
        :param botengine:
        :return: True if the timezone changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE
                in self.last_updated_params
            ):
                return True

        return False

    def get_timezone(self, botengine=None):
        """
        Get the timezone
        :param botengine:
        :return: Timezone
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE][0][
                0
            ]

        return None
    
    def set_timezone(self, botengine=None, timezone=None):
        """
        Set the timezone
        :param botengine:
        """
        if timezone is None:
            raise ValueError("Timezone must be set")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE,
                "value": timezone,
            },
        )

    def did_volume_change(self, botengine=None):
        """
        Did the volume change?
        :param botengine:
        :return: True if the volume changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_VOLUME in self.measurements:
            if ComarchButtonDevice.MEASUREMENT_NAME_VOLUME in self.last_updated_params:
                return True

        return False

    def get_volume(self, botengine=None):
        """
        Get the volume
        :param botengine:
        :return: Volume
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_VOLUME in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_VOLUME][0][0]

        return None
    
    def set_volume(self, botengine=None, volume=None):
        """
        Set the volume
        :param botengine:
        """
        if volume is None:
            raise ValueError("Volume must be set")
        if volume < Volume.MINIMUM.value:
            raise ValueError(f"Volume must be at least {Volume.MINIMUM.value}")
        if volume > Volume.MAXIMUM.value:
            raise ValueError(f"Volume must be at most {Volume.MAXIMUM.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_VOLUME,
                "value": int(volume),
            },
        )

    def did_immobility_change(self, botengine=None):
        """
        Did the immobility change?
        :param botengine:
        :return: True if the immobility changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_IMMOBILITY in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_IMMOBILITY
                in self.last_updated_params
            ):
                return True

        return False

    def get_immobility(self, botengine=None):
        """
        Get the immobility
        :param botengine:
        :return: Immobility
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_IMMOBILITY in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_IMMOBILITY][
                0
            ][0]

        return None

    def did_timezone_id_change(self, botengine=None):
        """
        Did the timezone id change?
        :param botengine:
        :return: True if the timezone id changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE_ID in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE_ID
                in self.last_updated_params
            ):
                return True

        return False

    def get_timezone_id(self, botengine=None):
        """
        Get the timezone id
        :param botengine:
        :return: Timezone id
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE_ID in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_TIMEZONE_ID][
                0
            ][0]

        return None
    
    def did_whitelist_change(self, botengine=None):
        """
        Did the whitelist change?
        :param botengine:
        :return: True if the whitelist changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_whitelist(self, botengine=None):
        """
        Get the whitelist
        :param botengine:
        :return: Whitelist
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST][0][0]

        return None
    
    def set_whitelist(self, botengine=None, whitelist=None):
        """
        Set the whitelist
        :param botengine:
        """
        if whitelist is None:
            raise ValueError("Whitelist must be set")

        if len(whitelist.split(",")) > 10:
            raise ValueError("Whitelist must have at most 10 phone numbers")
        # TODO: Validate phone numbers?

        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST,
                "value": whitelist,
            },
        )

    def did_whitelist_switch_change(self, botengine=None):
        """
        Did the whitelist switch change?
        :param botengine:
        :return: True if the whitelist switch changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST_SWITCH in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST_SWITCH
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_whitelist_switch(self, botengine=None):
        """
        Get the whitelist switch
        :param botengine:
        :return: Whitelist switch
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST_SWITCH in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST_SWITCH][0][0]

        return None
    
    def set_whitelist_switch(self, botengine=None, whitelist_switch=None):
        """
        Set the whitelist switch
        :param botengine:
        """
        if whitelist_switch is None:
            raise ValueError("Whitelist switch must be set")
        if whitelist_switch not in [WhitelistSwitch.OFF.value, WhitelistSwitch.ON.value]:
            raise ValueError(f"Whitelist switch must be one of {WhitelistSwitch.OFF.value} or {WhitelistSwitch.ON.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_WHITELIST_SWITCH,
                "value": int(whitelist_switch),
            },
        )

    def did_sequential_calls_change(self, botengine=None):
        """
        Did the sequential calls change?
        :param botengine:
        :return: True if the sequential calls changed
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_SEQUENTIAL_CALLS in self.measurements:
            if (
                ComarchButtonDevice.MEASUREMENT_NAME_SEQUENTIAL_CALLS
                in self.last_updated_params
            ):
                return True

        return False
    
    def get_sequential_calls(self, botengine=None):
        """
        Get the sequential calls
        :param botengine:
        :return: Sequential calls
        """
        if ComarchButtonDevice.MEASUREMENT_NAME_SEQUENTIAL_CALLS in self.measurements:
            return self.measurements[ComarchButtonDevice.MEASUREMENT_NAME_SEQUENTIAL_CALLS][0][0]

        return None
    
    def set_sequential_calls(self, botengine=None, sequential_calls=None):
        """
        Set the sequential calls
        :param botengine:
        """
        if sequential_calls is None:
            raise ValueError("Sequential calls must be set")
        if sequential_calls not in [SequentialCalls.OFF.value, SequentialCalls.ON.value]:
            raise ValueError(f"Sequential calls must be one of {SequentialCalls.OFF.value} or {SequentialCalls.ON.value}")
        
        botengine.send_commands(
            self.device_id,
            {
                "name": ComarchButtonDevice.MEASUREMENT_NAME_SEQUENTIAL_CALLS,
                "value": int(sequential_calls),
            },
        )