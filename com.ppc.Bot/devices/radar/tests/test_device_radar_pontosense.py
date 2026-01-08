import unittest

import signals.radar as radar
import utilities.utilities as utilities
from devices.radar.pontosense.radar import RadarPontosenseDevice
from devices.radar.radar import RadarDevice
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestRadarPontosenseDevice(unittest.TestCase):
    def test_radar_pontosense(self):
        botengine = BotEnginePyTest({})
        # botengine.logging_service_names = ["radar"]  # Uncomment to see logging
        location_object = Location(botengine, 0)
        device_id = "PNT1"
        device_type = 2007
        device_desc = "Pontosense Radar"
        mut = RadarPontosenseDevice(
            botengine,
            location_object,
            device_id,
            device_type,
            device_desc,
        )
        mut.is_connected = True
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        assert mut.location_object == location_object
        assert mut.device_id == device_id
        assert mut.device_type == device_type
        assert mut.description == device_desc
        assert mut.measurements == {}
        assert mut.last_alert == {}
        assert mut.last_updated_params == []
        assert mut.battery_level == 100
        assert mut.battery_levels == []
        assert mut.is_connected
        assert mut.DEVICE_TYPES == [2007]

        assert mut.get_icon() == "radar"
        assert mut.get_icon_font() == utilities.ICON_FONT_FONTAWESOME_REGULAR

        # Default boundaries
        room = mut.get_room_boundaries(botengine)
        assert room["x_min_meters"] == RadarPontosenseDevice.X_MIN_METERS
        assert room["x_max_meters"] == RadarPontosenseDevice.X_MAX_METERS
        assert room["y_min_meters"] == RadarPontosenseDevice.Y_MIN_METERS
        assert room["y_max_meters"] == RadarPontosenseDevice.Y_MAX_METERS
        assert room["z_max_meters"] == RadarPontosenseDevice.Z_MAX_METERS
        assert room["mounting_type"] == RadarDevice.SENSOR_MOUNTING_CORNER
        assert room["near_exit"] is False

        # Test constraints enforcement
        mut.set_room_boundaries(
            botengine, {"x_max_meters": 10, "y_max_meters": 10, "sensor_height_m": 5}
        )
        # Should not raise, and should clamp values

        mut.measurements = {
            RadarDevice.MEASUREMENT_NAME_FALL_STATUS: [
                (
                    RadarPontosenseDevice.FALL_STATUS_FALL_DETECTED,
                    botengine.get_timestamp(),
                )
            ]
        }
        assert mut.is_detecting_fall(botengine)

        # Test methods that should raise NotImplementedError
        with self.assertRaises(NotImplementedError):
            mut.set_test_mode(botengine, 1)
        with self.assertRaises(NotImplementedError):
            mut.get_test_mode(botengine)

        mut.last_updated_params = [
            RadarPontosenseDevice.MEASUREMENT_NAME_PNT_SCAN_HEIGHT
        ]
        assert mut.did_update_room_boundaries(botengine)

        # Should return a dict with expected keys
        props = mut.get_room_boundaries_properties(botengine)
        assert "x_min_meters" in props
        assert "x_max_meters" in props
        assert "y_min_meters" in props
        assert "y_max_meters" in props
        assert "z_min_meters" in props
        assert "z_max_meters" in props
        assert "mounting_type" in props
        assert "sensor_height_m" in props
        assert "updated_ms" in props
        assert "near_exit" in props

        mut.measurements = {
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}": [
                ("0:0,1,2", botengine.get_timestamp())
            ],
            RadarDevice.MEASUREMENT_NAME_FALL_STATUS: [
                (
                    RadarPontosenseDevice.FALL_STATUS_FALL_DETECTED,
                    botengine.get_timestamp(),
                )
            ],
        }
        positions = mut.get_fall_positions(botengine)
        assert len(positions) == 1
        assert positions[botengine.get_timestamp()]["x"] == "0"
        assert positions[botengine.get_timestamp()]["y"] == "1"
        assert positions[botengine.get_timestamp()]["z"] == "2"

        # Test subregions
        subregions = mut.get_subregions(botengine)
        assert isinstance(subregions, list)
        assert len(subregions) == 0  # No subregions set yet

        # Set subregions
        zones = [
            {
                "height": 200,
                "type": 10,
                "coordinates": [{"x": 50, "y": 0}, {"x": 100, "y": 50}],
            },
            {
                "height": 200,
                "type": 20,
                "coordinates": [{"x": 0, "y": 50}, {"x": 50, "y": 100}],
            }
        ]
        mut.set_subregions(botengine, zones)
        mut.measurements[RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES] = [
            (zones, botengine.get_timestamp())
        ]
        mut.last_updated_params.append(RadarPontosenseDevice.MEASUREMENT_NAME_PNT_ZONES)
        # Verify subregions were set
        subregions = mut.get_subregions(botengine)
        assert isinstance(subregions, list)
        assert len(subregions) == 2
        assert subregions[0]["height"] == 200
        assert subregions[0]["type"] == 10
        assert subregions[0]["coordinates"] == [{"x": 50, "y": 0}, {"x": 100, "y": 50}]
        assert subregions[1]["height"] == 200
        assert subregions[1]["type"] == 20
        assert subregions[1]["coordinates"] == [{"x": 0, "y": 50}, {"x": 50, "y": 100}]

        # Test if subregions were updated
        assert mut.did_update_subregions(botengine)

        # Get raw subregions
        raw_subregions = mut.get_raw_subregions(botengine)
        assert isinstance(raw_subregions, list)
        assert len(raw_subregions) == 2
        assert isinstance(raw_subregions[0], dict)
        subregion_data = raw_subregions[0]
        assert subregion_data["height"] == 200
        assert subregion_data["type"] == 10
        assert subregion_data["coordinates"] == [{"x": 50, "y": 0}, {"x": 100, "y": 50}]
        subregion_data = raw_subregions[1]
        assert subregion_data["height"] == 200
        assert subregion_data["type"] == 20
        assert subregion_data["coordinates"] == [{"x": 0, "y": 50}, {"x": 50, "y": 100}]

        # Test get subregion index
        subregion_1 = {
            "subregion_id": 0,
            "name": "BED",
            "x_min_meters": 0.5,
            "x_max_meters": 1.0,
            "y_min_meters": 0.0,
            "y_max_meters": 0.5,
            "z_min_meters": 0.0,
            "z_max_meters": 2.0,
            "detect_falls": False,
            "detect_presence": False,
            "enter_duration_s": 120,
            "exit_duration_s": 120,
            "context_id": radar.SUBREGION_CONTEXT_BED,
            "occupant_ids": [],
        }
        subregion_2 = {
            "subregion_id": 0,
            "name": "EXIT",
            "x_min_meters": 0.0,
            "x_max_meters": 0.5,
            "y_min_meters": 0.5,
            "y_max_meters": 1.0,
            "z_min_meters": 0.0,
            "z_max_meters": 2.0,
            "detect_falls": False,
            "detect_presence": False,
            "enter_duration_s": 120,
            "exit_duration_s": 120,
            "context_id": radar.SUBREGION_CONTEXT_EXIT,
            "occupant_ids": [],
        }
        subregion_index = mut.get_subregion_index(botengine, subregion_1)
        assert subregion_index == 0

        subregion_index = mut.get_subregion_index(botengine, subregion_2)
        assert subregion_index == 1

        nv_subregions = {mut.device_id: [subregion_1, subregion_2]}

        # Test sorted subregions
        api_subregion_list, native_subregion_list = mut.get_sorted_subregions(
            botengine,
            nv_subregions,
            z_max_meters=RadarPontosenseDevice.Z_MAX_METERS,
        )
        assert isinstance(api_subregion_list, list)
        assert isinstance(native_subregion_list, list)
        assert len(api_subregion_list) == 2
        assert len(native_subregion_list) == 2
        assert native_subregion_list[0]["context_id"] == radar.SUBREGION_CONTEXT_BED
        assert native_subregion_list[1]["context_id"] == radar.SUBREGION_CONTEXT_EXIT
        assert api_subregion_list[0]["type"] == 10
        assert api_subregion_list[1]["type"] == 20

        nv_subregions = {mut.device_id: [subregion_2, subregion_1]}
        api_subregion_list, native_subregion_list = mut.get_sorted_subregions(
            botengine,
            nv_subregions,
            z_max_meters=RadarPontosenseDevice.Z_MAX_METERS,
        )
        assert isinstance(api_subregion_list, list)
        assert isinstance(native_subregion_list, list)
        assert len(api_subregion_list) == 2
        assert len(native_subregion_list) == 2
        assert native_subregion_list[0]["context_id"] == radar.SUBREGION_CONTEXT_BED
        assert native_subregion_list[1]["context_id"] == radar.SUBREGION_CONTEXT_EXIT
        assert api_subregion_list[0]["type"] == 10
        assert api_subregion_list[1]["type"] == 20

        mut.measurements = {
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}": [
                ("0:0,1,2", botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}": [
                ("1:1,1,1", botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}": [
                ("2:2,2,2", botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}": [
                ("3:3,3,3", botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}": [
                ("4:4,4,4", botengine.get_timestamp())
            ],
        }
        mut.last_updated_params = [
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}",
        ]

        targets = mut.get_occupancy_targets(botengine)
        assert len(targets[botengine.get_timestamp()]) == 5

        mut.measurements = {
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}": [
                (None, botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}": [
                ("1:1,1,1", botengine.get_timestamp() - utilities.ONE_SECOND_MS)
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}": [
                (None, botengine.get_timestamp() - utilities.ONE_SECOND_MS)
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}": [
                (None, botengine.get_timestamp() - utilities.ONE_SECOND_MS)
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}": [
                (None, botengine.get_timestamp() - utilities.ONE_SECOND_MS)
            ],
        }
        mut.last_updated_params = [
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}",
        ]
        targets = mut.get_occupancy_targets(botengine)
        assert len(targets[botengine.get_timestamp()]) == 1
        assert len(targets[botengine.get_timestamp() - utilities.ONE_SECOND_MS]) == 1

        mut.measurements = {
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}": [
                (None, botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}": [
                (None, botengine.get_timestamp()),
                ("1:1,1,1", botengine.get_timestamp() - utilities.ONE_SECOND_MS),
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}": [
                (None, botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}": [
                (None, botengine.get_timestamp())
            ],
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}": [
                (None, botengine.get_timestamp())
            ],
        }
        mut.last_updated_params = [
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_BED_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_COUCH_IN}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_PRE_FALL}",
            f"{RadarDevice.MEASUREMENT_NAME_OCCUPANCY_TARGET}.{RadarPontosenseDevice.OCCUPANCY_TARGET_INDEX_OTHER}",
        ]
        targets = mut.get_occupancy_targets(botengine)
        assert len(targets[botengine.get_timestamp()]) == 0
        assert len(targets[botengine.get_timestamp() - utilities.ONE_SECOND_MS]) == 1
