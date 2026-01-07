from devices.button.comarch.button import ComarchButtonDevice
from locations.location import Location

from botengine_pytest import BotEnginePyTest
import utilities.utilities as utilities

import unittest

class TestComarchButtonDevice(unittest.TestCase):
    def test_device_button_comarch(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 2006
        device_desc = "Test"

        mut = ComarchButtonDevice(botengine, location_object, device_id, device_type, device_desc)
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)
        
        assert not mut.is_currently_pressed(botengine)
        assert not mut.is_single_button_pressed(botengine)
        assert not mut.is_single_button_released(botengine)
        assert mut.get_timestamp(botengine) is None

        mut.last_updated_params = ["buttonStatus.1"]
        mut.measurements = {
            "buttonStatus.1": [[True, botengine.get_timestamp()]]
        }

        assert mut.is_currently_pressed(botengine)
        assert mut.is_single_button_pressed(botengine)
        assert mut.get_timestamp(botengine) == botengine.get_timestamp()

        mut.last_updated_params = []
        mut.measurements = {
            "buttonStatus.1": [[True, botengine.get_timestamp()]]
        }

        assert mut.is_currently_pressed(botengine)
        assert not mut.is_single_button_pressed(botengine)
