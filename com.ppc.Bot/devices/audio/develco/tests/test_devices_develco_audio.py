from devices.audio.develco.audio import (
    DevelcoAudioAssistantDevice,
    BUTTON_INDEXES,
    BUTTON_STATUS_LONG,
    BUTTON_STATUS_SHORT,
)
from locations.location import Location

from botengine_pytest import BotEnginePyTest
import utilities.utilities as utilities

import unittest

class TestDevelcoAudioAssistantDevice(unittest.TestCase):
    def test_device_develco_audio_assistant(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # Initialize the location
        location_object = Location(botengine, 0)

        device_id = "A"
        device_type = 9109
        device_desc = "Test"

        mut = DevelcoAudioAssistantDevice(botengine, location_object, device_id, device_type, device_desc)
        location_object.devices[device_id] = mut

        location_object.initialize(botengine)
        location_object.new_version(botengine)
        
        assert not mut.is_short_button_pressed(botengine)
        assert not mut.is_long_button_pressed(botengine)
        assert mut.get_recent_button_status_timestamp(botengine) is None
        assert mut.did_update_bluetooth_status(botengine) is False
        assert mut.get_bluetooth_status(botengine) is None

        mut.last_updated_params = [f"buttonStatus.{BUTTON_INDEXES['SOS']}"]
        mut.measurements = {
            f"buttonStatus.{BUTTON_INDEXES['SOS']}": [[BUTTON_STATUS_SHORT, botengine.get_timestamp()]]
        }

        assert mut.is_short_button_pressed(botengine)
        assert not mut.is_long_button_pressed(botengine)
        assert mut.get_recent_button_status_timestamp(botengine) == botengine.get_timestamp()

        mut.last_updated_params = [f"buttonStatus.{BUTTON_INDEXES['SOS']}"]
        mut.measurements = {
            f"buttonStatus.{BUTTON_INDEXES['SOS']}": [[BUTTON_STATUS_LONG, botengine.get_timestamp()]]
        }

        assert not mut.is_short_button_pressed(botengine)
        assert mut.is_long_button_pressed(botengine)
