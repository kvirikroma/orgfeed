from flask_restx.namespace import Namespace
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import post_service, check_page, check_uuid
from .utils import OptionsResource
from apis.post_api import counted_posts_list
from models import required_query_params


api = Namespace("feed", "News feed api")


@api.route('/news/organization')
class OrgNews(OptionsResource):
    @api.doc("get_org_news", security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get news feed of all organization"""
        return None, 200


@api.route('/news/subunit')
class SubunitNews(OptionsResource):
    @api.doc("get_subunit_news", security='apikey', params=required_query_params(
        {'page': 'page number', "subunit_id": "ID of the subunit"}
    ))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get news feed of the subunit"""
        return None, 200


@api.route('/announcements/organization')
class OrgAnnouncements(OptionsResource):
    @api.doc("get_org_announcements", security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get announcements feed of all organization"""
        return None, 200


@api.route('/announcements/subunit')
class SubunitAnnouncements(OptionsResource):
    @api.doc("get_subunit_announcements", security='apikey', params=required_query_params(
        {'page': 'page number', "subunit_id": "ID of the subunit"}
    ))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get announcements feed of the subunit"""
        return None, 200
