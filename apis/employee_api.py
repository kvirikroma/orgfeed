from flask_restx.namespace import Namespace
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import employee_service, check_page, check_uuid
from .utils import OptionsResource
from models import required_query_params
from models.employee_model import auth_model


api = Namespace('employee', description='Employees-related actions')

auth = api.model(
    'auth_model',
    {},
)

token = api.model(
    'token',
    {}
)


@api.route('/auth')
class Albums(OptionsResource):
    @api.doc('employee_auth')
    @api.marshal_with(token, code=200)
    @api.expect(auth, validate=True)
    @api.response(401, description="Invalid credentials")
    def post(self):
        """Log into an account"""
        return None, 200
