# Signals - Goals

This signal provides a common interface to manage user goals within the BotEngine environment. It allows you to add, update, remove, and restore goals associated with a location or user. All changes are distributed via the datastream for real-time updates.

## Goal Removal and Restoration

When a goal is removed, it is marked as deleted but can be restored within a configurable time period (default is one week). To restore a goal before it is purged, call `remove_goal` with `deleted=False` and specify the `goal_id`.

# Example usage:

```python
import signals.goals.goals as goals

# Add a new goal
goals.add_goal(
	botengine,
	location_object,
	goal_id="goal-123",
	title="Drink Water",
	description="Drink 8 glasses of water today",
	category="Health",
	created_timestamp_ms=botengine.get_timestamp(),
	user_id="user-456"
)

# Update an existing goal
goals.update_goal(
	botengine,
	location_object,
	goal_id="goal-123",
	title="Drink More Water",
	completed_timestamp_ms=botengine.get_timestamp()
)

# Remove a goal
goals.remove_goal(
	botengine,
	location_object,
	goal_id="goal-123"
)

# Restore a removed goal (within the removal period)
goals.remove_goal(
    botengine,
    location_object,
    goal_id="goal-123",
    deleted=False
)
```