
from botengine_pytest import BotEnginePyTest
from devices.gateway.gateway import GatewayDevice
from devices.gateway.gateway_develco_squidlink import DevelcoSquidlinkDevice, POWER_STATUS_EXTERNAL, POWER_STATUS_BATTERY, MEASUREMENT_POWER_STATUS, CELL_STATUS_DISCONNECTED, CELL_STATUS_CONNECTED, MEASUREMENT_CELL_STATUS, NETWORK_TYPE_ETHERNET, NETWORK_TYPE_WIFI, NETWORK_TYPE_CELLULAR, NETWORK_TYPE_LOOPBACK, MEASUREMENT_NETWORK_TYPE

from locations.location import Location
import utilities.utilities as utilities

import unittest
from unittest.mock import patch, MagicMock

class TestGatewayDevice(unittest.TestCase):

    def test_device_init(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = GatewayDevice(botengine, location_object, device_id, device_type, device_desc)

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

    def test_device_gateway_cellular(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = DevelcoSquidlinkDevice(botengine, location_object, device_id, device_type, device_desc)

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == False
        assert mut.get_battery_level(botengine) == 100

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_CELLULAR, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.did_connect_cellular(botengine) == True
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == True

        mut.last_updated_params = []

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == True

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_ETHERNET, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == True
        assert mut.is_broadband_connected(botengine) == True
        assert mut.is_cellular_connected(botengine) == False

        mut.last_updated_params = []

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == True
        assert mut.is_cellular_connected(botengine) == False

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_WIFI, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == True
        assert mut.is_broadband_connected(botengine) == True
        assert mut.is_cellular_connected(botengine) == False
        
        mut.last_updated_params = []

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == True
        assert mut.is_cellular_connected(botengine) == False

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_LOOPBACK, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == False
        
        mut.last_updated_params = []

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == False

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()), (NETWORK_TYPE_CELLULAR, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == True


        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()), (NETWORK_TYPE_WIFI, botengine.get_timestamp())]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.is_broadband_connected(botengine) == True
        assert mut.is_cellular_connected(botengine) == False


        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [(NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()), (NETWORK_TYPE_CELLULAR, botengine.get_timestamp()), (NETWORK_TYPE_CELLULAR, botengine.get_timestamp() - utilities.ONE_HOUR_MS)]
        mut.last_updated_params = [NETWORK_TYPE_LOOPBACK]

        assert mut.did_connect_cellular(botengine) == False
        assert mut.did_connect_broadband(botengine) == False
        assert mut.is_broadband_connected(botengine) == False
        assert mut.is_cellular_connected(botengine) == True

        


