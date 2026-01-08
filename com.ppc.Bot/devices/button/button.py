"""
Created on January 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

from devices.device import Device


class ButtonDevice(Device):
    """
    Button Device
    
    Base class for all button devices in the system. Provides common functionality
    for detecting button press/release events, battery monitoring, and device status
    management.
    
    This class serves as the foundation for various types of button devices including:
    - Simple push buttons
    - Panic buttons
    - Multi-button devices
    - Mobile button devices with cellular connectivity
    
    Key Features:
    - Button state detection (pressed/released)
    - Support for multi-button devices via index parameter
    - Battery level monitoring
    - Timestamp tracking for button events
    - Device type identification and icon management
    
    Measurement Parameters:
    - buttonStatus: Boolean indicating if button is currently pressed
    - batteryLevel: Battery level percentage (0-100)
    
    Usage:
    Subclasses should extend this class and implement device-specific functionality
    while leveraging the common button detection and monitoring capabilities.
    """

    # List of Device Types this class is compatible with
    # Subclasses should override this with specific device type IDs
    DEVICE_TYPES = []

    # Measurement names for device status and monitoring
    MEASUREMENT_NAME_BUTTON_STATUS = "buttonStatus"  # Boolean: True if button is pressed
    MEASUREMENT_NAME_BATTERY_LEVEL = "batteryLevel"  # Integer: Battery level percentage (0-100)

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
        
        Initialize a new button device instance with the specified parameters.
        
        :param botengine: BotEngine instance for device communication and logging
        :param location_object: Location object this device belongs to
        :param device_id: Unique identifier for this device instance
        :param device_type: Type identifier for the device model/variant
        :param device_description: Human-readable description of the device
        :param precache_measurements: Whether to precache measurement data for faster access
        """
        Device.__init__(
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
        Get the localized name of this device type for display purposes.
        
        :return: Localized device type name, e.g. "Button"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Button")  # noqa: F821 # type: ignore

    def get_icon(self):
        """
        Get the font icon identifier for this device type.
        
        :return: Font icon name for UI display, e.g. "push-button"
        """
        return "push-button"

    def does_support_gps_wandering(self):
        """
        Does this device support GPS wandering?
        :return: True if the device supports GPS wandering
        """
        return False

    def did_battery_level_change(self, botengine=None):
        """
        Did the battery level change?
        :param botengine:
        :return: True if the battery level changed
        """
        if self.MEASUREMENT_NAME_BATTERY_LEVEL in self.measurements:
            if self.MEASUREMENT_NAME_BATTERY_LEVEL in self.last_updated_params:
                return True

        return False

    def get_battery_level(self, botengine=None):
        """
        Get the battery level
        :param botengine:
        :return: Battery level
        """
        if self.MEASUREMENT_NAME_BATTERY_LEVEL in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_BATTERY_LEVEL][0][0]

        return None

    def get_battery_level_timestamp(self, botengine=None):
        """
        Get the timestamp of the last battery level measurement received
        :param botengine:
        :return: Timestamp of the last battery level measurement in ms; None if it doesn't exist
        """
        if self.MEASUREMENT_NAME_BATTERY_LEVEL in self.measurements:
            return self.measurements[self.MEASUREMENT_NAME_BATTERY_LEVEL][0][1]

        return None

    def is_currently_pressed(self, botengine=None, index=None):
        """
        Check if the button is currently in a pressed state.
        
        This method returns the current state of the button based on the most recent
        measurement data received from the device.
        
        :param botengine: BotEngine instance (optional, for future extensibility)
        :param index: Button index for multi-button devices (0-based)
        :return: True if the button is currently pressed, False otherwise
        """
        param_name = self.MEASUREMENT_NAME_BUTTON_STATUS
        if index is not None:
            param_name += f".{index}"
        if param_name in self.measurements:
            return self.measurements[param_name][0][0]

        return False

    def is_single_button_pressed(self, botengine, index=None):
        """
        Detect if a button was just pressed in the current update cycle.
        
        This method checks if a button press event occurred in the most recent
        data update, indicating a new button press action.
        
        :param botengine: BotEngine instance for accessing update information
        :param index: Button index for multi-button devices (0-based)
        :return: True if the button was pressed in the current update cycle
        """
        param_name = self.MEASUREMENT_NAME_BUTTON_STATUS
        if index is not None:
            param_name += f".{index}"
        return (
            param_name in self.last_updated_params
            and self.measurements[param_name][0][0]
        )

    def is_single_button_released(self, botengine, index=None):
        """
        Detect if a button was just released in the current update cycle.
        
        This method checks if a button release event occurred in the most recent
        data update, indicating a button was released from a pressed state.
        
        :param botengine: BotEngine instance for accessing update information
        :param index: Button index for multi-button devices (0-based)
        :return: True if the button was released in the current update cycle
        """
        param_name = self.MEASUREMENT_NAME_BUTTON_STATUS
        if index is not None:
            param_name += f".{index}"
        return (
            self.MEASUREMENT_NAME_BUTTON_STATUS in self.last_updated_params
            and not self.measurements[param_name][0][0]
        )

    def get_timestamp(self, botengine=None, index=None):
        """
        Get the timestamp of the last buttonStatus measurement received
        :param botengine:
        :param index: Button index if there are multiple buttons on this device.
        :return: Timestamp of the last buttonStatus measurement in ms; None if it doesn't exist
        """
        param_name = self.MEASUREMENT_NAME_BUTTON_STATUS
        if param_name in self.measurements:
            return self.measurements[param_name][0][1]

        return None
