"""
Created on October 15, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

# Task colors
TASK_COLOR_NORMAL = "2A2A2A"
TASK_COLOR_GOOD = "67BD45"
TASK_COLOR_WARNING = "F8890C"
TASK_COLOR_CRITICAL = "D0021B"

# Light vs. Dark mode
TASK_UI_STYLE_LIGHT = "light" # Light background, dark text
TASK_UI_STYLE_DARK  = "dark" # Dark background, light text


def update_task(botengine, location_object, task_id, title, comment="", color=None, icon=None, icon_font=None, ui_style=None, url=None, editable=True):
    """
    Add or update a task
    :param botengine: BotEngine environment
    :param location_object: Location Object
    :param task_id: Unique Task ID for later reference
    :param title: Title of the task
    :param comment: Comment of the task
    :param color: Optional color of the task
    :param icon: Optional task icon
    :param icon_font: Icon font package to render the icon. See the ICON_FONT_* descriptions in com.ppc.Bot/utilities/utilities.py
    :param ui_style: Default is "light". "light" = light background, dark text. "dark" = dark background, light text.
    :param url: Instead of tapping into the task, jump straight to this URL when the user taps on the task from their Dashboard.
    :param editable: True if this task can be edited.
    """
    task = {
        "id": task_id,
        "title": title,
        "comment": comment,
        "editable": editable
    }

    if color is not None:
        task['color'] = color

    if icon is not None:
        task['icon'] = icon

    if icon_font is not None:
        task['icon_font'] = icon_font

    if ui_style is not None:
        task['ui_style'] = ui_style

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

