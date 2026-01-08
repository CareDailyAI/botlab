from locations.location import Location

from botengine_pytest import BotEnginePyTest

try:
    from intelligence.goals.location_goals_microservice import (
        GOALS_STATE_NAME,
    )
except ImportError:
    pass

import unittest

import pytest
from signals.goals import (
    add_goal,
    DEFAULT_GOAL_REMOVAL_INTERVAL_MS,
    GOALS_STATE_NAME,
    remove_goal,
    update_goal,
)


class TestGoals(unittest.TestCase):
    def test_goals(self):
        botengine = BotEnginePyTest({})

        # botengine.logging_service_names = ["goals"]  # Uncomment to see logging

        # Initialize the location
        location_object = Location(botengine, 0)

        location_object.initialize(botengine)
        location_object.new_version(botengine)

        goals_service = location_object.intelligence_modules.get(
            "intelligence.goals.location_goals_microservice"
        )
        if goals_service is None:
            pytest.skip("No goals service in bot bundle")

        goal_json = {
            "goal_id": "goal_1",
            "title": "Test Goal 1",
            "description": "This is a test goal",
            "category": "test",
            "created_timestamp_ms": botengine.get_timestamp(),
            "user_id": 123,
        }
        # Add a goal
        add_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
            title=goal_json["title"],
            description=goal_json["description"],
            category=goal_json["category"],
            created_timestamp_ms=goal_json["created_timestamp_ms"],
            user_id=goal_json["user_id"],
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goal_json["completed"] = False
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert "goal_1" in goals_state
        assert goals_state["goal_1"] == goal_json

        botengine.add_timestamp(1000)

        # Update the goal
        goal_json["title"] = "Updated Test Goal 1"
        update_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
            title=goal_json["title"],
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert goals_state["goal_1"] == goal_json

        botengine.add_timestamp(1000)

        # Remove the goal
        goal_json["remove_after_ms"] = DEFAULT_GOAL_REMOVAL_INTERVAL_MS
        remove_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goal_json["removed_timestamp_ms"] = botengine.get_timestamp()
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert "goal_1" in goals_state
        assert goals_state["goal_1"] == goal_json

        botengine.add_timestamp(1000)

        # Restore the goal
        del goal_json["removed_timestamp_ms"]
        del goal_json["remove_after_ms"]
        remove_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
            deleted=False,
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert "goal_1" in goals_state
        assert goals_state["goal_1"] == goal_json

        botengine.add_timestamp(1000)

        # Complete the goal
        goal_json["completed"] = True
        update_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
            completed=goal_json["completed"],
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goal_json["completed_timestamp_ms"] = botengine.get_timestamp()
        goal_json["remove_after_ms"] = DEFAULT_GOAL_REMOVAL_INTERVAL_MS
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert "goal_1" in goals_state
        assert goals_state["goal_1"] == goal_json

        botengine.add_timestamp(1000)
        
        # Reopen the goal
        goal_json["completed"] = False
        del goal_json["completed_timestamp_ms"]
        del goal_json["remove_after_ms"]
        update_goal(
            botengine,
            location_object,
            goal_id=goal_json["goal_id"],
            completed=goal_json["completed"],
        )
        goal_json["updated_timestamp_ms"] = botengine.get_timestamp()
        goals_state = botengine.get_state(GOALS_STATE_NAME)
        assert "goal_1" in goals_state
        assert goals_state["goal_1"] == goal_json
