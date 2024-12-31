
from botengine_pytest import BotEnginePyTest
from devices.radar.radar import RadarDevice
import signals.radar as radar

from locations.location import Location
import utilities.utilities as utilities

import json
import unittest
from unittest.mock import patch, MagicMock

class TestRadarDevice(unittest.TestCase):

    def test_device_radar_init(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = RadarDevice(botengine, location_object, device_id, device_type, device_desc)

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
        assert mut.low_battery == False
        assert mut.is_connected == False
        assert mut.can_control == False
        assert mut.can_read == False
        assert mut.remote_addr_hash == None
        assert mut.proxy_id == None
        assert mut.goal_id == RadarDevice.BEHAVIOR_TYPE_OTHER
        assert mut.is_goal_changed == False
        assert mut.latitude == None
        assert mut.longitude == None
        assert mut.born_on == None
        assert mut.enforce_cache_size == True
        assert mut.total_communications_odometer == 0
        assert mut.communications_odometer == 0
        assert mut.measurement_odometer == 0
        assert mut.last_communications_timestamp == None
        assert mut.intelligence_modules == {}

        assert mut.information_total_occupants == 0
        assert mut.knowledge_total_occupants == 0
        assert mut.fall_count == 0
        assert mut.near_exit == False
        assert mut.subregions == {}
        assert mut.information_occupied_subregions == []
        assert mut.knowledge_occupied_subregions == []

    def test_device_radar_intelligence_modules(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarDevice(botengine, location_object, device_id, device_type, device_desc)
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        # Depending on the bot bundle under testing there may or may not be device intelligence modules
        # If available, ensure the parent and intelligence_id are set
        for i in mut.intelligence_modules:
            assert mut.intelligence_modules[i].intelligence_id != None
            assert mut.intelligence_modules[i].parent == mut

    def test_device_radar_attributes(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        botengine.logging_service_names = ["radar"]

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarDevice(botengine, location_object, device_id, device_type, device_desc)
        mut.is_connected = True

        mut.measurements = {}
        mut.last_updated_params = []

        # Test results without measurements
        assert mut.did_change_fall_status(botengine) == False

        assert mut.get_fall_status(botengine) == None
        assert mut.get_previous_fall_status(botengine) == None

        assert mut.get_previous_fall_status(botengine) == None
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False
        assert mut.did_update_fall_position(botengine) == False
        assert mut.get_fall_positions(botengine) == {}
        assert mut.did_update_bed_status(botengine) == False
        assert mut.get_bed_status(botengine) == None
        assert mut.did_update_occupancy_targets(botengine) == False
        assert mut.get_occupancy_targets(botengine) == {}
        assert mut.get_newest_targets(botengine) == {}
        assert mut.did_start_detecting_motion(botengine) == False
        assert mut.is_detecting_occupancy(botengine) == False
        assert mut.did_start_detecting_occupancy(botengine) == False
        assert mut.did_stop_detecting_occupancy(botengine) == False
        assert mut.did_update_room_boundaries(botengine) == False
        assert mut.get_room_boundaries(botengine) == {
            "x_min_meters": RadarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False
        }
        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": RadarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False
        }

        # Test results with device properties and state
        botengine.device_properties[device_id] = [
            {
                "name": "room",
                "value": json.dumps({
                    "x_min_meters": -1.0,
                    "x_max_meters": 1.0,
                    "y_min_meters": -1.0,
                    "y_max_meters": 1.0,
                    "z_min_meters": 0,
                    "z_max_meters": 1.0,
                    "mounting_type": 1,
                    "sensor_height_m": 2.3,
                    "updated_ms": botengine.get_timestamp(),
                    "near_exit": False
                })
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
            "near_exit": False
        }

        del botengine.device_properties[device_id]

        botengine.states["radar_room"] = {
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
                "near_exit": False
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
            "near_exit": False
        }
        del botengine.states["radar_room"]

        # Test results with measurements
        mut.measurements = {
            RadarDevice.MEASUREMENT_NAME_FALL_STATUS: [
                (RadarDevice.FALL_STATUS_DETECTED, botengine.get_timestamp()),
            ],
            RadarDevice.MEASUREMENT_NAME_BED_STATUS: [
                (0, botengine.get_timestamp()),
            ],
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET: [
                ("0:0,0,0", botengine.get_timestamp()),
            ],
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY: [
                (1, botengine.get_timestamp()),
            ],
        }
        mut.last_updated_params = [
            RadarDevice.MEASUREMENT_NAME_FALL_STATUS,
            RadarDevice.MEASUREMENT_NAME_BED_STATUS,
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET,
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY,
        ]
        assert mut.did_change_fall_status(botengine) == True

        assert mut.get_fall_status(botengine) == RadarDevice.FALL_STATUS_DETECTED

        assert mut.get_previous_fall_status(botengine) == None
        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False
        assert mut.did_update_fall_position(botengine) == False
        assert mut.get_fall_positions(botengine) == {}
        assert mut.did_update_bed_status(botengine) == True
        assert mut.get_bed_status(botengine) == 0
        assert mut.did_update_occupancy_targets(botengine) == True
        assert mut.get_occupancy_targets(botengine) == {botengine.get_timestamp(): {'0': {'x': 0, 'y': 0, 'z': 0}}}
        assert mut.get_newest_targets(botengine) == {'0': {'x': 0, 'y': 0, 'z': 0}}
        assert mut.did_start_detecting_motion(botengine) == True
        assert mut.is_detecting_occupancy(botengine) == True
        assert mut.did_start_detecting_occupancy(botengine) == True
        assert mut.did_stop_detecting_occupancy(botengine) == False
        assert mut.did_update_room_boundaries(botengine) == False
        assert mut.get_room_boundaries(botengine) == {
            "x_min_meters": RadarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False
        }
        assert mut.get_room_boundaries_properties(botengine) == {
            "x_min_meters": RadarDevice.X_MIN_METERS_WALL,
            "x_max_meters": RadarDevice.X_MAX_METERS_WALL,
            "y_min_meters": RadarDevice.Y_MIN_METERS_WALL,
            "y_max_meters": RadarDevice.Y_MAX_METERS_WALL,
            "z_min_meters": RadarDevice.Z_MIN_METERS_WALL,
            "z_max_meters": RadarDevice.Z_MAX_METERS_WALL,
            "mounting_type": 0,
            "sensor_height_m": 1.5,
            "updated_ms": 0,
            "near_exit": False
        }

        # Test results with additional measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_X] = []
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y] = []
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z] = []
        
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_X].append((0, botengine.get_timestamp()))
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y].append((0, botengine.get_timestamp()))
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z].append((0, botengine.get_timestamp()))

        mut.last_updated_params.append(RadarDevice.MEASUREMENT_NAME_FALL_LOC_X)
        mut.last_updated_params.append(RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y)
        mut.last_updated_params.append(RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z)

        assert mut.did_update_fall_position(botengine) == True
        assert mut.get_fall_positions(botengine) == {botengine.get_timestamp(): {'x': 0, 'y': 0, 'z': 0}}

        # Test results with additional measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS].append((RadarDevice.FALL_STATUS_FINISHED, botengine.get_timestamp() - utilities.ONE_MINUTE_MS))
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_X].append((1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS))
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Y].append((1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS))
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_LOC_Z].append((1, botengine.get_timestamp() - utilities.ONE_MINUTE_MS))

        assert mut.get_previous_fall_status(botengine) == RadarDevice.FALL_STATUS_FINISHED

        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False
        
        assert mut.did_update_fall_position(botengine) == True
        assert mut.get_fall_positions(botengine) == {botengine.get_timestamp(): {'x': 0, 'y': 0, 'z': 0}}
        assert mut.get_fall_positions(botengine, oldest_timestamp_ms=botengine.get_timestamp() - utilities.ONE_MINUTE_MS) == {botengine.get_timestamp() - utilities.ONE_MINUTE_MS: {'x': 1, 'y': 1, 'z': 1}, botengine.get_timestamp(): {'x': 0, 'y': 0, 'z': 0}}
        assert mut.get_fall_positions(botengine, newest_timestamp_ms=botengine.get_timestamp() - utilities.ONE_MINUTE_MS) == {botengine.get_timestamp() - utilities.ONE_MINUTE_MS: {'x': 1, 'y': 1, 'z': 1}}

        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False

        # Test results with different measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (RadarDevice.FALL_STATUS_DETECTED, botengine.get_timestamp())

        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False

        # Test results with different measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (RadarDevice.FALL_STATUS_CALLING, botengine.get_timestamp())

        assert mut.is_detecting_fall(botengine) == True
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == False

        # Test results with different measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (RadarDevice.FALL_STATUS_FINISHED, botengine.get_timestamp())
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][1] = (RadarDevice.FALL_STATUS_CALLING, botengine.get_timestamp() - utilities.ONE_MINUTE_MS)

        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == True
        assert mut.did_cancel_confirmed_fall(botengine) == False

        # Test results with different measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][0] = (RadarDevice.FALL_STATUS_CANCELLED, botengine.get_timestamp())
        mut.measurements[RadarDevice.MEASUREMENT_NAME_FALL_STATUS][1] = (RadarDevice.FALL_STATUS_CONFIRMED, botengine.get_timestamp() - utilities.ONE_MINUTE_MS)

        assert mut.is_detecting_fall(botengine) == False
        assert mut.did_stop_detecting_fall(botengine) == False
        assert mut.did_cancel_confirmed_fall(botengine) == True

        # Test results with different measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY][0] = (0, botengine.get_timestamp())

        assert mut.did_stop_detecting_occupancy(botengine) == True

        # Test results without connectivity
        mut.is_connected = False

        assert mut.get_occupancy_targets(botengine) == {}
        assert mut.get_newest_targets(botengine) == {}
            
    def test_device_radar_attributes_subregions(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = RadarDevice(botengine, location_object, device_id, device_type, device_desc)
        mut.is_connected = True

        mut.measurements = {}
        mut.last_updated_params = []

        # Test results without measurements
        mut.record_subregion(botengine, '123', 0, 'test')
        assert mut.subregions == {'123': (0, 'test')}
        assert mut.subregions_with_context(botengine, 0) == [('123', 0, 'test')]
        mut.delete_recorded_subregions(botengine)
        assert mut.subregions == {}
        mut.record_occupied_subregion_information(botengine, '123', True)
        assert mut.information_occupied_subregions == ['123']
        mut.record_occupied_subregion_information(botengine, '123', False)
        assert mut.information_occupied_subregions == []
        mut.record_occupied_subregion_knowledge(botengine, '123', True)
        assert mut.knowledge_occupied_subregions == ['123']
        mut.record_occupied_subregion_knowledge(botengine, '123', False)
        assert mut.knowledge_occupied_subregions == []
        assert mut.is_in_shower(botengine) == False
        assert mut.is_in_chair(botengine) == False
        assert mut.is_in_bed(botengine) == False
        mut.subregions = {
            '1': (radar.SUBREGION_CONTEXT_WALK_IN_SHOWER, 'shower'),
            '2': (radar.SUBREGION_CONTEXT_CHAIR, 'chair'),
            '3': (radar.SUBREGION_CONTEXT_BED, 'bed'),
        }
        mut.knowledge_occupied_subregions = ['1', '2', '3']
        assert mut.is_in_shower(botengine) == True
        assert mut.is_in_chair(botengine) == True
        assert mut.is_in_bed(botengine) == True
        assert mut.did_update_subregions(botengine) == False
        assert mut.did_subregion_occupancy_change(botengine) == False
        assert mut.get_subregions_entered(botengine) == []
        assert mut.get_subregions_occupied(botengine) == []
        assert mut.get_subregions_exited(botengine) == []

        # Test results with measurements
        mut.measurements = {
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP: [
                ('100000', botengine.get_timestamp()),
                ('000000', botengine.get_timestamp() - utilities.ONE_HOUR_MS),
            ]
        }
        mut.last_updated_params = [
            RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP,
        ]
        # assert mut.did_update_subregions(botengine) == True
        assert mut.did_subregion_occupancy_change(botengine) == True
        assert mut.get_subregions_entered(botengine) == [0]
        assert mut.get_subregions_occupied(botengine) == [0]

        # Test results with updated measurements
        mut.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][0] = ('000000', botengine.get_timestamp())
        mut.measurements[RadarDevice.MEASUREMENT_NAME_OCCUPANCY_MAP][1] = ('100000', botengine.get_timestamp() - utilities.ONE_HOUR_MS)

        assert mut.get_subregions_exited(botengine) == [0]