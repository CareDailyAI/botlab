
from botengine_pytest import BotEnginePyTest

from locations.location import *
import utilities.utilities as utilities

import unittest
from unittest.mock import MagicMock, patch

class TestLocation(unittest.TestCase):

    def test_location_constructor(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        mut = Location(botengine, 0)

        assert mut is not None
        assert mut.location_id == 0
        
        assert mut.born_on == botengine.get_timestamp()
        assert mut.filters == {}
        assert mut.devices == {}
        assert mut.intelligence_modules == {}
        assert mut.mode == botengine.get_mode(mut.location_id)
        assert mut.conversational_ui == None
        assert mut.security_state == Location.SECURITY_STATE_DISARMED
        assert mut.occupancy_status == ""
        assert mut.occupancy_reason == ""
        assert mut.properties_timestamp_ms == 0
        assert mut.location_properties == {}
        assert mut.location_narratives == {}
        assert mut.org_narratives == {}
        assert mut.latitude == None
        assert mut.longitude == None
        assert mut.is_daylight == None
        assert mut.language == botengine.get_language()
        assert mut.users == {}
        # assert mut.synchronize_users(botengine)
        assert mut.deviceless_trends == False
        
    def test_location_new_version(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        mut = Location(botengine, 0)
        import time
        t = time.time()
        mut.new_version(botengine)
        x = (time.time() - t)

        dt = 0.0
        for i in mut.intelligence_modules.values():
            dt += i.statistics["time"]
        assert abs(dt - x) < 1.0 # Allow for some error in the timing