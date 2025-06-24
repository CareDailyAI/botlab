"""
Created on February 11, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import signals.radar as radar
import utilities.utilities as utilities
from devices.device import Device, MINIMUM_MEASUREMENTS_TO_CACHE


class RadarDevice(Device):
    """
    Radar Device
    """

    # Parameters
    MEASUREMENT_NAME_FALL_STATUS = "fallStatus"
    MEASUREMENT_NAME_OCCUPANCY = "occupancy"
    MEASUREMENT_NAME_OCCUPANCY_TARGET = "occupancyTarget"
    MEASUREMENT_NAME_OCCUPANCY_MAP = "occupancyMap"
    MEASUREMENT_NAME_BED_STATUS = "bedStatus"
    MEASUREMENT_NAME_FALL_LOC_X = "fallLocX"
    MEASUREMENT_NAME_FALL_LOC_Y = "fallLocY"
    MEASUREMENT_NAME_FALL_LOC_Z = "fallLocZ"

    # Measurement parameters list for machine learning data extraction
    MEASUREMENT_PARAMETERS_LIST = [
        MEASUREMENT_NAME_OCCUPANCY_TARGET,
        MEASUREMENT_NAME_OCCUPANCY_MAP,
        MEASUREMENT_NAME_OCCUPANCY,
    ]

    # Fall Status
    FALL_STATUS_DETECTED = "fall_detected"
    FALL_STATUS_CONFIRMED = "fall_confirmed"
    FALL_STATUS_SUSPECTED = "fall_suspected"
    FALL_STATUS_CALLING = "calling"
    FALL_STATUS_CANCELLED = "canceled"
    FALL_STATUS_FINISHED = "finished"
    FALL_STATUS_EXIT = "fall_exit"

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

    # Behavior ID's
    BEHAVIOR_TYPE_BEDROOM = 0
    BEHAVIOR_TYPE_BATHROOM = 1
    BEHAVIOR_TYPE_LIVINGROOM = 2
    BEHAVIOR_TYPE_KITCHEN = 3
    BEHAVIOR_TYPE_OTHER = 4
    BEHAVIOR_TYPE_OFFICE = 5

    # Mounting options
    SENSOR_MOUNTING_WALL = 0
    SENSOR_MOUNTING_WALL_45_DEGREE = 3
    SENSOR_MOUNTING_CEILING = 1
    SENSOR_MOUNTING_CEILING_45_DEGREE = 2

    # Maximum allowable subregions
    MAXIMUM_SUBREGIONS = 6

    # Low signal strength warning threshold
    LOW_RSSI_THRESHOLD = -70

    # List of Device Types this class is compatible with
    DEVICE_TYPES = []

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
        Device.__init__(
            self,
            botengine,
            location_object,
            device_id,
            device_type,
            device_description,
            precache_measurements=precache_measurements,
        )

        # Information (changes quickly): Total occupant information as measured and updated by a supporting microservice (location_radarsubregion_microservice)
        self.information_total_occupants = 0

        # Knowledge (changes more slowly): Total occupants knowledge as measured and updated by a supporting microservice (device_radar
        self.knowledge_total_occupants = 0

        # Count of times a target measurement has detected a fall on this device.
        # Every fall detect from a target increments this value to the MAXIMUM_FALL_COUNT
        # Every non-fall target measurement decrements the count.
        # This is used like a 'capacitor' of fall events, giving us confidence to call for help or that a person is still on the ground.
        self.fall_count = 0

        # True if this device is declared to be near an exit door.
        self.near_exit = False

        # Summary of existing subregions - { "unique_id": (context_id, name), ... }
        self.subregions = {}

        # List of occupied subregion information (high frequency / not validated) - [ "unique_id", ... ]
        self.information_occupied_subregions = []

        # List of occupied subregion knowledge (low frequency / higher reliability) - [ "unique_id", ... ]
        self.knowledge_occupied_subregions = []

        # Default Behavior
        self.goal_id = RadarDevice.BEHAVIOR_TYPE_OTHER

        # Minimum number of measurements to maintain in the cache, regardless of the cache duration.  Keyed by parameter name.
        self.minimum_measurements_to_cache_by_parameter_name = {
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP: 2,
        }

    def new_version(self, botengine):
        """
        New version
        :param botengine: BotEngine environment
        """
        Device.new_version(self, botengine)

        # Added: January 23, 2025
        if self.minimum_measurements_to_cache_by_parameter_name == MINIMUM_MEASUREMENTS_TO_CACHE:
            self.minimum_measurements_to_cache_by_parameter_name = {
                RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP: 2,
            }
        pass

    def get_device_type_name(self):
        """
        :return: the name of this device type in the given language, for example, "Entry Sensor"
        """
        # NOTE: Abstract device type name, doesn't show up in end user documentation
        return _("Radar")

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
        if self.goal_id == RadarDevice.BEHAVIOR_TYPE_BEDROOM:
            return True

        bedroom_names = [
            _("bed"),
            _("bett"),
            _("bdrm"),
            _("moms room"),
            _("dads room"),
            _("mom's room"),
            _("dad's room"),
        ]

        for name in bedroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, "bedroom") or self.is_goal_id(
            RadarDevice.BEHAVIOR_TYPE_BEDROOM
        )

    def is_in_bathroom(self, botengine):
        """
        :param botengine:
        :return: True if this device is in a bathroom
        """
        if self.goal_id == RadarDevice.BEHAVIOR_TYPE_BATHROOM:
            return True

        bathroom_names = [_("schlaf"), _("bath"), _("toilet"), _("shower"), _("powder")]

        for name in bathroom_names:
            if name in self.description.lower():
                return True

        return self.is_in_space(botengine, "bathroom") or self.is_goal_id(
            RadarDevice.BEHAVIOR_TYPE_BATHROOM
        )

    # ===========================================================================
    # Attributes
    # ===========================================================================
    def did_change_fall_status(self, botengine):
        """
        Did the fall status get updated
        :param botengine:
        :return: True if the fall status changed
        """
        if RadarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            if RadarDevice.MEASUREMENT_NAME_FALL_STATUS in self.last_updated_params:
                return True

        return False

    def get_fall_status(self, botengine):
        """
        Retrieve the most recent fall status value
        :param botengine:
        :return:
        """
        if RadarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements:
            return self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0][0]
        return None

    def get_previous_fall_status(self, botengine):
        """
        Retrieve the most recent fall status value
        :param botengine:
        :return:
        """
        if (
            RadarDevice.MEASUREMENT_NAME_FALL_STATUS in self.measurements
            and len(self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS]) > 1
        ):
            return self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][1][0]
        return None

    def is_detecting_fall(self, botengine):
        """
        Is this Radar device detecting any kind of fall
        :param botengine: BotEngine
        :return: True if this Radar device is detecting a fall (calling)
        """
        return self.get_fall_status(botengine) == RadarDevice.FALL_STATUS_CALLING

    def did_stop_detecting_fall(self, botengine):
        """
        Did this Radar device finish detecting a fall after having previously detecting one?
        :param botengine:
        :return: True if a fall is no longer detected
        """
        status = self.get_fall_status(botengine)
        previous_status = self.get_previous_fall_status(botengine)
        did_update = self.did_change_fall_status(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|did_stop_detecting_fall() "
            + utilities.Color.RED
            + "status={} previous_status={} did_update={}".format(
                status, previous_status, did_update
            )
            + utilities.Color.END
        )
        if status is not None and previous_status is not None and did_update:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return (
                status == RadarDevice.FALL_STATUS_FINISHED
                and previous_status == RadarDevice.FALL_STATUS_CALLING
            )

        return False

    def did_cancel_confirmed_fall(self, botengine):
        """
        Did this Radar device cancel a confirmed fall after having previously confirming one?
        :param botengine:
        :return: True if a fall is no longer detected
        """
        status = self.get_fall_status(botengine)
        previous_status = self.get_previous_fall_status(botengine)
        did_update = self.did_change_fall_status(botengine)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|did_cancel_confirmed_fall() "
            + utilities.Color.RED
            + "status={} previous_status={} did_update={}".format(
                status, previous_status, did_update
            )
            + utilities.Color.END
        )
        if status is not None and previous_status is not None and did_update:
            # We have more than one fallStatus measurement captured, and the latest parameter to get updated was fallStatus.
            # Make sure this newest parameter says we have exited a fall, and the last parameter did say we were calling a fall.
            return (
                status == RadarDevice.FALL_STATUS_CANCELLED
                and previous_status == RadarDevice.FALL_STATUS_CONFIRMED
            )

        return False

    def did_update_fall_position(self, botengine):
        """
        Check if fall position has changed
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        measurements = [
            RadarDevice.MEASUREMENT_NAME_FALL_LOC_X,
            RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y,
            RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z,
        ]
        return any(
            [measurement in self.last_updated_params for measurement in measurements]
        )

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
        if RadarDevice.MEASUREMENT_NAME_FALL_STATUS not in self.measurements:
            return {}
        # Build a time range to extract from the cache including the upper bounds by adding 1 ms to the newest or current timestamp
        time_range = range(
            oldest_timestamp_ms
            or newest_timestamp_ms
            or self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0][1],
            (
                newest_timestamp_ms
                or self.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0][1]
            )
            + 1,
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

            fall_x_locations = (
                [
                    positional_measurement[0]
                    for positional_measurement in self.measurements[
                        RadarDevice.MEASUREMENT_NAME_FALL_LOC_X
                    ]
                    if positional_measurement[1] <= timestamp
                ]
                if RadarDevice.MEASUREMENT_NAME_FALL_LOC_X in self.measurements
                else []
            )
            fall_y_locations = (
                [
                    positional_measurement[0]
                    for positional_measurement in self.measurements[
                        RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y
                    ]
                    if positional_measurement[1] <= timestamp
                ]
                if RadarDevice.MEASUREMENT_NAME_FALL_LOC_X in self.measurements
                else []
            )
            fall_z_locations = (
                [
                    positional_measurement[0]
                    for positional_measurement in self.measurements[
                        RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z
                    ]
                    if positional_measurement[1] <= timestamp
                ]
                if RadarDevice.MEASUREMENT_NAME_FALL_LOC_X in self.measurements
                else []
            )

            # Skip fall positions that are not complete
            if any(
                [
                    len(positional_measurement) == 0
                    for positional_measurement in [
                        fall_x_locations,
                        fall_y_locations,
                        fall_z_locations,
                    ]
                ]
            ):
                continue
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|get_fall_positions() fall_x_locations={}".format(fall_x_locations)
            )
            position = {
                "x": fall_x_locations[0],
                "y": fall_y_locations[0],
                "z": fall_z_locations[0],
            }
            fall_positions[timestamp] = position

        # Sort newest to oldest
        sorted_positions = dict(sorted(fall_positions.items(), reverse=True))
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_fall_positions() fall_positions={}".format(sorted_positions)
        )
        return sorted_positions

    def did_update_bed_status(self, botengine):
        """
        Check if bed status has changed
        :param botengine: BotEngine environment
        :return: True if we updated the bed status (to False)
        """
        return RadarDevice.MEASUREMENT_NAME_BED_STATUS in self.last_updated_params

    def get_bed_status(self, botengine):
        """
        Get the current bed status
        Note: This will always report as False (not in bed) because the device does not report in-bed status.  This is a placeholder for future functionality.
        :param botengine:
        :return:
        """
        if RadarDevice.MEASUREMENT_NAME_BED_STATUS in self.measurements:
            return self.measurements[RadarDevice.MEASUREMENT_NAME_BED_STATUS][0][0]
        return None

    def set_enter_duration(self, botengine, enter_duration):
        """
        The minimum detection time required to establish presence in the arena, in seconds.
        Default: 120
        :param botengine: BotEngine
        :param enter_duration: Duration in seconds
        """
        pass

    def get_enter_duration(self, botengine):
        """
        The minimum detection time required to establish presence in the arena, in seconds.
        Default: 120
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        return 120

    def set_exit_duration(self, botengine, exit_duration):
        """
        The minimum detection time required to establish non-presence in the arena, in seconds.
        Default: 120
        :param botengine: BotEngine
        :param exit_duration: Duration in seconds
        """
        pass

    def get_exit_duration(self, botengine):
        """
        The minimum detection time required to establish non-presence in the arena, in seconds.
        Default: 120
        :param botengine: BotEngine
        :return: Duration in seconds
        """
        return 120

    def did_update_occupancy(self, botengine):
        """
        Did we get new occupancy data
        :param botengine: BotEngine environment
        :return: True if we updated occupancy
        """
        return RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params

    def get_occupancy(
        self, botengine, oldest_timestamp_ms=None, newest_timestamp_ms=None
    ):
        """
        Get the current occupancy the Radar device is tracking

        You can optionally pass in a range of time to extract from the locally available 1-hour cache, with oldest_timestamp_ms and newest_timestamp_ms.

        If a range (both oldest and newest timestamp) is not specified, then this will only return the latest measurement and will ignore targets that are older than 30 minutes or from a disconnected device

        :param botengine:
        :param oldest_timestamp_ms:
        :param newest_timestamp_ms:
        :return: Dictionary of occupancy of the form { timestamp_ms : 1, ... }
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_occupancy()"
        )

        occupancy = {}
        if self.is_connected:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "|get_occupancy() occupancy={}".format(
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY]
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

                for t in self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY]:
                    if t[1] < oldest_timestamp_ms:
                        break

                    if t[1] > newest_timestamp_ms:
                        continue

                    occupancy[t[1]] = t[0]

                    if not extract_multiple:
                        break
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<get_occupancy() occupancy={}".format(occupancy)
        )
        return occupancy

    def did_update_occupancy_targets(self, botengine):
        """
        Did we get new occupancy target data
        :param botengine: BotEngine environment
        :return: True if we updated targets
        """
        return RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in self.last_updated_params

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
        targets = {}

        if self.is_connected:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET in self.measurements:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "|get_occupancy_targets() pure targets={}".format(
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET]
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

                for t in self.measurements[
                    RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET
                ]:
                    if t[1] < oldest_timestamp_ms:
                        break

                    if t[1] > newest_timestamp_ms:
                        continue

                    targets[t[1]] = self._extract_targets(t[0])

                    if not extract_multiple:
                        break
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<get_occupancy_targets() targets={}".format(targets)
        )
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

    def did_start_detecting_motion(self, botengine):
        """
        Helpful for translation to existing motion sensor functionality.

        Recommend using signals/motion.py with the appropriate microservice driving those signals for more serious motion detection work.

        :param botengine: BotEngine
        :return: True if the Radar did start detecting occupancy.
        """
        return self.did_start_detecting_occupancy(botengine)

    def is_detecting_occupancy(self, botengine):
        """
        True if this device is detecting an occupant, as indicated by the 'occupancy' parameter and not our targets
        :param botengine:
        :return:
        """
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                return (
                    self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0] == 1
                )
        return False

    def did_start_detecting_occupancy(self, botengine):
        """
        Did the Radar device start detecting occupancy in this room
        :param botengine:
        :return: True if occupants have entered the room
        """
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return (
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0]
                        == 1
                    )

        return False

    def did_stop_detecting_occupancy(self, botengine):
        """
        Did the Radar device stop detecting occupancy in this room
        :param botengine:
        :return: True if occupants have left the room
        """
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.measurements:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY in self.last_updated_params:
                if len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY]) > 0:
                    return (
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY][0][0]
                        == 0
                    )

        return False

    def set_room_boundaries(self, botengine, content={}):
        """
        Set the boundaries of the room.
        :param botengine: BotEngine environment
        :param content: Dictionary with room boundaries
        """
        pass

    def did_update_room_boundaries(self, botengine):
        """
        Determine if we updated the room boundaries in this execution
        :param botengine: BotEngine environment
        :return: True if we updated the room boundaries in this execution
        """
        return False

    def get_room_boundaries(self, botengine):
        """
        Return the boundaries of this room in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        x_min = RadarDevice.X_MIN_METERS_WALL
        x_max = RadarDevice.X_MAX_METERS_WALL
        y_min = RadarDevice.Y_MIN_METERS_WALL
        y_max = RadarDevice.Y_MAX_METERS_WALL
        z_min = RadarDevice.Z_MIN_METERS_WALL
        z_max = RadarDevice.Z_MAX_METERS_WALL
        mounting_type = 0
        sensor_height_m = 1.5
        updated_ms = 0

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
            "near_exit": self.near_exit,
        }

    def get_room_boundaries_properties(self, botengine):
        """
        Return the boundaries of this room FROM THE DEVICE PROPERTY in the form of a dictionary, and include an "updated_ms" value declaring the newest update timestamp in milliseconds.
        Note that some values will be internal default values if they haven't be reported by the device yet.
        :param botengine:
        :return: Dictionary with room boundaries
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">get_room_boundaries_properties()"
        )
        content = {}
        device_properties = botengine.get_device_property(self.device_id, "room")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "|get_room_boundaries_properties() device_properties={}".format(
                device_properties
            )
        )
        if device_properties is not None:
            import json

            for device_property in device_properties:
                property_name = device_property["name"]
                if property_name == "room":
                    content = json.loads(device_property["value"])

        if content == {}:
            # Check if the room boundaries are defined in the non-volatile memory
            nv_room = botengine.get_state("radar_room")
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "|get_room_boundaries_properties() nv_room={}".format(nv_room)
            )
            # Backwards compatibility
            if nv_room is None:
                nv_room = botengine.get_state("vayyar_room")
            if nv_room is not None and self.device_id in nv_room:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    "|get_room_boundaries_properties() Room has not been set, using non-volatile location state"
                )
                content = nv_room[self.device_id]

        x_min = content.get("x_min_meters", RadarDevice.X_MIN_METERS_WALL)
        x_max = content.get("x_max_meters", RadarDevice.X_MAX_METERS_WALL)
        y_min = content.get("y_min_meters", RadarDevice.Y_MIN_METERS_WALL)
        y_max = content.get("y_max_meters", RadarDevice.Y_MAX_METERS_WALL)
        z_min = content.get("z_min_meters", RadarDevice.Z_MIN_METERS_WALL)
        z_max = content.get("z_max_meters", RadarDevice.Z_MAX_METERS_WALL)
        mounting_type = content.get("mounting_type", RadarDevice.SENSOR_MOUNTING_WALL)
        sensor_height_m = content.get("sensor_height_m", 1.5)
        updated_ms = content.get("updated_ms", 0)

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
            "near_exit": self.near_exit,
        }
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<get_room_boundaries_properties() room_boundaries={}".format(
                room_boundaries
            )
        )
        return room_boundaries

    def record_subregion(self, botengine, unique_id, context_id, name):
        """
        Record the existence of a subregion without saving it to the device, so
        microservices can quickly check if we have a particular subregion defined.
        :param botengine: BotEngine
        :param unique_id: Unique ID to add/update
        :param context_id: Context ID of the subregion
        :param name: Name of the subregion
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "|record_subregion() '{}': Recording subregion - unique_id={}; context_id={}; name={}".format(
                self.description, unique_id, context_id, name
            )
        )
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
            if radar.is_same_general_context(target_context_id, context_id):
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
        relevant_subregions = self.subregions_with_context(
            botengine, radar.SUBREGION_CONTEXT_WALK_IN_SHOWER
        )
        for unique_id, context_id, name in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def is_in_chair(self, botengine):
        """
        Is a person in a chair subregion
        :param botengine: BotEngine
        :return: True if we have knowledge the person is in the chair
        """
        relevant_subregions = self.subregions_with_context(
            botengine, radar.SUBREGION_CONTEXT_CHAIR
        )
        for unique_id, context_id, name in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def is_in_bed(self, botengine):
        """
        Is a person in a bed subregion
        :param botengine: BotEngine
        :return: True if we have knowledge the person is in the bed
        """
        relevant_subregions = self.subregions_with_context(
            botengine, radar.SUBREGION_CONTEXT_BED
        )
        for unique_id, context_id, name in relevant_subregions:
            if unique_id in self.knowledge_occupied_subregions:
                return True

        return False

    def set_subregions(self, botengine, content={}):
        """
        Send a complete list of subregions to the device.

        :param botengine: BotEngine environment
        :param content: Dictionary with subregion information
        """
        pass

    def did_update_subregions(self, botengine):
        """
        Did this Radar device update subregions
        :param botengine:
        :return:
        """
        return False

    def get_subregions(self, botengine):
        """
        Get a list of subregions reported by the device, if there are any.
        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        return None

    def get_raw_subregions(self, botengine):
        """
        Get a list of subregions reported by the device, if there are any.

        :param botengine: BotEngine environment
        :return: Subregion list, or None if it doesn't exist.
        """
        return []

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

        Limit the number of subregions to 6, described by the device.
        Only 2 doors are allowed, and are always at the end of the list.
        Beds are represented first.
        :param botengine: BotEngine environment
        :return: Tuple of sorted subregion lists for both device API and native services
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">get_sorted_subregions() device_id={} subregion_list={} submit_all={} z_min_meters={} z_max_meters={}".format(
                self.device_id, subregion_list, submit_all, z_min_meters, z_max_meters
            )
        )

        api_subregion_list = []
        native_subregion_list = []

        number_of_doors = 0

        for s in subregion_list.get(self.device_id, []):
            if number_of_doors >= 2 and s.get("is_door", False):
                # Only 2 doors allowed
                continue
            # Only allow subregions that ignore presence to optimize data consumption from the Radar
            if not s["detect_presence"] or submit_all:
                if "z_min_meters" in s and "z_max_meters" in s:
                    if (
                        s["z_min_meters"] != z_min_meters
                        or s["z_max_meters"] != z_max_meters
                    ):
                        # This subregion is smaller than an X,Y area - it's a 3D space so let's not ignore the whole X,Y area.
                        continue

                # We want to ignore the full area, leverage the radar to do that.
                subregion = {
                    "xMin": s["x_min_meters"],
                    "xMax": s["x_max_meters"],
                    "yMin": s["y_min_meters"],
                    "yMax": s["y_max_meters"],
                    "zMin": s.get("z_min_meters", z_min_meters),
                    "zMax": s.get("z_max_meters", z_max_meters),
                    "isFallingDetection": s.get("detect_falls", False),
                    "isPresenceDetection": s.get("detect_presence", True),
                    "enterDuration": s.get(
                        "enter_duration_s", radar.DEFAULT_ENTER_DURATION
                    ),
                    "exitDuration": s.get(
                        "exit_duration_s", radar.DEFAULT_EXIT_DURATION
                    ),
                    "isLowSnr": s.get("low_sensor_energy", True),
                    "isDoor": s.get("is_door", False),
                }
                number_of_doors += 1 if subregion["isDoor"] else 0
                if "name" in s:
                    subregion["name"] = s["name"]

                if radar.is_context_bed(
                    s.get("context_id", radar.SUBREGION_CONTEXT_IGNORE)
                ):
                    subregion["context_id"] = s["context_id"]
                api_subregion_list.append(subregion)
                native_subregion_list.append(s.copy())

        # Sort subregions so that the list is prioritized in the following order: 1) Bed, 2) Door, 3) Largest Area
        api_subregion_list.sort(
            key=lambda s: abs(s["xMax"] - s["xMin"]) * abs(s["yMax"] - s["yMin"]),
            reverse=True,
        )
        native_subregion_list.sort(
            key=lambda s: abs(s["x_max_meters"] - s["x_min_meters"])
            * abs(s["y_max_meters"] - s["y_min_meters"]),
            reverse=True,
        )
        api_subregion_list.sort(key=lambda s: 1 if s["isDoor"] else 0, reverse=True)
        native_subregion_list.sort(key=lambda s: 1 if s["is_door"] else 0, reverse=True)
        api_subregion_list.sort(
            key=lambda s: 1
            if radar.is_context_bed(s.get("context_id", radar.SUBREGION_CONTEXT_IGNORE))
            else 0,
            reverse=True,
        )
        native_subregion_list.sort(
            key=lambda s: 1
            if radar.is_context_bed(s.get("context_id", radar.SUBREGION_CONTEXT_IGNORE))
            else 0,
            reverse=True,
        )

        # Remove "context_id" from the sorted lists
        for s in api_subregion_list:
            if "context_id" in s:
                del s["context_id"]

        # Make sure we don't have more than 6
        del api_subregion_list[RadarDevice.MAXIMUM_SUBREGIONS :]
        del native_subregion_list[RadarDevice.MAXIMUM_SUBREGIONS :]

        # Sort door subregions to be at last in our list
        api_subregion_list.sort(key=lambda s: 1 if s["isDoor"] else 0)
        native_subregion_list.sort(key=lambda s: 1 if s["is_door"] else 0)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<get_sorted_subregions() device_id={} api_subregion_list={} native_subregion_list={}".format(
                self.device_id, api_subregion_list, native_subregion_list
            )
        )
        return (api_subregion_list, native_subregion_list)

    def get_subregion_index(self, botengine, subregion):
        """
        Return the index of a locally stored subregion represented on the device.
        :param botengine: BotEngine environment
        :param subregion: Subregion object
        :return: Index of the subregion, or None if it is not stored on the device.
        """
        return None

    def did_subregion_occupancy_change(self, botengine):
        """
        Determine if subregion occupancy may have changed at all on this execution,
        as evidenced by receiving a new value for the 'occupancyMap' parameter.

        :param botengine: BotEngine environment
        :return: True if subregion occupancy may have been updated in this execution
        """
        return RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params

    def get_subregions_entered(self, botengine):
        """
        Get a list of subregion indices that were just entered.
        This does not provide context.
        :param botengine: BotEngine environment
        :return: List of subregion indices that were just entered, like [0, 2, 3] or [].
        """
        entered = []
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
                if (
                    len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP])
                    > 1
                ):
                    m_new = self._to_subregion_indices(
                        botengine,
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][
                            0
                        ][0],
                    )
                    m_old = self._to_subregion_indices(
                        botengine,
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][
                            1
                        ][0],
                    )
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        "|get_subregions_entered() m_new={} m_old={}".format(
                            m_new, m_old
                        )
                    )

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
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
            if len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP]) > 1:
                m_new = self._to_subregion_indices(
                    botengine,
                    self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0][0],
                )
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "|get_subregions_occupied() m_new={}".format(m_new)
                )
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
        if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.last_updated_params:
            if RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP in self.measurements:
                if (
                    len(self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP])
                    > 1
                ):
                    m_new = self._to_subregion_indices(
                        botengine,
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][
                            0
                        ][0],
                    )
                    m_old = self._to_subregion_indices(
                        botengine,
                        self.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][
                            1
                        ][0],
                    )

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        "|get_subregions_exited() m_new={} m_old={}".format(
                            m_new, m_old
                        )
                    )
                    for i in range(0, len(m_new)):
                        if not m_new[i] and m_old[i]:
                            exited.append(i)

        return exited

    def _to_subregion_indices(self, botengine, subregion_str):
        """
        Convert "101000" to [1, 0, 1, 0, 0, 0]

        :param subregion_str: Subregion string like "0" or "010000"
        :return: Subregion list [0, 0, 0, 0, 0, 0] or [0, 1, 0, 0, 0, 0]
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">_to_subregion_indices() subregion_str={}".format(subregion_str)
        )
        if int(subregion_str) == 0:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                "<_to_subregion_indices() indices={}".format([0, 0, 0, 0, 0, 0])
            )
            return [0, 0, 0, 0, 0, 0]

        indices = []
        for i in str(subregion_str):
            indices.append(int(i))

        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<_to_subregion_indices() indices={}".format(indices)
        )
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
            targets[identifier] = {"x": int(x), "y": int(y), "z": int(z)}

        return targets
