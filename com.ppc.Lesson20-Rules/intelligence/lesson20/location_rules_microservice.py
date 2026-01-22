"""
Lesson 20 - Rules

Rules are user-configurable IF/THEN automations. This lesson demonstrates:
- retrieving a rules list
- toggling rules on/off
- publishing a summary to a UI-facing state variable
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson20/rules"


class LocationRulesMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        self.refresh_rules(botengine, reason="initialize")

    def schedule_fired(self, botengine, schedule_id):
        self.refresh_rules(botengine, reason=f"schedule:{schedule_id}")

    def refresh_rules(self, botengine, reason):
        rules = None
        try:
            # BotEngine signature supports device_id=None; pytest engine uses device_id positional.
            rules = botengine.get_rules(device_id=None)
        except TypeError:
            try:
                rules = botengine.get_rules(None)
            except Exception:
                rules = None
        except Exception:
            rules = None

        botengine.set_state(
            STATE_ADDRESS,
            {"reason": reason, "rules": rules},
            overwrite=True,
        )

    def toggle_all(self, botengine, enable: bool):
        """
        Toggle all rules on/off (demo API).
        """
        try:
            result = botengine.toggle_all_rules(enable)
        except Exception:
            result = None

        botengine.set_state(
            STATE_ADDRESS,
            {"toggled": True, "enable": enable, "result": result},
            overwrite=True,
        )

