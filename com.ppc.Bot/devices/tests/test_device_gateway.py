import unittest

import utilities.utilities as utilities
from devices.gateway.gateway import GatewayDevice
from devices.gateway.gateway_develco_squidlink import (
    DevelcoSquidlinkDevice,
    MEASUREMENT_NETWORK_TYPE,
    NETWORK_TYPE_CELLULAR,
    NETWORK_TYPE_ETHERNET,
    NETWORK_TYPE_LOOPBACK,
    NETWORK_TYPE_WIFI,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest


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

        mut = GatewayDevice(
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

    def test_device_gateway_cellular(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 0
        device_desc = "Test"

        mut = DevelcoSquidlinkDevice(
            botengine, location_object, device_id, device_type, device_desc
        )

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)
        assert mut.get_battery_level(botengine) == 100

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_CELLULAR, botengine.get_timestamp())
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert mut.is_cellular_connected(botengine)

        mut.last_updated_params = []

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_ETHERNET, botengine.get_timestamp())
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert not mut.did_connect_cellular(botengine)
        assert mut.did_connect_broadband(botengine)
        assert mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.last_updated_params = []

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_WIFI, botengine.get_timestamp())
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert not mut.did_connect_cellular(botengine)
        assert mut.did_connect_broadband(botengine)
        assert mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.last_updated_params = []

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_LOOPBACK, botengine.get_timestamp())
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.last_updated_params = []

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()),
            (NETWORK_TYPE_CELLULAR, botengine.get_timestamp()),
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert not mut.is_broadband_connected(botengine)
        assert mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()),
            (NETWORK_TYPE_WIFI, botengine.get_timestamp()),
        ]
        mut.last_updated_params = [MEASUREMENT_NETWORK_TYPE]

        assert mut.is_broadband_connected(botengine)
        assert not mut.is_cellular_connected(botengine)

        mut.measurements[MEASUREMENT_NETWORK_TYPE] = [
            (NETWORK_TYPE_LOOPBACK, botengine.get_timestamp()),
            (NETWORK_TYPE_CELLULAR, botengine.get_timestamp()),
            (NETWORK_TYPE_CELLULAR, botengine.get_timestamp() - utilities.ONE_HOUR_MS),
        ]
        mut.last_updated_params = [NETWORK_TYPE_LOOPBACK]

        assert not mut.did_connect_cellular(botengine)
        assert not mut.did_connect_broadband(botengine)
        assert not mut.is_broadband_connected(botengine)
        assert mut.is_cellular_connected(botengine)
