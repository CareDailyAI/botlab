"""
Lesson 21 - Edge Computing

Demonstrates gating behavior based on whether the bot is running on the edge.

In production, edge bots often:
- avoid cloud calls when offline/air-gapped
- rely on local sensors/events and cached state
- publish lightweight UI state for local dashboards
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson21/edge"


class LocationEdgeMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        self.publish_edge_status(botengine, reason="initialize")

    def schedule_fired(self, botengine, schedule_id):
        self.publish_edge_status(botengine, reason=f"schedule:{schedule_id}")

    def publish_edge_status(self, botengine, reason):
        # In this repo, BotEngine provides `edge` in production. In local tests,
        # we treat a custom attribute `edge` as the signal.
        is_edge = bool(getattr(botengine, "edge", False))

        botengine.set_state(
            STATE_ADDRESS,
            {
                "reason": reason,
                "edge": is_edge,
                "mode": "edge" if is_edge else "cloud",
                "note": "Gate expensive/cloud-only calls when running on edge.",
            },
            overwrite=True,
        )

