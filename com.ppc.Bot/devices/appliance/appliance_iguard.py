'''
Created on May 6, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device

class IGuardApplianceDevice(Device):
    """Appliance iGuard"""

    # Goals
    GOAL_DEFAULT = 0

    # Measurement Names
    MEASUREMENT_NAME_FIRMWARE = "firmware" # Firmware version
    MEASUREMENT_NAME_HARDWARE = "hardware" # Hardware version
    MEASUREMENT_NAME_MAC_ADDRESS = "macAddress" # Mac address of the device
    MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF = "ig.audio.beforeShutoff" # True to enable a audio reminder before shutoff. False otherwise
    MEASUREMENT_NAME_AUDIO_USER_INPUT = "ig.audio.userInput" # True to enable audio response on user inputs (button presses). False otherwise
    MEASUREMENT_NAME_LOCK_MODE = "ig.lock.mode" # The main lock of the iguard device
    MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE = "ig.lock.extTimerMode" # the extended timer lock mode
    MEASUREMENT_NAME_LOCK_SERVICE_MODE = "ig.lock.serviceMode" # Service mode completely by-pass the iGuard protections and allows the stove to act normally. True to engage service mode, false otherwise
    MEASUREMENT_NAME_SAFETY = "ig.safety" # True if the child-safe mode is enabled. False otherwise.
    MEASUREMENT_NAME_STATUS_STOVE = "ig.status.stove" # True if the stove is on. False otherwise.
    MEASUREMENT_NAME_STATUS_TEMP = "ig.status.temp" # Measured temperature reported in tenths of degrees Celcius
    MEASUREMENT_NAME_STATUS_TIME_REMAINING = "ig.status.timeRemaining" # The amount of time remaining on a timer in seconds.
    MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT = "ig.stove.minOnCurrent" # The smallest current measurement considered at which the stove is considered to be "on".
    MEASUREMENT_NAME_TIMER_DEFAULT_DURATION = "ig.timer.defaultDuration" # The default timer duration in seconds
    MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION = "ig.timer.maxDuration" # The maximum timer duration in seconds
    MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER = "ig.timer.showAutoTimer" # If true, the iguard will display the timer when in auto mode
    MEASUREMENT_NAME_TIMER_TIMER_WARNING = "ig.timer.timerWarning" # The amount of time that the iGuard should send a notification prior to the timer elapsing
    MEASUREMENT_NAME_EVENT_STOVE = "ig.event.stove" # Stove on/off event provided by the device.
    MEASUREMENT_NAME_EVENT_TIMER = "ig.event.timer" # Timer shutoff/warning event provided by the device.
    MEASUREMENT_NAME_OCCUPANCY = "occupancy" # Motion absence/presence event provided by the device.
    MEASUREMENT_NAME_SERIAL_NUMBER = "serialNo" # Serial number of the device
    MEASUREMENT_NAME_VERSION = "version" # Software API version

    # Measurement Values
    LOCK_MODE_NONE = 0
    LOCK_MODE_SINGLE_SHOT = 1
    LOCK_MODE_LOCKED = 2
    EVENT_STOVE_ON  = 1
    EVENT_STOVE_OFF = 0
    EVENT_TIMER_SHUTOFF = 0
    EVENT_TIMER_WARNING = 1
    OCCUPANCY_ABSENCE = 0
    OCCUPANCY_PRESENT = 1

    # Command Names
    COMMAND_NAME_COMMAND = "command"
    COMMAND_NAME_REBOOT = "reboot"
    
    # Command Values
    COMMAND_VALUE_GET_SETTINGS = "getSettings"
    COMMAND_VALUE_GET_INFO = "getInfo"
    REBOOT_VALUE_SOFTWARE_RESET = 1
    REBOOT_VALUE_FACTORY_RESET = 2

    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_STATUS_STOVE,
        MEASUREMENT_NAME_STATUS_TEMP,
        MEASUREMENT_NAME_EVENT_STOVE,
        MEASUREMENT_NAME_EVENT_TIMER,
        MEASUREMENT_NAME_OCCUPANCY,
    ]

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2005]
    
    def __init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=True):
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Default behavior
        self.goal_id = IGuardApplianceDevice.GOAL_DEFAULT
        
    def initialize(self, botengine):
        """
        Initialize
        :param botengine:
        :return:
        """
        Device.initialize(self, botengine)
        
    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Device type name
        return _("iGuard")

    def get_icon(self):
        """
        :return: the font icon name of this device type
        """
        return "fire"
    
    #===========================================================================
    # Attributes
    #===========================================================================
    def did_update_firmware(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_FIRMWARE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_FIRMWARE in self.last_updated_params:
                return True
        return False
    
    def get_firmware(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_FIRMWARE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_FIRMWARE]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_FIRMWARE][0][0]
        return None
    
    def did_update_version(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_VERSION in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_VERSION in self.last_updated_params:
                return True
        return False
    
    def get_version(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_VERSION in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_VERSION]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_VERSION][0][0]
        return None
    
    def did_update_audio_before_shutoff(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF in self.last_updated_params:
                return True
        return False
    
    def get_audio_before_shutoff(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF][0][0]
        return None
    
    def did_update_audio_user_input(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT in self.last_updated_params:
                return True
        return False
    
    def get_audio_user_input(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT][0][0]
        return None
    
    def did_update_lock_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE in self.last_updated_params:
                return True
        return False
    
    def get_lock_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE][0][0]
        return None
    
    def did_update_lock_extended_timer_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE in self.last_updated_params:
                return True
        return False
    
    def get_lock_extended_timer_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE][0][0]
        return None
    
    def did_update_lock_service_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE in self.last_updated_params:
                return True
        return False
    
    def get_lock_service_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE][0][0]
        return None
    
    def did_update_child_safe_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY in self.last_updated_params:
                return True
        return False
    
    def get_child_safe_mode(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY][0][0]
        return None
    
    def did_update_stove_status(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_STOVE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_STOVE in self.last_updated_params:
                return True
        return False
    
    def get_stove_status(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_STOVE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_STOVE]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_STOVE][0][0]
        return None
    
    def did_update_stove_temperature(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TEMP in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TEMP in self.last_updated_params:
                return True
        return False
    
    def get_stove_temperature(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TEMP in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TEMP]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TEMP][0][0]
        return None
    
    def did_update_time_remaining_on_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TIME_REMAINING in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TIME_REMAINING in self.last_updated_params:
                return True
        return False
    
    def get_time_remaining_on_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TIME_REMAINING in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TIME_REMAINING]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STATUS_TIME_REMAINING][0][0]
        return None
    
    def did_update_stove_minimum_on_current(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT in self.last_updated_params:
                return True
        return False
    
    def get_stove_minimum_on_current(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT][0][0]
        return None
    
    def did_update_timer_default_duration(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION in self.last_updated_params:
                return True
        return False
    
    def get_timer_default_duration(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION][0][0]
        return None
    
    def did_update_timer_maximum_duration(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION in self.last_updated_params:
                return True
        return False
    
    def get_timer_maximum_duration(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION][0][0]
        return None
    
    def did_update_timer_show_auto_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER in self.last_updated_params:
                return True
        return False
    
    def get_timer_show_auto_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER][0][0]
        return None
    
    def did_update_timer_timer_warning(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING in self.last_updated_params:
                return True
        return False
    
    def get_timer_timer_warning(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING][0][0]
        return None
    
    def did_update_event_stove(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_STOVE in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_STOVE in self.last_updated_params:
                return True
        return False
    
    def get_event_stove(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_STOVE in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_STOVE]) > 0:
                return True == self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_STOVE][0][0]
        return None
    
    def did_update_event_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_TIMER in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_TIMER in self.last_updated_params:
                return True
        return False
    
    def get_event_timer(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_TIMER in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_TIMER]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_EVENT_TIMER][0][0]
        return None
    
    def did_update_occupancy(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if IGuardApplianceDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                return True
        return False
    
    def get_occupancy(self, botengine):
        if IGuardApplianceDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if len(self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                return self.measurements[IGuardApplianceDevice.MEASUREMENT_NAME_OCCUPANCY][0][0]
        return None
    
    #===========================================================================
    # Commands
    #===========================================================================
    def get_settings(self, botengine, command_timeout_ms=5000):
        """
        Get the settings from the iGuard
        :param botengine:
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.COMMAND_NAME_COMMAND, IGuardApplianceDevice.COMMAND_VALUE_GET_SETTINGS, command_timeout_ms=command_timeout_ms)
        return True
    
    def get_info(self, botengine, command_timeout_ms=5000):
        """
        Get the info from the iGuard
        :param botengine:
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.COMMAND_NAME_COMMAND, IGuardApplianceDevice.COMMAND_VALUE_GET_INFO, command_timeout_ms=command_timeout_ms)
        return True
    
    def reboot(self, botengine, factory_reset=False, command_timeout_ms=5000):
        """
        Reboot the iGuard
        :param botengine:
        :param factory_reset: True to factory reset
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.COMMAND_NAME_REBOOT, str(IGuardApplianceDevice.REBOOT_VALUE_FACTORY_RESET) if factory_reset else str(IGuardApplianceDevice.REBOOT_VALUE_SOFTWARE_RESET), command_timeout_ms=command_timeout_ms)
        return True
    
    def set_lock_mode(self, botengine, lock_mode, command_timeout_ms=5000):
        """
        Set the lock mode
        :param botengine:
        :param lock_mode: 0 or 2 
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False
        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_MODE, str(lock_mode), command_timeout_ms=command_timeout_ms)
        return True
    
    def set_lock_extended_timer_mode(self, botengine, lock_mode, command_timeout_ms=5000):
        """
        Set the lock extended timer mode
        :param botengine:
        :param lock_mode: Lock mode. See LOCK_MODE_*
        :param command_timeout_ms:
        :return:
        """
        # Not supported
        # raise NotImplementedError("Not supported")
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_EXTENDED_TIMER_MODE, str(lock_mode), command_timeout_ms=command_timeout_ms)
        return True

    def set_lock_service_mode(self, botengine, enabled, command_timeout_ms=5000):
        """
        Set the lock service mode
        :param botengine:
        :param enabled: True to enable
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_LOCK_SERVICE_MODE, "1" if enabled else "0", command_timeout_ms=command_timeout_ms)
        return True
    
    def set_audio_before_shutoff(self, botengine, enabled, command_timeout_ms=5000):
        """
        Set audio before shutoff
        :param botengine:
        :param enabled: True to enable
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_BEFORE_SHUTOFF, "1" if enabled else "0", command_timeout_ms=command_timeout_ms)
        return True
    
    def set_audio_user_input(self, botengine, enabled, command_timeout_ms=5000):
        """
        Set audio during user input
        :param botengine:
        :param enabled: True to enable
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_AUDIO_USER_INPUT, "1" if enabled else "0", command_timeout_ms=command_timeout_ms)
        return True
    
    def set_timer_default_duration(self, botengine, duration=900, command_timeout_ms=5000):
        """
        Set timer default duration
        :param botengine:
        :param duration: int
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_DEFAULT_DURATION, f'{int(duration)}', command_timeout_ms=command_timeout_ms)
        return True
    
    def set_timer_maximum_duration(self, botengine, duration=36000, command_timeout_ms=5000):
        """
        Set timer maximum duration
        :param botengine:
        :param duration: int
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_MAXIMUM_DURATION, f'{int(duration)}', command_timeout_ms=command_timeout_ms)
        return True
    
    def set_timer_show_auto_timer(self, botengine, enabled, command_timeout_ms=5000):
        """
        Set timer show auto timer setting
        :param botengine:
        :param enabled: True to enable
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_SHOW_AUTO_TIMER, "1" if enabled else "0", command_timeout_ms=command_timeout_ms)
        return True
    
    def set_timer_timer_warning(self, botengine, duration=300, command_timeout_ms=5000):
        """
        Set timer warning duration
        :param botengine:
        :param duration: int
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_TIMER_TIMER_WARNING, f'{int(duration)}', command_timeout_ms=command_timeout_ms)
        return True
    
    def set_child_safe_mode(self, botengine, enabled, command_timeout_ms=5000):
        """
        Set child-safe mode
        :param botengine:
        :param enabled: True to enable
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_SAFETY, "1" if enabled else "0", command_timeout_ms=command_timeout_ms)
        return True
    
    def set_stove_minimum_on_current(self, botengine, current=1200, command_timeout_ms=5000):
        """
        Set stove minimum on current
        :param botengine:
        :param current: int
        :param command_timeout_ms:
        :return:
        """
        if not self.is_connected and False:
            return False

        botengine.send_command(self.device_id, IGuardApplianceDevice.MEASUREMENT_NAME_STOVE_MINIMUM_ON_CURRENT, f'{int(current)}', command_timeout_ms=command_timeout_ms)
        return True