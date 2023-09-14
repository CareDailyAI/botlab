"""
Created on July 24, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

def sunset_fired(botengine, location_object):
    """
    Sunset
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(botengine,
                                                  "sunset_fired",
                                                  content=None,
                                                  internal=True,
                                                  external=False)


def sunrise_fired(botengine, location_object):
    """
    Sunrise
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(botengine,
                                                  "sunrise_fired",
                                                  content=None,
                                                  internal=True,
                                                  external=False)


def midnight_fired(botengine, location_object):
    """
    It's midnight
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(botengine,
                                                  "midnight_fired",
                                                  content=None,
                                                  internal=True,
                                                  external=False)


def hour_fired(botengine, location_object):
    """
    Schedule triggered on the hour
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(botengine,
                                                  "hour_fired",
                                                  content=None,
                                                  internal=True,
                                                  external=False)