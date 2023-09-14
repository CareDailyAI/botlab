"""
Created on November 20, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Section ID's
SECTION_ID_ALERTS = "alerts"
SECTION_ID_NOTES = "notes"
SECTION_ID_TASKS = "tasks"
SECTION_ID_SLEEP = "sleep"
SECTION_ID_ACTIVITIES = "activities"
SECTION_ID_MEALS = "meals"
SECTION_ID_MEDICATION = "medication"
SECTION_ID_BATHROOM = "bathroom"
SECTION_ID_SOCIAL = "social"
SECTION_ID_MEMORIES = "memories"
SECTION_ID_SYSTEM = "system"

def add_entry(botengine, location_object, section_id, comment=None, subtitle=None, identifier=None, include_timestamp=False, timestamp_override_ms=None):
    """
    Add a section and bullet point the current daily report
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param section_id: Section ID like dailyreport.SECTION_ID_ACTIVITIES
    :param comment: Comment like "Woke up."
    :param subtitle: Subtitle comment like "Consistent sleep schedule and good quality sleep last night."
    :param identifier: Optional identifier to come back and edit this entry later.
    :param include_timestamp: True to include a timestamp like "7:00 AM - <comment>" (default is False)
    :param timestamp_override_ms: Optional timestamp in milliseconds to override the current time when citing the timestamp with include_timestamp=True
    """
    content = {
        "section_id": section_id,
        "comment": comment,
        "subtitle": subtitle,
        "identifier": identifier,
        "include_timestamp": include_timestamp,
        "timestamp_override_ms": timestamp_override_ms
    }

    location_object.distribute_datastream_message(botengine, "daily_report_entry", content, internal=True, external=False)