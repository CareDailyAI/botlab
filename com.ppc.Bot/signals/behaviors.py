"""
Created on May 7, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def set_behaviors(botengine, location_object, device_types, behaviors):
    """
    Set behaviors for specific device types to appear in mobile apps and web consoles.

    Each behavior dictionary is defined as:

        {
            "id": 123,
            "weight": 0,
            "name": "Protect my home (default)",
            "description": "The motion sensor will recognize movement patterns to help protect your home and reduce energy consumption.",

            # Optional arguments:
            "icon": "home",
            "media_url": "s3://some_url"
            "media_content_type": "image/png"
        }

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_types: List of device types this set of behaviors applies to
    :param behaviors: List of behavior dictionaries
    """
    menu = {}
    for device_type in device_types:
        if behaviors is None:
            menu[device_type] = None
        else:
            menu[device_type] = "behaviors_{}".format(device_type)
        botengine.save_shared_variable("behaviors_{}".format(device_type), behaviors)

    location_object.distribute_datastream_message(botengine, "set_behaviors", menu, internal=True, external=True)
