'''
Created on February 11, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
from devices.radar.radar import RadarDevice
import signals.radar as radar
import utilities.utilities as utilities

class RadarVayyarDevice(RadarDevice):
    """
    Vayyar Device
    """
    # Parameters
    MEASUREMENT_NAME_TRACKER_SUBREGIONS             = "vyrc.trackerSubRegions"
    MEASUREMENT_NAME_X_MIN                          = "vyrc.xMin"
    MEASUREMENT_NAME_X_MAX                          = "vyrc.xMax"
    MEASUREMENT_NAME_Y_MIN                          = "vyrc.yMin"
    MEASUREMENT_NAME_Y_MAX                          = "vyrc.yMax"
    MEASUREMENT_NAME_Z_MIN                          = "vyrc.zMin"
    MEASUREMENT_NAME_Z_MAX                          = "vyrc.zMax"
    MEASUREMENT_NAME_FALLING_SENSITIVITY            = "vyrc.fallingSensitivity"
    MEASUREMENT_NAME_CONFIRMED_TO_ALERT_TIMEOUT_SEC = "vyrc.confirmedToAlertTimeoutSec"
    MEASUREMENT_NAME_LED_MODE                       = "vyrc.ledMode"
    MEASUREMENT_NAME_VOLUME                         = "vyrc.volume"
    MEASUREMENT_NAME_TELEMTRY_POLICY                = "vyrc.telemetryPolicy"
    MEASUREMENT_NAME_PRESENCE_REPORT_MIN_RATE_MILLS = "vyrc.presenceReportMinRateMills"
    MEASUREMENT_NAME_PRESENCE_PERIODIC_REPORT       = "vyrc.presencePeriodicReport"
    MEASUREMENT_NAME_SILENT_MODE                    = "vyrc.silentMode"
    MEASUREMENT_NAME_SENSOR_HEIGHT                  = "vyrc.sensorHeight"
    MEASUREMENT_NAME_SENSOR_MOUNTING                = "vyrc.sensorMounting"
    MEASUREMENT_NAME_ENTER_DURATION                 = "vyrc.enterDuration"
    MEASUREMENT_NAME_EXIT_DURATION                  = "vyrc.exitDuration"
    MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM         = "vyrc.durationUntilConfirm"
    MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC    = "vyrc.minTimeOfTarInFallLoc"
    MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION = "vyrc.dryContactActivationDuration"
    MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED      = "vyrc.fallingMitigatorEnabled"
    MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY       = "vyrc.aboveThPointTelemetry"
    MEASUREMENT_NAME_OFFLINE_MODE                   = "vyrc.offlineMode"
    MEASUREMENT_NAME_CALLING_DURATION_SEC           = "vyrc.callingDurationSec"
    MEASUREMENT_NAME_LEARNING_MODE_END              = "vyrc.learningModeEnd"
    MEASUREMENT_NAME_TEST_MODE                      = "vyrc.testMode"
    MEASUREMENT_NAME_DRY_CONTRACTS                  = "vyrc.dryContacts"
    MEASUREMENT_NAME_DEMO_MODE                      = "vyrc.demoMode"
    MEASUREMENT_NAME_DOOR_EVENTS                    = "vyrc.doorEvents"
    MEASUREMENT_NAME_OUT_OF_BED                     = "vyrc.outOfBed"
    MEASUREMENT_NAME_SENSITIVE_MODE                 = "vyrc.sensitiveMode"
    MEASUREMENT_NAME_SENSITIVITY_LEVEL              = "vyrc.sensitivityLevel"
    MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION  = "vyrc.minEventsForFirstDecision"
    MEASUREMENT_NAME_DETECTIONS_IN_CHAIN            = "vyrc.detectionsInChain"
    MEASUREMENT_NAME_FALL_LEARNING                  = "fallLearning"
    

    # Measurement parameters list for machine learning data extraction
    MEASUREMENT_PARAMETERS_LIST = [
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET,
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP,
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY
    ]

    # Fall Status
    FALL_STATUS_DETECTED    = "fall_detected"
    FALL_STATUS_CONFIRMED   = "fall_confirmed"
    FALL_STATUS_SUSPECTED   = "fall_suspected"
    FALL_STATUS_CALLING     = "calling"
    FALL_STATUS_CANCELLED   = "canceled"
    FALL_STATUS_FINISHED    = "finished"
    FALL_STATUS_EXIT        = "fall_exit"

    # Min and max values
    X_MIN_METERS_WALL = -3.0
    X_MAX_METERS_WALL = 2.0
    Y_MIN_METERS_WALL = 0.3
    Y_MAX_METERS_WALL = 4.0
    Z_MIN_METERS_WALL = 0
    Z_MAX_METERS_WALL = 2.0
    X_MIN_METERS_CEILING = -2.5
    X_MAX_METERS_CEILING = 2.5
    Y_MIN_METERS_CEILING = -3
    Y_MAX_METERS_CEILING = 3
    SENSOR_HEIGHT_MIN_METERS_CEILING = 2.3
    SENSOR_HEIGHT_MAX_METERS_CEILING = 3.0

    # Mounting options
    SENSOR_MOUNTING_WALL = 0
    SENSOR_MOUNTING_CEILING = 1
    SENSOR_MOUNTING_CEILING_45_DEGREE = 2

    # Maximum allowable subregions
    MAXIMUM_SUBREGIONS = 6

    # Low signal strength warning threshold
    LOW_RSSI_THRESHOLD = -70

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2000]

    # Maximum stability event counter value
    MAXIMUM_STABILITY_EVENT_COUNT = 20

    # Learning mode status
    LEARNING_MODE_REST = 0
    LEARNING_MODE_GOING = 1
    LEARNING_MODE_DONE = 2

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

        # Count of times a target measurement has detected a stability event on this device.
        # Every fall detect from a target increments this value to the MAXIMUM_STABILITY_EVENT_COUNT
        # Every non-stability-event target measurement decrements the count.
        # This is used like a 'capacitor' of stability events, giving us confidence to declare that the person has stability issues and may be a precurser to a fall event.
        self.stability_event_count = 0

        # True if the device is in learning mode
        self.learning_mode_status = RadarVayyarDevice.LEARNING_MODE_REST

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
        return _("Vayyar Care")
    
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
    
    #===========================================================================
    # Attributes
    #===========================================================================

    def did_update_leds(self, botengine):
        """
        :param botengine:
        :return: True if this Vayyar device updated its leds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE in self.measurements:
            if RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE in self.last_updated_params:
                return True

        return False

    def get_leds(self, botengine):
        """
        :param botengine:
        :return: LED status
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE]) > 0:
                return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE][0][0]

        return None

    def did_update_volume(self, botengine):
        """
        :param botengine:
        :return: True if this Vayyar device updated its volume
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_VOLUME in self.measurements:
            if RadarVayyarDevice.MEASUREMENT_NAME_VOLUME in self.last_updated_params:
                return True

        return False

    def get_volume(self, botengine):
        """
        :param botengine:
        :return: Volume
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_VOLUME in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_VOLUME]) > 0:
                return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_VOLUME][0][0]

        return None

    def get_telemetry_policy(self, botengine):
        """
        :param botengine:
        :return: Volume
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY]) > 0:
                return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY][0][0]

        return None

    def is_detecting_stability_event(self, botengine):
        """
        Is this Vayyar device detecting any kind of stability event
        :param botengine: BotEngine
        :return: True if this Vayyar device is detecting a stability event (fall_confirmed or fall_detected)
        """
        status = self.get_fall_status(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|is_detecting_stability_event() " + utilities.Color.RED + "status={} learning_mode_status={}".format(status, self.learning_mode_status) + utilities.Color.END)
        if status is not None and not self.learning_mode_status != RadarVayyarDevice.LEARNING_MODE_DONE:
            return status == RadarDevice.FALL_STATUS_CONFIRMED or status == RadarDevice.FALL_STATUS_DETECTED
        return False

    def is_detecting_fall(self, botengine):
        """
        Is this Vayyar device detecting any kind of fall
        :param botengine: BotEngine
        :return: True if this Vayyar device is detecting a fall (calling)
        """
        status = self.get_fall_status(botengine)
        if status is not None and not self.learning_mode_status != RadarVayyarDevice.LEARNING_MODE_DONE:
            return status == RadarDevice.FALL_STATUS_CALLING
        return False

    def did_stop_detecting_fall(self, botengine):
        """
        Did this Vayyar device finish detecting a fall after having previously detecting one?
        :param botengine:
        :return: True if a fall is no longer detected
        """
        status = self.get_fall_status(botengine)
        previous_status = self.get_previous_fall_status(botengine)
        did_update = self.did_change_fall_status(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|did_stop_detecting_fall() " + utilities.Color.RED + "status={} previous_status={} did_update={} learning_mode_status={}".format(status, previous_status, did_update, self.learning_mode_status) + utilities.Color.END)
        if status is not None and previous_status is not None and did_update and not self.learning_mode_status != RadarVayyarDevice.LEARNING_MODE_DONE:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return status == RadarDevice.FALL_STATUS_FINISHED and previous_status == RadarDevice.FALL_STATUS_CALLING

        return False

    def did_cancel_confirmed_fall(self, botengine):
        """
        Did this Vayyar device cancel a confirmed fall after having previously confirming one?
        :param botengine:
        :return: True if a fall is no longer detected
        """
        status = self.get_fall_status(botengine)
        previous_status = self.get_previous_fall_status(botengine)
        did_update = self.did_change_fall_status(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("|did_cancel_confirmed_fall() " + utilities.Color.RED + "status={} previous_status={} did_update={} learning_mode_status={}".format(status, previous_status, did_update, self.learning_mode_status) + utilities.Color.END)
        if status is not None and previous_status is not None and did_update and not self.learning_mode_status != RadarVayyarDevice.LEARNING_MODE_DONE:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return status == RadarDevice.FALL_STATUS_CANCELLED and previous_status == RadarDevice.FALL_STATUS_CONFIRMED

        return False

    def did_update_fall_learning(self, botengine):
        """
        Check if fall learning has changed
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        return RadarVayyarDevice.MEASUREMENT_NAME_FALL_LEARNING in self.last_updated_params

    def get_fall_learning(self, botengine):
        """
        Get the current fall learning status
        :param botengine:
        :return:
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_FALL_LEARNING in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LEARNING][0][0]
        return None

    def need_start_learning(self, botengine):
        return self.learning_mode_status == RadarVayyarDevice.LEARNING_MODE_REST

    def did_boot(self, botengine):
        """
        Did the device boot?
        This should only be accessed during a device_alert() event.
        :param botengine: BotEngine environment
        :return: True if the device just booted up
        """
        if hasattr(self, "last_alert"):
            if "boot" in self.last_alert:
                return self.last_alert["boot"]["timestamp_ms"] == botengine.get_timestamp()
        return False

    def did_press_button(self, botengine):
        """
        Did the person press the button on the Vayyar Home device?
        This should only be accessed during a device_alert() event.
        :param botengine:
        :return: True if the button was pressed
        """
        if hasattr(self, "last_alert"):
            if "button_press" in self.last_alert:
                return self.last_alert["button_press"]["timestamp_ms"] == botengine.get_timestamp()
        return False

    def button_press_duration(self, botengine):
        """
        Get the duration of the button press in seconds
        This should only be accessed during a device_alert() event.
        :param botengine:
        :return: Number of seconds the button was held
        """
        if hasattr(self, "last_alert"):
            if "button_press" in self.last_alert:
                if self.last_alert["button_press"]["timestamp_ms"] == botengine.get_timestamp():
                    return self.last_alert["button_press"]["press_duration_s"]
        return 0

    def set_fall_sensitivity(self, botengine, sensitivity):
        """
        Set the fall sensitivity
        :param botengine: BotEngine environment
        :param sensitivity: 0=no falling; 1=low; 2=normal
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_FALLING_SENSITIVITY, int(sensitivity))

    def set_alert_delay_s(self, botengine, alert_delay_s):
        """
        Set the delay from the 'confirmed' state to 'calling' state, in seconds.

        :param botengine: BotEngine environment
        :param alert_delay_s: Alert delay in seconds. 15-30 is recommended.
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_CONFIRMED_TO_ALERT_TIMEOUT_SEC, int(alert_delay_s))

    def set_led_mode(self, botengine, led_mode):
        """
        Set the LED mode
        :param botengine: BotEngine environment
        :param led_mode: 0 = all off; 1 = on
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE, int(led_mode))

    def set_volume(self, botengine, volume):
        """
        Set the volume level from 0 - 100
        :param botengine: BotEngine environment
        :param volume: 0 = silence; 100 = buzzer on
        :return:
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_VOLUME, int(volume))

    def set_telemetry_policy(self, botengine, telemetry_policy):
        """
        Set the telemetry policy
        :param botengine: BotEngine environment
        :param telemetry_policy: 
            * 0 : Telemetry is Off
            * 1 : Telemetry is always On
            * 2 : Telemetry is on during fall event (Recommended Default value)
            * 3 : Telemetry is on while presence is detected in the arena
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY, int(telemetry_policy))

    def set_learning_mode(self, botengine, learning_mode):
        """
        Set end of learning mode in milliseconds.
        :param botengine: BotEngine environment
        :param learning_mode: True/False on/off
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">set_learning_mode()")
        if learning_mode:
            if self.learning_mode_status != RadarVayyarDevice.LEARNING_MODE_GOING:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|set_learning_mode() starting learning")
                self.learning_mode_status = RadarVayyarDevice.LEARNING_MODE_GOING
                end_timestamp_ms = botengine.get_timestamp() + (2 * utilities.ONE_WEEK_MS)

                botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_LEARNING_MODE_END, end_timestamp_ms)
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|set_learning_mode() already going")

        else:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|set_learning_mode() setting as done")
            self.learning_mode_status = RadarVayyarDevice.LEARNING_MODE_DONE
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<set_learning_mode()")
    
    def get_learning_mode_end(self, botengine):
        """
        Refers to the time that the learning period ends. When Learning mode is activated this should be ‘NOW’ + the amount of milliseconds in the learning period (2 week). End of learning mode in milliseconds. The device in learning mode may behave differently to allow data collection for the sensitivity map. The device should be on silent mode and fall events shouldn’t cause alerts in the customer view. 
        Default: "learningModeStartTs + 14 * 1000 * 60 * 60 * 24"

        :param botengine: BotEngine environment
        :return: Timestamp in milliseconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_LEARNING_MODE_END in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_LEARNING_MODE_END][0][0]
        return 0

    def set_reporting_rate_ms(self, botengine, reporting_rate_ms):
        """
        Set the presence reporting rate in milliseconds.

        :param botengine: BotEngine environment
        :param reporting_rate_ms: Reporting rate in milliseconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_PRESENCE_REPORT_MIN_RATE_MILLS, reporting_rate_ms)

    def set_reporting_enabled(self, botengine, reporting_enabled):
        """
        Enable/Disable presence reporting.

        :param botengine: BotEngine environment
        :param reporting_enabled: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_PRESENCE_PERIODIC_REPORT, int(reporting_enabled))
        

    def set_silent_mode(self, botengine, silent_mode):
        """
        Set silent mode
        :param botengine: BotEngine
        :param silent_mode: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_SILENT_MODE, silent_mode)

    def set_target_change_threshold_m(self, botengine, target_change_threshold_m):
        """
        Set the occupancy target change threshold in meters (i.e. 0.2)
        :param botengine: BotEngine
        :param target_change_threshold_m: Threshold in meters (i.e. 0.2)
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|set_target_change_threshold_m() is no longer supported.  This method will be removed in a future release.")
        pass

    def set_falling_mitigator(self, botengine, falling_mitigator):
        """
        Set the falling mitigator
        :param botengine: BotEngine
        :param falling_mitigator: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED, falling_mitigator)

    def get_falling_mitigator(self, botengine):
        """
        Get the falling mitigator
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED][0][0]
        return False
    
    def set_enter_duration(self, botengine, enter_duration):
        """
        The minimum detection time required to establish presence in the arena, in seconds. 
        Default: 120
        :param botengine: BotEngine
        :param enter_duration: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_ENTER_DURATION, enter_duration)

    def get_enter_duration(self, botengine):
        """
        The minimum detection time required to establish presence in the arena, in seconds. 
        Default: 120
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_ENTER_DURATION in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_ENTER_DURATION][0][0]
        return 120
    
    def set_exit_duration(self, botengine, exit_duration):
        """
        The minimum detection time required to establish non-presence in the arena, in seconds. 
        Default: 120
        :param botengine: BotEngine
        :param exit_duration: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_EXIT_DURATION, exit_duration)
    
    def get_exit_duration(self, botengine):
        """
        The minimum detection time required to establish non-presence in the arena, in seconds. 
        Default: 120
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_EXIT_DURATION in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_EXIT_DURATION][0][0]
        return 120
    
    def set_duration_until_confirm_sec(self, botengine, duration_until_confirm_sec):
        """
        Time in seconds from fall_detected to fall_confirmed. 
        Default: 52
        :param botengine: BotEngine
        :param duration_until_confirm_sec: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM, duration_until_confirm_sec)

    def get_duration_until_confirm_sec(self, botengine):
        """
        Time in seconds from fall_detected to fall_confirmed. 
        Default: 52
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM][0][0]
        return 52
    
    def set_min_time_of_target_in_fall_location(self, botengine, min_time_of_target_in_fall_location):
        """
        The minimum number of seconds that the target should be detected in the fall location after fall detection to reach the fall confirmed state. This value should be set to 0.6 * durationUntilConfirm. 
        Default: 30
        :param botengine: BotEngine
        :param min_time_of_target_in_fall_location: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC, min_time_of_target_in_fall_location)

    def get_min_time_of_target_in_fall_location(self, botengine):
        """
        The minimum number of seconds that the target should be detected in the fall location after fall detection to reach the fall confirmed state. This value should be set to 0.6 * durationUntilConfirm. 
        Default: 30
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC][0][0]
        return 30
    
    def set_dry_contact_activation_duration_sec(self, botengine, dry_contact_activation_duration_sec):
        """
        The time in seconds that the dry contact will be activated when a fall is detected. 
        Default: 30
        :param botengine: BotEngine
        :param dry_contact_activation_duration_esc: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION, dry_contact_activation_duration_sec)
    
    def get_dry_contact_activation_duration_sec(self, botengine):
        """
        The time in seconds that the dry contact will be activated when a fall is detected. 
        Default: 30
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION][0][0]
        return 30
    
    def set_enable_above_th_point_telemetry_enables(self, botengine, enable_above_th_point_telemetry_enables):
        """
        Above th point telemetry for skeleton data (V40 and above). 
        Default: false
        :param botengine: BotEngine
        :param enable_above_th_point_telemetry_enables: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY, enable_above_th_point_telemetry_enables)

    def get_enable_above_th_point_telemetry_enables(self, botengine):
        """
        Above th point telemetry for skeleton data (V40 and above). 
        Default: false
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY][0][0]
        return False

    def set_test_mode(self, botengine, test_mode):
        """
        Enables test mode. To test during learning mode, the user should activate test mode. When learning and test mode are activated at the same time, the data will be marked and ignored in the sensitivity map creation. 
        Default: "false"
        :param botengine: BotEngine
        :param test_mode: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_TEST_MODE, test_mode)
    
    def get_test_mode(self, botengine):
        """
        Enables test mode. To test during learning mode, the user should activate test mode. When learning and test mode are activated at the same time, the data will be marked and ignored in the sensitivity map creation. 
        Default: "false"
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_TEST_MODE in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TEST_MODE][0][0]
        return False
    
    def set_offline_mode(self, botengine, offline_mode):
        """
        When offline mode is set to true, the device will not reboot if losses the Wi-Fi or internet connectivity. When offline mode is set to false, the device will reboot automatically after 5 minutes of MQTT disconnection. Note: daily reboot / OTA check will keep performing every 24 hours. 
        Default: true
        :param botengine: BotEngine
        :param offline_mode: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_OFFLINE_MODE, offline_mode)

    def get_offline_mode(self, botengine):
        """
        When offline mode is set to true, the device will not reboot if losses the Wi-Fi or internet connectivity. When offline mode is set to false, the device will reboot automatically after 5 minutes of MQTT disconnection. Note: daily reboot / OTA check will keep performing every 24 hours. 
        Default: true
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_OFFLINE_MODE in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_OFFLINE_MODE][0][0]
        return True
    
    def set_calling_duration_sec(self, botengine, calling_duration_sec):
        """
        This is the time in seconds that the device stays in the ‘calling’ state. 
        Default: 30
        :param botengine: BotEngine
        :param calling_duration_sec: Duration in seconds
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_CALLING_DURATION_SEC, calling_duration_sec)

    def set_dry_contacts(self, botengine, dry_contacts):
        """
        Set the dry contacts
        * vyrc.dryContacts = “primary” and “secondary”
            * object (Dry Contact Config)
                * mode = number (DryContactMode) Default: "ActiveHigh" Enum: 0 1
                    * 0 - "ActiveLow" - For use with a normally closed circuit. The dry contact alert is triggered when the circuit is open.
                    * 1 - "ActiveHigh" - For use with a normally open circuit. The dry contact alert is triggered when the circuit is closed.
                * policy = number (DryContactPolicy) Default: "Off" Enum: 0 1 2 3 4. determines when a dry contact alert will be triggered.
                    * Off - no dry contact alert
                    * OnFall - in the event of a fall, the dry contact alert will be triggered when the device reaching the calling stage
                    * OutOfBed - In an out of bed event the dry contact will be triggered
                    * OnSensitiveFall - in the event of a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage
                    * OnAnyFall “in the event of either a standard fall or a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage.

        :param botengine: BotEngine
        :param dry_contacts: Dry contact configuration
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACTS, dry_contacts)

    def get_dry_contacts(self, botengine):
        """
        Get the dry contacts
        * vyrc.dryContacts = “primary” and “secondary”
            * object (Dry Contact Config)
                * mode = number (DryContactMode) Default: "ActiveHigh" Enum: 0 1
                    * 0 - "ActiveLow" - For use with a normally closed circuit. The dry contact alert is triggered when the circuit is open.
                    * 1 - "ActiveHigh" - For use with a normally open circuit. The dry contact alert is triggered when the circuit is closed.
                * policy = number (DryContactPolicy) Default: "Off" Enum: 0 1 2 3 4. determines when a dry contact alert will be triggered.
                    * Off - no dry contact alert
                    * OnFall - in the event of a fall, the dry contact alert will be triggered when the device reaching the calling stage
                    * OutOfBed - In an out of bed event the dry contact will be triggered
                    * OnSensitiveFall - in the event of a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage
                    * OnAnyFall “in the event of either a standard fall or a target on the ground fall, the dry contact alert will be triggered when the device reaching the calling stage.

        :param botengine: BotEngine
        :return: Dry contact configuration
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACTS in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACTS][0][0]
        return None
    
    def set_demo_mode(self, botengine, demo_mode):
        """
        When demoMode is set to true, fall_detected and fall_confirmed times are each 10sec, so time to calling is 20sec. Not to be used for deployment, only client demonstrations. 
        Default: false
        :param botengine: BotEngine
        :param demo_mode: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DEMO_MODE, demo_mode)

    def get_demo_mode(self, botengine):
        """
        When demoMode is set to true, fall_detected and fall_confirmed times are each 10sec, so time to calling is 20sec. Not to be used for deployment, only client demonstrations. 
        Default: false
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DEMO_MODE in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DEMO_MODE][0][0]
        return False

    def set_door_events(self, botengine, door_events):
        """
        When set to 'True', enables the user to receive event messages when a target exit the room (Empty room) or enters the room, this feature requires setting upto 2 subregions with isDoor set to true and isLowSnr set to false. 
        Default: false
        :param botengine: BotEngine
        :param door_events: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DOOR_EVENTS, door_events)
    
    def get_door_events(self, botengine):
        """
        When set to 'True', enables the user to receive event messages when a target exit the room (Empty room) or enters the room, this feature requires setting upto 2 subregions with isDoor set to true and isLowSnr set to false. 
        Default: false
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DOOR_EVENTS in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DOOR_EVENTS][0][0]
        return False

    def set_out_of_bed_enabled(self, botengine, out_of_bed_enabled):
        """
        When set to True, the device will report Empty bed (out of bed) event in the first defined subregion, the subregion must be defined as low SNR subregion - set IsLowSNR to true. 
        Default: false
        :param botengine: BotEngine
        :param out_of_bed_enabled: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_OUT_OF_BED, out_of_bed_enabled)

    def get_out_of_bed_enabled(self, botengine):
        """
        When set to True, the device will report Empty bed (out of bed) event in the first defined subregion, the subregion must be defined as low SNR subregion - set IsLowSNR to true. 
        Default: false
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_OUT_OF_BED in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_OUT_OF_BED][0][0]
        return False

    def set_senstive_mode(self, botengine, senstive_mode):
        """
        Enable the target on the ground alerts. 
        Default: false
        :param botengine: BotEngine
        :param senstive_mode: 1 or 0
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVE_MODE, senstive_mode)

    def get_sensitive_mode(self, botengine):
        """
        Enable the target on the ground alerts. 
        Default: false
        :param botengine: BotEngine
        :return: 1 or 0
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVE_MODE in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVE_MODE][0][0]
        return False

    def set_sensitivity_level(self, botengine, sensitivity_level):
        """
        Suspected fall events with a confidence level that is above this threshold are considered human falls. 
        Default: 0.78
        
        :param botengine: BotEngine
        :param sensitivity_level: 0-1
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVITY_LEVEL, sensitivity_level)

    def get_sensitivity_level(self, botengine):
        """
        Suspected fall events with a confidence level that is above this threshold are considered human falls. 
        Default: 0.78
        :param botengine: BotEngine
        :return: 0-1
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVITY_LEVEL in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVITY_LEVEL][0][0]
        return 0.78
    
    def set_min_events_for_first_decision(self, botengine, min_events_for_first_decision):
        """
        minimum number of 'fall_suspected' events required in a chain to detect a fall and trigger a 'calling' event. 
        Default: 5
        :param botengine: BotEngine
        :param min_events_for_first_decision: 0-10
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION, min_events_for_first_decision)
    
    def get_min_events_for_first_decision(self, botengine):
        """
        minimum number of 'fall_suspected' events required in a chain to detect a fall and trigger a 'calling' event. 
        Default: 5
        :param botengine: BotEngine
        :return: 0-10
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION][0][0]
        return 5
    
    def set_num_of_detections_in_chain(self, botengine, num_of_detections_in_chain):
        """
        minimum number of human falls in chain to detect fall. Human falls are defined as falls that are detected with a confidence which is above the set 'sensitivityLevel' parameter. 
        Default: 4
        :param botengine: BotEngine
        :param num_of_detections_in_chain: 0-10
        """
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_DETECTIONS_IN_CHAIN, num_of_detections_in_chain)

    def get_num_of_detections_in_chain(self, botengine):
        """
        minimum number of human falls in chain to detect fall. Human falls are defined as falls that are detected with a confidence which is above the set 'sensitivityLevel' parameter. 
        Default: 4
        :param botengine: BotEngine
        :return: 0-10
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_DETECTIONS_IN_CHAIN in self.measurements:
            return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_DETECTIONS_IN_CHAIN][0][0]
        return 4
    
    def set_ceiling_mount(self, botengine, sensor_height_m=2.0):
        """
        Configure this Vayyar Home for a ceiling mount
        :param botengine: BotEngine environment
        :param sensor_height: Sensor height in meters (for example 2.0 - 3.0 meters)
        """
        all_params = []

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
            "value": RadarDevice.SENSOR_MOUNTING_CEILING
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
            "value": sensor_height_m
        })

        botengine.send_commands(self.device_id, all_params)

    def set_wall_mount(self, botengine):
        """
        Configure this Vayyar Home for a wall mount
        :param botengine: BotEngine environment
        """
        all_params = []

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
            "value": RadarDevice.SENSOR_MOUNTING_WALL
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
            "value": 1.5
        })

        botengine.send_commands(self.device_id, all_params)

    def set_room_boundaries(self, botengine, content={}):
        """
        Set the boundaries of the room. Measurements are in meters.

        Mounting type is either wall (0), ceiling (1), or ceiling45Deg (2).
        
        Wall mounting:

        Facing out into the room from the device for a wall installation:
        
        * **X-axis** = left/right, and the center of the Vayyar Care is 0 (so left is a negative number). Maximum to the left is -3.0 meters. Maximum to the right is 2.0 meters.
        * **Y-axis** = forward in front of the device. Again, center of the Vayyar Care is 0. There are no negative numbers here. Maximum is 4.0 meters. Minimum is 0.3 meters
        * **Z-axis** = up/down in the room. The device should always be 1.5 meters off the ground (~5 feet off the ground to the center of the device). The ceiling might be 2.5 to 3 meters high.
        
        **Offset**: A wall installation may be offset 1 meter along the X-axis to the left of the device.  The total distance along the X-axis must be adjusted so that it is 4.0 meters or less.
        
        Ceiling mounting:

        Standing under the vayyar with the cable leading infront and to the left at 45 degrees:
        
        * **X-axis** = left/right, and the center of the Vayyar Care is 0 (so left is a negative number). Maximum to the left is -2.0 meters. Maximum to the right is 2.0 meters.
        * **Y-axis** = forward/backward, and the center of the Vayyar Care is 0 (so behind you is a negative number). Maximum is 3.0 meters. Minimum is 3.0 meters
        * **Z-axis** = up/down in the room. The ceiling might be 2.5 to 3 meters high.

        **Offset**: A ceiling installation may be offset 0.5 meters along the Y-axis in either direction.  The total distance along the Y-axis must be adjusted so that it is 5.0 meters or less.

        :param botengine:
        :param content: Dictionary of the following parameters:
            'x_min_meters' - Distance of the room to the left, minimum is -3.0 meters
            'x_max_meters' - Distance of the room to the right, maximum is 2.0 meters
            'y_min_meters' - Distance directly in front of the Vayyar Home, minimum is 0.3 meters (wall) or -2.5 meters (ceiling)
            'y_max_meters' - Distance across the room from the Vayyar Home, maximum is 4.0 meters (wall) or 2.5 meters (ceiling)
            'z_min_meters' - Doesn't matter, if the Vayyar Home is wall-mounted.
            'z_max_meters' - Doesn't matter, if the Vayyar Home is wall-mounted.
            'mounting_type' - Mounting type, 0 = wall, 1 = ceiling, 2 = ceiling45Deg, 3 = wall45Deg
            'sensor_height_m' - Height of the sensor in meters. Optional for mounting type 0 (wall).  Requried for all others.
            'near_exit' - True if this device is near an exit door
        """
        all_params = []


        x_min_meters = content.get('x_min_meters', -2.0)
        x_max_meters = content.get('x_max_meters', 2.0)
        y_min_meters = content.get('y_min_meters', 0.3)
        y_max_meters = content.get('y_max_meters', 4.0)
        z_min_meters = content.get('z_min_meters', 0)
        z_max_meters = content.get('z_max_meters', 2.0)
        mounting_type = content.get('mounting_type', 0)
        sensor_height_m = content.get('sensor_height_m', 1.5)
        near_exit = content.get('near_exit', False)

        self.near_exit = near_exit

        if mounting_type == RadarDevice.SENSOR_MOUNTING_WALL:
            # Guardrails for wall mount
            
            # Round to 3 decimal places
            x_min_meters = round(x_min_meters, 3)
            x_max_meters = round(x_max_meters, 3)
            y_max_meters = round(y_max_meters, 3)
            z_max_meters = round(z_max_meters, 3)

            # Constraints
            if x_min_meters < RadarDevice.X_MIN_METERS_WALL:
                x_min_meters = RadarDevice.X_MIN_METERS_WALL

            if x_max_meters > RadarDevice.X_MAX_METERS_WALL:
                x_max_meters = RadarDevice.X_MAX_METERS_WALL

            if y_max_meters > RadarDevice.Y_MAX_METERS_WALL:
                y_max_meters = RadarDevice.Y_MAX_METERS_WALL

            if y_min_meters < RadarDevice.Y_MIN_METERS_WALL:
                y_min_meters = RadarDevice.Y_MIN_METERS_WALL

            if z_max_meters > RadarDevice.Z_MAX_METERS_WALL:
                z_max_meters = RadarDevice.Z_MAX_METERS_WALL

            # Smallest boundary is 1 m^2
            if x_max_meters - x_min_meters < 1.0:
                x_max_meters = x_min_meters + 1.0
                
            if y_max_meters - y_min_meters < 1.0:
                y_max_meters = y_min_meters + 1.0

            # Fixed sensor height on walls
            all_params.append({
                "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                "value": 1.5
            })

        elif mounting_type == RadarDevice.SENSOR_MOUNTING_CEILING or mounting_type == RadarDevice.SENSOR_MOUNTING_CEILING_45_DEGREE:
            # Guardrails for ceiling mount

            # Round to 3 decimal places
            x_min_meters = round(x_min_meters, 3)
            x_max_meters = round(x_max_meters, 3)
            y_max_meters = round(y_max_meters, 3)
            y_min_meters = round(y_min_meters, 3)

            if x_min_meters < RadarDevice.X_MIN_METERS_CEILING:
                x_min_meters = RadarDevice.X_MIN_METERS_CEILING

            if x_max_meters > RadarDevice.X_MAX_METERS_CEILING:
                x_max_meters = RadarDevice.X_MAX_METERS_CEILING

            if y_min_meters < RadarDevice.Y_MIN_METERS_CEILING:
                y_min_meters = RadarDevice.Y_MIN_METERS_CEILING

            if y_max_meters > RadarDevice.Y_MAX_METERS_CEILING:
                y_max_meters = RadarDevice.Y_MAX_METERS_CEILING

            if sensor_height_m < RadarDevice.SENSOR_HEIGHT_MIN_METERS_CEILING:
                sensor_height_m = RadarDevice.SENSOR_HEIGHT_MIN_METERS_CEILING

            if sensor_height_m > RadarDevice.SENSOR_HEIGHT_MAX_METERS_CEILING:
                sensor_height_m = RadarDevice.SENSOR_HEIGHT_MAX_METERS_CEILING

            # Smallest boundary is 1 m^2
            if x_max_meters - x_min_meters < 1.0:
                x_max_meters = x_min_meters + 1.0
                
            if y_max_meters - y_min_meters < 1.0:
                y_max_meters = y_min_meters + 1.0

            # Variable sensor height on ceilings
            all_params.append({
                "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                "value": sensor_height_m
            })


        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
            "value": mounting_type
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_X_MIN,
            "value": x_min_meters
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_X_MAX,
            "value": x_max_meters
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN,
            "value": y_min_meters
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX,
            "value": y_max_meters
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN,
            "value": z_min_meters
        })

        all_params.append({
            "name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX,
            "value": z_max_meters
        })

        botengine.send_commands(self.device_id, all_params)

    def did_update_room_boundaries(self, botengine):
        """
        Determine if we updated the room boundaries in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the room boundaries in this execution
        """
        return any([param in self.last_updated_params for param in [
            RadarVayyarDevice.MEASUREMENT_NAME_X_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_X_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
        ]])


    def get_mounting_type(self, botengine):
        """
        Get the mounting type
        * 0 = wall
        * 1 = ceiling
        * 2 = ceiling @ 45-degree angle
        :param botengine: BotEngine environment
        :return: Mounting type
        """
        if RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING]) > 0:
                return self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][0]
        return RadarDevice.SENSOR_MOUNTING_WALL

    def get_room_boundaries(self, botengine):
        """
        Return the boundaries of this room in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        room = RadarDevice.get_room_boundaries(self, botengine)

        if RadarVayyarDevice.MEASUREMENT_NAME_X_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN]) > 0:
                room["x_min_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_X_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX]) > 0:
                room["x_max_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN]) > 0:
                room["y_min_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX]) > 0:
                room["y_max_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN]) > 0:
                room["z_min_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX]) > 0:
                room["z_max_meters"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING]) > 0:
                room["mounting_type"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT]) > 0:
                room["sensor_height_m"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT][0][0]
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT][0][1] > room["updated_ms"]:
                    room["updated_ms"] = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT][0][1]

        return room
    
    def get_room_boundaries_properties(self, botengine):
        """
        Return the boundaries of this room FROM THE DEVICE PROPERTY in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_room_boundaries_properties()")
        content = RadarDevice.get_room_boundaries_properties(self, botengine)
        
        # Backwards compability between "radar_room" and "vayyar_room" non-volatile memory
        if content == {
            "x_min_meters": RadarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarDevice.Z_MAX_METERS_WALL,
            "mounting_type": RadarDevice.SENSOR_MOUNTING_WALL,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": self.near_exit
        }:
            # Check if the room boundaries are defined in the non-volatile memory
            nv_room = botengine.get_state("vayyar_room")
            if nv_room is not None and self.device_id in nv_room:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("|get_room_boundaries_properties() Room has not been set, using non-volatile location state")
                content = nv_room[self.device_id]

        x_min = content.get('x_min_meters', RadarDevice.X_MIN_METERS_WALL)
        x_max = content.get('x_max_meters', RadarDevice.X_MAX_METERS_WALL)
        y_min = content.get('y_min_meters', RadarDevice.Y_MIN_METERS_WALL)
        y_max = content.get('y_max_meters', RadarDevice.Y_MAX_METERS_WALL)
        z_min = content.get('z_min_meters', RadarDevice.Z_MIN_METERS_WALL)
        z_max = content.get('z_max_meters', RadarDevice.Z_MAX_METERS_WALL)
        mounting_type = content.get('mounting_type', RadarDevice.SENSOR_MOUNTING_WALL)
        sensor_height_m = content.get('sensor_height_m', 1.5)
        updated_ms = content.get('updated_ms', 0)

        if RadarVayyarDevice.MEASUREMENT_NAME_X_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_X_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_X_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING][0][1]

        if RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT]) > 0:
                if self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT][0][1] > updated_ms:
                    updated_ms = self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT][0][1]

        room_boundaries = {
            "x_min_meters": x_min,
            "x_max_meters": x_max,
            "y_min_meters": y_min,
            "y_max_meters": y_max,
            "z_min_meters": z_min,
            "z_max_meters": z_max,
            "mounting_type": mounting_type,
            "sensor_height_m": sensor_height_m,
            "updated_ms": updated_ms,
            "near_exit": self.near_exit
        }
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_room_boundaries_properties() room_boundaries={}".format(room_boundaries))
        return room_boundaries

    def set_subregions(self, botengine, subregion_list):
        """
        Send a complete list of subregions to the device.

        * vyrc.trackerSubRegions = Array of objects (Tracker Sub Regions)
            * xMin = Default: 0
            * xMax = Default: 1
            * yMin = Default: 0.3
            * yMax = Default: 1
            * zMin = Default: 0
            * zMax = Default: 1.2
            * enterDuration = The minimum detection time required to establish presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
            * exitDuration = The minimum detection time required to establish non-presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
            * isFallingDetection = True - Detect fall in the subregion; False - Exclude fall in the subregion. Default: false
            * isPresenceDetection = Default: true
            * isLowSnr = allows for better tracking of targets in a subregion with lower energy (low SNR). Default: true
            * isDoor = up to two subregions can be configured as doors by setting isDoor to True. When enableDoorEvents is true, isLowSNR must be set to false. Default: false
            * name = Meaningful name of the subregion, e.g. Bed / Door / Toilet

        :param botengine: BotEngine environment
        :param subregion_list: Correctly formatted list of sub-regions
        """
        import json
        botengine.send_command(self.device_id, RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS, json.dumps(subregion_list, separators=(',', ':')))

    def did_update_subregions(self, botengine):
        """
        Did this Vayyar device update subregions
        :param botengine:
        :return:
        """
        return RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS in self.last_updated_params
    
    def get_subregions(self, botengine):
        """
        Get a list of subregions reported by the device, if there are any.
        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        return self.get_raw_subregions(botengine)

    def get_raw_subregions(self, botengine):
        """
        Get a list of subregions reported by the device, if there are any.

        A subregion list looks like this:
        * vyrc.trackerSubRegions = Array of objects (Tracker Sub Regions)
            * xMin = Default: 0
            * xMax = Default: 1
            * yMin = Default: 0.3
            * yMax = Default: 1
            * zMin = Default: 0
            * zMax = Default: 1.2
            * enterDuration = The minimum detection time required to establish presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
            * exitDuration = The minimum detection time required to establish non-presence in the subregion, in seconds. Note: This parameter does not influence the time of Door Events (V40 and above). Default: 120
            * isFallingDetection = True - Detect fall in the subregion; False - Exclude fall in the subregion. Default: false
            * isPresenceDetection = Default: true
            * isLowSnr = allows for better tracking of targets in a subregion with lower energy (low SNR). Default: true
            * isDoor = up to two subregions can be configured as doors by setting isDoor to True. When enableDoorEvents is true, isLowSNR must be set to false. Default: false
            * name = Meaningful name of the subregion, e.g. Bed / Door / Toilet

        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        import json
        if RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS in self.measurements:
            if len(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS]) > 0:
                try:
                    return json.loads(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS][0][0])
                except:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning("|get_raw_subregions() Couldn't load tracker subregion from JSON: {}".format(self.measurements[RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS][0][0]))
                    pass

        return []
    
    def get_subregion_index(self, botengine, subregion):
        """
        Return the index of a locally stored subregion represented on the device.
        :param botengine: BotEngine environment
        :param subregion: Subregion object
        :return: Index of the subregion, or None if it is not stored on the device.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">get_subregion_index() device_id={} subregion={}".format(self.device_id, subregion))

        is_occupied = None

        for idx, raw_subregion in enumerate(self.get_raw_subregions(botengine)):
            if raw_subregion.get("name") == subregion.get("name") and \
                raw_subregion.get("xMin") == subregion.get("x_min_meters") and \
                raw_subregion.get("xMax") == subregion.get("x_max_meters") and \
                raw_subregion.get("yMin") == subregion.get("y_min_meters") and \
                raw_subregion.get("yMax") == subregion.get("y_max_meters"):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_subregion_index() device_id={} index={}".format(self.device_id, idx))
                return idx

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<get_subregion_index() device_id={} index={}".format(self.device_id, None))
        return None