"""
Created on October 15, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Task priorities
TASK_PRIORITY_DETAIL = 0
TASK_PRIORITY_INFO = 1
TASK_PRIORITY_WARNING = 2
TASK_PRIORITY_CRITICAL = 3

def update_task(botengine, location_object, task_id, title, comment="", priority=TASK_PRIORITY_INFO, icon=None, icon_font=None, url=None, editable=True):
    """
    Add or update a task
    :param botengine: BotEngine environment
    :param location_object: Location Object
    :param task_id: Unique Task ID for later reference
    :param title: Title of the task
    :param comment: Comment of the task
    :param priority: Priority of the task: 0=detail; 1=info; 2=warning; 3=critical
    :param icon: Optional task icon
    :param icon_font: Icon font package to render the icon. See the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
    :param url: Instead of tapping into the task, jump straight to this URL when the user taps on the task from their Dashboard.
    :param editable: True if this task can be edited.
    """
    task = {
        "id": task_id,
        "title": title,
        "comment": comment,
        "editable": editable
    }

    if priority is not None:
        task['priority'] = priority

    if icon is not None:
        task['icon'] = icon

    if icon_font is not None:
        task['icon_font'] = icon_font

    if url is not None:
        task['url'] = url

    location_object.distribute_datastream_message(botengine, "update_task", task, internal=True, external=False)


def delete_task(botengine, location_object, task_id):
    """
    Delete a task
    :param botengine: BotEngine environment
    :param location_object: Location object
    :param task_id: Task ID to delete
    """
    task = {
        "id": task_id
    }

    location_object.distribute_datastream_message(botengine, "update_task", task, internal=True, external=False)

