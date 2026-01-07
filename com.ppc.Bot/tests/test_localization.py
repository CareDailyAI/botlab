import unittest

import pytest
from localization import (
    get_translation,
    get_translations,
    initialize,
)

from botengine_pytest import BotEnginePyTest


class TestLocalization(unittest.TestCase):
    def test_localization(self):
        message = "Device"
        translations = get_translations(None, message)
        if translations == {}:
            pytest.skip("No translations found")
        assert translations["en"] == message
        assert translations["es"] == "Dispositivo"
        assert translations["fr"] in ["Dispositif", "Appareil"]
        assert get_translation(None, message, language_code="fr") in ["Dispositif", "Appareil"]

        botengine = BotEnginePyTest(
            {
                "access": [
                    {
                        "category": 1,
                        "control": True,
                        "location": {
                            "language": "fr",
                            "timezone": {
                                "id": "US/Eastern",
                            },
                        },
                        "read": True,
                        "trigger": True,
                    }
                ]
            }
        )

        # botengine.logging_service_names = ["localization"]
        initialize(botengine)
        assert botengine.get_language() == "fr"
        assert _(message) in ["Dispositif", "Appareil"]  # noqa: F821 # type: ignore
        translations = get_translations(botengine, message)
        assert translations["en"] == message
        assert translations["fr"] in ["Dispositif", "Appareil"]
        assert get_translation(None, message, language_code="en") == message
