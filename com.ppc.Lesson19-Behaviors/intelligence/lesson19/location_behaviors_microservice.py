"""
Lesson 19 - Behaviors

Demonstrates how to publish Behavior menus (per device type) that UIs can render.
"""

from intelligence.intelligence import Intelligence  # type: ignore

import signals.behaviors as behaviors  # type: ignore


STATE_ADDRESS = "lesson19/behaviors"


class LocationBehaviorsMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        # Publish a default behaviors menu for demo purposes.
        self.publish_demo_behaviors(botengine, reason="initialize")

    def schedule_fired(self, botengine, schedule_id):
        self.publish_demo_behaviors(botengine, reason=f"schedule:{schedule_id}")

    def publish_demo_behaviors(self, botengine, reason):
        device_types = [9138]  # example: motion sensor (common in test payloads)
        menu = [
            {
                "id": 1,
                "weight": 0,
                "name": _("Demo behavior"),
                "description": _("Example behavior published by Lesson 19."),
                "icon": "home",
            }
        ]

        behaviors.set_behaviors(
            botengine, self.parent, device_types=device_types, behaviors=menu
        )

        botengine.set_state(
            STATE_ADDRESS,
            {"reason": reason, "deviceTypes": device_types, "behaviors": menu},
            overwrite=True,
        )

