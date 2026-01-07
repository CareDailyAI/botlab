from locations.location import Location
from signals.goals import (
    GOALS_STATE_NAME,
)

from botengine_pytest import BotEnginePyTest


class TestGoalsMicroservice:
    def test_goals_initialization(self):
        botengine = BotEnginePyTest({})
        # Clear out any previous tests
        botengine.reset()

        # botengine.logging_service_names = ["goals"]  # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        mut = location_object.intelligence_modules[
            "intelligence.goals.location_goals_microservice"
        ]
        assert mut is not None
        assert botengine.get_state(GOALS_STATE_NAME) is None
