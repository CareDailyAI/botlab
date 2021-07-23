"""
Created on May 14, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

import utilities.utilities as utilities

def track(botengine, location_object, event_name, properties={}):
    """
    Track an event.
    This will buffer your events and flush them to the server altogether at the end of all bot executions,
    and before variables get saved.

    :param botengine: BotEngine environment
    :param event_name: (string) A name describing the event
    :param properties: (dict) Additional data to record; keys should be strings and values should be strings, numbers, or booleans
    """
    if properties is not None:
        properties.update({
            "test": botengine.is_test_location()
        })

    botengine.narrate(title=event_name,
                      description=None,
                      priority=botengine.NARRATIVE_PRIORITY_ANALYTIC,
                      icon="cogs",
                      icon_font=utilities.ICON_FONT_FONTAWESOME_REGULAR,
                      status=None,
                      timestamp_ms=None,
                      file_ids=None,
                      extra_json_dict=properties,
                      event_type="analytic.{}".format(event_name),
                      update_narrative_id=None,
                      update_narrative_timestamp=None,
                      admin=False,
                      publish_to_partner=True)

    # Do not corrupt our analytics with internal test / beta locations.
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(botengine, "analytics_track", content={"event_name": event_name, "properties": properties}, internal=True, external=False)


def people_set(botengine, location_object, properties_dict):
    """
    Set some key/value attributes for this user
    :param botengine: BotEngine environment
    :param properties_dict: Dictionary of key/value pairs to track
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(botengine, "analytics_people_set", content={"properties_dict": properties_dict}, internal=True, external=False)


def people_increment(botengine, location_object, properties_dict):
    """
    Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
    :param botengine: BotEngine environment
    :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(botengine, "analytics_people_increment", content={"properties_dict": properties_dict}, internal=True, external=False)


def people_unset(botengine, location_object, properties_list):
    """
    Delete a property from a user
    :param botengine: BotEngine
    :param properties_dict: Key/Value dictionary pairs to remove from a people record.
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(botengine, "analytics_people_unset", content={"properties_list": properties_list}, internal=True, external=False)

