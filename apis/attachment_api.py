from flask_restx.namespace import Namespace
from flask_restx.reqparse import RequestParser
from flask_restx import fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.datastructures import FileStorage

from services import attachment_service, get_page, get_uuid
from .utils import OptionsResource
from models import pages_count_model, required_query_params
from models.attachment_model import AttachmentModel


api = Namespace("attachment", "Attachments for news posts")


parser: RequestParser = api.parser()
parser.add_argument('file', location='files',
                    type=FileStorage, required=True)


attachment = api.model(
    'attachment_model',
    AttachmentModel()
)


counted_attachments_list = api.model(
    'counted_list_of_attachments',
    {
        "attachments":
            fields.List(
                fields.Nested(attachment)
            ),
        "pages_count": pages_count_model
    }
)


@api.route('')
class Attachment(OptionsResource):
    @api.doc("attachment_upload", security='apikey')
    @api.marshal_with(attachment, code=201)
    @api.response(400, description="Cannot get file from request")
    @api.response(413, description="Attachment size is too large")
    @api.expect(parser, validate=True)
    @jwt_required
    def post(self):
        """Upload an attachment to the server"""
        return attachment_service.save_attachment(get_jwt_identity(), request.files.get('file')), 201

    @api.doc("attachment_download", params=required_query_params({"id": "Attachment ID"}), security='apikey')
    @api.response(200, description="Success (response contains a requested file)")
    @api.response(404, description="Attachment not found")
    @jwt_required
    def get(self):
        """Download an attachment from server"""
        return attachment_service.get_attachment(get_uuid(request))

    @api.doc("attachment_remove", params=required_query_params({"id": "Attachment ID"}), security='apikey')
    @api.response(201, description="Success")
    @api.response(403, description="Can not delete attachments of other users")
    @api.response(404, description="Attachment not found")
    @jwt_required
    def delete(self):
        """Delete an attachment from server"""
        return attachment_service.delete_attachment(get_jwt_identity(), get_uuid(request)), 201


@api.route('/employee')
class UserAttachments(OptionsResource):
    @api.doc(
        "get_employee_attachments",
        params=required_query_params({"page": "page number", "id": "Employee`s ID"}),
        security='apikey'
    )
    @api.marshal_with(counted_attachments_list, code=200)
    @api.response(404, description="Employee not found")
    @jwt_required
    def get(self):
        """Get list of employee`s attachments"""
        return attachment_service.get_all_attachments(get_uuid(request), get_page(request)), 200
