from enum import Enum

from flask_restx import fields

from . import create_id_field, create_email_field, ModelCreator, PASSWORD_EXAMPLE


class EmployeeType(Enum):
    user = 0
    moderator = 1
    admin = 2


class EmailModel(ModelCreator):
    email = create_email_field(
        required=True,
        description="Employee`s email (login)"
    )


class EmployeeIdModel(ModelCreator):
    id = create_id_field(
        required=True,
        description="Employee`s ID in database"
    )


class PasswordModel(ModelCreator):
    password = fields.String(
        required=True,
        description='Employee`s password',
        example=PASSWORD_EXAMPLE,
        min_length=8,
        max_length=64
    )


class AuthModel(PasswordModel, EmailModel):
    pass


class CommonEmployeeModel(EmailModel):
    full_name = fields.String(
        required=True,
        description="Employee`s name, surname, etc.",
        example="Gordon Freeman",
        min_length=2,
        max_length=512
    )
    subunit = create_id_field(
        required=True,
        description="ID of the subunit in which the employee works"
    )
    user_type = fields.String(
        required=True,
        description="Type of employee that describes his/her privileges",
        example="user",
        enum=[e_type.name for e_type in EmployeeType]
    )
    fired = fields.Boolean(
        required=True,
        description="Is the employee fired or not",
        example=False
    )


class FullEmployeeModel(CommonEmployeeModel, EmployeeIdModel):
    pass


class TokenModel(ModelCreator):
    access_token = fields.String(
        required=True,
        description='Token to access resources',
        example='qwerty'
    )
    refresh_token = fields.String(
        required=True,
        description='Token to refresh pair of tokens',
        example='qwerty'
    )
    user_id = FullEmployeeModel.id


class EmployeeRegistrationModel(CommonEmployeeModel, PasswordModel):
    pass
