import json
import unittest
from unittest.mock import MagicMock

import signals.radar as radar
import utilities.utilities as utilities
from devices.radar.vayyar.radar import RadarVayyarDevice
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestRadarVayyarDevice(unittest.TestCase):
    # TODO: Address vayyar sensor mounting type 3 (Wall at 45)
    def test_device_vayyar_init(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = RadarVayyarDevice(
            botengine, location_object, device_id, device_type, device_desc
        )

        assert mut.location_object == location_object
        assert mut.device_id == device_id
        assert mut.device_type == device_type
        assert mut.description == device_desc
        assert mut.measurements == {}
        assert mut.last_alert == {}
        assert mut.spaces == []
        assert mut.last_updated_params == []
        assert mut.battery_level == 100
        assert mut.battery_levels == []
        assert mut.last_battery_update_ms == 0
        assert not mut.low_battery
        assert not mut.is_connected
        assert not mut.can_control
        assert not mut.can_read
        assert mut.remote_addr_hash is None
        assert mut.proxy_id is None
        assert mut.goal_id == RadarVayyarDevice.BEHAVIOR_TYPE_OTHER
        assert not mut.is_goal_changed
        assert mut.latitude is None
        assert mut.longitude is None
        assert mut.born_on is botengine.get_timestamp()
        assert mut.enforce_cache_size
        assert mut.total_communications_odometer == 0
        assert mut.communications_odometer == 0
        assert mut.measurement_odometer == 0
        assert mut.last_communications_timestamp is None
        assert mut.intelligence_modules == {}

        assert mut.information_total_occupants == 0
        assert mut.knowledge_total_occupants == 0
        assert mut.fall_count == 0
        assert mut.stability_event_count == 0
        assert not mut.near_exit
        assert mut.subregions == {}
        assert mut.information_occupied_subregions == []
        assert mut.knowledge_occupied_subregions == []
        assert mut.learning_mode_status == RadarVayyarDevice.LEARNING_MODE_REST

    def test_device_vayyar_intelligence_modules(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarVayyarDevice(
            botengine, location_object, device_id, device_type, device_desc
        )
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        # Depending on the bot bundle under testing there may or may not be device intelligence modules
        # If available, ensure the parent and intelligence_id are set
        for i in mut.intelligence_modules:
            assert mut.intelligence_modules[i].intelligence_id is not None
            assert mut.intelligence_modules[i].parent == mut

    def test_device_vayyar_attributes(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["vayyar"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarVayyarDevice(
            botengine, location_object, device_id, device_type, device_desc
        )
        mut.is_connected = True

        mut.measurements = {}
        mut.last_updated_params = []

        # Test results without measurements
        assert not mut.did_change_fall_status(botengine)
        assert not mut.did_update_leds(botengine)
        assert not mut.did_update_volume(botengine)

        assert mut.get_fall_status(botengine) is None
        assert mut.get_previous_fall_status(botengine) is None
        assert mut.get_leds(botengine) is None
        assert mut.get_volume(botengine) is None
        assert mut.get_telemetry_policy(botengine) is None

        assert mut.get_previous_fall_status(botengine) is None
        assert not mut.is_detecting_stability_event(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)
        assert not mut.did_update_fall_position(botengine)
        assert mut.get_fall_positions(botengine) == {}
        assert not mut.did_update_fall_learning(botengine)
        assert mut.get_fall_learning(botengine) is None
        assert not mut.did_update_bed_status(botengine)
        assert mut.get_bed_status(botengine) is None
        assert not mut.did_update_occupancy_targets(botengine)
        assert mut.get_occupancy_targets(botengine) == {}
        assert mut.get_newest_targets(botengine) == {}
        assert mut.need_start_learning(botengine)
        assert not mut.did_start_detecting_motion(botengine)
        assert not mut.is_detecting_occupancy(botengine)
        assert not mut.did_start_detecting_occupancy(botengine)
        assert not mut.did_stop_detecting_occupancy(botengine)
        assert not mut.did_boot(botengine)
        assert not mut.did_press_button(botengine)
        assert not mut.button_press_duration(botengine)
        assert mut.get_learning_mode_end(botengine) == 0
        assert not mut.get_falling_mitigator(botengine)
        assert mut.get_enter_duration(botengine) == 120
        assert mut.get_exit_duration(botengine) == 120
        assert mut.get_duration_until_confirm_sec(botengine) == 52
        assert mut.get_min_time_of_target_in_fall_location(botengine) == 30
        assert mut.get_dry_contact_activation_duration_sec(botengine) == 30
        assert not mut.get_enable_above_th_point_telemetry_enables(botengine)
        assert not mut.get_test_mode(botengine)
        assert mut.get_offline_mode(botengine)
        assert mut.get_dry_contacts(botengine) is None
        assert not mut.get_demo_mode(botengine)
        assert not mut.get_door_events(botengine)
        assert not mut.get_out_of_bed_enabled(botengine)
        assert not mut.get_sensitive_mode(botengine)
        assert mut.get_sensitivity_level(botengine) == 0.78
        assert mut.get_min_events_for_first_decision(botengine) == 5
        assert mut.get_num_of_detections_in_chain(botengine) == 4
        assert not mut.did_update_room_boundaries(botengine)
        assert (
            mut.get_mounting_type(botengine) == RadarVayyarDevice.SENSOR_MOUNTING_WALL
        )
        assert mut.get_room_boundaries(botengine) == {
            "x_min_meters": RadarVayyarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarVayyarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarVayyarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarVayyarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarVayyarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarVayyarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False,
        }
        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": RadarVayyarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarVayyarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarVayyarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarVayyarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarVayyarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarVayyarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False,
        }

        # Test results with device properties and state
        botengine.device_properties[device_id] = [
            {
                "name": "room",
                "value": json.dumps(
                    {
                        "x_min_meters": -1.0,
                        "x_max_meters": 1.0,
                        "y_min_meters": -1.0,
                        "y_max_meters": 1.0,
                        "z_min_meters": 0,
                        "z_max_meters": 1.0,
                        "mounting_type": 1,
                        "sensor_height_m": 2.3,
                        "updated_ms": botengine.get_timestamp(),
                        "near_exit": False,
                    }
                ),
            }
        ]

        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": -1.0,
            "x_max_meters": 1.0,
            "y_min_meters": -1.0,
            "y_max_meters": 1.0,
            "z_min_meters": 0,
            "z_max_meters": 1.0,
            "mounting_type": 1,
            "sensor_height_m": 2.3,
            "updated_ms": botengine.get_timestamp(),
            "near_exit": False,
        }

        del botengine.device_properties[device_id]

        botengine.states["vayyar_room"] = {
            device_id: {
                "x_min_meters": -1.0,
                "x_max_meters": 1.0,
                "y_min_meters": -1.0,
                "y_max_meters": 1.0,
                "z_min_meters": 0,
                "z_max_meters": 1.0,
                "mounting_type": 1,
                "sensor_height_m": 2.3,
                "updated_ms": botengine.get_timestamp(),
                "near_exit": False,
            }
        }

        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": -1.0,
            "x_max_meters": 1.0,
            "y_min_meters": -1.0,
            "y_max_meters": 1.0,
            "z_min_meters": 0,
            "z_max_meters": 1.0,
            "mounting_type": 1,
            "sensor_height_m": 2.3,
            "updated_ms": botengine.get_timestamp(),
            "near_exit": False,
        }

        del botengine.states["vayyar_room"]

        # Test results with measurements
        mut.measurements = {
            RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS: [
                (RadarVayyarDevice.FALL_STATUS_DETECTED, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_VOLUME: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_FALL_LEARNING: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_BED_STATUS: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET: [
                ("0:0,0,0", botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_LEARNING_MODE_END: [
                (
                    botengine.get_timestamp() + (2 * utilities.ONE_WEEK_MS),
                    botengine.get_timestamp(),
                ),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_ENTER_DURATION: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_EXIT_DURATION: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_TEST_MODE: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_OFFLINE_MODE: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_CALLING_DURATION_SEC: [
                (10, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACTS: [
                (
                    {
                        "primary": {"mode": 0, "policy": 0},
                        "secondary": {"mode": 0, "policy": 0},
                    },
                    botengine.get_timestamp(),
                ),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DEMO_MODE: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DOOR_EVENTS: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_OUT_OF_BED: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVE_MODE: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVITY_LEVEL: [
                (0.5, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_DETECTIONS_IN_CHAIN: [
                (1, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_X_MIN: [
                (-1.0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_X_MAX: [
                (1.0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN: [
                (-1.0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX: [
                (1.0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN: [
                (0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX: [
                (1.0, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING: [
                (RadarVayyarDevice.SENSOR_MOUNTING_CEILING, botengine.get_timestamp()),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT: [
                (2.3, botengine.get_timestamp()),
            ],
        }
        mut.last_updated_params = [
            RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS,
            RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE,
            RadarVayyarDevice.MEASUREMENT_NAME_VOLUME,
            RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY,
            RadarVayyarDevice.MEASUREMENT_NAME_FALL_LEARNING,
            RadarVayyarDevice.MEASUREMENT_NAME_BED_STATUS,
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET,
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY,
            RadarVayyarDevice.MEASUREMENT_NAME_X_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_X_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN,
            RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX,
            RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
            RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
        ]
        assert mut.did_change_fall_status(botengine)
        assert mut.did_update_leds(botengine)
        assert mut.did_update_volume(botengine)

        assert mut.get_fall_status(botengine) == RadarVayyarDevice.FALL_STATUS_DETECTED
        assert mut.get_leds(botengine) == 1
        assert mut.get_volume(botengine) == 0
        assert mut.get_telemetry_policy(botengine) == 0

        assert mut.get_previous_fall_status(botengine) is None
        assert not mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)
        assert not mut.did_update_fall_position(botengine)
        assert mut.get_fall_positions(botengine) == {}
        assert mut.did_update_fall_learning(botengine)
        assert mut.get_fall_learning(botengine) == 0
        assert mut.did_update_bed_status(botengine)
        assert mut.get_bed_status(botengine) == 0
        assert mut.did_update_occupancy_targets(botengine)
        assert mut.get_occupancy_targets(botengine) == {
            botengine.get_timestamp(): {"0": {"x": 0, "y": 0, "z": 0}}
        }
        assert mut.get_newest_targets(botengine) == {"0": {"x": 0, "y": 0, "z": 0}}
        assert mut.did_start_detecting_motion(botengine)
        assert mut.is_detecting_occupancy(botengine)
        assert mut.did_start_detecting_occupancy(botengine)
        assert not mut.did_stop_detecting_occupancy(botengine)
        assert mut.get_learning_mode_end(botengine) == botengine.get_timestamp() + (
            2 * utilities.ONE_WEEK_MS
        )
        assert mut.get_falling_mitigator(botengine) == 1
        assert mut.get_enter_duration(botengine) == 10
        assert mut.get_exit_duration(botengine) == 10
        assert mut.get_duration_until_confirm_sec(botengine) == 10
        assert mut.get_min_time_of_target_in_fall_location(botengine) == 10
        assert mut.get_dry_contact_activation_duration_sec(botengine) == 10
        assert mut.get_enable_above_th_point_telemetry_enables(botengine) == 1
        assert mut.get_test_mode(botengine) == 1
        assert mut.get_offline_mode(botengine) == 0
        assert mut.get_dry_contacts(botengine) == {
            "primary": {"mode": 0, "policy": 0},
            "secondary": {"mode": 0, "policy": 0},
        }
        assert mut.get_demo_mode(botengine) == 1
        assert mut.get_door_events(botengine) == 1
        assert mut.get_out_of_bed_enabled(botengine) == 1
        assert mut.get_sensitive_mode(botengine) == 1
        assert mut.get_sensitivity_level(botengine) == 0.5
        assert mut.get_min_events_for_first_decision(botengine) == 1
        assert mut.get_num_of_detections_in_chain(botengine) == 1
        assert mut.did_update_room_boundaries(botengine)
        assert (
            mut.get_mounting_type(botengine)
            == RadarVayyarDevice.SENSOR_MOUNTING_CEILING
        )
        assert mut.get_room_boundaries(botengine) == {
            "x_min_meters": -1.0,
            "x_max_meters": 1.0,
            "y_min_meters": -1.0,
            "y_max_meters": 1.0,
            "z_min_meters": 0,
            "z_max_meters": 1.0,
            "mounting_type": 1,
            "sensor_height_m": 2.3,
            "updated_ms": botengine.get_timestamp(),
            "near_exit": False,
        }
        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": RadarVayyarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarVayyarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarVayyarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarVayyarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarVayyarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarVayyarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": botengine.get_timestamp(),
            "near_exit": False,
        }

        # Test results with additional measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_X] = []
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Y] = []
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Z] = []

        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_X].append(
            (0, botengine.get_timestamp())
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Y].append(
            (0, botengine.get_timestamp())
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Z].append(
            (0, botengine.get_timestamp())
        )

        mut.last_updated_params.append(RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_X)
        mut.last_updated_params.append(RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Y)
        mut.last_updated_params.append(RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Z)

        assert mut.did_update_fall_position(botengine)
        assert mut.get_fall_positions(botengine) == {
            botengine.get_timestamp(): {"x": 0, "y": 0, "z": 0}
        }

        # Test results with additional measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS].append(
            (
                RadarVayyarDevice.FALL_STATUS_FINISHED,
                botengine.get_timestamp() - utilities.ONE_MINUTE_MS,
            )
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_X].append(
            (1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS)
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Y].append(
            (1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS)
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_LOC_Z].append(
            (1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS)
        )

        assert (
            mut.get_previous_fall_status(botengine)
            == RadarVayyarDevice.FALL_STATUS_FINISHED
        )

        assert not mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)

        assert mut.did_update_fall_position(botengine)
        assert mut.get_fall_positions(botengine) == {
            botengine.get_timestamp(): {"x": 0, "y": 0, "z": 0}
        }
        assert mut.get_fall_positions(
            botengine,
            oldest_timestamp_ms=botengine.get_timestamp() - utilities.ONE_MINUTE_MS,
        ) == {
            botengine.get_timestamp() - utilities.ONE_MINUTE_MS: {
                "x": 1,
                "y": 1,
                "z": 1,
            },
            botengine.get_timestamp(): {"x": 0, "y": 0, "z": 0},
        }
        assert mut.get_fall_positions(
            botengine,
            newest_timestamp_ms=botengine.get_timestamp() - utilities.ONE_MINUTE_MS,
        ) == {
            botengine.get_timestamp() - utilities.ONE_MINUTE_MS: {
                "x": 1,
                "y": 1,
                "z": 1,
            }
        }

        # Test results with additional measurements and completed learning mode
        mut.learning_mode_status = RadarVayyarDevice.LEARNING_MODE_DONE

        assert mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)
        assert not mut.need_start_learning(botengine)

        # Test results with different measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (
            RadarVayyarDevice.FALL_STATUS_DETECTED,
            botengine.get_timestamp(),
        )

        assert mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)

        # Test results with different measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (
            RadarVayyarDevice.FALL_STATUS_CALLING,
            botengine.get_timestamp(),
        )

        assert not mut.is_detecting_stability_event(botengine)
        assert mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)

        # Test results with different measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (
            RadarVayyarDevice.FALL_STATUS_FINISHED,
            botengine.get_timestamp(),
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][1] = (
            RadarVayyarDevice.FALL_STATUS_CALLING,
            botengine.get_timestamp() - utilities.ONE_MINUTE_MS,
        )

        assert not mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert mut.did_stop_detecting_fall(botengine)
        assert not mut.did_cancel_confirmed_fall(botengine)

        # Test results with different measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (
            RadarVayyarDevice.FALL_STATUS_CANCELLED,
            botengine.get_timestamp(),
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_FALL_STATUS][1] = (
            RadarVayyarDevice.FALL_STATUS_CONFIRMED,
            botengine.get_timestamp() - utilities.ONE_MINUTE_MS,
        )

        assert not mut.is_detecting_stability_event(botengine)
        assert not mut.is_detecting_fall(botengine)
        assert not mut.did_stop_detecting_fall(botengine)
        assert mut.did_cancel_confirmed_fall(botengine)

        # Test results with different measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY][0] = (
            0,
            botengine.get_timestamp(),
        )

        assert mut.did_stop_detecting_occupancy(botengine)

        # Test results with alerts

        mut.last_alert = {
            "boot": {
                "timestamp_ms": botengine.get_timestamp(),
                "version_name": "vayyar-care-0xdf16f335-walabot-home-v0.40.20",
                "reset_reason": "SW",
            },
            "SW_initiated_reboot": {
                "timestamp_ms": botengine.get_timestamp(),
                "reason": "RebootRequired",
            },
            "low_wifi_signal": {
                "timestamp_ms": botengine.get_timestamp(),
                "rssi": "-83",
            },
            "on": {
                "timestamp_ms": botengine.get_timestamp(),
            },
            "http": {
                "timestamp_ms": botengine.get_timestamp(),
                "url": "https://app.peoplepowerco.com/espapi/integration/v",
                "method": "POST",
                "req_body_len": "47",
                "resp_code": "200",
                "resp_body_len": "352",
                "latency_ms": "1358",
            },
            "sensitivity_map": {
                "timestamp_ms": botengine.get_timestamp(),
                "is_found": "false",
            },
            "button_press": {
                "timestamp_ms": botengine.get_timestamp(),
                "press_duration_s": "1",
            },
        }

        assert mut.did_boot(botengine)
        assert mut.did_press_button(botengine)
        assert mut.button_press_duration(botengine) == "1"

        # Test results without connectivity
        mut.is_connected = False

        assert mut.get_occupancy_targets(botengine) == {}
        assert mut.get_newest_targets(botengine) == {}

        # Test with sending commands
        botengine.send_command = MagicMock()
        param_name = None
        param_value = None

        def send_command(device_id, name, value):
            botengine.get_logger("TEST").debug(
                "|send_command()       name={}       value={}".format(name, value)
            )
            botengine.get_logger("TEST").debug(
                "|send_command() param_name={} param_value={}".format(
                    param_name, param_value
                )
            )
            assert param_name == name
            assert param_value == value

        botengine.send_command.side_effect = send_command

        botengine.send_commands = MagicMock()
        all_params = None

        def send_commands(device_id, params):
            botengine.get_logger("TEST").debug(
                "|send_command()     params={}".format(params)
            )
            botengine.get_logger("TEST").debug(
                "|send_command() all_params={}".format(all_params)
            )
            assert all_params == params

        botengine.send_commands.side_effect = send_commands

        try:
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_FALLING_SENSITIVITY,
                1,
            )
            mut.set_fall_sensitivity(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_CONFIRMED_TO_ALERT_TIMEOUT_SEC,
                15,
            )
            mut.set_alert_delay_s(botengine, param_value)
            param_name, param_value = (RadarVayyarDevice.MEASUREMENT_NAME_LED_MODE, 1)
            mut.set_led_mode(botengine, param_value)
            param_name, param_value = (RadarVayyarDevice.MEASUREMENT_NAME_VOLUME, 0)
            mut.set_volume(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_TELEMTRY_POLICY,
                0,
            )
            mut.set_telemetry_policy(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_LEARNING_MODE_END,
                botengine.get_timestamp() + (2 * utilities.ONE_WEEK_MS),
            )
            mut.set_learning_mode(botengine, True)
            assert mut.learning_mode_status == RadarVayyarDevice.LEARNING_MODE_GOING
            mut.set_learning_mode(botengine, False)
            assert mut.learning_mode_status == RadarVayyarDevice.LEARNING_MODE_DONE
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_PRESENCE_REPORT_MIN_RATE_MILLS,
                5500,
            )
            mut.set_reporting_rate_ms(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_PRESENCE_PERIODIC_REPORT,
                1,
            )
            mut.set_reporting_enabled(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_SILENT_MODE,
                1,
            )
            mut.set_silent_mode(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_FALLING_MITIGATOR_ENABLED,
                1,
            )
            mut.set_falling_mitigator(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_ENTER_DURATION,
                10,
            )
            mut.set_enter_duration(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_EXIT_DURATION,
                10,
            )
            mut.set_exit_duration(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_DURATION_UNTIL_CONFIRM,
                10,
            )
            mut.set_duration_until_confirm_sec(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_MIN_TIME_OF_TAR_IN_FALL_LOC,
                10,
            )
            mut.set_min_time_of_target_in_fall_location(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACT_ACTIVATION_DURATION,
                10,
            )
            mut.set_dry_contact_activation_duration_sec(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_ABOVE_TH_POINT_TELEMETRY,
                1,
            )
            mut.set_enable_above_th_point_telemetry_enables(botengine, param_value)
            param_name, param_value = (RadarVayyarDevice.MEASUREMENT_NAME_TEST_MODE, 1)
            mut.set_test_mode(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_OFFLINE_MODE,
                0,
            )
            mut.set_offline_mode(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_CALLING_DURATION_SEC,
                10,
            )
            mut.set_calling_duration_sec(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_DRY_CONTRACTS,
                {
                    "primary": {"mode": 0, "policy": 0},
                    "secondary": {"mode": 0, "policy": 0},
                },
            )
            mut.set_dry_contacts(botengine, param_value)
            param_name, param_value = (RadarVayyarDevice.MEASUREMENT_NAME_DEMO_MODE, 1)
            mut.set_demo_mode(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_DOOR_EVENTS,
                1,
            )
            mut.set_door_events(botengine, param_value)
            param_name, param_value = (RadarVayyarDevice.MEASUREMENT_NAME_OUT_OF_BED, 1)
            mut.set_out_of_bed_enabled(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVE_MODE,
                1,
            )
            mut.set_senstive_mode(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_SENSITIVITY_LEVEL,
                0.5,
            )
            mut.set_sensitivity_level(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_MIN_EVENTS_FOR_FIRST_DECISION,
                1,
            )
            mut.set_min_events_for_first_decision(botengine, param_value)
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_DETECTIONS_IN_CHAIN,
                1,
            )
            mut.set_num_of_detections_in_chain(botengine, param_value)
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_CEILING,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 2.0,
                },
            ]
            mut.set_ceiling_mount(botengine)
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_WALL,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 1.5,
                },
            ]
            mut.set_wall_mount(botengine)
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_WALL_45_DEGREE,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 2.0,
                },
            ]
            mut.set_wall_mount(botengine, sensor_mounting=RadarVayyarDevice.SENSOR_MOUNTING_WALL_45_DEGREE, sensor_height_m=2.0)
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 1.5,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_WALL,
                },
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MIN, "value": -2.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MAX, "value": 2.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN, "value": 0.3},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX, "value": 4.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN, "value": 0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX, "value": 2.0},
            ]
            mut.set_room_boundaries(botengine)
            assert not mut.near_exit
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 1.5,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_WALL,
                },
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MIN, "value": -1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MAX, "value": 1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN, "value": 1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX, "value": 3.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN, "value": 0.5},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX, "value": 1.5},
            ]
            mut.set_room_boundaries(
                botengine,
                {
                    "x_min_meters": -1.0,
                    "x_max_meters": 1.0,
                    "y_min_meters": 1.0,
                    "y_max_meters": 3.0,
                    "z_min_meters": 0.5,
                    "z_max_meters": 1.5,
                    "near_exit": True,
                },
            )
            assert mut.near_exit
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 2.3,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_CEILING,
                },
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MIN, "value": -2.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MAX, "value": 2.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN, "value": 0.3},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX, "value": 3},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN, "value": 0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX, "value": 2.0},
            ]
            mut.set_room_boundaries(
                botengine, {"mounting_type": RadarVayyarDevice.SENSOR_MOUNTING_CEILING}
            )
            assert not mut.near_exit
            all_params = [
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_HEIGHT,
                    "value": 2.3,
                },
                {
                    "name": RadarVayyarDevice.MEASUREMENT_NAME_SENSOR_MOUNTING,
                    "value": RadarVayyarDevice.SENSOR_MOUNTING_CEILING,
                },
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MIN, "value": -1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_X_MAX, "value": 1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MIN, "value": 1.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Y_MAX, "value": 3.0},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MIN, "value": 0.5},
                {"name": RadarVayyarDevice.MEASUREMENT_NAME_Z_MAX, "value": 1.5},
            ]
            mut.set_room_boundaries(
                botengine,
                {
                    "x_min_meters": -1.0,
                    "x_max_meters": 1.0,
                    "y_min_meters": 1.0,
                    "y_max_meters": 3.0,
                    "z_min_meters": 0.5,
                    "z_max_meters": 1.5,
                    "mounting_type": RadarVayyarDevice.SENSOR_MOUNTING_CEILING,
                    "near_exit": True,
                },
            )
            assert mut.near_exit

        except Exception as e:
            assert False, "Exception: {}".format(e)

    def test_device_vayyar_attributes_subregions(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarVayyarDevice(
            botengine, location_object, device_id, device_type, device_desc
        )
        mut.is_connected = True

        mut.measurements = {}
        mut.last_updated_params = []

        # Test results without measurements
        mut.record_subregion(botengine, "123", 0, "test")
        assert mut.subregions == {"123": (0, "test")}
        assert mut.subregions_with_context(botengine, 0) == [("123", 0, "test")]
        mut.delete_recorded_subregions(botengine)
        assert mut.subregions == {}
        mut.record_occupied_subregion_information(botengine, "123", True)
        assert mut.information_occupied_subregions == ["123"]
        mut.record_occupied_subregion_information(botengine, "123", False)
        assert mut.information_occupied_subregions == []
        mut.record_occupied_subregion_knowledge(botengine, "123", True)
        assert mut.knowledge_occupied_subregions == ["123"]
        mut.record_occupied_subregion_knowledge(botengine, "123", False)
        assert mut.knowledge_occupied_subregions == []
        assert not mut.is_in_shower(botengine)
        assert not mut.is_in_chair(botengine)
        assert not mut.is_in_bed(botengine)
        mut.subregions = {
            "1": (radar.SUBREGION_CONTEXT_WALK_IN_SHOWER, "shower"),
            "2": (radar.SUBREGION_CONTEXT_CHAIR, "chair"),
            "3": (radar.SUBREGION_CONTEXT_BED, "bed"),
        }
        mut.knowledge_occupied_subregions = ["1", "2", "3"]
        assert mut.is_in_shower(botengine)
        assert mut.is_in_chair(botengine)
        assert mut.is_in_bed(botengine)
        assert not mut.did_update_subregions(botengine)
        assert mut.get_raw_subregions(botengine) == []
        assert mut.get_sorted_subregions(botengine, {}) == ([], [])
        assert mut.get_subregion_index(botengine, {}) is None
        assert not mut.did_subregion_occupancy_change(botengine)
        assert mut.get_subregions_entered(botengine) == []
        assert mut.get_subregions_occupied(botengine) == []
        assert mut.get_subregions_exited(botengine) == []

        # Test results with measurements
        mut.measurements = {
            RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS: [
                (
                    json.dumps(
                        [
                            {
                                "xMin": -1.0,
                                "xMax": 1.0,
                                "yMin": -1.0,
                                "yMax": 1.0,
                                "zMin": 0.0,
                                "zMax": 2.0,
                                "isFallingDetection": True,
                                "isPresenceDetection": True,
                                "enterDuration": 120,
                                "exitDuration": 120,
                                "isLowSnr": True,
                                "isDoor": False,
                                "name": "test",
                            }
                        ],
                        separators=(",", ":"),
                    ),
                    botengine.get_timestamp(),
                ),
            ],
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP: [
                ("100000", botengine.get_timestamp()),
                ("000000", botengine.get_timestamp() - utilities.ONE_HOUR_MS),
            ],
        }
        mut.last_updated_params = [
            RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS,
            RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP,
        ]
        assert mut.did_update_subregions(botengine)
        assert mut.get_raw_subregions(botengine) == [
            {
                "xMin": -1.0,
                "xMax": 1.0,
                "yMin": -1.0,
                "yMax": 1.0,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "test",
            }
        ]
        subregion = {
            "x_min_meters": -1.0,
            "x_max_meters": 1.0,
            "y_min_meters": -1.0,
            "y_max_meters": 1.0,
            "z_min_meters": 0.0,
            "z_max_meters": 2.0,
            "detect_falls": True,
            "detect_presence": True,
            "enter_duration_s": 120,
            "exit_duration_s": 120,
            "low_sensor_energy": True,
            "is_door": False,
            "name": "test",
        }
        assert mut.get_sorted_subregions(botengine, {device_id: [subregion]}) == (
            [
                {
                    "xMin": -1.0,
                    "xMax": 1.0,
                    "yMin": -1.0,
                    "yMax": 1.0,
                    "zMin": 0.0,
                    "zMax": 2.0,
                    "isFallingDetection": True,
                    "isPresenceDetection": True,
                    "enterDuration": 120,
                    "exitDuration": 120,
                    "isLowSnr": True,
                    "isDoor": False,
                    "name": "test",
                }
            ],
            [subregion],
        )
        assert mut.get_subregion_index(botengine, subregion) == 0
        assert mut.did_subregion_occupancy_change(botengine)
        assert mut.get_subregions_entered(botengine) == [0]
        assert mut.get_subregions_occupied(botengine) == [0]

        # Test results with updated measurements
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0] = (
            "000000",
            botengine.get_timestamp(),
        )
        mut.measurements[RadarVayyarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][1] = (
            "100000",
            botengine.get_timestamp() - utilities.ONE_HOUR_MS,
        )

        assert mut.get_subregions_exited(botengine) == [0]

        # Test with sending commands
        botengine.send_command = MagicMock()
        param_name = None
        param_value = None

        def send_command(device_id, name, value):
            botengine.get_logger("TEST").debug(
                "|send_command()       name={}       value={}".format(name, value)
            )
            botengine.get_logger("TEST").debug(
                "|send_command() param_name={} param_value={}".format(
                    param_name, param_value
                )
            )
            assert param_name == name
            assert param_value == json.loads(value)

        botengine.send_command.side_effect = send_command

        botengine.send_commands = MagicMock()
        all_params = None

        def send_commands(device_id, params):
            botengine.get_logger("TEST").debug(
                "|send_command()     params={}".format(params)
            )
            botengine.get_logger("TEST").debug(
                "|send_command() all_params={}".format(all_params)
            )
            assert all_params == params

        botengine.send_commands.side_effect = send_commands

        try:
            param_name, param_value = (
                RadarVayyarDevice.MEASUREMENT_NAME_TRACKER_SUBREGIONS,
                [
                    {
                        "xMin": -1.0,
                        "xMax": 1.0,
                        "yMin": -1.0,
                        "yMax": 1.0,
                        "zMin": 0.0,
                        "zMax": 2.0,
                        "isFallingDetection": True,
                        "isPresenceDetection": True,
                        "enterDuration": 120,
                        "exitDuration": 120,
                        "isLowSnr": True,
                        "isDoor": False,
                    }
                ],
            )
        except Exception as e:
            assert False, "Exception: {}".format(e)

        mut.set_subregions(botengine, param_value)

    def test_device_vayyar_sorted_subregions(self):
        # Subregion sorting does not rely on stored variables and can be tested independently
        botengine = BotEnginePyTest({})

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarVayyarDevice(
            botengine, location_object, device_id, device_type, device_desc
        )

        assert mut.get_sorted_subregions(botengine, {}) == ([], [])

        # Subregion = (native, device)
        subregion_tiny = (
            {
                "x_min_meters": -0.2,
                "x_max_meters": 0.2,
                "y_min_meters": -0.2,
                "y_max_meters": 0.2,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": True,
                "is_door": False,
                "name": "tiny",
            },
            {
                "xMin": -0.2,
                "xMax": 0.2,
                "yMin": -0.2,
                "yMax": 0.2,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "tiny",
            },
        )
        subregion_small = (
            {
                "x_min_meters": -0.5,
                "x_max_meters": 0.5,
                "y_min_meters": -0.5,
                "y_max_meters": 0.5,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": True,
                "is_door": False,
                "name": "small",
            },
            {
                "xMin": -0.5,
                "xMax": 0.5,
                "yMin": -0.5,
                "yMax": 0.5,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "small",
            },
        )
        subregion_medium = (
            {
                "x_min_meters": -1.0,
                "x_max_meters": 1.0,
                "y_min_meters": -1.0,
                "y_max_meters": 1.0,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": True,
                "is_door": False,
                "name": "medium",
            },
            {
                "xMin": -1.0,
                "xMax": 1.0,
                "yMin": -1.0,
                "yMax": 1.0,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "medium",
            },
        )
        subregion_large = (
            {
                "x_min_meters": -2.0,
                "x_max_meters": 2.0,
                "y_min_meters": -2.0,
                "y_max_meters": 2.0,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": True,
                "is_door": False,
                "name": "large",
            },
            {
                "xMin": -2.0,
                "xMax": 2.0,
                "yMin": -2.0,
                "yMax": 2.0,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "large",
            },
        )
        subregion_bed = (
            {
                "x_min_meters": -1.0,
                "x_max_meters": 1.0,
                "y_min_meters": -1.0,
                "y_max_meters": 1.0,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": True,
                "is_door": False,
                "context_id": radar.SUBREGION_CONTEXT_BED,
                "name": "bed",
            },
            {
                "xMin": -1.0,
                "xMax": 1.0,
                "yMin": -1.0,
                "yMax": 1.0,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": True,
                "isDoor": False,
                "name": "bed",
            },
        )
        subregion_door = (
            {
                "x_min_meters": -1.0,
                "x_max_meters": 1.0,
                "y_min_meters": -1.0,
                "y_max_meters": 1.0,
                "z_min_meters": 0.0,
                "z_max_meters": 2.0,
                "detect_falls": True,
                "detect_presence": True,
                "enter_duration_s": 120,
                "exit_duration_s": 120,
                "low_sensor_energy": False,
                "is_door": True,
                "name": "door",
            },
            {
                "xMin": -1.0,
                "xMax": 1.0,
                "yMin": -1.0,
                "yMax": 1.0,
                "zMin": 0.0,
                "zMax": 2.0,
                "isFallingDetection": True,
                "isPresenceDetection": True,
                "enterDuration": 120,
                "exitDuration": 120,
                "isLowSnr": False,
                "isDoor": True,
                "name": "door",
            },
        )
        assert mut.get_sorted_subregions(
            botengine,
            {
                device_id: [
                    subregion_tiny[0],
                    subregion_small[0],
                    subregion_large[0],
                    subregion_medium[0],
                    subregion_door[0],
                    subregion_bed[0],
                ]
            },
        ) == (
            [
                subregion_bed[1],
                subregion_large[1],
                subregion_medium[1],
                subregion_small[1],
                subregion_tiny[1],
                subregion_door[1],
            ],
            [
                subregion_bed[0],
                subregion_large[0],
                subregion_medium[0],
                subregion_small[0],
                subregion_tiny[0],
                subregion_door[0],
            ],
        )

        assert mut.get_sorted_subregions(
            botengine,
            {
                device_id: [
                    subregion_medium[0],
                    subregion_door[0],
                    subregion_door[0],
                    subregion_door[0],
                ]
            },
        ) == (
            [
                subregion_medium[1],
                subregion_door[1],
                subregion_door[1],
            ],
            [
                subregion_medium[0],
                subregion_door[0],
                subregion_door[0],
            ],
        )

        pass
