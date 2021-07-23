'''
Created on February 11, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from devices.device import Device
import utilities.utilities as utilities

class VayyarDevice(Device):
    """
    Vayyar Home Device
    """
    # Parameters
    MEASUREMENT_NAME_FALL_STATUS = "fallStatus"
    MEASUREMENT_NAME_OCCUPANCY = "occupancy"
    MEASUREMENT_NAME_OCCUPANCY_TARGET = "occupancyTarget"
    MEASUREMENT_NAME_OCCUPANCY_MAP = "occupancyMap"

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
    X_MIN_METERS = -1.9
    X_MAX_METERS = 1.9
    Y_MIN_METERS = 0.3
    Y_MAX_METERS = 3.9

    # Behavior ID's
    BEHAVIOR_TYPE_BEDROOM = 0
    BEHAVIOR_TYPE_BATHROOM = 1
    BEHAVIOR_TYPE_LIVINGROOM = 2
    BEHAVIOR_TYPE_KITCHEN = 3
    BEHAVIOR_TYPE_OTHER = 4

    # Maximum allowable subregions
    MAXIMUM_SUBREGIONS = 4

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2000]

    def __init__(self, botengine, device_id, device_type, device_description, precache_measurements=True):
        """
        Constructor
        :param botengine:
        :param device_id:
        :param device_type:
        :param device_description:
        :param precache_measurements:
        """
        Device.__init__(self, botengine, device_id, device_type, device_description, precache_measurements=precache_measurements)

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Vayyar Home")
    
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
        bedroom_names = ['bed', 'bett', 'bdrm', 'moms room', 'dads room', 'mom\'s room', 'dad\'s room']

        for name in bedroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, 'bedroom')

    def is_in_bathroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bathroom
        """
        bathroom_names = ['schlaf', 'bath', 'toilet', 'shower', 'powder']

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, 'bathroom')

    #===========================================================================
    # Attributes
    #===========================================================================
    def did_start_detecting_fall(self, botengine):
        """
        :param botengine:
        :return: True if a fall is newly detected
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.last_updated_params:
                return self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0][0] == VayyarDevice.FALL_STATUS_CALLING

        return False

    def did_stop_detecting_fall(self, botengine):
        """
        :param botengine:
        :return: True if a fall is no longer detected
        """
        if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            if VayyarDevice.MEASUREMENT_NAME_FALL_STATUS in self.last_updated_params:
                if len(self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS]) > 1:
                    # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
                    # Make sure this newest parameter says we are not calling for help, and the last parameter did say we were calling for help.
                    return self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0][0] != VayyarDevice.FALL_STATUS_CALLING and self.measurements[VayyarDevice.MEASUREMENT_NAME_FALL_STATUS][1][0] == VayyarDevice.FALL_STATUS_CALLING

        return False

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

        If a range (both oldest and newest timestamp) is not specified, then this will only return the latest measurement and will ignore targets that are older than 10 minutes or from a disconnected device

        :param botengine:
        :param oldest_timestamp_ms:
        :param newest_timestamp_ms:
        :return: Dictionary of occupancy targets of the form { timestamp_ms : { 'target_id': { 'x': x, 'y': y, 'z': z } }, ... }
        """
        targets = {}

        if self.is_connected:
            if VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in self.measurements:
                extract_multiple = newest_timestamp_ms is not None and oldest_timestamp_ms is not None

                if newest_timestamp_ms is None:
                    newest_timestamp_ms = botengine.get_timestamp()

                if oldest_timestamp_ms is None:
                    oldest_timestamp_ms = newest_timestamp_ms - (utilities.ONE_MINUTE_MS * 10)

                for t in self.measurements[VayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET]:
                    if t[1] < oldest_timestamp_ms:
                        break

                    if t[1] > newest_timestamp_ms:
                        continue

                    targets[t[1]] = self._extract_targets(t[0])

                    if not extract_multiple:
                        break

        return targets

    def print_occupant_positions(self, botengine):
        """
        Print the occupant position to the CLI
        :param botengine:
        """
        targets = self.get_occupancy_targets(botengine)
        for timestamp_ms in targets:
            for target_id in targets[timestamp_ms]:
                botengine.get_logger().info(utilities.Color.GREEN + "VayyarDevice target {}: x = {} inches; y = {} inches".format(target_id, round(targets[timestamp_ms][target_id]['x'] * 0.393701, 1), round(targets[timestamp_ms][target_id]['y'] * 0.393701, 1)) + utilities.Color.END)

    def total_occupants(self, botengine):
        """
        Get the current total occupants (0, 1, or "more than one" (2+))
        :param botengine:
        :return: 0, 1, or 2+
        """
        total = len(self.get_occupancy_targets(botengine))
        if total > 2:
            total = 2
        return total

    def did_start_detecting_motion(self, botengine):
        """
        Helpful for translation to existing motion sensor functionality.

        Recommend using signals/motion.py with the appropriate microservice driving those signals for more serious motion detection work.

        :param botengine: BotEngine
        :return: True if the Vayyar Home did start detecting occupancy.
        """
        return self.did_start_detecting_occupancy(botengine)

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

    def set_room_boundaries(self, botengine, x_min_meters=-1.9, x_max_meters=1.9, y_min_meters=0.3, y_max_meters=3.9, z_min_meters=0, z_max_meters=2.5):
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
        """
        all_params = []

        if x_min_meters < VayyarDevice.X_MIN_METERS:
            x_min_meters = VayyarDevice.X_MIN_METERS

        if x_max_meters > VayyarDevice.X_MAX_METERS:
            x_max_meters = VayyarDevice.X_MAX_METERS

        if y_min_meters < VayyarDevice.Y_MIN_METERS:
            y_min_meters = VayyarDevice.Y_MIN_METERS

        if y_max_meters > VayyarDevice.Y_MAX_METERS:
            y_max_meters = VayyarDevice.Y_MAX_METERS

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

        botengine.send_commands(self.device_id, all_params)

    def did_update_room_boundaries(self, botengine):
        """
        Determine if we updated the room boundaries in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the room boundaries in this execution
        """
        return "vyrc.xMin" in self.last_updated_params or "vyrc.xMax" in self.last_updated_params or "vyrc.yMin" in self.last_updated_params or "vyrc.yMax" in self.last_updated_params or "vyrc.zMin" in self.last_updated_params or "vyrc.zMax" in self.last_updated_params or "vyrc.zMin" in self.last_updated_params

    def get_room_boundaries(self, botengine):
        """
        Return the boundaries of this room in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        x_min = -1.9
        x_max = 1.9
        y_min = 0.3
        y_max = 3.9
        z_min = 0
        z_max = 2.5
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

        return {
            "x_min": x_min,
            "x_max": x_max,
            "y_min": y_min,
            "y_max": y_max,
            "z_min": z_min,
            "z_max": z_max,
            "updated_ms": updated_ms
        }

    def set_subregions(self, botengine, subregion_list):
        """
        Set a complete list of subregions.

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