from flask_restx.namespace import Namespace
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import employee_service, check_page, check_uuid
from .utils import OptionsResource


api = Namespace("attachment", "Attachments for news posts")

