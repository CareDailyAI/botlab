import json
import unittest
from typing import List

from intelligence.engage_kit_cloud.types.cloud_model import (
    BotMessage,
    CloudDeliveryType,
    CloudMessage,
    CloudQuestion,
    CloudTopic,
    Content,
    ContentType,
    Recipient,
)
from pydantic import TypeAdapter


class TestEngageKitCloud(unittest.TestCase):
    def test_engage_kit_cloud_class_tmp(self):
        text_content = {"en": "test"}
        message_recipient = Recipient(user_id=123)
        message_content_api = Content(
            delivery_type=CloudDeliveryType.IN_APP,
            contentType=ContentType.TEXT,
            text=text_content,
        )
        message_content = Content(
            delivery_type=CloudDeliveryType.SMS,
            contentType=ContentType.TEXT,
            text=text_content,
        )

        cloud_message = CloudMessage(
            status=1,
            topic_id="TOPIC_ID",
            schedule_type=0,
            content_key="AI message",
            contents=[message_content_api, message_content],
            max_delivery_date="1736470743000",
            delivery_day_time=61173,
            time_to_live=3600,
            recipients=[message_recipient],
        )

        json.loads(
            cloud_message.model_dump_json(by_alias=True, indent=4, exclude_none=True)
        )

    def test_engage_kit_cloud_class_validation(self):
        message_data_str = """
        {
          "status": 1,
          "originalMessageId": 111,
          "topicId": "general",
          "scheduleType": 0,
          "contentKey": "Short content description",
          "contents": [
            {
              "deliveryType": 0,
              "contentType": 2,
              "text": {
                "en": "In-App message text",
                "es": "..."
              }
            },
            {
              "deliveryType": 1,
              "contentType": 2,
              "text": {
                "en": "Push notification",
                "es": "..."
              },
              "type": 100,
              "title": "Title",
              "subtitle": "Subtitle",
              "category": "21.0.1",
              "sound": "sound.wav"
            },
            {
              "deliveryType": 2,
              "contentType": 1,
              "text": {
                "en": "Email message text",
                "es": "..."
              },
              "subject": {
                "en": "Email subject",
                "es": "..."
              },
              "attachments": [
                {
                  "name": "imageName.jpg",
                  "content": "/9j/4AAQSkZJRgABAgEAAAAAAAD/4",
                  "contentType": "image/jpeg",
                  "contentId": "inlineImageId"
                }
              ]
            }
          ],
          "questionId": 987,
          "mediaUrl": "https://s3.amazon.com/images/picture.png",
          "mediaContentType": "image/png",
          "maxDeliveryDate": "2024-01-01T00:00:00Z",
          "deliveryDayTime": 36000,
          "timeToLive": 3600,
          "schedule": "0 0 10 ? * SUN",
          "recipients": [
            {
              "categories": [
                1,
                2
              ],
              "roles": [
                1,
                2
              ],
              "locationAccess": 10
            },
            {
              "userId": 678
            }
          ]
        }
        """

        # Convert JSON string to Pydantic model
        message_dict = json.loads(message_data_str)

        message_instance = CloudMessage.model_validate(message_dict)
        message_instance.model_dump_json(by_alias=True, indent=4, exclude_none=True)

        topic_data_str = """
        {
            "topicId": "general",
            "name": "General",
            "bots": [
                {
                    "appId": 2345,
                    "bundle": "com.peoplepowerco.engage",
                    "name": "My Engage Bot",
                    "author": "Your Company",
                    "category": "S,W",
                    "type": 0,
                    "core": -1
                }
            ]
        }
        """

        topic_dict = json.loads(topic_data_str)

        topic_instance = CloudTopic.model_validate(topic_dict)
        topic_instance.model_dump_json(by_alias=True, indent=4, exclude_none=True)

        question_data_str = r"""
        {
                            "id": 50234,
                            "appInstanceId": 67,
                            "creationDate": "2023-03-04T12:12:12-07:00",
                            "creationDateMs": 1646537712000,
                            "key": "Question key",
                            "editable": true,
                            "question": "What do you think of this question?",
                            "placeholder": "Some hint",
                            "collection": {
                                "name": "Urgent questions",
                                "description": "Some description",
                                "icon": "Icon name",
                                "media": "Reference to media",
                                "mediaContentType": "image/jpeg",
                                "weight": 10
                            },
                            "deviceId": "optional_device_id",
                            "icon": "optional_icon_name",
                            "displayType": 0,
                            "defaultAnswer": "1000",
                            "answerFormat": "^\\d{4}$",
                            "slider": {
                                "min": 0,
                                "max": 100,
                                "inc": 5,
                                "minDesc": "min value description",
                                "maxDesc": "max value description",
                                "unitsDesc": "UOM description"
                            },
                            "sectionTitle": "Main questions",
                            "sectionId": 2,
                            "questionWeight": 3,
                            "responseType": 4,
                            "responseOptions": [
                                {
                                    "id": 0,
                                    "text": "Red"
                                },
                                {
                                    "id": 1,
                                    "text": "Yellow"
                                }
                            ],
                            "answerStatus": 4,
                            "answer": "This is some text input",
                            "answerDate": "2016-03-04T12:12:12-07:00",
                            "answerDateMs": 1446539712000,
                            "answerModified": false
        }
        """

        # Convert JSON string to Pydantic model
        question_dict = json.loads(question_data_str)

        question_instance = CloudQuestion.model_validate(question_dict)
        question_instance.model_dump_json(by_alias=True, indent=4, exclude_none=True)

        bot_messages_str = """
        [
                        {
                                "messageId": 123,
                                "scheduleType": 0,
                                "status": 1,
                                "topicId": "general",
                                "appInstanceId": 456,
                                "contentKey": "Short content description",
                                "creationTime": 1646537712000,
                                "maxDeliveryTime": 1666537712000,
                                "deliveryDayTime": 36000,
                                "timeToLive": 3600
                            },
                            {
                                "messageId": 124,
                                "scheduleType": 0,
                                "status": 2,
                                "topicId": "general",
                                "appInstanceId": 456,
                                "contentKey": "Short content description",
                                "creationTime": 1646537712000,
                                "maxDeliveryTime": 1666537712000,
                                "deliveryDayTime": 36000,
                                "timeToLive": 3600,
                                "deliveryTime": 1666037712000
                            },
                            {   "messageId": 125,
                                "scheduleType": 1,
                                "status": 1,
                                "topicId": "general",
                                "appInstanceId": 457,
                                "contentKey": "Short content description",
                                "creationTime": 1646537712000,
                                "maxDeliveryTime": 1666537712000,
                                "timeToLive": 3600,
                                "schedule": "0 0 10 ? * SUN"
                            },
                            {
                                "messageId": 126,
                                "originalMessageId": 123,
                                "scheduleType": 0,
                                "status": 3,
                                "topicId": "general",
                                "userId": 789,
                                "contentText": "Reply from a user",
                                "lang": "en",
                                "creationTime": 1646537712000
                            }
        ]
        """

        bot_trigger_dict = json.loads(bot_messages_str)

        ta = TypeAdapter(List[BotMessage])
        message_list = ta.validate_python(bot_trigger_dict)

        # serialized_objects = [dict(message) for message  in message_list]

        # to filter null keys
        serialized_objects = [
            json.loads(
                message.model_dump_json(by_alias=True, indent=4, exclude_none=True)
            )
            for message in message_list
        ]

        # Serialize the list of serialized objects to JSON string
        json.dumps(serialized_objects, indent=4)
