"""
Created on October 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import gettext
import os

import properties

# Set some default language here to allow the system to initialize
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "locale")
gettext.translation(
    "messages", localedir, languages=[properties.get_property(None, "DEFAULT_LANGUAGE")]
).install()


def initialize(botengine):
    """
    Override the default language with the user's selected language
    :param botengine: BotEngine environment
    :return:
    """
    botengine.get_logger(f"{__name__}").debug(">initialize()")
    lang = botengine.get_language()
    if lang is None:
        lang = properties.get_property(botengine, "DEFAULT_LANGUAGE")
    botengine.get_logger().debug(
        "|initialize() lang={}".format(lang)
    )
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "locale")
    try:
        gettext.translation("messages", localedir, languages=[lang]).install()
    except FileNotFoundError:
        # Fallback to default language if set language is not supported
        import utilities.utilities as utilities

        botengine.get_logger().warning(
            utilities.Color.RED
            + "localization: Locale '{}' not supported.".format(lang)
            + utilities.Color.END
        )
        gettext.translation(
            "messages",
            localedir,
            languages=[properties.get_property(botengine, "DEFAULT_LANGUAGE")],
        ).install()
    botengine.get_logger(f"{__name__}").debug("<initialize()")

def get_translations(botengine, key, language_codes=None):
    """
    Get all translations for a key for a list of languages
    :param botengine: BotEngine environment
    :param key: Translation key
    :param languages: List of languages to try to get the translation
    :return: Translated strings {language: translation}
    """
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "locale")
    if language_codes is None:
        # Get any languages available in the locale directory
        language_codes = [f for f in os.listdir(localedir) if os.path.isdir(os.path.join(localedir, f))]
    translations = {}
    for language_code in language_codes:
        try:
            translations[language_code] = gettext.translation("messages", localedir, languages=(language_code,)).gettext(key)
        except FileNotFoundError:
            continue
    return translations

def get_translation(botengine, key, language_code=None):
    """
    Get the translation for a key for a specific language
    :param botengine: BotEngine environment
    :param key: Translation key
    :param language_code: Language code to get the translation
    :return: Translated string
    """
    if language_code is None and botengine is not None:
        lang = botengine.get_language()
        if lang is None:
            lang = properties.get_property(botengine, "DEFAULT_LANGUAGE")
    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "locale")
    try:
        return gettext.translation("messages", localedir, languages=(language_code,)).gettext(key)
    except FileNotFoundError:
        return gettext.gettext(key)