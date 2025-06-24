"""
Created on May 19, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def did_start_detecting_motion(botengine, location_object, device_object):
    """
    Device did start detecting motion

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object that started detecting motion
    """
    # Note this cannot be distributed externally because we're passing the device_object directly as an argument.
    location_object.distribute_datastream_message(
        botengine,
        "did_start_detecting_motion",
        device_object,
        internal=True,
        external=False,
    )


def did_stop_detecting_motion(botengine, location_object, device_object):
    """
    Device did stop detecting motion

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object that stopped detecting motion
    """
    # Note this cannot be distributed externally because we're passing the device_object directly as an argument.
    location_object.distribute_datastream_message(
        botengine,
        "did_stop_detecting_motion",
        device_object,
        internal=True,
        external=False,
    )


def did_continue_detecting_motion(botengine, location_object, device_object):
    """
    Device did continuously detecting motion

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param device_object: Device object that stopped detecting motion
    """
    # Note this cannot be distributed externally because we're passing the device_object directly as an argument.
    location_object.distribute_datastream_message(
        botengine,
        "did_continue_detecting_motion",
        device_object,
        internal=True,
        external=False,
    )
