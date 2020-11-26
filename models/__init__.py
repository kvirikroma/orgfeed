from typing import Dict

from flask_restx import fields


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
