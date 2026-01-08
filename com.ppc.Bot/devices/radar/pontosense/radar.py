"""
Created on February 11, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import signals.radar as radar
import utilities.utilities as utilities
from devices.radar.radar import RadarDevice


class RadarPontosenseDevice(RadarDevice):
    """
    Pontosense SilverShield radar device for occupancy detection, fall monitoring, and spatial tracking.

    This device uses radar technology to provide comprehensive room monitoring capabilities including:
    - Real-time occupancy detection and tracking of multiple targets
    - Fall detection with configurable thresholds (0-300 seconds)
    - Spatial positioning of detected targets with X, Y, Z coordinates
    - Room boundary configuration for corner-mounted installations
    - Subregion management for advanced tracking zones (beds, doors, sofas, toilets)
    - Multiple occupancy target types: bed occupancy, couch occupancy, fall detection, pre-fall detection, and general movement

    The device supports corner mounting only and can monitor areas up to 6.0 meters in X and Y directions.
    It provides real-time occupancy target detection with configurable reporting rates and supports
    up to 6 subregions for detailed spatial analysis.

    Key capabilities:
    - Fall detection with position tracking and threshold configuration
    - Multi-target occupancy tracking with specific target indices
    - Room boundary management with sensor height configuration
    - Subregion-based occupancy monitoring for specific areas
    - Real-time target detection with configurable update rates
    - Signal strength monitoring with low signal warnings
    """

    # Parameters
    MEASUREMENT_NAME_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_FIRMWARE = "firmware"
    MEASUREMENT_NAME_MODEL = "model"
    MEASUREMENT_NAME_PNT_FALL_THRESHOLD = "pnt.fallThreshold"
    MEASUREMENT_NAME_PNT_SCAN_HEIGHT = "pnt.scanHeight"
    MEASUREMENT_NAME_PNT_SCAN_LEFT = "pnt.scanLeft"
    MEASUREMENT_NAME_PNT_SCAN_RIGHT = "pnt.scanRight"
    MEASUREMENT_NAME_PNT_UNIT = "pnt.unit"
    MEASUREMENT_NAME_PNT_ZONES = "pnt.zones"
    MEASUREMENT_NAME_PNT_REAL_TIME_TARGET = "pnt.realTimeTarget"
    MEASUREMENT_NAME_RSSI = "rssi"
    MEASUREMENT_NAME_STATUS = "status"

    # Measurement parameters list for machine learning data extraction
    MEASUREMENT_PARAMETERS_LIST = [
        RadarDevice.MEASUREMENT_NAME_BED_STATUS,
        RadarDevice.MEASUREMENT_NAME_FALL_STATUS,
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY,
        RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET,
    ]

    # Fall Status
    FALL_STATUS_NO_FALL = 0
    FALL_STATUS_FALL_DETECTED = 1

    # Scan Area Min and max values
    X_MIN_METERS = 0.0
    X_MAX_METERS = 6.0
    X_DEFAULT_METERS = 6.0
    Y_MIN_METERS = 0.0
    Y_MAX_METERS = 6.0
    Y_DEFAULT_METERS = 6.0
    Z_MIN_METERS = 0.0
    Z_MAX_METERS = 6.0
    SENSOR_HEIGHT_MIN_METERS = 2.0
    SENSOR_HEIGHT_MAX_METERS = 2.2
    SENSOR_HEIGHT_DEFAULT_METERS = 2.0

    # Maximum allowable subregions
    MAXIMUM_SUBREGIONS = 6

    # Low signal strength warning threshold
    LOW_RSSI_THRESHOLD = -70

    OCCUPANCY_TARGET_INDEX_BED_IN = "bedin"
    OCCUPANCY_TARGET_INDEX_COUCH_IN = "couchin"
    OCCUPANCY_TARGET_INDEX_FALL = "fall"
    OCCUPANCY_TARGET_INDEX_PRE_FALL = "pfall"
    OCCUPANCY_TARGET_INDEX_OTHER = "other"

    # Fall threshold in seconds
    FALL_THRESHOLD_MIN = 0
    FALL_THRESHOLD_MAX = 300

    # Sensor detection zone types
    DETECTION_ZONE_TYPE_BED = 10
    DETECTION_ZONE_TYPE_DOOR = 20
    DETECTION_ZONE_TYPE_SOFA = 30
    DETECTION_ZONE_TYPE_MEDICATION_STATION = 40
    DETECTION_ZONE_TYPE_TOILET = 50

    # Device status
    DEVICE_STATUS_NORMAL = 0
    DEVICE_STATUS_ERROR = 1
    DEVICE_STATUS_ALIGNMENT = 2

    # Occupancy target detection reading rate in milliseconds.
    DEFAULT_REPORTING_RATE_MS = 2000

    # List of Device Types this class is compatible with
    DEVICE_TYPES = [2007]

    # Note: Pontosense devices inherit SUBREGION_TRANSITION_DELAY_MS = 0 from RadarDevice base class
    # This provides immediate knowledge promotion for reliable Pontosense devices
    
    # Occupancy transition timing - immediate knowledge promotion for Pontosense devices
    OCCUPANCY_TRANSITION_DELAY_MS = 0

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
        RadarDevice.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

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
        return _("SilverShield")  # noqa: F821 # type: ignore

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
        return utilities.ICON_FONT_FONTAWESOME_REGULAR

    # ===========================================================================
    # Attributes
    # ===========================================================================

    def is_detecting_fall(self, botengine):
        """
        Is this device detecting any kind of fall?
        :param botengine: BotEngine
        :return: True if this device is detecting a fall
        """
        return (
            self.get_fall_status(botengine)
            == RadarPontosenseDevice.FALL_STATUS_FALL_DETECTED
        )

    def did_stop_detecting_fall(self, botengine):
        """
        Did this device stop detecting a fall?
        :param botengine:
        :return: True if a fall is no longer detected
        """
        status = self.get_fall_status(botengine)
        previous_status = self.get_previous_fall_status(botengine)
        did_update = self.did_change_fall_status(botengine)
        return status is not None and previous_status is not None and did_update

    def did_update_fall_position(self, botengine):
        """
        Check if fall position has changed
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        measurement_name = f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}"
        return measurement_name in self.last_updated_params

    def get_fall_positions(
        self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None
    ):
        """
        Get the current fall position or multiple fall positions within a given time range
        :param botengine: BotEngine environment
        :param oldest_timestamp_ms: Optional oldest timestamp in the range to extract from the cache
        :param newest_timestamp_ms: Optional newest timestamp in the range to extract from the cache
        :return: Dictionary of occupancy targets of the form { timestamp_ms : { 'x': x, 'y': y, 'z': z } }, ... }
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_fall_positions()"
        )
        measurement_name = f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}"
        if measurement_name not in self.measurements:
            return {}
        # Build a time range to extract from the cache including the upper bounds by adding 1 ms to the newest or current timestamp
        time_range = range(
            oldest_timestamp_ms
            or newest_timestamp_ms
            or self.measurements[measurement_name][0][1],
            (newest_timestamp_ms or self.measurements[measurement_name][0][1]) + 1,
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|get_fall_positions() time_range={}".format(time_range)
        )
        # Extract the fall positions from the cache
        fall_positions = {}
        for fall_status in self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS]:
            # Skip fall_status that are not in the time range
            if fall_status[1] not in time_range:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "|get_fall_positions() skipping fall_status={}".format(fall_status)
                )
                continue
            timestamp = fall_status[1]
            # Get the associated fall position for this status, if available
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|get_fall_positions() measurements={}".format(self.measurements)
            )

            fall_locations = (
                [
                    positional_measurement[0]
                    for positional_measurement in self.measurements[measurement_name]
                    if positional_measurement[1] <= timestamp
                ]
                if measurement_name in self.measurements
                else []
            )

            # Skip fall positions that are not complete
            if any(
                [
                    len(positional_measurement) == 0
                    for positional_measurement in [
                        fall_locations,
                    ]
                ]
            ):
                continue
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|get_fall_positions() fall_locations={}".format(fall_locations)
            )
            if fall_locations[0] is None:
                continue
            fall_target = fall_locations[0].split(":")[-1]
            if ";" in fall_locations[0]:
                fall_target = fall_locations[0].split(";")[0]
            fall_target = fall_target.split(",")
            position = {
                "x": fall_target[0],
                "y": fall_target[1],
                "z": fall_target[2],
            }
            fall_positions[timestamp] = position

        # Sort newest to oldest
        sorted_positions = dict(sorted(fall_positions.items(), reverse=True))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_fall_positions() fall_positions={}".format(sorted_positions)
        )
        return sorted_positions

    def did_update_occupancy_targets(self, botengine):
        """
        Did we get new occupancy target data
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        measurements = [
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}",
        ]
        return any(
            [measurement in self.last_updated_params for measurement in measurements]
        )

    def get_occupancy_targets(
        self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None
    ):
        """
        Get the current occupant targets the Radar device is tracking and their positions

        You can optionally pass in a range of time to extract from the locally available 1-hour cache, with oldest_timestamp_ms and newest_timestamp_ms.

        If a range (both oldest and newest timestamp) is not specified, then this will only return the latest measurement and will ignore targets that are older than 30 minutes or from a disconnected device

        :param botengine:
        :param oldest_timestamp_ms:
        :param newest_timestamp_ms:
        :return: Dictionary of occupancy targets of the form { timestamp_ms : { 'target_id': { 'x': x, 'y': y, 'z': z } }, ... }
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_occupancy_targets()"
        )
        measurements = [
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}",
        ]
        targets = {}

        if self.is_connected:
            for measurement in sorted(
                self.measurements.keys(),
                key=lambda key: self.measurements[key][0][1],
                reverse=True,
            ):
                if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET not in measurement:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                        f"|get_occupancy_targets() {measurement} Excluded"
                    )
                    continue
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "|get_occupancy_targets() {} targets={}".format(
                        measurement, self.measurements[measurement]
                    )
                )
                extract_multiple = (
                    newest_timestamp_ms is not None and oldest_timestamp_ms is not None
                )

                if newest_timestamp_ms is None:
                    newest_timestamp_ms = botengine.get_timestamp()

                if oldest_timestamp_ms is None:
                    oldest_timestamp_ms = newest_timestamp_ms - (
                        utilities.ONE_MINUTE_MS * 30
                    )
                discovered = None
                for t in self.measurements[measurement]:
                    if t[1] < oldest_timestamp_ms:
                        break
                    if t[1] > newest_timestamp_ms:
                        continue
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                        f"|get_occupancy_targets() {measurement} t={t}"
                    )
                    discovered = t
                    if t[1] in targets:
                        # Already have targets for this timestamp, merge them
                        new_targets = self._extract_targets(t[0])
                        for target_id in new_targets:
                            botengine.get_logger(
                                f"{__name__}.{__class__.__name__}"
                            ).debug(
                                f"|get_occupancy_targets() {measurement} merging {target_id}={new_targets[target_id]}"
                            )
                            targets[t[1]][target_id] = new_targets[target_id]
                    else:
                        targets[t[1]] = self._extract_targets(t[0])
                    if not extract_multiple:
                        # Only extract the latest target
                        break

                # Check last known occupancy targets for a given timestamp
                if discovered:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                        "|get_occupancy_targets() {} discovered targets={}".format(
                            measurement, targets
                        )
                    )
                    for occupancy_measurement_name in measurements:
                        if occupancy_measurement_name == measurement:
                            continue
                        for t in self.measurements.get(occupancy_measurement_name, []):
                            if t[1] > discovered[1]:
                                continue
                            if t[0] is None:
                                break
                            _targets = self._extract_targets(t[0])
                            for target_id in _targets:
                                botengine.get_logger(
                                    f"{__name__}.{__class__.__name__}"
                                ).debug(
                                    f"|get_occupancy_targets() {measurement} discovered {occupancy_measurement_name} {target_id}={_targets[target_id]}"
                                )
                                targets[discovered[1]][target_id] = _targets[target_id]
                                break
                            break

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_occupancy_targets() targets={}".format(targets)
        )
        return targets

    def set_fall_threshold(self, botengine, fall_threshold):
        """
        Set the fall detection threshold in seconds.

        :param botengine: BotEngine environment
        :param fall_threshold: Fall detection threshold. 0-300.
        """
        botengine.send_command(
            self.device_id,
            RadarPontosenseDevice.MEASUREMENT_NAME_PNT_FALL_THRESHOLD,
            int(fall_threshold),
        )

    def get_fall_threshold(self, botengine):
        """
        Get the current fall detection threshold in seconds.

        :param botengine: BotEngine environment
        :return: Current fall threshold in seconds, or None if not available
        """
        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_FALL_THRESHOLD in self.measurements:
            if len(self.measurements[RadarPontosenseDevice.MEASUREMENT_NAME_PNT_FALL_THRESHOLD]) > 0:
                return self.measurements[RadarPontosenseDevice.MEASUREMENT_NAME_PNT_FALL_THRESHOLD][0][0]
        return None
        
    def set_test_mode(self, botengine, test_mode):
        """
        Enables test mode. To test during learning mode, the user should activate test mode. When learning and test mode are activated at the same time, the data will be marked and ignored in the sensitivity map creation.
        Default: "false"
        :param botengine: BotEngine
        :param test_mode: 1 or 0
        """
        raise NotImplementedError(
            "set_test_mode is not implemented for RadarPontosenseDevice"
        )

    def get_test_mode(self, botengine):
        """
        Enables test mode. To test during learning mode, the user should activate test mode. When learning and test mode are activated at the same time, the data will be marked and ignored in the sensitivity map creation.
        Default: "false"
        :param botengine: BotEngine
        :return: 1 or 0
        """
        raise NotImplementedError(
            "get_test_mode is not implemented for RadarPontosenseDevice"
        )

    def get_realtime_occupancy_target_detection(self, botengine):
        """
        Describes if this device provides realtime updates to occupancy target changes
        :param botengine:
        :return: True if the device provides realtime updates, False otherwise
        """

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_REAL_TIME_TARGET in self.measurements:
            return self.measurements[RadarPontosenseDevice.MEASUREMENT_NAME_PNT_REAL_TIME_TARGET][0][0] == 1
        return False
    
    def set_realtime_occupancy_target_detection(self, botengine, is_realtime=True):
        """
        Sets the realtime occupancy target detection state.
        :param botengine: BotEngine environment
        :param is_realtime: True to enable realtime updates, False to disable
        """
        botengine.send_command(
            self.device_id,
            RadarPontosenseDevice.MEASUREMENT_NAME_PNT_REAL_TIME_TARGET,
            int(is_realtime),
        )

    def realtime_occupancy_target_detection_rate(self, botengine):
        """
        Get the reading rate for realtime occupancy target detection in ms.
        :param botengine: BotEngine environment
        :return: Reading rate in milliseconds
        """
        return RadarPontosenseDevice.DEFAULT_REPORTING_RATE_MS

    def set_room_boundaries(self, botengine, content={}):
        """
        Set the boundaries of the room. Measurements are in meters.

        Installations are only available for corner mounting.

        * **X-axis** = left from the perspective of the device. Maximum to the left is 6.0 meters.
        * **Y-axis** = right from the perspective of the device.  Maximum to the right is 6.0 meters.
        * **Z-axis** = height from the ground.  Minimum is 2.0 meters, maximum is 3.5 meters.

        :param botengine:
        :param content: Dictionary of the following parameters:
            'x_max_meters' - Distance of the room to the left, maximum is 6.0 meters
            'y_max_meters' - Distance of the room to the right, maximum is 6.0 meters
            'sensor_height_m' - Height of the sensor in meters, minimum is 2.0 meters, maximum is 3.5 meters
        """
        all_params = []

        x_max_meters = content.get("x_max_meters", RadarPontosenseDevice.X_MAX_METERS)
        y_max_meters = content.get("y_max_meters", RadarPontosenseDevice.Y_MAX_METERS)
        sensor_height_m = content.get(
            "sensor_height_m", RadarPontosenseDevice.SENSOR_HEIGHT_MIN_METERS
        )

        # Constraints
        if x_max_meters > RadarPontosenseDevice.X_MAX_METERS:
            x_max_meters = RadarPontosenseDevice.X_MAX_METERS

        if y_max_meters > RadarPontosenseDevice.Y_MAX_METERS:
            y_max_meters = RadarPontosenseDevice.Y_MAX_METERS

        # Smallest boundary is 1 m^2
        if x_max_meters < 1.0:
            x_max_meters = 1.0

        if y_max_meters < 1.0:
            y_max_meters = 1.0

        # Fixed sensor height on walls
        all_params.append(
            {
                "name": RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT,
                "value": int(sensor_height_m * 100),
            }
        )

        all_params.append(
            {
                "name": RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT,
                "value": int(x_max_meters * 100),
            }
        )

        all_params.append(
            {
                "name": RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT,
                "value": int(y_max_meters * 100),
            }
        )

        botengine.send_commands(self.device_id, all_params)

    def did_update_room_boundaries(self, botengine):
        """
        Determine if we updated the room boundaries in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the room boundaries in this execution
        """
        return any(
            [
                param in self.last_updated_params
                for param in [
                    RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT,
                    RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT,
                    RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT,
                ]
            ]
        )

    def get_room_boundaries(self, botengine):
        """
        Return the boundaries of this room in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        room = RadarDevice.get_room_boundaries(self, botengine)

        # This device provides only a corner installation, provide some defaults for interoperability
        room["x_min_meters"] = RadarPontosenseDevice.X_MIN_METERS
        room["x_max_meters"] = RadarPontosenseDevice.X_MAX_METERS
        room["y_min_meters"] = RadarPontosenseDevice.Y_MIN_METERS
        room["y_max_meters"] = RadarPontosenseDevice.Y_MAX_METERS
        room["z_max_meters"] = RadarPontosenseDevice.Z_MAX_METERS
        room["mounting_type"] = RadarDevice.SENSOR_MOUNTING_CORNER
        room["near_exit"] = False

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ]
                )
                > 0
            ):
                room["x_max_meters"] = (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ][0][0]
                    / 100.0
                )
                if room["x_max_meters"] == 0.0:
                    room["x_max_meters"] = RadarPontosenseDevice.X_DEFAULT_METERS
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ][0][1]
                    > room["updated_ms"]
                ):
                    room["updated_ms"] = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ][0][1]

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ]
                )
                > 0
            ):
                room["y_max_meters"] = (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ][0][0]
                    / 100.0
                )
                if room["y_max_meters"] == 0.0:
                    room["y_max_meters"] = RadarPontosenseDevice.Y_DEFAULT_METERS
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ][0][1]
                    > room["updated_ms"]
                ):
                    room["updated_ms"] = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ][0][1]

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ]
                )
                > 0
            ):
                room["sensor_height_m"] = (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ][0][0]
                    / 100.0
                )
                if room["sensor_height_m"] == 0.0:
                    room["sensor_height_m"] = (
                        RadarPontosenseDevice.SENSOR_HEIGHT_DEFAULT_METERS
                    )
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ][0][1]
                    > room["updated_ms"]
                ):
                    room["updated_ms"] = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ][0][1]

        return room

    def get_room_boundaries_properties(self, botengine, return_defaults=True):
        """
        Return the boundaries of this room FROM THE DEVICE PROPERTY in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :param return_defaults: If True, return default values for any missing properties.  If False, return only the properties that are defined in the device property.
        :return: Dictionary with room boundaries
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_room_boundaries_properties()"
        )
        # Retrieve room boundaries from properties, without retrieving default boundaries from underlying class
        content = RadarDevice.get_room_boundaries_properties(self, botengine, return_defaults=False)

        if not return_defaults:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|get_room_boundaries_properties() returning properties only"
            )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "<get_room_boundaries_properties() room_boundaries={}".format(
                    content
                )
            )
            return content
        
        x_min = content.get("x_min_meters", RadarPontosenseDevice.X_MIN_METERS)
        x_max = content.get("x_max_meters", RadarPontosenseDevice.X_MAX_METERS)
        y_min = content.get("y_min_meters", RadarPontosenseDevice.Y_MIN_METERS)
        y_max = content.get("y_max_meters", RadarPontosenseDevice.Y_MAX_METERS)
        z_min = content.get("z_min_meters", RadarPontosenseDevice.Z_MIN_METERS)
        z_max = content.get("z_max_meters", RadarPontosenseDevice.Z_MAX_METERS)
        mounting_type = content.get(
            "mounting_type", RadarPontosenseDevice.SENSOR_MOUNTING_CORNER
        )
        sensor_height_m = content.get(
            "sensor_height_m", RadarPontosenseDevice.SENSOR_HEIGHT_MIN_METERS
        )
        updated_ms = content.get("updated_ms", 0)

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ]
                )
                > 0
            ):
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ][0][1]
                    > updated_ms
                ):
                    updated_ms = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_LEFT
                    ][0][1]
        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ]
                )
                > 0
            ):
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ][0][1]
                    > updated_ms
                ):
                    updated_ms = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_RIGHT
                    ][0][1]

        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT in self.measurements:
            if (
                len(
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ]
                )
                > 0
            ):
                if (
                    self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ][0][1]
                    > updated_ms
                ):
                    updated_ms = self.measurements[
                        RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
                    ][0][1]

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
            "near_exit": False,
        }
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_room_boundaries_properties() room_boundaries={}".format(
                room_boundaries
            )
        )
        return room_boundaries

    def set_subregions(self, botengine, subregion_list):
        """
        Send a complete list of subregions to the device.

        * pnt.zones = Array of objects (Tracker Sub Regions)
            * height = The height of the zone in centimeters. Default: 120?
            * type = The type of the zone. Default: 10 (Bed), 20 (Door), 30 (Sofa), 40 (Toilet)?
            * coordinates = Array of coordinates (x, y) in centimeters

        :param botengine: BotEngine environment
        :param subregion_list: Correctly formatted list of sub-regions
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            f"|set_subregions() device_id={self.device_id} subregions={subregion_list}"
        )
        import json

        botengine.send_command(
            self.device_id,
            RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES,
            json.dumps(subregion_list, separators=(",", ":")),
        )

    def did_update_subregions(self, botengine):
        """
        Did this Vayyar device update subregions
        :param botengine:
        :return:
        """
        return (
            RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES in self.last_updated_params
        )

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
        * pnt.zones = Array of objects (Tracker Sub Regions)
            * height = The height of the zone in centimeters. Default: 120?
            * type = The type of the zone. Default: 10 (Bed), 20 (Door), 30 (Sofa), 40 (Toilet)?
            * coordinates = Array of coordinates (x, y) in centimeters
        If the subregions are not available, this will return an empty list.

        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        if RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES in self.measurements:
            if (
                len(self.measurements[RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES])
                > 0
            ):
                zones_string = self.measurements[
                    RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES
                ][0][0]
                if zones_string is None or zones_string == "[]":
                    return []

                if isinstance(zones_string, list):
                    return zones_string
                try:
                    import json
                    return json.loads(zones_string)
                except Exception as e:
                    import traceback
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        "|get_raw_zones() Couldn't load tracker zone. json={}; e={}; trace={}".format(
                            zones_string, e, traceback.format_exc()
                        )
                    )
                    pass

        return []

    def get_subregion_index(self, botengine, subregion):
        """
        Return the index of a locally stored subregion represented on the device.
        :param botengine: BotEngine environment
        :param subregion: Subregion object
        :return: Index of the subregion, or None if it is not stored on the device.
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_subregion_index() device_id={} subregion={}".format(
                self.device_id, subregion
            )
        )

        for idx, raw_subregion in enumerate(self.get_raw_subregions(botengine)):
            coordinates_x = sorted(
                [coordinate["x"] for coordinate in raw_subregion.get("coordinates", [])]
            )
            coordinates_y = sorted(
                [coordinate["y"] for coordinate in raw_subregion.get("coordinates", [])]
            )
            min_x = coordinates_x[0] / 100
            max_x = coordinates_x[-1] / 100
            min_y = coordinates_y[0] / 100
            max_y = coordinates_y[-1] / 100
            if (
                subregion["x_min_meters"] == min_x
                and subregion["x_max_meters"] == max_x
                and subregion["y_min_meters"] == min_y
                and subregion["y_max_meters"] == max_y
            ):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "<get_subregion_index() device_id={} index={}".format(
                        self.device_id, idx
                    )
                )
                return idx

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_subregion_index() device_id={} index={}".format(self.device_id, None)
        )
        return None

    def target_is_in_subregion(self, botengine, target, subregion):
        """
        Determine if a given occupancy target is in a given subregion.
        :param botengine: BotEngine environment
        :param target: Occupancy target dictionary with 'x', 'y', 'z' keys
        :param subregion: Subregion object
        :return: True if the target is in the subregion, False otherwise
        """
        if target is None or subregion is None:
            return False
        try:
            x = float(target.get("x", None))
            y = float(target.get("y", None))
            z = float(target.get("z", None))
            if x is None or y is None or z is None:
                return False
            coordinates_x = sorted(
                [coordinate["x"] for coordinate in subregion.get("coordinates", [])]
            )
            coordinates_y = sorted(
                [coordinate["y"] for coordinate in subregion.get("coordinates", [])]
            )
            min_x = coordinates_x[0]
            max_x = coordinates_x[-1]
            min_y = coordinates_y[0]
            max_y = coordinates_y[-1]
            height_cm = subregion.get("height", 120)
            min_z = 0.0  # Assume floor level
            max_z = height_cm
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|target_is_in_subregion() target={} subregion={} bounds=(x: {}-{}, y: {}-{}, z: {}-{})".format(
                    target, subregion, min_x, max_x, min_y, max_y, min_z, max_z
                )
            )
            in_subregion = (
                (min_x <= x <= max_x)
                and (min_y <= y <= max_y)
                and (min_z <= z <= max_z)
            )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|target_is_in_subregion() target={} subregion={} in_subregion={}".format(
                    target, subregion, in_subregion
                )
            )
            return in_subregion
        except Exception as e:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                "|target_is_in_subregion() Exception: {}".format(e)
            )
            return False

    def did_subregion_occupancy_change(self, botengine):
        """
        Determine if subregion occupancy may have changed at all on this execution,
        as evidenced by receiving occupancy target updates and comparing occupied subregions
        to previous occupied subregions.

        :param botengine: BotEngine environment
        :return: True if subregion occupancy may have been updated in this execution
        """
        subregions = self.get_raw_subregions(botengine)
        if subregions is None or len(subregions) == 0:
            return False
        targets = self.get_occupancy_targets(botengine)
        if len(targets) == 0:
            return False
        current_timestamp = max(targets.keys())
        previous_timestamp = None
        for ts in sorted(targets.keys(), reverse=True):
            if ts < current_timestamp:
                previous_timestamp = ts
                break
        current_targets = targets[current_timestamp]
        previous_targets = targets[previous_timestamp] if previous_timestamp else {}
        current_occupied_subregions = set()
        previous_occupied_subregions = set()
        for subregion_index, subregion in enumerate(subregions):
            for target_id in current_targets:
                if self.target_is_in_subregion(
                    botengine, current_targets[target_id], subregion
                ):
                    current_occupied_subregions.add(subregion_index)
            for target_id in previous_targets:
                if self.target_is_in_subregion(
                    botengine, previous_targets[target_id], subregion
                ):
                    previous_occupied_subregions.add(subregion_index)

        if current_occupied_subregions != previous_occupied_subregions:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|did_subregion_occupancy_change() current_occupied={} previous_occupied={}".format(
                    current_occupied_subregions, previous_occupied_subregions
                )
            )
            return True

        return False

    def get_subregions_occupied(self, botengine):
        """
        Get a list of subregion indices that are currently occupied.
        This does not provide context.
        :param botengine: BotEngine environment
        :return: List of subregion indices that are occupied, like [1, 2] or []
        """

        subregions = self.get_raw_subregions(botengine)
        if subregions is None or len(subregions) == 0:
            return []
        targets = self.get_occupancy_targets(botengine)
        if len(targets) == 0:
            return []

        current_timestamp = max(targets.keys())

        occupied_subregions = set()
        for subregion_index, subregion in enumerate(subregions):
            for target_id in targets[current_timestamp]:
                if self.target_is_in_subregion(
                    botengine, targets[current_timestamp][target_id], subregion
                ):
                    occupied_subregions.add(subregion_index)
        return list(occupied_subregions)

    def get_subregions_entered(self, botengine):
        """
        Get a list of subregion indices that were just entered.
        This does not provide context.
        :param botengine: BotEngine environment
        :return: List of subregion indices that were just entered, like [0, 2, 3] or [].
        """
        subregions = self.get_raw_subregions(botengine)
        if subregions is None or len(subregions) == 0:
            return []
        targets = self.get_occupancy_targets(botengine)
        if len(targets) < 2:
            return []
        current_timestamp = max(targets.keys())
        previous_timestamp = None
        for ts in sorted(targets.keys(), reverse=True):
            if ts < current_timestamp:
                previous_timestamp = ts
                break
        current_targets = targets[current_timestamp]
        previous_targets = targets[previous_timestamp] if previous_timestamp else {}
        entered_subregions = set()
        for subregion_index, subregion in enumerate(subregions):
            currently_occupied = False
            previously_occupied = False
            for target_id in current_targets:
                if self.target_is_in_subregion(
                    botengine, current_targets[target_id], subregion
                ):
                    currently_occupied = True
                    break
            for target_id in previous_targets:
                if self.target_is_in_subregion(
                    botengine, previous_targets[target_id], subregion
                ):
                    previously_occupied = True
                    break
            if currently_occupied and not previously_occupied:
                entered_subregions.add(subregion_index)
        return list(entered_subregions)

    def get_subregions_exited(self, botengine):
        """
        Get a list of subregion indices that were just exited
        :param botengine: BotEngine environment
        :return: List of subregion indices that were just exited, like [0, 2, 3] or [].
        """
        subregions = self.get_raw_subregions(botengine)
        if subregions is None or len(subregions) == 0:
            return []
        targets = self.get_occupancy_targets(botengine)
        if len(targets) < 2:
            return []
        current_timestamp = max(targets.keys())
        previous_timestamp = None
        for ts in sorted(targets.keys(), reverse=True):
            if ts < current_timestamp:
                previous_timestamp = ts
                break
        current_targets = targets[current_timestamp]
        previous_targets = targets[previous_timestamp] if previous_timestamp else {}
        exited_subregions = set()
        for subregion_index, subregion in enumerate(subregions):
            currently_occupied = False
            previously_occupied = False
            for target_id in current_targets:
                if self.target_is_in_subregion(
                    botengine, current_targets[target_id], subregion
                ):
                    currently_occupied = True
                    break
            for target_id in previous_targets:
                if self.target_is_in_subregion(
                    botengine, previous_targets[target_id], subregion
                ):
                    previously_occupied = True
                    break
            if not currently_occupied and previously_occupied:
                exited_subregions.add(subregion_index)
        return list(exited_subregions)

    def has_bed_subregion(self, botengine):
        """
        Check if this device has any bed subregions configured.
        :param botengine: BotEngine environment
        :return: True if the device has at least one bed subregion, False otherwise
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">has_bed_subregion()"
        )
        
        subregions = self.get_raw_subregions(botengine)
        if subregions is None or len(subregions) == 0:
            return False
        
        for subregion in subregions:
            # Check if this subregion has a bed zone type
            if subregion.get("type") == RadarPontosenseDevice.DETECTION_ZONE_TYPE_BED:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "<has_bed_subregion() found bed subregion, returning True"
                )
                return True
        
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<has_bed_subregion() no bed subregions found, returning False"
        )
        return False

    def get_sorted_subregions(
        self,
        botengine,
        subregion_list,
        submit_all=True,
        z_min_meters=0,
        z_max_meters=2.0,
    ):
        """
        Provides a sorted list of subregions based on the input list, with the following priority:
        1) Bed
        2) Door
        3) Largest Area

        Limit the number of subregions to 6, described by the device.  TODO: Confirm for Pontosense.
        Only 2 doors are allowed, and are always at the end of the list.  TODO: Confirm for Pontosense.
        Beds are represented first.
        :param botengine: BotEngine environment
        :param subregion_list: Dictionary of subregions by device_id
        :param submit_all: If True, will submit all subregions that ignore presence.  If False, will only submit subregions that ignore presence and are not doors.
        :param z_min_meters: Minimum Z height in meters to consider for this subregion
        :param z_max_meters: Maximum Z height in meters to consider for this subregion
        :return: Tuple of sorted subregion lists for both device API and native services
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_sorted_subregions() device_id={} subregion_list={} submit_all={} z_min_meters={} z_max_meters={}".format(
                self.device_id, subregion_list, submit_all, z_min_meters, z_max_meters
            )
        )

        api_subregion_list = []
        native_subregion_list = []

        number_of_doors = 0

        for s in subregion_list.get(self.device_id, []):
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                f"|get_sorted_subregions() device_id={self.device_id} Processing subregion {s}"
            )
            if number_of_doors >= 2 and s.get("is_door", False):
                # Only 2 doors allowed
                continue

            if "z_min_meters" in s and "z_max_meters" in s:
                if s["z_min_meters"] < z_min_meters or s["z_max_meters"] > z_max_meters:
                    # This subregion is smaller than an X,Y area - it's a 3D space so let's not ignore the whole X,Y area.
                    continue
            # We want to ignore the full area, leverage the radar to do that.
            zone_type = None
            context_id = s.get("context_id")
            if context_id is None:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    f"|get_sorted_subregions() device_id={self.device_id} No context id, skip"
                )
                continue
            if radar.is_context_bed(context_id):
                zone_type = RadarPontosenseDevice.DETECTION_ZONE_TYPE_BED
            elif context_id == radar.SUBREGION_CONTEXT_EXIT or s.get("is_door", False):
                zone_type = RadarPontosenseDevice.DETECTION_ZONE_TYPE_DOOR
            elif radar.is_context_chair(context_id):
                zone_type = RadarPontosenseDevice.DETECTION_ZONE_TYPE_SOFA
            elif radar.is_context_toilet(context_id):
                zone_type = RadarPontosenseDevice.DETECTION_ZONE_TYPE_TOILET
            else:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    f"|get_sorted_subregions() device_id={self.device_id} Context ID {context_id} not supported, skip"
                )
                continue
            subregion = {
                "height": int(s.get("z_max_meters", z_max_meters) * 100),  # in cm
                "type": zone_type,
                "coordinates": [
                    {"x": int(s["x_min_meters"] * 100), "y": int(s["y_min_meters"] * 100)},
                    {"x": int(s["x_max_meters"] * 100), "y": int(s["y_max_meters"] * 100)},
                ],
            }

            number_of_doors += (
                1
                if context_id == radar.SUBREGION_CONTEXT_EXIT or s.get("is_door", False)
                else 0
            )
            api_subregion_list.append(subregion)
            native_subregion_list.append(s.copy())
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                f"|get_sorted_subregions() device_id={self.device_id} Added zone {subregion}"
            )
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                f"|get_sorted_subregions() device_id={self.device_id} number of doors is now {number_of_doors}"
            )

        # Sort subregions so that the list is prioritized in the following order: 1) Bed, 2) Door, 3) Largest Area
        api_subregion_list.sort(
            key=lambda s: abs(s["coordinates"][1]["x"] - s["coordinates"][0]["x"])
            * abs(s["coordinates"][1]["y"] - s["coordinates"][0]["y"]),
            reverse=True,
        )
        native_subregion_list.sort(
            key=lambda s: abs(s["x_max_meters"] - s["x_min_meters"])
            * abs(s["y_max_meters"] - s["y_min_meters"]),
            reverse=True,
        )
        api_subregion_list.sort(
            key=lambda s: 1
            if s["type"] == RadarPontosenseDevice.DETECTION_ZONE_TYPE_BED
            else 0,
            reverse=True,
        )
        native_subregion_list.sort(
            key=lambda s: 1 if radar.is_context_bed(s["context_id"]) else 0, reverse=True
        )
        # Make sure we don't have more than 6
        del api_subregion_list[RadarDevice.MAXIMUM_SUBREGIONS :]
        del native_subregion_list[RadarDevice.MAXIMUM_SUBREGIONS :]

        # Sort door subregions to be at last in our list
        api_subregion_list.sort(
            key=lambda s: 1
            if s["type"] == RadarPontosenseDevice.DETECTION_ZONE_TYPE_DOOR
            else 0
        )
        native_subregion_list.sort(key=lambda s: 1 if s.get("is_door", False) else 0)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_sorted_subregions() device_id={} api_subregion_list={} native_subregion_list={}".format(
                self.device_id, api_subregion_list, native_subregion_list
            )
        )
        return (api_subregion_list, native_subregion_list)
