'''
Created on January 3rd, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
'''
from devices.audio.audio import AudioDevice
import utilities.utilities as utilities

BUTTON_INDEXES = {
    "SOS": 1,
    "CALL": 2,
    "CONFIG": 3,
}

BUTTON_STATUS_SHORT = 1
BUTTON_STATUS_LONG = 2

BLUETOOTH_STATUS_INITIALIZING = 0
BLUETOOTH_STATUS_FIRMWARE_UPGRADE = 1
BLUETOOTH_STATUS_NOT_PAIRED = 2
BLUETOOTH_STATUS_PAIRING_MODE = 3
BLUETOOTH_STATUS_PAIRED = 4
BLUETOOTH_STATUS_CONNECTED = 5

class DevelcoAudioAssistantDevice(AudioDevice):
    """
    Develco Audio Assistant Device
    """

    MEASUREMENT_NAME_BUTTON_STATUS = "buttonStatus"
    MEASUREMENT_NAME_BLUETOOTH_STATUS = "btStatus"

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [9109]

    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        AudioDevice.__init__(self, botengine, location_object, device_id, device_type, device_description,
                                   precache_measurements=precache_measurements)

    def is_short_button_pressed(self, botengine, index=None):
        """
        Find out if a button is pressed for a short duration on this device
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: True if the button was pressed for a short duration
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['SOS']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CALL']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CONFIG']}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        for param_name in param_names:
            if param_name in self.last_updated_params and self.measurements[param_name][0][0] == BUTTON_STATUS_SHORT:
                return True
        return False

    def is_long_button_pressed(self, botengine, index=None):
        """
        Find out if a button is pressed for a long duration on this device
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: True if the button was pressed for a long duration
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['SOS']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CALL']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CONFIG']}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        for param_name in param_names:
            if param_name in self.last_updated_params and self.measurements[param_name][0][0] == BUTTON_STATUS_LONG:
                return True
        return False

    def get_recent_button_status_timestamp(self, botengine=None, index=None):
        """
        Get the timestamp of the last buttonStatus measurement received
        :param botengine:
        :return: Timestamp of the last buttonStatus measurement in ms; None if it doesn't exist
        """
        if index is None:
            param_names = [
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['SOS']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CALL']}",
                f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{BUTTON_INDEXES['CONFIG']}",
            ]
        else:
            param_names = [f"{self.MEASUREMENT_NAME_BUTTON_STATUS}.{index}"]

        # Sort the param names by timestamp
        params = [self.measurements[param_name][0] for param_name in param_names if param_name in self.measurements]
        params.sort(key=lambda x: x[1], reverse=True)
        return params[0][1] if params else None

    def did_update_bluetooth_status(self, botengine=None):
        """
        Check if the Bluetooth status was updated in the last event.
        :param botengine:
        :return: True if Bluetooth status was updated, False otherwise
        """
        param_name = self.MEASUREMENT_NAME_BLUETOOTH_STATUS
        return param_name in self.last_updated_params

    def get_bluetooth_status(self, botengine=None):
        """
        Get the most recent Bluetooth status value.
        :param botengine:
        :return: Integer Bluetooth status value, or None if not available
        """
        param_name = self.MEASUREMENT_NAME_BLUETOOTH_STATUS
        if param_name in self.measurements:
            return self.measurements[param_name][0][0]
        return None

