
from botengine_pytest import BotEnginePyTest

from locations.location import Location
import utilities.utilities as utilities

import bot

from intelligence.daylight.location_daylight_microservice import *

import binascii
import json

import unittest
from unittest.mock import patch, MagicMock

class TestDaylight(unittest.TestCase):

    def test_daylight_initialization(self):
        botengine = BotEnginePyTest({})

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = LocationDaylightMicroservice(botengine, location_object)
        assert mut is not None

        mut = location_object.intelligence_modules["intelligence.daylight.location_daylight_microservice"]
        assert mut is not None


    def test_daylight_default_sunrise_sunset(self):
        botengine = BotEnginePyTest({})
        botengine.set_timestamp(1685602800000) # Midnight on June 1, 2023 PST

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules["intelligence.daylight.location_daylight_microservice"]
        assert mut is not None
        
        assert mut.next_sunrise_timestamp_ms(botengine) == botengine.get_timestamp() + 8 * utilities.ONE_HOUR_MS
        assert mut.next_sunset_timestamp_ms(botengine) == botengine.get_timestamp() + 20 * utilities.ONE_HOUR_MS

        botengine.set_timestamp(1685602800000 + 12 * utilities.ONE_HOUR_MS) # Noon on June 1, 2023 PST

        assert mut.next_sunrise_timestamp_ms(botengine) == botengine.get_timestamp() + (20) * utilities.ONE_HOUR_MS
        assert mut.next_sunset_timestamp_ms(botengine) == botengine.get_timestamp() + (8) * utilities.ONE_HOUR_MS

        botengine.set_timestamp(1685602800000 + 22 * utilities.ONE_HOUR_MS) # 10 PM on June 1, 2023 PST

        assert mut.next_sunrise_timestamp_ms(botengine) == botengine.get_timestamp() + (10) * utilities.ONE_HOUR_MS
        assert mut.next_sunset_timestamp_ms(botengine) == botengine.get_timestamp() + (22) * utilities.ONE_HOUR_MS


    def test_daylight_geocoordinate_sunrise_sunset(self):
        botengine = BotEnginePyTest(
            {
                'time': 1685602800000,  # Midnight on June 1, 2023 PST
                'trigger': 1, 
                'source': 8, 
                'locationId': 0, 
                'triggerIds': [], 
                'access': [
                    {
                        'category': 1, 'trigger': False, 'read': True, 'control': True, 'location': {'locationId': 0, 'name': "Home", 'event': 'HOME.:.PRESENT.AI', 'timezone': {'id': 'America/Los_Angeles', 'offset': -480, 'dst': True, 'name': 'Pacific Standard Time'}, 'zip': '83501', 'latitude': '46.39950', 'longitude': '-117.02710', 'language': 'en'}
                    },
                    {
                        'category': 4, 'trigger': True, 'read': True, 'control': False, 'device': {'deviceId': '_device_id_', 'deviceType': 7004, 'description': 'IP Camera', 'locationId': 0, 'startDate': 1687068846000, 'connected': True}
                    },
                ]
            }
        )

        bot.run(botengine)

        controller = bot.load_controller(botengine)
        assert controller is not None
        assert len(controller.locations) == 1

        mut = controller.locations[0].intelligence_modules["intelligence.daylight.location_daylight_microservice"]
        assert mut is not None
        assert mut.next_sunrise_timestamp_ms(botengine) == 1685620744000
        assert mut.next_sunset_timestamp_ms(botengine) == 1685676801000

        botengine.set_timestamp(1685602800000 + 12 * utilities.ONE_HOUR_MS) # Noon on June 1, 2023 PST

        assert mut.next_sunrise_timestamp_ms(botengine) == 1685707110000
        assert mut.next_sunset_timestamp_ms(botengine) == 1685676801000

        botengine.set_timestamp(1685602800000 + 22 * utilities.ONE_HOUR_MS) # 10 PM on June 1, 2023 PST

        assert mut.next_sunrise_timestamp_ms(botengine) == 1685707110000
        assert mut.next_sunset_timestamp_ms(botengine) == 1685763253000