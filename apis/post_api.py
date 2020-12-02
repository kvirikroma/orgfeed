from flask_restx.namespace import Namespace
from flask_restx import fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from services import post_service, check_page, check_uuid
from .utils import OptionsResource
from models import pages_count_model, required_query_params, DATETIME_FORMAT
from models.post_model import PostCreateModel, PostFullModel, PostsStatistics


api = Namespace("post", "Endpoints for news posts")

post_create = api.model(
    "post_create_model",
    PostCreateModel()
)

full_post = api.model(
    "full_post_model",
    PostFullModel()
)

posts_list = api.model(
    'list_of_posts',
    {
        "posts":
            fields.List(
                fields.Nested(full_post)
            )
    }
)

counted_posts_list = api.model(
    'counted_list_of_posts',
    {
        "posts":
            fields.List(
                fields.Nested(full_post)
            ),
        "pages_count": pages_count_model
    }
)

posts_statistics = api.model(
    'posts_statistics_model',
    PostsStatistics()
)


@api.route('')
class Post(OptionsResource):
    @api.doc("create_post", security='apikey')
    @api.marshal_with(full_post, code=201)
    @api.response(404, description="Attachment not found")
    @api.expect(post_create, validate=True)
    @jwt_required
    def post(self):
        """Create a post"""
        return None, 201

    @api.doc("edit_post", security='apikey', params=required_query_params({"id": "Post ID"}))
    @api.marshal_with(full_post, code=201)
    @api.response(404, description="Post or attachment not found")
    @api.response(403, description="Have no privileges to edit this post")
    @api.expect(post_create, validate=True)
    @jwt_required
    def put(self):
        """Edit a post"""
        return None, 201

    @api.doc("get_post", security='apikey', params=required_query_params({"id": "Post ID"}))
    @api.marshal_with(full_post, code=200)
    @api.response(404, description="Post not found")
    @jwt_required
    def get(self):
        """Get a post by ID"""
        return None, 200

    @api.doc("delete_post", security='apikey', params=required_query_params(
        {"id": "Post ID", "with_attachments": "Delete also every attachment of the post"}
    ))
    @api.response(201, description="Success")
    @api.response(403, description="Can not remove other users` posts or attachments")
    @api.response(404, description="Post not found")
    @jwt_required
    def delete(self):
        """Remove a post"""
        return None, 201


@api.route('/approve')
class ApprovePost(OptionsResource):
    @api.doc("approve_post", security='apikey', params=required_query_params({"id": "Post ID"}))
    @api.marshal_with(full_post, code=201)
    @api.response(404, description="Post not found")
    @api.response(403, description="Have no privileges to approve this post")
    @jwt_required
    def post(self):
        """Approve a post (only for moderators and admins)"""
        return None, 201


@api.route('/archive')
class ArchivePost(OptionsResource):
    @api.doc("archive_post", security='apikey', params=required_query_params({"id": "Post ID"}))
    @api.marshal_with(full_post, code=201)
    @api.response(404, description="Post not found")
    @api.response(403, description="Have no privileges to archive this post")
    @jwt_required
    def post(self):
        """Archive a post (only for moderators and admins)"""
        return None, 201

    @api.doc("get_archived_posts", security='apikey', params=required_query_params({'page': 'page number'}))
    @api.marshal_with(counted_posts_list, code=200)
    @jwt_required
    def get(self):
        """Get archived posts"""
        return None, 200


@api.route('/biggest')
class BiggestPost(OptionsResource):
    @api.doc("get_biggest_post", security='apikey', params=required_query_params({
        "date": f"Date in '{DATETIME_FORMAT}' format",
        "include_archived": "Search in archived posts or not ('true' or 'false')"
    }))
    @api.marshal_with(full_post, code=201)
    @api.response(404, description="Post not found")
    @jwt_required
    def get(self):
        """Get biggest post by date"""
        return None, 201


@api.route('/statistics')
class PostStat(OptionsResource):
    @api.doc("get_posts_statistics", security='apikey', params=required_query_params({
        "start_year": "Year to start from",
        "start_month": "Month to start from",
        "end_year": "Year to finish with",
        "end_month": "Month to finish with",
        "subunit": "Subunit to get data from"
    }))
    @api.marshal_with(posts_statistics, code=200, as_list=True)
    @jwt_required
    def get(self):
        """Get statistics of posts for each employee of the subunit"""
        return None, 200
