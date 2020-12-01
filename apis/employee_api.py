from flask_restx.namespace import Namespace
from flask_restx import fields
from flask import request
from flask_jwt_extended import (jwt_required, get_jwt_identity, jwt_refresh_token_required,
                                create_access_token, create_refresh_token)

from services import employee_service, check_page, check_uuid
from .utils import OptionsResource
from models import required_query_params, pages_count_model
from models.employee_model import AuthModel, FullEmployeeModel, EmployeeRegistrationModel, TokenModel, CommonEmployeeModel


api = Namespace('employee', description='Employees-related actions')

auth = api.model(
    'auth_model',
    AuthModel(),
)

token = api.model(
    'token_model',
    TokenModel()
)

employee_registration = api.model(
    'employee_registration_model',
    EmployeeRegistrationModel()
)

full_employee = api.model(
    'full_employee_model',
    FullEmployeeModel()
)

employee_edit = api.model(
    'employee_edit_model',
    CommonEmployeeModel()
)

counted_employees_list = api.model(
    'counted_list_of_employees',
    {
        "employees":
            fields.List(
                fields.Nested(full_employee)
            ),
        "pages_count": pages_count_model
    }
)


@api.route('')
class Employee(OptionsResource):
    @api.doc('get_employee', security='apikey', params=required_query_params({'id': 'employee ID'}))
    @api.marshal_with(full_employee, code=200)
    @api.response(404, description="Employee not found")
    @jwt_required
    def get(self):
        """Get employee`s account info"""
        return None, 200

    @api.doc('edit_employee', security='apikey', params=required_query_params({'id': 'employee ID'}))
    @api.marshal_with(full_employee, code=200)
    @api.response(404, description="Employee not found")
    @api.response(403, description="Not allowed to edit this employee's info")
    @api.expect(employee_edit, validate=True)
    @jwt_required
    def put(self):
        """Edit employee`s account info (only for admins)"""
        return None, 201

    @api.doc('employee_register', security='apikey')
    @api.expect(employee_registration, validate=True)
    @api.response(201, description="Success")
    @api.response(403, description="Non-admins can not register new employees")
    @api.response(409, description="Employee with given email already exists")
    @jwt_required
    def post(self):
        """Register a new employee (only for admins)"""
        return None, 201


@api.route('/auth')
class Auth(OptionsResource):
    @api.doc('employee_auth')
    @api.marshal_with(token, code=200)
    @api.expect(auth, validate=True)
    @api.response(401, description="Invalid credentials")
    def post(self):
        """Log into an account"""
        return None, 200


@api.route('/auth/refresh')
class AuthRefresh(OptionsResource):
    @api.doc('employee_auth_refresh', security='apikey')
    @api.marshal_with(token, code=200)
    @jwt_refresh_token_required
    def post(self):
        """Refresh pair of tokens"""
        identity = get_jwt_identity()
        return {
               'access_token': create_access_token(identity=identity),
               'refresh_token': create_refresh_token(identity=identity),
               'user_id': identity
        }, 200


@api.route('/fired_moderators')
class AuthRefresh(OptionsResource):
    @api.doc('fired_moderators_of_subunit', security='apikey', params=required_query_params({'id': 'SubUnit ID'}))
    @api.marshal_with(counted_employees_list, code=200)
    @jwt_required
    def get(self):
        """Get fired admins and moderators of the subunit"""
        return None, 200
