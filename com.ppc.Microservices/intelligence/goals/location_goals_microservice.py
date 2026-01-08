"""
Created on December 18, 2025

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter
"""

import json

from intelligence.intelligence import Intelligence
from signals.goals import (
    DEFAULT_GOAL_REMOVAL_INTERVAL_MS,
    GOAL_ATTRIBUTE_REMOVE_FLAG,
    GOALS_STATE_NAME,
)

TIMER_GOAL_REMOVAL_ID = "remove_goal"


class LocationGoalsMicroservice(Intelligence):
    """
    Goals Microservice
    """

    def __init__(self, botengine, parent):
        """
        Instantiate this object
        :param parent: Parent object, either a location or a device object.
        """
        Intelligence.__init__(self, botengine, parent)

    def new_version(self, botengine):
        """
        Upgraded to a new bot version
        :param botengine: BotEngine environment
        """
        return

    def datastream_updated(self, botengine, address, content):
        """
        Data Stream Message Received
        :param botengine: BotEngine environment
        :param address: Data Stream address
        :param content: Content of the message
        """
        if hasattr(self, address):
            getattr(self, address)(botengine, content)

    def timer_fired(self, botengine, argument):
        """
        The bot's intelligence timer fired
        :param botengine: Current botengine environment
        :param argument: Argument applied when setting the timer
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(">timer_fired()")
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            f"|timer_fired() argument={argument}"
        )
        if argument and isinstance(argument, tuple) and len(argument) == 2:
            timer_id, goal_id = argument
            if timer_id == TIMER_GOAL_REMOVAL_ID:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|timer_fired() Processing goal removal for goal {goal_id}"
                )
                try:
                    goals_state = botengine.get_state(GOALS_STATE_NAME) or {}
                    if goal_id in goals_state:
                        goal = goals_state[goal_id]
                        if "completed_timestamp_ms" in goal:
                            self.parent.set_location_property_separately(
                                botengine,
                                GOALS_STATE_NAME,
                                goals_state,
                                timestamp_ms=goal["completed_timestamp_ms"],
                            )
                        del goals_state[goal_id]
                        self.parent.set_location_property_separately(
                            botengine, GOALS_STATE_NAME, goals_state, overwrite=True
                        )
                        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                            f"|timer_fired() Removed goal {goal_id} from state"
                        )
                    else:
                        botengine.get_logger(
                            f"{__name__}.{__class__.__name__}"
                        ).warning(
                            f"|timer_fired() Goal {goal_id} not found in state for removal"
                        )
                except Exception as e:
                    import traceback

                    botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                        f"|timer_fired() Error processing timer {argument}: {e}; trace={traceback.format_exc()}"
                    )

            self._schedule_goal_removal(botengine, goals_state)
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug("<timer_fired()")

    def goals_updated(self, botengine, content):
        """
        Goals updated
        :param botengine: BotEngine environment
        :param content: Content of the data stream message
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">goals_updated()"
        )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            f"|goals_updated() content={json.dumps(content)}"
        )

        goal_id = content.get("goal_id")
        if goal_id is None:
            botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                "<goals_updated() Missing goal_id in content"
            )
            return
        goals_state = botengine.get_state(GOALS_STATE_NAME) or {}

        goal = goals_state.get(goal_id, {})

        # Handle goal removal or restoration
        if "deleted" in content:
            goal = self._remove_or_restore_goal(botengine, goal_id, goal, content)

        # Update the goal
        elif goal:
            goal = self._update_goal(botengine, goal_id, goal, content)

        # New goal
        else:
            goal = self._add_goal(botengine, goal_id, content)

        if goal:
            goal["updated_timestamp_ms"] = botengine.get_timestamp()
            # Save the updated goal state
            botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                f"|goals_updated() goal={json.dumps(goal)}"
            )
            goals_state[goal_id] = goal
            self.parent.set_location_property_separately(
                botengine, GOALS_STATE_NAME, goals_state, overwrite=True
            )

        # Schedule goal removal if marked as removed
        self._schedule_goal_removal(botengine, goals_state)

        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<goals_updated()"
        )

    def _add_goal(self, botengine, goal_id, content):
        """
        Add a new goal
        :param botengine: BotEngine environment
        :param goal_id: Goal ID
        :param content: Content of the data stream message
        :return: New goal json
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_add_goal()")
        try:
            goal = {k: v for k, v in content.items() if v is not None}
            if any(field not in goal for field in ["title", "description", "category"]):
                missing_fields = [
                    field
                    for field in ["title", "description", "category"]
                    if field not in goal
                ]
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    f"<_add_goal() Missing required fields {missing_fields} in new goal {goal_id}"
                )
                return None
            goal["created_timestamp_ms"] = content.get(
                "created_timestamp_ms", botengine.get_timestamp()
            )
            goal["completed"] = False
            botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                f"|_add_goal() New goal {goal_id} added"
            )
        except Exception as e:
            import traceback

            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                f"|_add_goal() Error adding goal {goal_id}: {e}; trace={traceback.format_exc()}"
            )
            return None
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info("<_add_goal()")
        return goal

    def _schedule_goal_removal(self, botengine, goals):
        """
        Schedule goal removal timers
        :param botengine: BotEngine environment
        :param goals: Current goals state
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            ">_schedule_goal_removal()"
        )
        try:
            goal_id_to_remove = (None, None)
            removed_goals = [
                gid for gid, g in goals.items() if "removed_timestamp_ms" in g
            ]
            if removed_goals:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    f"|_schedule_goal_removal() removed_goals={removed_goals}"
                )
                sorted_goals = sorted(
                    removed_goals,
                    key=lambda gid: goals[gid]["removed_timestamp_ms"]
                    + goals[gid]["remove_after_ms"],
                )
                next_goal_id = sorted_goals[0]
                next_goal = goals[next_goal_id]

                removal_timestamp_ms = (
                    next_goal["removed_timestamp_ms"] + next_goal["remove_after_ms"]
                )
                goal_id_to_remove = (next_goal_id, removal_timestamp_ms)

            completed_goals = [
                gid for gid, g in goals.items() if "completed_timestamp_ms" in g
            ]
            if completed_goals:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
                    f"|_schedule_goal_removal() completed_goals={completed_goals}"
                )
                sorted_goals = sorted(
                    completed_goals,
                    key=lambda gid: goals[gid]["completed_timestamp_ms"]
                    + goals[gid].get(
                        "remove_after_ms", DEFAULT_GOAL_REMOVAL_INTERVAL_MS
                    ),
                )
                next_goal_id = sorted_goals[0]
                next_goal = goals[next_goal_id]

                removal_timestamp_ms = next_goal[
                    "completed_timestamp_ms"
                ] + next_goal.get("remove_after_ms", DEFAULT_GOAL_REMOVAL_INTERVAL_MS)
                if (
                    goal_id_to_remove[0] is None
                    or removal_timestamp_ms < goal_id_to_remove[1]
                ):
                    goal_id_to_remove = (next_goal_id, removal_timestamp_ms)

            if goal_id_to_remove[0] is not None:
                self.set_alarm(
                    botengine,
                    timestamp_ms=goal_id_to_remove[1],
                    argument=(TIMER_GOAL_REMOVAL_ID, goal_id_to_remove[0]),
                    reference=TIMER_GOAL_REMOVAL_ID,
                )
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|_schedule_goal_removal() Scheduled removal of goal {goal_id_to_remove[0]} at {goal_id_to_remove[1]} ms"
                )
            elif self.is_timer_running(botengine, TIMER_GOAL_REMOVAL_ID):
                self.cancel_timer(botengine, TIMER_GOAL_REMOVAL_ID)
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    "|_schedule_goal_removal() No goals to remove, cancelled removal timer"
                )

        except Exception as e:
            import traceback

            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                f"|_schedule_goal_removal() Error scheduling goal removals: {e}; trace={traceback.format_exc()}"
            )
        botengine.get_logger(f"{__name__}.{__class__.__name__}").debug(
            "<_schedule_goal_removal()"
        )

    def _remove_or_restore_goal(self, botengine, goal_id, goal, content):
        """
        Remove or restore a goal
        :param botengine: BotEngine environment
        :param goal_id: Goal ID
        :param goal: Current goal json
        :param content: Content of the data stream message
        :return: Updated goal json
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            ">_remove_or_restore_goal()"
        )
        try:
            if not goal:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    f"<_remove_or_restore_goal() Cannot remove non-existent goal {goal_id}"
                )
                return None
            if goal.get("completed_timestamp_ms"):
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    f"<_remove_or_restore_goal() Cannot remove completed goal {goal_id}"
                )
                return None
            deleted = content["deleted"]
            if deleted:
                if goal.get("removed_timestamp_ms"):
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        f"<_remove_or_restore_goal() Goal {goal_id} already removed"
                    )
                    return None
                removed_timestamp_ms = botengine.get_timestamp()
                goal["removed_timestamp_ms"] = removed_timestamp_ms
                remove_after_ms = content.get("remove_after_ms")
                if remove_after_ms is None:
                    remove_after_ms = DEFAULT_GOAL_REMOVAL_INTERVAL_MS
                goal["remove_after_ms"] = remove_after_ms
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|_remove_or_restore_goal() Goal {goal_id} marked as removed, will be purged after {remove_after_ms} ms"
                )
            else:
                if not goal:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                        f"<_remove_or_restore_goal() Cannot restore non-existent goal {goal_id}"
                    )
                    return None
                del goal["removed_timestamp_ms"]
                del goal["remove_after_ms"]
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"|_remove_or_restore_goal() Goal {goal_id} restored"
                )
        except Exception as e:
            import traceback

            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                f"|_remove_or_restore_goal() Error processing goal {goal_id} removal/restoration: {e}; trace={traceback.format_exc()}"
            )
            return None
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            "<_remove_or_restore_goal()"
        )
        return goal

    def _update_goal(self, botengine, goal_id, goal, content):
        """
        Update goal attributes
        :param botengine: BotEngine environment
        :param goal_id: Goal ID
        :param goal: Current goal json
        :param content: Content of the data stream message
        :return: Updated goal json
        """
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(">_update_goal()")
        try:
            if not goal:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    f"<_update_goal() Cannot update non-existent goal {goal_id}"
                )
                return None
            if "removed_timestamp_ms" in goal:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").warning(
                    f"<_update_goal() Cannot update removed goal {goal_id}"
                )
                return None
            updated = False
            for key, value in content.items():
                if key == "goal_id":
                    continue
                if value != goal.get(key):
                    # Update or remove the field
                    if value == GOAL_ATTRIBUTE_REMOVE_FLAG:
                        if key in ["title", "description", "category"]:
                            botengine.get_logger(
                                f"{__name__}.{__class__.__name__}"
                            ).warning(
                                f"|_update_goal() Cannot remove required field {key} from goal {goal_id}"
                            )
                            continue
                        if key in goal:
                            updated = True
                            botengine.get_logger(
                                f"{__name__}.{__class__.__name__}"
                            ).debug(
                                f"|_update_goal() Removing field {key} from goal {goal_id}"
                            )
                            del goal[key]
                    elif value is not None:
                        updated = True
                        goal[key] = value
            if not updated:
                botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                    f"<_update_goal() No updates for goal {goal_id}"
                )
                return None
            goal = {k: v for k, v in goal.items() if v is not None}
            if "completed" in content:
                if goal["completed"]:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        f"|_update_goal() Goal {goal_id} marked as completed"
                    )
                    goal["completed_timestamp_ms"] = botengine.get_timestamp()
                    goal["remove_after_ms"] = DEFAULT_GOAL_REMOVAL_INTERVAL_MS
                else:
                    botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
                        f"|_update_goal() Goal {goal_id} marked as reopened"
                    )
                    if "completed_timestamp_ms" in goal:
                        del goal["completed_timestamp_ms"]
                    if "remove_after_ms" in goal:
                        del goal["remove_after_ms"]
        except Exception as e:
            import traceback

            botengine.get_logger(f"{__name__}.{__class__.__name__}").error(
                f"|_update_goal() Error updating goal {goal_id}: {e}; trace={traceback.format_exc()}"
            )
            return None
        botengine.get_logger(f"{__name__}.{__class__.__name__}").info(
            f"|_update_goal() Goal {goal_id} updated"
        )
        return goal
