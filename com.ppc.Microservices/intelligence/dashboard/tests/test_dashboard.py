
from botengine_pytest import BotEnginePyTest

from locations.location import Location
from devices.gateway.gateway import GatewayDevice
import utilities.utilities as utilities

from intelligence.dashboard.location_dashboard_microservice import *

from unittest.mock import patch, MagicMock

class TestDashboardMicroservice():

    def test_dashboard_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["dashboard"] # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)
        
        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules['intelligence.dashboard.location_dashboard_microservice']
        assert mut is not None
        assert len(mut.content_id) > 0
        assert botengine.get_state(NOW_UI_PROPERTY_NAME) == None
        assert botengine.get_state(SERVICES_UI_PROPERTY_NAME) != None
        assert len(botengine.get_state(SERVICES_UI_PROPERTY_NAME)["cards"][0]["content"]) > 0