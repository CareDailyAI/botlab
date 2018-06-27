'''
Created on October 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

import gettext
import os
import domain

# Set some default language here to allow the system to initialize (uncomment the next 2 lines)
#localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
#gettext.translation('messages', localedir, languages=[domain.DEFAULT_LANGUAGE]).install()

def initialize(botengine):
    """
    Override the default language with the user's selected language
    :param botengine: BotEngine environment
    """
    return

    # lang = botengine.lang
    # if lang is None:
    #     lang = domain.DEFAULT_LANGUAGE

    # Add any code below to import and apply localization one time.
    # For example, uncomment the next 2 lines of code to add in localization.
    # Use the 'i18n.sh' script inside your bot's directory to automatically generate localizable .po files.
    # Once translated, run the 'i18n.sh' script again to transform the .po files into .mo files which are used by Python.

    #localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    #gettext.translation('messages', localedir, languages=[lang]).install()
