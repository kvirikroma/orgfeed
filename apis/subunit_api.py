from flask_restx.namespace import Namespace
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import subunit_service, check_page, check_uuid
from .utils import OptionsResource
from models import required_query_params, pages_count_model, update_dict
from apis.employee_api import full_employee
from models.subunit_model import CommonSubunitModel, FullSubunitModel, fields


api = Namespace('subunit', description='SubUnit-related actions')

subunit = api.model(
    'subunit_model',
    CommonSubunitModel()
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

raw_su_list = fields.List(fields.Nested(full_subunit))

subunits_list = api.model(
    'counted_list_of_subunits',
    {
        "subunits": raw_su_list,
        "pages_count": pages_count_model
    }
)


@api.route('')
class Subunit(OptionsResource):
    @api.doc('get_subunit', security='apikey', params=required_query_params({'id': 'SubUnit ID'}))
    @api.marshal_with(full_subunit, code=200)
    @api.response(404, description="SubUnit not found")
    @jwt_required
    def get(self):
        """Get info about subunit"""
        return None, 200

    @api.doc('edit_subunit', security='apikey', params=required_query_params({'id': 'SubUnit ID'}))
    @api.marshal_with(full_subunit, code=201)
    @api.response(404, description="SubUnit not found")
    @api.response(403, description="Non-admin tried to change a subunit")
    @api.expect(subunit, validate=True)
    @jwt_required
    def put(self):
        """Change info about subunit (only for admins)"""
        return None, 201

    @api.doc('add_subunit', security='apikey')
    @api.marshal_with(full_subunit, code=201)
    @api.response(403, description="Non-admin tried to create a subunit")
    @api.expect(subunit, validate=True)
    @jwt_required
    def post(self):
        """Create a new subunit (only for admins)"""
        return None, 201


@api.route('/multiple')
class SubunitList(OptionsResource):
    @api.doc('get_subunit_multiple', security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(subunits_list, code=200)
    @api.response(404, description="SubUnit not found")
    @jwt_required
    def get(self):
        """Get list of subunits"""
        return None, 200
