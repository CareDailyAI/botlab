"""
Created on December 18, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

import utilities.utilities as utilities

DEFAULT_GOAL_REMOVAL_INTERVAL_MS = utilities.ONE_WEEK_MS
GOAL_ATTRIBUTE_REMOVE_FLAG = "__remove__"
GOALS_STATE_NAME = "goals"


def add_goal(
    botengine,
    location_object,
    goal_id,
    title,
    description,
    category,
    created_timestamp_ms=None,
    user_id=None,
):
    """
    Add a goal
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param goal_id: Unique Goal ID
    :param title: Human-readable title for end-users
    :param description: Human-readable description for end-users
    :param category: Goal category
    :param created_timestamp_ms: Optional Timestamp when the goal was created
    :param user_id: Optional user ID
    :return:
    """
    content = {
        "goal_id": goal_id,
        "title": title,
        "description": description,
        "category": category,
        "created_timestamp_ms": created_timestamp_ms,
        "user_id": user_id,
    }
    content = {k: v for k, v in content.items() if v is not None}

    location_object.distribute_datastream_message(
        botengine, "goals_updated", content=content, internal=True, external=False
    )


def update_goal(
    botengine,
    location_object,
    goal_id,
    user_id=None,
    title=None,
    description=None,
    category=None,
    completed=None,
):
    """
    Update a goal.
    Any parameter set to GOAL_ATTRIBUTE_REMOVE_FLAG ("__remove__") will be removed from the goal (does not apply to title, description, category).
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param user_id: User ID
    :param goal_id: Unique Goal ID
    :param title: Human-readable title for end-users
    :param description: Human-readable description for end-users
    :param category: Goal category
    :param completed: Optional flag indicating if the goal is completed
    :return:
    """
    content = {
        "goal_id": goal_id,
        "user_id": user_id,
        "title": title,
        "description": description,
        "category": category,
        "completed": completed,
    }

    content = {k: v for k, v in content.items() if v is not None}

    location_object.distribute_datastream_message(
        botengine, "goals_updated", content=content, internal=True, external=False
    )


def remove_goal(
    botengine,
    location_object,
    goal_id,
    remove_after_ms=DEFAULT_GOAL_REMOVAL_INTERVAL_MS,
    deleted=True,
):
    """
    Mark a goal as removed or restore a removed goal
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param goal_id: Unique Goal ID
    :param remove_after_ms: Time in milliseconds after which the goal data will be purged
    :param deleted: True to mark as removed, False to restore
    :return:
    """
    content = {
        "goal_id": goal_id,
        "remove_after_ms": remove_after_ms,
        "deleted": deleted,
    }

    location_object.distribute_datastream_message(
        botengine, "goals_updated", content=content, internal=True, external=False
    )
