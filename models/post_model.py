from enum import Enum

from flask_restx import fields

from apis.attachment_api import attachment
from . import ModelCreator, create_id_field, create_datetime_field, copy_field


class PostType(Enum):
    organization_news = 0
    subunit_news = 1
    organization_announcement = 2
    subunit_announcement = 3


class PostStatus(Enum):
    under_consideration = 0
    posted = 1
    archived = 2
    returned_for_improvement = 3
    rejected = 4


class AttachmentsListModel(ModelCreator):
    attachments = fields.List(
        create_id_field(
            required=True,
            description="Attachment ID to include into the post"
        ),
        description="List of an attachment IDs to include into the post",
        required=False
    )


class PostBaseModel(ModelCreator):
    title = fields.String(
        required=True,
        description="Title of the post",
        example="The friday demo",
        min_length=3,
        max_length=512
    )
    body = fields.String(
        required=True,
        description="Body of the post",
        example="The demo day is at this friday at 5:00 PM, don't be late!",
        min_length=0,
        max_length=81920
    )
    post_type = fields.String(
        required=True,
        description="Type of the post",
        example=PostType.organization_news.name,
        enum=[p_type.name for p_type in PostType]
    )


class PostCreateModel(PostBaseModel, AttachmentsListModel):
    pass


class PostEditModel(AttachmentsListModel):
    title = copy_field(PostBaseModel.title, required=False)
    body = copy_field(PostBaseModel.body, required=False)
    post_type = copy_field(PostBaseModel.post_type, required=False)


class PostFullModel(PostBaseModel):
    id = create_id_field(
        required=True,
        description="Post ID in database"
    )
    created_on = create_datetime_field(
        required=True,
        description="The time post was created on"
    )
    published_on = create_datetime_field(
        required=False,
        description="The time post was published on"
    )
    archived_on = create_datetime_field(
        required=True,
        description="The time post was (or will be) archived on"
    )
    author = create_id_field(
        required=True,
        description="ID of the author of the post"
    )
    approved_by = create_id_field(
        required=False,
        description="ID of the employee in charge of reviewing this post"
    )
    status = fields.String(
        required=True,
        description="Status of the post",
        example=PostStatus.under_consideration.name,
        enum=[p_status.name for p_status in PostStatus]
    )
    size = fields.Integer(
        required=True,
        description="Post size in bytes (including its attachments)",
        example=256,
        min=1
    )
    attachments = fields.List(
        fields.Nested(attachment),
        description="List of an attachments of the post"
    )
