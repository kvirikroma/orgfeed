from flask_restx import fields

from apis.employee_api import full_employee
from . import create_id_field, ModelCreator
from utils.config import MAX_FILE_SIZE


class AttachmentModel(ModelCreator):
    id = create_id_field(
        required=True,
        description="Attachment ID in database",
    )
    author = fields.Nested(full_employee)
    post = create_id_field(
        required=True,
        description="ID of Post that contains this attachment"
    )
    filename = fields.String(
        required=True,
        description="Name of an attachment",
        example="gravity_gun_firmware.bin",
        min_length=1
    )
    size = fields.Integer(
        required=True,
        description="Size of attachment (in bytes)",
        example=256256,
        min=0,
        max=MAX_FILE_SIZE
    )
