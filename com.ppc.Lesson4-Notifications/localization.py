'''
Created on October 27, 2017

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

# Add any code here to import and apply localization one time.

import gettext
import os
import domain


# Set some default language here to allow the system to initialize
# Uncomment the following lines to enable language localization
#localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
#gettext.translation('messages', localedir, languages=[domain.DEFAULT_LANGUAGE]).install()

def initialize(botengine):
    """
    Override the default language with the user's selected language
    :param botengine: BotEngine environment
    :return:
    """
    # Uncomment the following lines to enable language localization
    #lang = botengine.lang
    #if lang is None:
    #    lang = domain.DEFAULT_LANGUAGE
    #localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
    #gettext.translation('messages', localedir, languages=[lang]).install()
    return
