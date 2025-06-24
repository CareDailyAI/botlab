"""
Created on October 9, 2023

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: Destry Teeter, Konstantin Manyakin
"""


# values = {
#     "messages":
#         [
#             {
#                 "status": 1,
#                 "originalMessageId": 111,
#                 "topicId": "general",
#                 "scheduleType": 0,
#                 "contentKey": "Short content description",
#                 "contents": [
#                     {
#                         "deliveryType": 0,
#                         "contentType": 2,
#                         "text": {
#                             "en": "In-App message text",
#                             "es": "..."
#                         }
#                     },
#                     {
#                         "deliveryType": 1,
#                         "text": {
#                             "en": "Push notification",
#                             "es": "..."
#                         },
#                         "type": 100,
#                         "title": "Title",
#                         "subtitle": "Subtitle",
#                         "category": "21.0.1",
#                         "sound": "sound.wav"
#                     },
#                     {
#                         "deliveryType": 2,
#                         "contentType": 1,
#                         "text": {
#                             "en": "Email message text",
#                             "es": "..."
#                         },
#                         "subject": {
#                             "en": "Email subject",
#                             "es": "..."
#                         },
#                         "attachments": [
#                             {
#                                 "name": "imageName.jpg",
#                                 "content": "/9j/4AAQSkZJRgABAgEAAAAAAAD/4",
#                                 "contentType": "image/jpeg",
#                                 "contentId": "inlineImageId"
#                             }
#                         ]
#                     }
#                 ],
#                 "questionId": 987,
#                 "mediaUrl": "https://s3.amazon.com/images/picture.png",
#                 "mediaContentType": "image/png",
#                 "maxDeliveryDate": "2024-01-01T00:00:00Z",
#                 "deliveryDayTime": 36000,
#                 "timeToLive": 3600,
#                 "schedule": "0 0 10 ? * SUN",
#                 "recipients": [
#                     {
#                         "categories": [
#                             1,
#                             2
#                         ],
#                         "roles": [
#                             1,
#                             2
#                         ],
#                         "locationAccess": 10
#                     },
#                     {
#                         "userId": 678
#                     }
#                 ]
#             }
#         ]
#
#  response:
# {
#     "resultCode": 0,
#     "messages": [
#         {
#             "messageId": 123
#         }
#     ]
# }


def add_cloud_messages(
    botengine, location_object, messages_list: list, by_user: bool = False
):
    """
    Create a new messages to topic
    :param botengine:  BotEngine environment
    :param location_object: Location object
    :param messages_list: messages JSON content.
    :param by_user: messages created by user.
    :return: array of messages ids
    """
    botengine.get_logger().info(
        "engage_kit_cloud.add_cloud_messages: messages_list={}, by_user={}".format(
            messages_list, by_user
        )
    )
    if messages_list is None or len(messages_list) == 0:
        raise ValueError("messages_list is required")
    if not isinstance(messages_list, list):
        raise ValueError("messages_list must be a list")
    if not all(isinstance(message, dict) for message in messages_list):
        raise ValueError("messages_list must be a list of dictionaries")

    content = {"messages": messages_list}
    # location_id = location_object.location_id if by_user else None

    return botengine.create_cloud_messages(content, by_user)


# '''{
#   "messages": [
#     {
#       "messageId": 123,
#       "status": 2,
#       "deliveryDate": "2024-01-01T00:00:00Z"
#     },
#     {
#       "messageId": 124,
#       "status": 2,
#       "schedule": "0 15 10 ? * SUN"
#     }
#   ]
# }'''


def update_cloud_messages(botengine, updated_messages_list: list):
    """
    Update the status and/or delivery time for list of messsages
    :param botengine:  BotEngine environment
    :param updated_messages_list: messages JSON content.
    """
    botengine.get_logger().info(
        "engage_kit_cloud.update_cloud_messages: updated_messages_list={}".format(
            updated_messages_list
        )
    )
    if updated_messages_list is None or len(updated_messages_list) == 0:
        raise ValueError("updated_messages_list is required")
    if not isinstance(updated_messages_list, list):
        raise ValueError("messages_list must be a list")
    if not all(isinstance(message, dict) for message in updated_messages_list):
        raise ValueError("messages_list must be a list of dictionaries")

    content = {"messages": updated_messages_list}

    botengine.update_cloud_messages(content)

    return
