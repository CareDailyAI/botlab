import unittest

from intelligence.intelligence import Intelligence
from locations.location import Location

from botengine_pytest import BotEnginePyTest


class TestIntelligence(unittest.TestCase):
    def test_intelligence_constructor(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        location_object = Location(botengine, 0)

        mut = Intelligence(botengine, location_object)
        mut.reset_statistics(botengine)

        assert mut is not None
        assert mut.intelligence_id is not None
        assert mut.parent == location_object
        assert mut.statistics == {"calls": 0, "time": 0}

    def test_intelligence_track_statistics(self):
        # Initial setup
        botengine = BotEnginePyTest({})
        location_object = Location(botengine, 0)

        mut = Intelligence(botengine, location_object)
        assert mut is not None

        import time

        t = time.time()
        time.sleep(1)
        mut.track_statistics(botengine, (time.time() - t) * 1000)
        assert mut.statistics["calls"] == 1
        assert int(mut.statistics["time"] / 1000) == 1
