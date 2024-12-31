'''
Created on January 3, 2024

This file is subject to the terms and conditions defined in the
file 'LICENSE.txt', which is part of this source code package.

@author: David Moss
'''

from enum import Enum
import json
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Dict
from pydantic import RootModel


class CloudDeliveryType(Enum):
    IN_APP = 0
    PUSH = 1
    EMAIL = 2
    SMS = 3
    MMS = 5
    VOICE_CALL = 7


class ContentType(Enum):
    TEXT = 0
    HTML = 1
    MARKDOWN = 2


class SchedulingType(Enum):
    ONE_TIME = 0
    RECURRING = 1


class CloudTopicPriority(Enum):
    UNSET = -1
    LOW = 0
    MEDIUM = 1
    HIGH = 2


class CloudMessageStatus(Enum):
    INITIAL = 0
    READY = 1
    SCHEDULED = 2
    DELIVERED = 3
    DELETED = 4


class CloudBot(BaseModel):
    app_id: int = Field(..., alias='appId')
    bundle: str
    name: str
    author: str
    category: str
    type: int
    core: int


class CloudTopic(BaseModel):
    topic_id: str = Field(..., alias='topicId')
    name: str
    bots: List[CloudBot]


class Collection(BaseModel):
    name: str
    description: str
    icon: str
    media: str
    media_content_type: str = Field(..., alias='mediaContentType')
    weight: int


class Slider(BaseModel):
    min: int
    max: int
    inc: int
    min_desc: str = Field(..., alias='minDesc')
    max_desc: str = Field(..., alias='maxDesc')
    units_desc: str = Field(..., alias='unitsDesc')


class ResponseOption(BaseModel):
    id: int
    text: str


class CloudQuestion(BaseModel):
    id: int
    app_instance_id: int = Field(..., alias='appInstanceId')
    creation_date: datetime = Field(..., alias='creationDate')
    creation_date_ms: int = Field(..., alias='creationDateMs')
    key: str
    editable: bool
    question: str
    placeholder: Optional[str] = None
    collection: Collection
    device_id: Optional[str] = Field(None, alias='deviceId')
    icon: Optional[str] = Field(None)
    display_type: int = Field(..., alias='displayType')
    default_answer: Optional[str] = Field(None, alias='defaultAnswer')
    answer_format: Optional[str] = Field(None, alias='answerFormat')
    slider: Optional[Slider] = None
    section_title: str = Field(..., alias='sectionTitle')
    section_id: int = Field(..., alias='sectionId')
    question_weight: int = Field(..., alias='questionWeight')
    response_type: int = Field(..., alias='responseType')
    response_options: Optional[List[ResponseOption]] = Field(None, alias='responseOptions')
    answer_status: int = Field(..., alias='answerStatus')
    answer: Optional[str] = None
    answer_date: Optional[datetime] = Field(None, alias='answerDate')
    answer_date_ms: Optional[int] = Field(None, alias='answerDateMs')
    answer_modified: Optional[bool] = Field(None, alias='answerModified')


TextContent = RootModel[Dict[str, str]]
SubjectContent = RootModel[Dict[str, str]]


class Attachment(BaseModel):
    name: str
    content: str
    content_type: str = Field(..., alias='contentType')
    content_id: str = Field(..., alias='contentId')


class Content(BaseModel):
    delivery_type: CloudDeliveryType = Field(..., alias='deliveryType')
    content_type: ContentType = Field(..., alias='contentType')
    text: TextContent = Field(..., alias='text')
    type: Optional[int] = None
    title: Optional[str] = None
    subtitle: Optional[str] = None
    category: Optional[str] = None
    sound: Optional[str] = None
    subject: Optional[SubjectContent] = None
    attachments: Optional[List[Attachment]] = None

    class Config:
        use_enum_values = True  # Serialize enums using their values
        populate_by_name = True


class Recipient(BaseModel):
    categories: Optional[List[int]] = None
    roles: Optional[List[int]] = None
    location_access: Optional[int] = Field(None, alias='locationAccess')
    user_id: Optional[int] = Field(None, alias='userId')


class CloudMessage(BaseModel):
    message_id: Optional[int] = Field(None, alias='messageId')
    status: CloudMessageStatus
    original_message_id: Optional[int] = Field(None, alias='originalMessageId')
    topic_id: str = Field(..., alias='topicId')
    schedule_type: SchedulingType = Field(..., alias='scheduleType')
    content_key: str = Field(..., alias='contentKey')
    contents: List[Content]
    question_id: Optional[int] = Field(None, alias='questionId')
    media_url: Optional[str] = Field(None, alias='mediaUrl')
    media_content_type: Optional[str] = Field(None, alias='mediaContentType')
    max_delivery_date: str = Field(..., alias='maxDeliveryDate')
    delivery_day_time: int = Field(..., alias='deliveryDayTime')
    time_to_live: int = Field(..., alias='timeToLive')
    schedule: Optional[str] = Field(None, alias='schedule')
    recipients: List[Recipient]
    question: Optional[CloudQuestion] = None  # Question is optional

    class Config:
        use_enum_values = True  # Serialize enums using their values
        populate_by_name = True


class BotMessage(BaseModel):
    message_id: int = Field(..., alias='messageId')
    original_message_id: Optional[int] = Field(None, alias='originalMessageId')
    schedule_type: SchedulingType = Field(..., alias='scheduleType')
    status: CloudMessageStatus
    topic_id: Optional[str] = Field(None, alias='topicId')
    app_instance_id: Optional[int] = Field(None, alias='appInstanceId')
    content_key: Optional[str] = Field(None, alias='contentKey')
    content_text: Optional[str] = Field(None, alias='contentText')
    creation_time: Optional[int] = Field(None, alias='creationTime')
    max_delivery_time: Optional[int] = Field(None, alias='maxDeliveryTime')
    delivery_day_time: Optional[int] = Field(None, alias='deliveryDayTime')
    time_to_live: Optional[int] = Field(None, alias='timeToLive')
    delivery_time: Optional[int] = Field(None, alias='deliveryTime')
    lang: Optional[str] = Field(None, alias='lang')
    schedule: Optional[str] = Field(None, alias='schedule')
    delivery_date: Optional[str] = Field(None, alias='deliveryDate')

    class Config:
        allow_mutation = False
        frozen = True
        use_enum_values = True  # Serialize enums using their values
        populate_by_name = True

    def priority_phrase(self) -> str:
        return self.content_key if self.content_key not in [None, ''] else self.content_text


class BotUpdatedMessage(BaseModel):
    messageId: int = Field(alias='messageId')
    status: CloudMessageStatus
    delivery_date: Optional[str] = Field(None, alias='deliveryDate')
    schedule: Optional[str] = Field(None, alias='schedule')

    @classmethod
    def from_bot_message(cls, bot_message: BotMessage) -> 'BotUpdatedMessage':
        return cls(
            messageId=bot_message.message_id,
            status=bot_message.status,
            delivery_date=bot_message.delivery_date,
            schedule=bot_message.schedule
        )

    class Config:
        use_enum_values = True  # Serialize enums using their values
        populate_by_name = True
