from devices.device import Device, TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestDevice:
    def test_device_init(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = Device(botengine, location_object, device_id, device_type, device_desc)

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
        assert mut.goal_id is None
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

    def test_device_intelligence_modules(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = Device(botengine, location_object, device_id, device_type, device_desc)
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        # Depending on the bot bundle under testing there may or may not be device intelligence modules
        # If available, ensure the parent and intelligence_id are set
        for i in mut.intelligence_modules:
            assert mut.intelligence_modules[i].intelligence_id is not None
            assert mut.intelligence_modules[i].parent == mut

    def test_device_measurements_cache(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 23
        device_desc = "Test"

        mut = Device(botengine, location_object, device_id, device_type, device_desc)
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        # Ensure the measurements cache is working

        # Ensure the cache size is enforced with default (TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS = 1)
        mut.add_measurement(botengine, "test", 3, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS*3)
        assert mut.measurements["test"] == [
            (3, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS*3)
        ]
        assert len(mut.measurements["test"]) == 1

        mut.add_measurement(botengine, "test", 2, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS*2)
        assert mut.measurements["test"] == [
            (2, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS*2),
        ]
        assert len(mut.measurements["test"]) == 1

        # Ensure the cache size is enforced with custom value
        mut.minimum_measurements_to_cache_by_parameter_name = {"test": 2}

        mut.add_measurement(botengine, "test", 1, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS)
        assert mut.measurements["test"] == [
            (1, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS),
            (2, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS*2),
        ]
        assert len(mut.measurements["test"]) == 2

        mut.add_measurement(botengine, "test", 0, botengine.get_timestamp())
        assert mut.measurements["test"] == [
            (0, botengine.get_timestamp()),
            (1, botengine.get_timestamp() - TOTAL_DURATION_TO_CACHE_MEASUREMENTS_MS),
        ]
        assert len(mut.measurements["test"]) == 2