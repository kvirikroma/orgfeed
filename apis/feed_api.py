from datetime import date

from flask_restx.namespace import Namespace
from flask import request, abort
from flask_jwt_extended import jwt_required

from services import post_service, get_page, get_uuid
from .utils import OptionsResource
from apis.post_api import counted_posts_list, full_post
from models import required_query_params, DATETIME_FORMAT
from models.post_model import PostType


api = Namespace("feed", "News feed api")


@api.route('/news/organization')
class OrgNews(OptionsResource):
    @api.doc("get_org_news", security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get news feed of all organization"""
        return post_service.get_feed(PostType.organization_news, get_page(request)), 200


@api.route('/news/subunit')
class SubunitNews(OptionsResource):
    @api.doc("get_subunit_news", security='apikey', params=required_query_params(
        {'page': 'page number', "id": "ID of the subunit"}
    ))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get news feed of the subunit"""
        return post_service.get_feed(PostType.subunit_news, get_page(request), get_uuid(request)), 200


@api.route('/announcements/organization')
class OrgAnnouncements(OptionsResource):
    @api.doc("get_org_announcements", security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get announcements feed of all organization"""
        return post_service.get_feed(PostType.organization_announcement, get_page(request)), 200


@api.route('/announcements/subunit')
class SubunitAnnouncements(OptionsResource):
    @api.doc("get_subunit_announcements", security='apikey', params=required_query_params(
        {'page': 'page number', "id": "ID of the subunit"}
    ))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get announcements feed of the subunit"""
        return post_service.get_feed(PostType.subunit_announcement, get_page(request), get_uuid(request)), 200


@api.route('/biggest')
class BiggestPost(OptionsResource):
    @api.doc("get_biggest_post", security='apikey', params=required_query_params({
        "day": f"Date in '{DATETIME_FORMAT}' format (example: '2020-12-31')",
        "include_archived": {'description': "Search in archived posts or not", "enum": ['true', 'false']}
    }))
    @api.marshal_with(full_post, code=200)
    @api.response(404, description="Post not found")
    @api.response(422, description="Can not parse parameters")
    @jwt_required
    def get(self):
        """Get biggest post by date"""
        try:
            day = date.fromisoformat(request.args.get("day", ''))
        except ValueError:
            return abort(422, "Incorrect date format")
        if request.args.get("include_archived", '').lower() == 'true':
            include_archived = True
        elif request.args.get("include_archived", '').lower() == 'false':
            include_archived = False
        else:
            return abort(422, "Incorrect 'include_archived' parameter")
        return post_service.get_biggest_post(day, include_archived), 200
