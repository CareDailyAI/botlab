"""
Created on October 15, 2019

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
"""

def update_task(botengine, location_object, task_id, title, comment):
    """
    Add or update a task
    :param botengine: BotEngine environment
    :param location_object: Location Object
    :param task_id: Unique Task ID for later reference
    :param title: Title of the task
    :param comment: Comment of the task
    """
    task = {
        "id": task_id,
        "title": title,
        "comment": comment
    }

    location_object.distribute_datastream_message(botengine, "update_task", task)


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

    location_object.distribute_datastream_message(botengine, "update_task", task)

