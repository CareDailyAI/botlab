"""
Created on January 26, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def capture_rtls_event(botengine, location_object, event: dict):
    """
    Capture a far away event at address 'rtls_capture_event'
    :param botengine: BotEngine
    :param location_object: Location Object
    :param event: Event dictionary
        :param start_time_ms: Start time of the event in milliseconds
        :param end_time_ms: End time of the event in milliseconds
        :param device_id: Device ID that detected the event
        :param latitude: Latitude of the event
        :param longitude: Longitude of the event
    """
    body = {
        "start_time_ms": event.get("start_time_ms"),
        "end_time_ms": event.get("end_time_ms"),
        "device_id": event.get("device_id"),
        "latitude": event.get("latitude"),
        "longitude": event.get("longitude"),
    }
    body = {k: f"{v}" for k, v in body.items() if v is not None}

    location_object.distribute_datastream_message(
        botengine, "rtls_capture_event", body, internal=True, external=False
    )
