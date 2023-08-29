
from botengine_pytest import BotEnginePyTest
from devices.device import Device

from locations.location import Location
import utilities.utilities as utilities


class TestDevice():

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
        assert mut.last_alert == None
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
        assert mut.goal_id == None
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

        location_object.new_version(botengine)
        location_object.initialize(botengine)
        mut.new_version(botengine)

        assert len(mut.intelligence_modules) > 0

        mut.initialize(botengine)

        for i in mut.intelligence_modules:
            assert mut.intelligence_modules[i].intelligence_id != None
            assert mut.intelligence_modules[i].parent == mut


