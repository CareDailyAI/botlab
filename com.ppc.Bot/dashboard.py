"""
Created on September 19, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Titles of the cards
CARD_TITLE_NOW = _("NOW")
CARD_TITLE_SERVICES = _("SERVICES")

# Types of cards
CARD_TYPE_NOW = 0
CARD_TYPE_SERVICES = 1

# Card Weights - lower numbers float to the top
CARD_TYPE_NOW_WEIGHT = 0
CARD_TYPE_SERVICES_WEIGHT = 10

# Status fields for color coding
STATUS_HIDDEN = -1
STATUS_GOOD = 0
STATUS_WARNING = 1
STATUS_CRITICAL = 2

# Timestamped commands
COMMAND_DELETE = -2
COMMAND_SET_STATUS_HIDDEN = -1
COMMAND_SET_STATUS_GOOD = 0
COMMAND_SET_STATUS_WARNING = 1
COMMAND_SET_STATUS_CRITICAL = 2


def set_status(botengine, location_object, unique_identifier, comment, status=STATUS_GOOD, comment_weight=50, device_id=None, section_title=CARD_TITLE_NOW, section_weight=CARD_TYPE_NOW_WEIGHT, set_status_good_timestamp_ms=None, set_status_warning_timestamp_ms=None, set_status_critical_timestamp_ms=None, delete_timestamp_ms=None):
    """
    Set content for a status-style card.
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param unique_identifier: Unique identifier for this content
    :param comment: Comment to display. If None then this content gets deleted.
    :param status: Status for color-coding the content
    :param comment_weight: Weight of the comment relative to other comments inside this card.
    :param device_id: Optional device ID to create a link to a device that is having a problem
    :param section_title: Title of the section, in case we want multiple NOW-style cards
    :param section_weight: Weight of the section, in case we want to change it
    """
    alarms = {}

    element = {
        "status": status,
        "comment": comment,
        "weight": comment_weight,
        "id": unique_identifier,
        "alarms": alarms
    }

    if device_id is not None:
        element["device_id"] = device_id

    content = {
        "type": 0,
        "title": section_title,
        "weight": section_weight,
        "content": element
    }

    if set_status_good_timestamp_ms is not None:
        alarms[set_status_good_timestamp_ms] = COMMAND_SET_STATUS_GOOD

    if set_status_warning_timestamp_ms is not None:
        alarms[set_status_warning_timestamp_ms] = COMMAND_SET_STATUS_WARNING

    if set_status_critical_timestamp_ms is not None:
        alarms[set_status_critical_timestamp_ms] = COMMAND_SET_STATUS_CRITICAL

    if delete_timestamp_ms is not None:
        alarms[delete_timestamp_ms] = COMMAND_DELETE

    location_object.distribute_datastream_message(botengine, "update_dashboard_content", content, internal=True, external=False)


def delete_status(botengine, location_object, unique_identifier, section_title=CARD_TITLE_NOW):
    """
    Delete content within a status-style card
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param unique_identifier: Unique identifier for this content
    :param section_title: Section title in case we need to delete the section
    :return:
    """
    content = {
        "type": CARD_TYPE_NOW,
        "title": section_title,
        "content": {
            "id": unique_identifier,
            "comment": None
        }
    }

    location_object.distribute_datastream_message(botengine, "update_dashboard_content", content, internal=True, external=False)


def set_service(botengine, location_object, unique_identifier, title, comment, icon, status=STATUS_GOOD, percent=100.0, active=True, description=None, question_id=None, collection_id=None, section_id=None, comment_weight=50, section_title=CARD_TITLE_SERVICES, section_weight=CARD_TYPE_SERVICES_WEIGHT):
    """
    Set content for a service-style card.
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param unique_identifier: Unique identifier for this content
    :param title: Title of the content
    :param comment: Comment to display. If None then this content gets deleted
    :param icon: Icon name to render from fontawesome.com
    :param status: Status for color-coding the content
    :param percent: Percent complete
    :param active: True if this element is active, False if it is disabled
    :param question_id: Optional Question ID to link to
    :param collection_id: Optional Collection ID to link to
    :param comment_weight: Weight of this comment relative to other comments
    :param section_title: Title of the section, in case we want multiple NOW-style cards
    :param section_weight: Weight of the section, in case we want to change it
    """
    if comment is not None:
        element = {
            "title": title,
            "comment": comment,
            "icon": icon,
            "status": status,
            "percent": percent,
            "active": active,
            "id": unique_identifier,
            "weight": comment_weight
        }

        if question_id is not None:
            element["question_id"] = question_id

        if collection_id is not None:
            element["collection_id"] = collection_id

        if section_id is not None:
            element["section_id"] = section_id

        if description is not None:
            element["description"] = description

    else:
        element = None

    content = {
        "type": CARD_TYPE_SERVICES,
        "title": section_title,
        "weight": section_weight,
        "content": element
    }

    location_object.distribute_datastream_message(botengine, "update_dashboard_content", content, internal=True, external=False)


def delete_service(botengine, location_object, unique_identifier, section_title=CARD_TITLE_SERVICES):
    """
    Delete content within a service-style card
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param unique_identifier: Unique identifier for this content
    :param section_title: Title of the section in case we need to delete it
    """
    content = {
        "type": CARD_TYPE_SERVICES,
        "title": section_title,
        "content": {
            "id": unique_identifier,
            "comment": None
        }
    }

    location_object.distribute_datastream_message(botengine, "update_dashboard_content", content, internal=True, external=False)
