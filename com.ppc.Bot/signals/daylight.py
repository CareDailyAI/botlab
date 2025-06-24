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
    location_object.distribute_datastream_message(
        botengine, "sunset_fired", content=None, internal=True, external=False
    )


def get_next_sunrise_timestamp_ms(botengine, location_object):
    """
    Return the next sunrise time relative to now
    Provides a standard time of 8:00 AM if the daylight location microservice is not available
    :param botengine: BotEngine
    :param location_object: Location Object
    :param timestamp_ms: Timestamp in milliseconds
    :return: Next sunrise time in milliseconds
    """
    botengine.get_logger(f"{__name__}").info(">get_next_sunrise_timestamp_ms()")
    timestamp_ms = None
    if location_object.intelligence_modules.get(
        "intelligence.daylight.location_daylight_microservice"
    ):
        timestamp_ms = location_object.intelligence_modules.get(
            "intelligence.daylight.location_daylight_microservice"
        ).next_sunrise_timestamp_ms(botengine)
    else:
        dt = location_object.get_local_datetime(botengine).replace(hour=8)
        now = location_object.get_local_datetime(botengine)
        if dt < now:
            botengine.get_logger(f"{__name__}").debug(
                "|get_next_sunrise_timestamp_ms() Already past sunrise. Adding 24 hours."
            )
            import datetime

            dt = dt + datetime.timedelta(hours=24)
        botengine.get_logger(f"{__name__}").info(
            "|get_next_sunrise_timestamp_ms() local_dt={}".format(dt)
        )
        timestamp_ms = int(dt.timestamp()) * 1000
    botengine.get_logger(f"{__name__}").info(
        "<get_next_sunrise_timestamp_ms() timestamp_ms={}".format(timestamp_ms)
    )
    return timestamp_ms


def sunrise_fired(botengine, location_object):
    """
    Sunrise
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(
        botengine, "sunrise_fired", content=None, internal=True, external=False
    )


def get_next_sunset_timestamp_ms(botengine, location_object):
    """
    Return the next sunset time relative to now
    Provides a standard time of 10:00 PM if the daylight location microservice is not available
    :param botengine: BotEngine
    :param location_object: Location Object
    :param timestamp_ms: Timestamp in milliseconds
    :return: Next sunset time in milliseconds
    """
    botengine.get_logger(f"{__name__}").info(">get_next_sunset_timestamp_ms()")
    timestamp_ms = None
    if location_object.intelligence_modules.get(
        "intelligence.daylight.location_daylight_microservice"
    ):
        timestamp_ms = location_object.intelligence_modules.get(
            "intelligence.daylight.location_daylight_microservice"
        ).next_sunset_timestamp_ms(botengine)
    else:
        dt = location_object.get_local_datetime(botengine).replace(hour=20)
        now = location_object.get_local_datetime(botengine)
        if dt < now:
            botengine.get_logger(f"{__name__}").debug(
                "|get_next_sunset_timestamp_ms() Already past sunset. Adding 24 hours."
            )
            import datetime

            dt = dt + datetime.timedelta(hours=24)
        botengine.get_logger(f"{__name__}").info(
            "|get_next_sunset_timestamp_ms() local_dt={}".format(dt)
        )
        timestamp_ms = int(dt.timestamp()) * 1000
    botengine.get_logger(f"{__name__}").info(
        "<get_next_sunset_timestamp_ms() timestamp_ms={}".format(timestamp_ms)
    )
    return timestamp_ms


def midnight_fired(botengine, location_object):
    """
    It's midnight
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(
        botengine, "midnight_fired", content=None, internal=True, external=False
    )


def hour_fired(botengine, location_object):
    """
    Schedule triggered on the hour
    :param botengine: BotEngine
    :param location_object: Location Object
    """
    location_object.distribute_datastream_message(
        botengine, "hour_fired", content=None, internal=True, external=False
    )
