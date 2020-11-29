from typing import Dict

from flask_restx import fields


ID_EXAMPLE = 'd1d3ee42-731c-04d9-0eee-16d3e7a62948'
EMAIL_EXAMPLE = 'test@mail.com'
EMAIL_PATTERN = r'\S+@\S+\.\S+'
PASSWORD_EXAMPLE = 'Qwerty123'


class ModelCreator:
    def __new__(cls, *args, **kwargs):
        result = {}
        raw_result = dir(cls)
        for item in raw_result:
            if not item.startswith("__") or not item.endswith("__"):
                result[item] = getattr(cls, item)
        return result


def create_id_field(required=False, description=""):
    return fields.String(
        required=required,
        description=description,
        example=ID_EXAMPLE,
        min_length=36,
        max_length=36
    )


def create_email_field(required=False, description=""):
    return fields.String(
        required=required,
        description=description,
        example=EMAIL_EXAMPLE,
        min_length=5,
        max_length=256
    )


pages_count_model = fields.Integer(
    required=False,
    description="Total count of pages in the resource",
    example=1,
    min=0
)


def required_query_params(request_args: Dict[str, str]) -> Dict[str, Dict[str, str or bool]]:
    result = {}
    for item in request_args:
        result[item] = {"description": request_args[item], "required": True}
    return result


def update_dict(dict1: dict or ModelCreator, dict2: dict or ModelCreator) -> dict:
    result = dict1.copy()
    result.update(dict2)
    return result
