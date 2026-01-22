"""
Lesson 17 - Delivering content from bots to UIs

Demonstrates writing UI-facing state JSON via botengine.set_state().
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson17/ui"


class LocationUiStateMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        # Publish an initial payload so UIs can render something right away.
        self.publish_ui_state(botengine, reason="initialize")

    def schedule_fired(self, botengine, schedule_id):
        self.publish_ui_state(botengine, reason=f"schedule:{schedule_id}")

    def publish_ui_state(self, botengine, reason):
        botengine.set_state(
            address=STATE_ADDRESS,
            json_content={
                "lesson": 17,
                "reason": reason,
                "generatedAtMs": botengine.get_timestamp(),
                "message": _("Hello UI — this is Lesson 17 state."),
            },
            overwrite=True,
        )

    def lesson17_ui_state(self, botengine, content):
        botengine.set_state(
            address=STATE_ADDRESS,
            json_content={
                "response": content
            },
            overwrite=False,
        )

