"""
Lesson 13 - Language Localization

Demonstrates gettext best practices:
- Use _("Static key") and format later: _("Hello {}").format(name)
- Do NOT interpolate inside _(...), because it changes the lookup key.
"""

from intelligence.intelligence import Intelligence  # type: ignore


STATE_ADDRESS = "lesson13/localization"


class LocationLocalizationMicroservice(Intelligence):
    def __init__(self, botengine, parent):
        super().__init__(botengine, parent)

    def initialize(self, botengine):
        """
        Publish a small localized payload so UIs (and tests) can see the results.
        """
        name = "BotLab"

        # CORRECT: dynamic values formatted after translation lookup
        correct = _("Hello from {}").format(name)

        # WRONG (shown here only as a string so you can compare): would produce
        # a different lookup key each time name changes.
        wrong_example_key = "Hello from {}".format(name)

        botengine.set_state(
            STATE_ADDRESS,
            {
                "correct": correct,
                "wrongExampleKey": wrong_example_key,
                "note": "Only 'correct' should be passed through _() as a stable key.",
            },
            overwrite=True,
        )

