"""
Created on July 2, 2021

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""


def capture_insight(botengine, location_object, insight_id, value, title, description, icon=None, icon_font=None, device_object=None, confidence_state=None, confidence_reason=None):
    """
    Capture an insight
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param insight_id: Unique Insight ID
    :param value: Insight value
    :param title: Human-readable title for end-users
    :param description: Human-readable description for end-users
    :return:
    """
    content = {
        "insight_id": insight_id,
        "value": value,
        "title": title,
        "description": description
    }

    if icon is not None:
        content['icon'] = icon
        if icon_font is not None:
            content['icon_font'] = icon_font

    if device_object is not None:
        content['device_id'] = device_object.device_id
        content['device_desc'] = device_object.description
        content['device_type'] = device_object.device_type

    if confidence_state is not None:
        content['confidence_state'] = confidence_state
        if confidence_reason is not None:
            content['confidence_reason'] = confidence_reason

    location_object.distribute_datastream_message(botengine,
                                                  "capture_insight",
                                                  content=content,
                                                  internal=True,
                                                  external=False)

def delete_insight(botengine, location_object, insight_id):
    """
    Delete an insight
    :param botengine:
    :param location_object:
    :param device_object:
    :return:
    """
    location_object.distribute_datastream_message(botengine,
                                                  "capture_insight",
                                                  content={
                                                      "insight_id": insight_id
                                                  },
                                                  internal=True,
                                                  external=False)

