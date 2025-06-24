"""
Created on May 14, 2020

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""
import json

import utilities.utilities as utilities


def track(
    botengine, location_object, event_name, properties=None, event_description=None
):
    """
    Track an event.
    This will buffer your events and flush them to the server altogether at the end of all bot executions,
    and before variables get saved.

    :param botengine: BotEngine environment
    :param location_object: Location object
    :param event_name: (string) A name describing the event
    :param properties: (dict) Additional data to record; keys should be strings and values should be strings, numbers, or booleans
    :param event_description: (string) A description of the event for narrative purposes
    """
    # handle default argument
    if properties is None:
        properties = {}

    # Preserve test status
    properties.update({"test": botengine.is_test_location()})

    if not location_object.is_definitely_absent(botengine):
        botengine.narrate(
            title=event_name,
            description=event_description,
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
            publish_to_partner=True,
        )

    # Do not corrupt our analytics with internal test / beta locations.
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(
        botengine,
        "analytics_track",
        content={"event_name": event_name, "properties": properties},
        internal=True,
        external=False,
    )

    botengine.get_logger(f"{__name__}").debug("|track() O properties={}".format(json.dumps(properties)))


def track_and_notify(
    botengine,
    location_object,
    event_name,
    properties={},
    push_title=None,
    push_subtitle=None,
    push_content=None,
    push_category=None,
    push_sound=None,
    push_sms_fallback_content=None,
    push_template_filename=None,
    push_template_model=None,
    push_info=None,
    email_subject=None,
    email_content=None,
    email_html=False,
    email_attachments=None,
    email_template_filename=None,
    email_template_model=None,
    email_addresses=None,
    sms_content=None,
    sms_template_filename=None,
    sms_template_model=None,
    sms_group_chat=True,
    admin_domain_name=None,
    brand=None,
    language=None,
    user_id=None,
    user_id_list=None,
    to_residents=False,
    to_supporters=False,
    to_admins=False,
):
    track(botengine, location_object, "notify.{}".format(event_name), properties)
    botengine.notify(
        push_title=push_title,
        push_subtitle=push_subtitle,
        push_content=push_content,
        push_category=push_category,
        push_sound=push_sound,
        push_sms_fallback_content=push_sms_fallback_content,
        push_template_filename=push_template_filename,
        push_template_model=push_template_model,
        push_info=push_info,
        email_subject=email_subject,
        email_content=email_content,
        email_html=email_html,
        email_attachments=email_attachments,
        email_template_filename=email_template_filename,
        email_template_model=email_template_model,
        email_addresses=email_addresses,
        sms_content=sms_content,
        sms_template_filename=sms_template_filename,
        sms_template_model=sms_template_model,
        sms_group_chat=sms_group_chat,
        admin_domain_name=admin_domain_name,
        brand=brand,
        language=language,
        user_id=user_id,
        user_id_list=user_id_list,
        to_residents=to_residents,
        to_supporters=to_supporters,
        to_admins=to_admins,
    )


def people_set(botengine, location_object, properties_dict):
    """
    Set some key/value attributes for this user
    :param botengine: BotEngine environment
    :param properties_dict: Dictionary of key/value pairs to track
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(
        botengine,
        "analytics_people_set",
        content={"properties_dict": properties_dict},
        internal=True,
        external=False,
    )


def people_increment(botengine, location_object, properties_dict):
    """
    Adds numerical values to properties of a people record. Nonexistent properties on the record default to zero. Negative values in properties will decrement the given property.
    :param botengine: BotEngine environment
    :param properties_dict: Dictionary of key/value pairs. The value is numeric, either positive or negative. Default record is 0. The value will increment or decrement the property by that amount.
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(
        botengine,
        "analytics_people_increment",
        content={"properties_dict": properties_dict},
        internal=True,
        external=False,
    )


def people_unset(botengine, location_object, properties_list):
    """
    Delete a property from a user
    :param botengine: BotEngine
    :param properties_dict: Key/Value dictionary pairs to remove from a people record.
    """
    if botengine.is_test_location():
        return

    location_object.distribute_datastream_message(
        botengine,
        "analytics_people_unset",
        content={"properties_list": properties_list},
        internal=True,
        external=False,
    )
