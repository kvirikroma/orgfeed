from flask_restx.namespace import Namespace
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import subunit_service, get_uuid
from .utils import OptionsResource
from models import required_query_params, update_dict
from apis.employee_api import full_employee
from models.subunit_model import CommonSubunitModel, SubunitEditModel, FullSubunitModel, fields


api = Namespace('subunit', description='SubUnit-related actions')

subunit_create = api.model(
    'subunit_create_model',
    CommonSubunitModel()
)

subunit_edit = api.model(
    'subunit_edit_model',
    SubunitEditModel()
)

full_subunit = api.model(
    'full_subunit_model',
    update_dict(
        FullSubunitModel(),
        {
            "employees": fields.List(fields.Nested(full_employee))
        }
    )
)


@api.route('')
class Subunit(OptionsResource):
    @api.doc('get_subunit', security='apikey', params=required_query_params({'id': 'SubUnit ID'}))
    @api.marshal_with(full_subunit, code=200)
    @api.response(404, description="SubUnit not found")
    @jwt_required
    def get(self):
        """Get info about subunit"""
        return subunit_service.get_subunit(get_uuid(request)), 200

    @api.doc('edit_subunit', security='apikey', params=required_query_params({'id': 'SubUnit ID'}))
    @api.marshal_with(full_subunit, code=201)
    @api.response(404, description="SubUnit or leader not found")
    @api.response(403, description="Non-admin tried to change a subunit")
    @api.response(409, description="SubUnit with this name or email already exists")
    @api.response(422, description="All fields are null")
    @api.expect(subunit_edit, validate=True)
    @jwt_required
    def put(self):
        """Change info about subunit (only for admins)"""
        return subunit_service.edit_subunit(get_jwt_identity(), get_uuid(request), **api.payload), 201

    @api.doc('add_subunit', security='apikey')
    @api.marshal_with(full_subunit, code=201)
    @api.response(403, description="Non-admin tried to create a subunit")
    @api.response(404, description="Leader not found")
    @api.response(409, description="SubUnit with this name or email already exists")
    @api.expect(subunit_create, validate=True)
    @jwt_required
    def post(self):
        """Create a new subunit (only for admins)"""
        return subunit_service.create_subunit(get_jwt_identity(), **api.payload), 201


@api.route('/multiple')
class SubunitList(OptionsResource):
    @api.doc('get_subunit_multiple', security='apikey')
    @api.marshal_with(full_subunit, code=200, as_list=True)
    @api.response(404, description="SubUnit not found")
    @jwt_required
    def get(self):
        """Get list of subunits"""
        return subunit_service.get_all_subunits(), 200
