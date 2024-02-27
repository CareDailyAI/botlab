'''
Created on February 11, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import signals.vayyar as vayyar
import utilities.utilities as utilities

# We had established code to avoid going all the way to the wall, but this caused interferences between
# subregions and the arena where subregions were not also adjusted to the arena side. This caused some
# kinds of false positive presence detects, apparently, so we're backing this feature off for now.
WALL_PADDING_M = 0

class VayyarDevice(Device):
    """
    Vayyar Home Device
    """
    # Parameters
    MEASUREMENT_NAME_FALL_STATUS = "fallStatus"
    MEASUREMENT_NAME_OCCUPANCY = "occupancy"
    MEASUREMENT_NAME_OCCUPANCY_TARGET = "occupancyTarget"
    MEASUREMENT_NAME_OCCUPANCY_MAP = "occupancyMap"
    MEASUREMENT_NAME_FALL_LEARNING = "fallLearning"

    # Measurement parameters list for machine learning data extraction
    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_OCCUPANCY_TARGET,
        MEASUREMENT_NAME_OCCUPANCY_MAP,
        MEASUREMENT_NAME_OCCUPANCY
    ]

    # Fall Status
    FALL_STATUS_DETECTED = "fall_detected"
    FALL_STATUS_CONFIRMED = "fall_confirmed"
    FALL_STATUS_CALLING = "calling"
    FALL_STATUS_CANCELLED = "canceled"
    FALL_STATUS_FINISHED = "finished"
    FALL_STATUS_EXIT = "fall_exit"

    # Min and max values
    X_MIN_METERS_WALL = -2.5
    X_MAX_METERS_WALL = 2.5
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

    # Behavior ID's
    BEHAVIOR_TYPE_BEDROOM = 0
    BEHAVIOR_TYPE_BATHROOM = 1
    BEHAVIOR_TYPE_LIVINGROOM = 2
    BEHAVIOR_TYPE_KITCHEN = 3
    BEHAVIOR_TYPE_OTHER = 4

    # Mounting options
    SENSOR_MOUNTING_WALL = 0
    SENSOR_MOUNTING_CEILING = 1
    SENSOR_MOUNTING_CEILING_45_DEGREE = 2

    # Maximum allowable subregions
    MAXIMUM_SUBREGIONS = 4

    # Low signal strength warning threshold
    LOW_RSSI_THRESHOLD = -75

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
        Device.__init__(self, botengine, location_object, device_id, device_type, device_description, precache_measurements=precache_measurements)

        # Information (changes quickly): Total occupant information as measured and updated by a supporting microservice (location_vayyarsubregion_microservice)
        self.information_total_occupants = 0

        # Knowledge (changes more slowly): Total occupants knowledge as measured and updated by a supporting microservice (device_vayyar
        self.knowledge_total_occupants = 0

        # Count of times a target measurement has detected a fall on this device.
        # Every fall detect from a target increments this value to the MAXIMUM_FALL_COUNT
        # Every non-fall target measurement decrements the count.
        # This is used like a 'capacitor' of fall events, giving us confidence to call for help or that a person is still on the ground.
        # NOTE: Deprecated 9/29/22.  Falls are directly aligned with the "calling" fall_status measurement.  Logic is repurposed to measure stability events.  See `stability_event_count`
        self.fall_count = 0

        # Count of times a target measurement has detected a stability event on this device.
        # Every fall detect from a target increments this value to the MAXIMUM_STABILITY_EVENT_COUNT
        # Every non-stability-event target measurement decrements the count.
        # This is used like a 'capacitor' of stability events, giving us confidence to declare that the person has stability issues and may be a precurser to a fall event.
        self.stability_event_count = 0

        # True if this device is declared to be near an exit door.
        self.near_exit = False

        # Summary of existing subregions - { "unique_id": (context_id, name), ... }
        self.subregions = {}

        # List of occupied subregion information (high frequency / not validated) - [ "unique_id", ... ]
        self.information_occupied_subregions = []

        # List of occupied subregion knowledge (low frequency / higher reliability) - [ "unique_id", ... ]
        self.knowledge_occupied_subregions = []

        # True if the device is in learning mode
        self.learning_mode_status = VayyarDevice.LEARNING_MODE_REST

        # Default Behavior
        self.goal_id = VayyarDevice.BEHAVIOR_TYPE_OTHER

    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        Device.new_version(self, botengine)
        
        # Added May 18, 2022
        if not hasattr(self, 'learning_mode_status'):
            self.learning_mode_status = VayyarDevice.LEARNING_MODE_REST

        # Added November 24, 2021
        if not hasattr(self, 'information_total_occupants'):
            self.information_total_occupants = 0

        # Added December 14, 2021
        if not hasattr(self, 'knowledge_total_occupants'):
            self.knowledge_total_occupants = 0

        # Added November 24, 2021
        if not hasattr(self, 'fall_count'):
            self.fall_count = 0

        # Added September 29, 2022
        if not hasattr(self, 'stability_event_count'):
            self.stability_event_count = 0

        # Added November 30, 2021
        if not hasattr(self, 'near_exit'):
            self.near_exit = False

        # Added January 17, 2022
        if not hasattr(self, 'subregions'):
            self.subregions = {}

        # Added January 17, 2022
        if not hasattr(self, 'information_occupied_subregions'):
            self.information_occupied_subregions = []

        # Added January 17, 2022
        if not hasattr(self, 'knowledge_occupied_subregions'):
            self.knowledge_occupied_subregions = []


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

    def is_in_bedroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bedroom
        """
        if self.goal_id == VayyarDevice.BEHAVIOR_TYPE_BEDROOM:
            return True
        
        bedroom_names = [_('bed'), _('bett'), _('bdrm'), _('moms room'), _('dads room'), _('mom\'s room'), _('dad\'s room')]

        for name in bedroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, 'bedroom') or self.is_goal_id(VayyarDevice.BEHAVIOR_TYPE_BEDROOM)

    def is_in_bathroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bathroom
        """
        if self.goal_id == VayyarDevice.BEHAVIOR_TYPE_BATHROOM:
            return True

        bathroom_names = [_('schlaf'), _('bath'), _('toilet'), _('shower'), _('powder')]

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, 'bathroom') or self.is_goal_id(VayyarDevice.BEHAVIOR_TYPE_BATHROOM)

    #===========================================================================
    # Attributes
    #===========================================================================
    def did_change_fall_status(self, botengine):
        """
        Did the fall status get updated
        :param botengine:
        :return: True if the fall status changed
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.last_updated_params:
                return True

        return False

    def did_update_leds(self, botengine):
        """
        :param botengine:
        :return: True if this Vayyar device updated its leds
        """
        if "vyrc.ledMode" in self.measurements:
            if "vyrc.ledMode" in self.last_updated_params:
                return True

        return False

    def get_leds(self, botengine):
        """
        :param botengine:
        :return: LED status
        """
        if "vyrc.ledMode" in self.measurements:
            if len(self.measurements["vyrc.ledMode"]) > 0:
                return self.measurements["vyrc.ledMode"][0][0]

        return None

    def did_update_volume(self, botengine):
        """
        :param botengine:
        :return: True if this Vayyar device updated its volume
        """
        if "vyrc.volume" in self.measurements:
            if "vyrc.volume" in self.last_updated_params:
                return True

        return False

    def get_volume(self, botengine):
        """
        :param botengine:
        :return: Volume
        """
        if "vyrc.volume" in self.measurements:
            if len(self.measurements["vyrc.volume"]) > 0:
                return self.measurements["vyrc.volume"][0][0]

        return None

    def get_telemetry_policy(self, botengine):
        """
        :param botengine:
        :return: Volume
        """
        if "vyrc.telemetryPolicy" in self.measurements:
            if len(self.measurements["vyrc.telemetryPolicy"]) > 0:
                return self.measurements["vyrc.telemetryPolicy"][0][0]

        return None
        
    def get_fall_status(self, botengine):
        """
        Retrieve the most recent fall status value
        :param botengine:
        :return:
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            return self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0][0]
        return None
        
    def get_previous_fall_status(self, botengine):
        """
        Retrieve the most recent fall status value
        :param botengine:
        :return:
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements and len(self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS]) > 1:
            return self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS][1][0]
        return None

    def is_detecting_stability_event(self, botengine):
        """
        Is this Vayyar device detecting any kind of stability event
        :param botengine: BotEngine
        :return: True if this Vayyar device is detecting a stability event (fall_confirmed or fall_detected)
        """
        status = self.get_fall_status(botengine)
        botengine.get_logger().debug(utilities.Color.RED + "is_detecting_stability_event: status={} learning_mode_status={}".format(status, self.learning_mode_status) + utilities.Color.END)
        if status is not None and not self.learning_mode_status != VayyarDevice.LEARNING_MODE_DONE:
            return status == VayyarDevice.FALL_STATUS_CONFIRMED or status == VayyarDevice.FALL_STATUS_DETECTED
        return False

    def is_detecting_fall(self, botengine):
        """
        Is this Vayyar device detecting any kind of fall
        :param botengine: BotEngine
        :return: True if this Vayyar device is detecting a fall (calling)
        """
        status = self.get_fall_status(botengine)
        if status is not None and not self.learning_mode_status != VayyarDevice.LEARNING_MODE_DONE:
            return status == VayyarDevice.FALL_STATUS_CALLING
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
        botengine.get_logger().debug(utilities.Color.RED + "did_stop_detecting_fall: status={} previous_status={} did_update={} learning_mode_status={}".format(status, previous_status, did_update, self.learning_mode_status) + utilities.Color.END)
        if status is not None and previous_status is not None and did_update and not self.learning_mode_status != VayyarDevice.LEARNING_MODE_DONE:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return status == VayyarDevice.FALL_STATUS_FINISHED and previous_status == VayyarDevice.FALL_STATUS_CALLING

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
        botengine.get_logger().debug(utilities.Color.RED + "did_cancel_confirmed_fall: status={} previous_status={} did_update={} learning_mode_status={}".format(status, previous_status, did_update, self.learning_mode_status) + utilities.Color.END)
        if status is not None and previous_status is not None and did_update and not self.learning_mode_status != VayyarDevice.LEARNING_MODE_DONE:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return status == VayyarDevice.FALL_STATUS_CANCELLED and previous_status == VayyarDevice.FALL_STATUS_CONFIRMED

        return False

    def did_update_fall_learning(self, botengine):
        """
        Check if fall learning has changed
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        return VayyarDevice.MEASUREMENT_NAME_FALL_LEARNING in self.last_updated_params

    def get_fall_learning(self, botengine):
        """
        Get the current fall learning status
        :param botengine:
        :return:
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_LEARNING in self.measurements:
            return self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_LEARNING][0][0]
        return None

    def did_update_occupancy_targets(self, botengine):
        """
        Did we get new occupancy target data
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        return VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in self.last_updated_params

    def get_occupancy_targets(self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None):
        """
        Get the current occupant targets the Vayyar Home device is tracking and their positions

        You can optionally pass in a range of time to extract from the locally available 1-hour cache, with oldest_timestamp_ms and newest_timestamp_ms.

        If a range (both oldest and newest timestamp) is not specified, then this will only return the latest measurement and will ignore targets that are older than 30 minutes or from a disconnected device

        :param botengine:
        :param oldest_timestamp_ms:
        :param newest_timestamp_ms:
        :return: Dictionary of occupancy targets of the form { timestamp_ms : { 'target_id': { 'x': x, 'y': y, 'z': z } }, ... }
        """
        targets = {}

        if self.is_connected:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in self.measurements:
                botengine.get_logger().debug("get_occupancy_targets: pure targets={}".format(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET]))
                extract_multiple = newest_timestamp_ms is not None and oldest_timestamp_ms is not None

                if newest_timestamp_ms is None:
                    newest_timestamp_ms = botengine.get_timestamp()

                if oldest_timestamp_ms is None:
                    oldest_timestamp_ms = newest_timestamp_ms - (utilities.ONE_MINUTE_MS * 30)

                for t in self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET]:
                    if t[1] < oldest_timestamp_ms:
                        break

                    if t[1] > newest_timestamp_ms:
                        continue

                    targets[t[1]] = self._extract_targets(t[0])

                    if not extract_multiple:
                        break
        botengine.get_logger().info("get_occupancy_targets: targets={}".format(targets))
        return targets

    def get_newest_targets(self, botengine):
        """
        Retrieve only the current targets, without organizing by timestamp.
        { 'target_id': { 'x': x, 'y': y, 'z': z } }
        :param botengine: BotEngine environment
        :return: { 'target_id': { 'x': x, 'y': y, 'z': z } }
        """
        targets = self.get_occupancy_targets(botengine)
        for timestamp_ms in targets:
            return targets[timestamp_ms]
        return {}

    def print_occupant_positions(self, botengine):
        """
        Print the occupant position to the CLI
        :param botengine:
        """
        targets = self.get_occupancy_targets(botengine)
        for timestamp_ms in targets:
            for target_id in targets[timestamp_ms]:
                botengine.get_logger().info(utilities.Color.GREEN + "VayyarDevice target {}: x = {} inches; y = {} inches".format(target_id, round(targets[timestamp_ms][target_id]['x'] * 0.393701, 1), round(targets[timestamp_ms][target_id]['y'] * 0.393701, 1)) + utilities.Color.END)

    # def total_occupants(self, botengine):
    #     """
    #     Get the current total occupants (0, 1, or "more than one" (2+))
    #     :param botengine:
    #     :return: 0, 1, or 2+
    #     """
    #     total = 0
    #     if not self.is_detecting_occupancy(botengine):
    #         # If the device can update us that occupancy is no longer detected in the room, then there's nobody there.
    #         # But we don't trust this - because sometimes we've observed nobody in the room
    #         # and no targets getting updated, but the occupancy parameter remained a '1'.
    #         # So we do another double check below on the timestamp on the most recent target detection.
    #         return 0
    #
    #     targets = self.get_occupancy_targets(botengine)
    #     if len(targets) > 0:
    #         # There's at least a measurement captured.
    #         for timestamp_ms in targets:
    #             if timestamp_ms > botengine.get_timestamp() - utilities.ONE_SECOND_MS * 15:
    #                 total = len(targets[timestamp_ms])
    #                 if total > 2:
    #                     total = 2
    #     return total

    def need_start_learning(self, botengine):
        return self.learning_mode_status == VayyarDevice.LEARNING_MODE_REST

    def did_start_detecting_motion(self, botengine):
        """
        Helpful for translation to existing motion sensor functionality.

        Recommend using signals/motion.py with the appropriate microservice driving those signals for more serious motion detection work.

        :param botengine: BotEngine
        :return: True if the Vayyar Home did start detecting occupancy.
        """
        return self.did_start_detecting_occupancy(botengine)

    def is_detecting_occupancy(self, botengine):
        """
        True if this device is detecting an occupant, as indicated by the 'occupancy' parameter and not our targets
        :param botengine:
        :return:
        """
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                return self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 1
        return False

    def did_start_detecting_occupancy(self, botengine):
        """
        Did the Vayyar Home device start detecting occupancy in this room
        :param botengine:
        :return: True if occupants have entered the room
        """
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 1

        return False

    def did_stop_detecting_occupancy(self, botengine):
        """
        Did the Vayyar Home device stop detecting occupancy in this room
        :param botengine:
        :return: True if occupants have left the room
        """
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 0

        return False

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

    def did_update_firmware(self, botengine):
        """
        Did the device firmware get updated?
        :param botengine:
        :return:
        """
        if hasattr(self, "firmware"):
            if "firmware" in self.last_updated_params:
                return True

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
        :param sensitivity: 1=low; 2=normal
        """
        botengine.send_command(self.device_id, "vyrc.fallingSensitivity", int(sensitivity))

    def set_alert_delay_s(self, botengine, alert_delay_s):
        """
        Set the delay from the 'confirmed' state to 'calling' state, in seconds.

        :param botengine: BotEngine environment
        :param alert_delay_s: Alert delay in seconds. 15-30 is recommended.
        """
        botengine.send_command(self.device_id, "vyrc.confirmedToAlertTimeoutSec", int(alert_delay_s))

    def set_led_mode(self, botengine, led_mode):
        """
        Set the LED mode
        :param botengine: BotEngine environment
        :param led_mode: 0 = all off; 1 = on
        """
        botengine.send_command(self.device_id, "vyrc.ledMode", int(led_mode))

    def set_volume(self, botengine, volume):
        """
        Set the volume level from 0 - 100
        :param botengine: BotEngine environment
        :param volume: 0 = silence; 100 = buzzer on
        :return:
        """
        botengine.send_command(self.device_id, "vyrc.volume", int(volume))

    def set_telemetry_policy(self, botengine, telemetry_policy):
        """
        Set the telemetry policy
        :param botengine: BotEngine environment
        :param telemetry_policy: 0 is off; 1 is on; 2 is only on falls (default)
        """
        botengine.send_command(self.device_id, "vyrc.telemetryPolicy", int(telemetry_policy))

    def set_learning_mode(self, botengine, learning_mode):
        """
        Set end of learning mode in milliseconds.
        :param botengine: BotEngine environment
        :param learning_mode: True/False on/off
        """
        if learning_mode:
            if self.learning_mode_status != VayyarDevice.LEARNING_MODE_GOING:
                self.learning_mode_status = VayyarDevice.LEARNING_MODE_GOING
                end_timestamp_ms = botengine.get_timestamp() + (2 * utilities.ONE_WEEK_MS)

                botengine.send_command(self.device_id, "vyrc.learningModeEnd", end_timestamp_ms)

        else:
            self.learning_mode_status = VayyarDevice.LEARNING_MODE_DONE

    def set_reporting_rate_ms(self, botengine, reporting_rate_ms):
        """
        Set the presence reporting rate in milliseconds.

        :param botengine: BotEngine environment
        :param reporting_rate_ms: Reporting rate in milliseconds
        """
        botengine.send_command(self.device_id, "vyrc.presenceReportMinRateMills", reporting_rate_ms)

    def set_silent_mode(self, botengine, silent_mode):
        """
        Set silent mode
        :param botengine: BotEngine
        :param silent_mode: True or False
        """
        botengine.send_command(self.device_id, "vyrc.silentMode", silent_mode)

    def set_target_change_threshold_m(self, botengine, target_change_threshold_m):
        """
        Set the occupancy target change threshold in meters (i.e. 0.2)
        :param botengine: BotEngine
        :param target_change_threshold_m: Threshold in meters (i.e. 0.2)
        """
        botengine.send_command(self.device_id, "vyrc.targetPositionChangeThresholdMeters", float(target_change_threshold_m))

    def set_falling_mitigator(self, botengine, falling_mitigator):
        """
        Set the falling mitigator
        :param botengine: BotEngine
        :param falling_mitigator: True or False
        """
        botengine.send_command(self.device_id, "vyrc.fallingMitigatorEnabled", falling_mitigator)

    def set_ceiling_mount(self, botengine, sensor_height_m=2.0):
        """
        Configure this Vayyar Home for a ceiling mount
        :param botengine: BotEngine environment
        :param sensor_height: Sensor height in meters (for example 2.0 - 3.0 meters)
        """
        all_params = []

        all_params.append({
            "name": "vyrc.sensorMounting",
            "value": VayyarDevice.SENSOR_MOUNTING_CEILING
        })

        all_params.append({
            "name": "vyrc.sensorHeight",
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
            "name": "vyrc.sensorMounting",
            "value": VayyarDevice.SENSOR_MOUNTING_WALL
        })

        all_params.append({
            "name": "vyrc.sensorHeight",
            "value": 1.5
        })

        botengine.send_commands(self.device_id, all_params)

    def set_room_boundaries(self, botengine, x_min_meters=-2.0, x_max_meters=2.0, y_min_meters=0.3, y_max_meters=4.0, z_min_meters=0, z_max_meters=2.0, mounting_type=0, sensor_height_m=1.5, near_exit=False):
        """
        Set the boundaries of the room. Measurements are in meters.

        X-axis is along the wall the Vayyar Home is attached to. The Vayyar Home is at 0.0.
        To the left of Vayyar Home (facing out into the room) are negative numbers, down to -1.9 meters.
        To the right of Vayyar Home are positive numbers, up to 1.9 meters.

        Y-axis is projecting out into the room. Again, the Vayyar Home is at 0.0.
        The farthest wall across from the Vayyar Home is y_max, and the largest value can be 3.9 meters.
        The nearest point the Vayyar Home can detect is 0.3 meters, which is y_min.

        Z-axis is useful if the Vayyar Home is mounted to the ceiling looking down.

        :param botengine:
        :param x_min_meters: Distance of the room to the left, minimum is -1.9 meters
        :param x_max_meters: Distance of the room to the right, maximum is 1.9 meters
        :param y_min_meters: Distance directly in front of the Vayyar Home, minimum is 0.3 (not 0)
        :param y_max_meters: Distance across the room from the Vayyar Home, maximum is 3.9 meters
        :param z_min_meters: Doesn't matter, if the Vayyar Home is wall-mounted.
        :param z_max_meters: Doesn't matter, if the Vayyar Home is wall-mounted.
        :param near_exit: True if this device is near an exit door
        """
        all_params = []

        self.near_exit = near_exit

        if mounting_type == VayyarDevice.SENSOR_MOUNTING_WALL:
            # Guardrails for wall mount
            if x_min_meters > 0:
                x_min_meters = -x_min_meters

            if x_max_meters < 0:
                x_max_meters = -x_max_meters

            if y_max_meters < 1.0:
                y_max_meters = 1.0

            x_min_meters = round(x_min_meters + WALL_PADDING_M, 3)
            x_max_meters = round(x_max_meters - WALL_PADDING_M, 3)
            y_max_meters = round(y_max_meters - WALL_PADDING_M, 3)
            z_max_meters = round(z_max_meters - WALL_PADDING_M, 3)

            if x_min_meters < VayyarDevice.X_MIN_METERS_WALL:
                x_min_meters = VayyarDevice.X_MIN_METERS_WALL

            if x_max_meters > VayyarDevice.X_MAX_METERS_WALL:
                x_max_meters = VayyarDevice.X_MAX_METERS_WALL

            if y_max_meters > VayyarDevice.Y_MAX_METERS_WALL:
                y_max_meters = VayyarDevice.Y_MAX_METERS_WALL

            if y_min_meters < VayyarDevice.Y_MIN_METERS_WALL:
                y_min_meters = VayyarDevice.Y_MIN_METERS_WALL

            if z_max_meters > VayyarDevice.Z_MAX_METERS_WALL:
                z_max_meters = VayyarDevice.Z_MAX_METERS_WALL

            # Fixed sensor height on walls
            all_params.append({
                "name": "vyrc.sensorHeight",
                "value": 1.5
            })

        elif mounting_type == VayyarDevice.SENSOR_MOUNTING_CEILING or mounting_type == VayyarDevice.SENSOR_MOUNTING_CEILING_45_DEGREE:
            # Guardrails for ceiling mount
            if x_min_meters > 0:
                x_min_meters = -x_min_meters

            if x_max_meters < 0:
                x_max_meters = -x_max_meters

            if y_min_meters > 0:
                y_min_meters = -y_min_meters

            if y_max_meters < 0:
                y_max_meters = -y_max_meters

            x_min_meters = round(x_min_meters + WALL_PADDING_M, 3)
            x_max_meters = round(x_max_meters - WALL_PADDING_M, 3)
            y_max_meters = round(y_max_meters - WALL_PADDING_M, 3)
            y_min_meters = round(y_min_meters + WALL_PADDING_M, 3)

            if x_min_meters < VayyarDevice.X_MIN_METERS_CEILING:
                x_min_meters = VayyarDevice.X_MIN_METERS_CEILING

            if x_max_meters > VayyarDevice.X_MAX_METERS_CEILING:
                x_max_meters = VayyarDevice.X_MAX_METERS_CEILING

            if y_min_meters < VayyarDevice.Y_MIN_METERS_CEILING:
                y_min_meters = VayyarDevice.Y_MIN_METERS_CEILING

            if y_max_meters > VayyarDevice.Y_MAX_METERS_CEILING:
                y_max_meters = VayyarDevice.Y_MAX_METERS_CEILING

            if sensor_height_m < VayyarDevice.SENSOR_HEIGHT_MIN_METERS_CEILING:
                sensor_height_m = VayyarDevice.SENSOR_HEIGHT_MIN_METERS_CEILING

            if sensor_height_m > VayyarDevice.SENSOR_HEIGHT_MAX_METERS_CEILING:
                sensor_height_m = VayyarDevice.SENSOR_HEIGHT_MAX_METERS_CEILING

            # Variable sensor height on ceilings
            all_params.append({
                "name": "vyrc.sensorHeight",
                "value": sensor_height_m
            })


        all_params.append({
            "name": "vyrc.sensorMounting",
            "value": mounting_type
        })

        all_params.append({
            "name": "vyrc.xMin",
            "value": x_min_meters
        })

        all_params.append({
            "name": "vyrc.xMax",
            "value": x_max_meters
        })

        all_params.append({
            "name": "vyrc.yMin",
            "value": y_min_meters
        })

        all_params.append({
            "name": "vyrc.yMax",
            "value": y_max_meters
        })

        all_params.append({
            "name": "vyrc.zMin",
            "value": z_min_meters
        })

        all_params.append({
            "name": "vyrc.zMax",
            "value": z_max_meters
        })

        all_params.append({
            "name": "near_exit",
            "value": near_exit
        })

        botengine.send_commands(self.device_id, all_params)

    def did_update_room_boundaries(self, botengine):
        """
        Determine if we updated the room boundaries in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the room boundaries in this execution
        """
        return "vyrc.xMin" in self.last_updated_params or "vyrc.xMax" in self.last_updated_params or "vyrc.yMin" in self.last_updated_params or "vyrc.yMax" in self.last_updated_params or "vyrc.zMin" in self.last_updated_params or "vyrc.zMax" in self.last_updated_params or "vyrc.zMin" in self.last_updated_params or "vyrc.sensorMounting" in self.last_updated_params

    def get_mounting_type(self, botengine):
        """
        Get the mounting type
        * 0 = wall
        * 1 = ceiling
        * 2 = ceiling @ 45-degree angle
        :param botengine: BotEngine environment
        :return: Mounting type
        """
        if "vyrc.sensorMounting" in self.measurements:
            if len(self.measurements["vyrc.sensorMounting"]) > 0:
                return self.measurements["vyrc.sensorMounting"][0][0]
        return VayyarDevice.SENSOR_MOUNTING_WALL

    def get_room_boundaries(self, botengine):
        """
        Return the boundaries of this room in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        x_min = VayyarDevice.X_MIN_METERS_WALL
        x_max = VayyarDevice.X_MAX_METERS_WALL
        y_min = VayyarDevice.Y_MIN_METERS_WALL
        y_max = VayyarDevice.Y_MAX_METERS_WALL
        z_min = VayyarDevice.Z_MIN_METERS_WALL
        z_max = VayyarDevice.Z_MAX_METERS_WALL
        mounting_type = 0
        sensor_height_m = 1.5
        updated_ms = 0

        if "vyrc.xMin" in self.measurements:
            if len(self.measurements["vyrc.xMin"]) > 0:
                x_min = self.measurements["vyrc.xMin"][0][0]
                if self.measurements["vyrc.xMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.xMin"][0][1]

        if "vyrc.xMax" in self.measurements:
            if len(self.measurements["vyrc.xMax"]) > 0:
                x_max = self.measurements["vyrc.xMax"][0][0]
                if self.measurements["vyrc.xMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.xMax"][0][1]

        if "vyrc.yMin" in self.measurements:
            if len(self.measurements["vyrc.yMin"]) > 0:
                y_min = self.measurements["vyrc.yMin"][0][0]
                if self.measurements["vyrc.yMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.yMin"][0][1]

        if "vyrc.yMax" in self.measurements:
            if len(self.measurements["vyrc.yMax"]) > 0:
                y_max = self.measurements["vyrc.yMax"][0][0]
                if self.measurements["vyrc.yMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.yMax"][0][1]

        if "vyrc.zMin" in self.measurements:
            if len(self.measurements["vyrc.zMin"]) > 0:
                z_min = self.measurements["vyrc.zMin"][0][0]
                if self.measurements["vyrc.zMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.zMin"][0][1]

        if "vyrc.zMax" in self.measurements:
            if len(self.measurements["vyrc.zMax"]) > 0:
                z_max = self.measurements["vyrc.zMax"][0][0]
                if self.measurements["vyrc.zMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.zMax"][0][1]

        if "vyrc.sensorMounting" in self.measurements:
            if len(self.measurements["vyrc.sensorMounting"]) > 0:
                mounting_type = self.measurements["vyrc.sensorMounting"][0][0]
                if self.measurements["vyrc.sensorMounting"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.sensorMounting"][0][1]

        if "vyrc.sensorHeight" in self.measurements:
            if len(self.measurements["vyrc.sensorHeight"]) > 0:
                sensor_height_m = self.measurements["vyrc.sensorHeight"][0][0]
                if self.measurements["vyrc.sensorHeight"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.sensorHeight"][0][1]

        # Undo our wall padding
        if mounting_type == VayyarDevice.SENSOR_MOUNTING_WALL:
            x_min = round(x_min - WALL_PADDING_M, 3)
            x_max = round(x_max + WALL_PADDING_M, 3)
            y_max = round(y_max + WALL_PADDING_M, 3)
            z_max = round(z_max + WALL_PADDING_M, 3)

        else:
            x_min = round(x_min - WALL_PADDING_M, 3)
            x_max = round(x_max + WALL_PADDING_M, 3)
            y_max = round(y_max + WALL_PADDING_M, 3)
            y_min = round(y_min - WALL_PADDING_M, 3)

        return {
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
    
    def get_room_boundaries_properties(self, botengine):
        """
        Return the boundaries of this room FROM THE DEVICE PROPERTY in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        x_min = VayyarDevice.X_MIN_METERS_WALL
        x_max = VayyarDevice.X_MAX_METERS_WALL
        y_min = VayyarDevice.Y_MIN_METERS_WALL
        y_max = VayyarDevice.Y_MAX_METERS_WALL
        z_min = VayyarDevice.Z_MIN_METERS_WALL
        z_max = VayyarDevice.Z_MAX_METERS_WALL
        mounting_type = 0
        sensor_height_m = 1.5
        updated_ms = 0
        content = None

        device_properties = botengine.get_device_property(self.device_id, "room")

        import json
        for device_property in device_properties:
            property_name = device_property['name']
            if property_name == 'room':
                content = json.loads(device_property['value'])
                break

        if content is None:
            # Check if the room boundaries are defined in the non-volatile memory
            nv_room = botengine.get_state("vayyar_room")
            if nv_room is not None and self.device_id in nv_room:
                botengine.get_logger().info("VayyarDevice.get_room_boundaries_properties() Room has not been set, using non-volatile location state")
                content = nv_room[self.device_id]

        if content is not None:
            if 'x_min_meters' in content:
                x_min = content['x_min_meters']

            if 'x_max_meters' in content:
                x_max = content['x_max_meters']

            if 'y_min_meters' in content:
                y_min = content['y_min_meters']

            if 'y_max_meters' in content:
                y_max = content['y_max_meters']

            if 'z_min_meters' in content:
                z_min = content['z_min_meters']

            if 'z_max_meters' in content:
                z_max = content['z_max_meters']

            if 'mounting_type' in content:
                mounting_type = content['mounting_type']

            if 'sensor_height_m' in content:
                sensor_height_m = content['sensor_height_m']

        if "vyrc.xMin" in self.measurements:
            if len(self.measurements["vyrc.xMin"]) > 0:
                if self.measurements["vyrc.xMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.xMin"][0][1]

        if "vyrc.xMax" in self.measurements:
            if len(self.measurements["vyrc.xMax"]) > 0:
                if self.measurements["vyrc.xMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.xMax"][0][1]

        if "vyrc.yMin" in self.measurements:
            if len(self.measurements["vyrc.yMin"]) > 0:
                if self.measurements["vyrc.yMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.yMin"][0][1]

        if "vyrc.yMax" in self.measurements:
            if len(self.measurements["vyrc.yMax"]) > 0:
                if self.measurements["vyrc.yMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.yMax"][0][1]

        if "vyrc.zMin" in self.measurements:
            if len(self.measurements["vyrc.zMin"]) > 0:
                if self.measurements["vyrc.zMin"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.zMin"][0][1]

        if "vyrc.zMax" in self.measurements:
            if len(self.measurements["vyrc.zMax"]) > 0:
                if self.measurements["vyrc.zMax"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.zMax"][0][1]

        if "vyrc.sensorMounting" in self.measurements:
            if len(self.measurements["vyrc.sensorMounting"]) > 0:
                if self.measurements["vyrc.sensorMounting"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.sensorMounting"][0][1]

        if "vyrc.sensorHeight" in self.measurements:
            if len(self.measurements["vyrc.sensorHeight"]) > 0:
                if self.measurements["vyrc.sensorHeight"][0][1] > updated_ms:
                    updated_ms = self.measurements["vyrc.sensorHeight"][0][1]

        # Undo our wall padding
        if mounting_type == VayyarDevice.SENSOR_MOUNTING_WALL:
            x_min = round(x_min - WALL_PADDING_M, 3)
            x_max = round(x_max + WALL_PADDING_M, 3)
            y_max = round(y_max + WALL_PADDING_M, 3)
            z_max = round(z_max + WALL_PADDING_M, 3)

        else:
            x_min = round(x_min - WALL_PADDING_M, 3)
            x_max = round(x_max + WALL_PADDING_M, 3)
            y_max = round(y_max + WALL_PADDING_M, 3)
            y_min = round(y_min - WALL_PADDING_M, 3)

        return {
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

    def record_subregion(self, botengine, unique_id, context_id, name):
        """
        Record the existence of a subregion without saving it to the device, so
        microservices can quickly check if we have a particular subregion defined.
        :param botengine: BotEngine
        :param unique_id: Unique ID to add/update
        :param context_id: Context ID of the subregion
        :param name: Name of the subregion
        """
        botengine.get_logger().info("VayyarDevice '{}': Recording subregion - unique_id={}; context_id={}; name={}".format(self.description, unique_id, context_id, name))
        self.subregions[unique_id] = (context_id, name)

    def delete_recorded_subregions(self, botengine):
        """
        Delete a subregion record without saving it to the device.
        :param botengine: BotEngine
        :param unique_id: Unique ID to delete
        """
        self.subregions = {}

    def subregions_with_context(self, botengine, target_context_id):
        """
        Check if this device has a subregion with the given context
        :param botengine: BotEngine
        :param context_id: Context ID
        :return: List of tuples: [ (unique_id, context_id, name), ... ] or an empty list if there are no subregions defined with this same general context
        """
        return_list = []
        for unique_id in self.subregions:
            context_id, name = self.subregions[unique_id]
            if vayyar.is_same_general_context(target_context_id, context_id):
                return_list.append((unique_id, context_id, name))

        return return_list

    def record_occupied_subregion_information(self, botengine, unique_id, occupied):
        """
        Record information (high-frequency / lower accuracy) that a subregion is occupied
        :param botengine: BotEngine
        :param unique_id: Unique ID of the subregion
        :param occupied: True if the subregion is occupied
        """
        if occupied:
            if unique_id not in self.information_occupied_subregions:
                self.information_occupied_subregions.append(unique_id)
        else:
            if unique_id in self.information_occupied_subregions:
                self.information_occupied_subregions.remove(unique_id)

    def record_occupied_subregion_knowledge(self, botengine, unique_id, occupied):
        """
        Record knowledge (low-frequency / higher accuracy) that a subregion is occupied
        :param botengine: BotEngine
        :param unique_id: Unique ID of the subregion
        :param occupied: True if the subregion is occupied
        """
        if occupied:
            if unique_id not in self.knowledge_occupied_subregions:
                self.knowledge_occupied_subregions.append(unique_id)
        else:
            if unique_id in self.knowledge_occupied_subregions:
                self.knowledge_occupied_subregions.remove(unique_id)

    def is_in_shower(self, botengine):
        """
        Is a person in a shower subregion
        :param botengine: BotEngine
        :return: True if we have knowledge the person is in the shower
        """
        relevant_subregions = self.subregions_with_context(botengine, vayyar.SUBREGION_CONTEXT_WALK_IN_SHOWER)
        for (unique_id, context_id, name) in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def is_in_chair(self, botengine):
        """
        Is a person in a chair subregion
        :param botengine: BotEngine
        :return: True if we have knowledge the person is in the chair
        """
        relevant_subregions = self.subregions_with_context(botengine, vayyar.SUBREGION_CONTEXT_CHAIR)
        for (unique_id, context_id, name) in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def is_in_bed(self, botengine):
        """
        Is a person in a bed subregion
        :param botengine: BotEngine
        :return: True if we have knowledge the person is in the bed
        """
        relevant_subregions = self.subregions_with_context(botengine, vayyar.SUBREGION_CONTEXT_BED)
        for (unique_id, context_id, name) in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def set_subregions(self, botengine, subregion_list):
        """
        Send a complete list of subregions to the device.

        subregion_list format:
            [
                   {
                        "enterDuration": 1,
                        "exitDuration": 3,
                        "isFallingDetection": false,
                        "isPresenceDetection": true,
                        "xMax": 1,
                        "xMin": 0,
                        "yMax": 1,
                        "yMin": 0.3
                  }
            ]

        :param botengine: BotEngine environment
        :param subregion_list: Correctly formatted list of sub-regions
        """
        import json
        botengine.send_command(self.device_id, "vyrc.trackerSubRegions", json.dumps(subregion_list))

    def did_update_subregions(self, botengine):
        """
        Did this Vayyar device update subregions
        :param botengine:
        :return:
        """
        return "vyrc.trackerSubRegions" in self.last_updated_params

    def get_raw_subregions(self, botengine):
        """
        Get a list of subregions reported by the device, if there are any.

        A subregion list looks like this:  [{"xMin":-1.0,"xMax":1.0,"yMin":0.3,"yMax":1.0,"enterDuration":3,"exitDuration":3,"isFallingDetection":true,"isPresenceDetection":true}]

        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        import json
        if "vyrc.trackerSubRegions" in self.measurements:
            if len(self.measurements["vyrc.trackerSubRegions"]) > 0:
                try:
                    return json.loads(self.measurements["vyrc.trackerSubRegions"][0][0])
                except:
                    botengine.get_logger().warning("vayyar: Couldn't load tracker subregion from JSON: {}".format(self.measurements["vyrc.trackerSubRegions"][0][0]))
                    pass

        return None

    def did_subregion_occupancy_change(self, botengine):
        """
        Determine if subregion occupancy may have changed at all on this execution,
        as evidenced by receiving a new value for the 'occupancyMap' parameter.

        :param botengine: BotEngine environment
        :return: True if subregion occupancy may have been updated in this execution
        """
        return VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params

    def get_subregions_entered(self, botengine):
        """
        Get a list of subregion indices that were just entered.
        This does not provide context.
        :param botengine: BotEngine environment
        :return: List of subregion indices that were just entered, like [0, 2, 3] or [].
        """
        entered = []
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
                if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP]) > 1:
                    m_new = self._to_subregion_indices(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0][0])
                    m_old = self._to_subregion_indices(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][1][0])
                    botengine.get_logger().info("vayyar.py: \n\tm_new = {}\nm_old = {}".format(m_new, m_old))
                    for i in range(0, len(m_new)):
                        if m_new[i] and not m_old[i]:
                            entered.append(i)

        return entered

    def get_subregions_occupied(self, botengine):
        """
        Get a list of subregion indices that are currently occupied.
        This does not provide context.
        :param botengine: BotEngine environment
        :return: List of subregion indices that are occupied, like [1, 2] or []
        """
        occupied = []
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
            if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP]) > 1:
                m_new = self._to_subregion_indices(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0][0])
                for i in range(0, len(m_new)):
                    if m_new[i]:
                        occupied.append(i)

        return occupied

    def get_subregions_exited(self, botengine):
        """
        Get a list of subregion indices that were just exited
        :param botengine: BotEngine environment
        :return: List of subregion indices that were just exited, like [0, 2, 3] or [].
        """
        exited = []
        if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
                if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP]) > 1:
                    m_new = self._to_subregion_indices(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0][0])
                    m_old = self._to_subregion_indices(self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][1][0])
                    for i in range(0, len(m_new)):
                        if not m_new[i] and m_old[i]:
                            exited.append(i)

        return exited

    def _to_subregion_indices(self, subregion_str):
        """
        Convert "1010" to [1, 0, 1, 0]

        :param subregion_str: Subregion string like "0" or "0100"
        :return: Subregion list [0, 0, 0, 0] or [0, 1, 0, 0]
        """
        if int(subregion_str) == 0:
            return [0, 0, 0, 0]

        indices = []
        for i in str(subregion_str):
            indices.append(int(i))
        return indices


    def _extract_targets(self, target):
        """
        Private method to extract the occupancy targets from a single occupancy presence measurement
        :param botengine:
        :param target:
        :return:
        """
        targets = {}
        for t in target.split(";"):
            identifier = t.split(":")[0]
            x = t.split(":")[1].split(",")[0]
            y = t.split(":")[1].split(",")[1]
            z = t.split(":")[1].split(",")[2]
            targets[identifier] = {
                "x": int(x),
                "y": int(y),
                "z": int(z)
            }

        return targets
