'''
Created on October 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Add any code here to import and apply localization one time.

import gettext
import os
import properties


# Set some default language here to allow the system to initialize
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
gettext.translation('messages', localedir, languages=[properties.get_property(None, "DEFAULT_LANGUAGE")]).install()

def initialize(botengine):
    """
    Override the default language with the user's selected language
    :param botengine: BotEngine environment
    :return:
    """
    lang = botengine.get_language()
    if lang is None:
        lang = properties.get_property(botengine, "DEFAULT_LANGUAGE")

    localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    try:
        gettext.translation('messages', localedir, languages=[lang]).install()
    except FileNotFoundError:
        # Fallback to default language if set language is not supported
        import utilities.utilities as utilities
        botengine.get_logger().warning(utilities.Color.RED + "localization: Locale '{}' not supported.".format(lang) + utilities.Color.END)
        gettext.translation('messages', localedir, languages=[properties.get_property(botengine, "DEFAULT_LANGUAGE")]).install()
