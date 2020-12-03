from typing import List, Dict
from datetime import date, datetime, timedelta
from uuid import uuid4
from math import ceil

from flask import abort

from repositories import post_repository, attachment_repository, employee_repository, subunit_repository, Post
from models.post_model import PostStatus, PostType
from models.employee_model import EmployeeType
from . import attachment_service, any_non_nones, default_page_size


def prepare_post(post: Post) -> dict:
    result = post.__dict__
    result['post_type'] = PostType(post.type).name
    result['status'] = PostStatus(post.status).name
    result['attachments'] = [attachment_service.prepare_attachment(attachment) for attachment in post.attachments]
    return result


def prepare_posts_list(posts: List[Post]) -> List[dict]:
    return [prepare_post(post) for post in posts]


def calculate_post_size(post: Post) -> int:
    size = len(post.body.encode())
    size += len(post.title.encode())
    size += sum(attachment_repository.get_attachment_size(attachment.id) for attachment in post.attachments)
    return size


def archive_pages_count():
    return ceil(post_repository.count_archived_posts() / default_page_size)


def feed_pages_count(posts_type: PostType, subunit_id: str = None):
    return ceil(post_repository.feed_count(posts_type, subunit_id) / default_page_size)


def get_post(post_id: str) -> dict:
    return prepare_post(post_repository.get_post_by_id(post_id))


def create_post(creator_id: str, title: str, body: str, post_type: str, attachments: List[str], **kwargs) -> dict:
    if not attachment_repository.ensure_attachments_exist(attachments):
        abort(404, "Attachment not found")
    post = Post()
    post.creator = creator_id
    post.type = PostType[post_type].value
    post.title = title
    post.body = body
    post.status = PostStatus.posted
    post.id = str(uuid4())
    creator = employee_repository.get_employee_by_id(creator_id)
    if not creator or creator.user_type == EmployeeType.user.value:
        post.status = PostStatus.under_consideration
    post_repository.add_or_edit_post(post)
    attachment_repository.add_attachments_to_post(post.id, attachments)
    return get_post(post.id)


def edit_post(editor_id: str, post_id: str, title: str, body: str, post_type: str, attachments: List[str], **kwargs) -> dict:
    if not any_non_nones((title, body, post_type, attachments)):
        abort(422, "All fields are null")
    post = post_repository.get_post_by_id(post_id)
    if not post:
        abort(404, "Post not found")
    if post.author != editor_id:
        editor = employee_repository.get_employee_by_id(editor_id)
        if not editor or editor.user_type != EmployeeType.admin.value:
            abort(403, "Non-admins can not edit posts of other users")
    for existing, new in (('title', title), ('body', body), ('post_type', post_type)):
        setattr(post, existing, new or getattr(post, existing))
    post_repository.add_or_edit_post(post)
    if attachments is not None:
        attachment_repository.add_attachments_to_post(None, [attachment.id for attachment in post.attachments])
        attachment_repository.add_attachments_to_post(post.id, attachments)
    return get_post(post.id)


def set_post_status(setter_id: str, post_id: str, status: PostStatus) -> dict:
    post = post_repository.get_post_by_id(post_id)
    if not post:
        abort(404, "Post not found")
    editor = employee_repository.get_employee_by_id(setter_id)
    if not editor or editor.user_type == EmployeeType.user.value:
        abort(403, "Non-(admins/moderators) can not change post statuses")
    if post.status != status.value:
        if status.value == PostStatus.archived:
            post.archived_on = datetime.utcnow()
        if status.value == PostStatus.posted:
            post.published_on = datetime.utcnow()
            post.approved_by = setter_id
        if post.status == PostStatus.archived.value:
            post.archived_on = datetime.utcnow() + timedelta(hours=4380)
    post.status = status.value
    return prepare_post(post_repository.add_or_edit_post(post))


def delete_post(deleter_id: str, post_id: str) -> None:
    post = post_repository.get_post_by_id(post_id)
    if not post:
        abort(404, "Post not found")
    if post.author != deleter_id:
        editor = employee_repository.get_employee_by_id(deleter_id)
        if not editor or editor.user_type == EmployeeType.user.value:
            abort(403, "Non-(admins/moderators) can not delete posts of other users")
    return post_repository.delete_post(post)


def get_all_employee_posts(employee_id: str) -> List[dict]:
    if not employee_repository.get_employee_by_id(employee_id):
        abort(404, "Employee not found")
    return prepare_posts_list(post_repository.get_posts_of_employee(employee_id))


def get_biggest_post(day: date, include_archived: bool) -> dict:
    posts_of_day = prepare_posts_list(post_repository.get_posts_by_date(day, include_archived))
    return max(posts_of_day, key=lambda post: post["size"])


def get_statistics(
        subunit_id: str, start_year: int, start_month: int, end_year: int, end_month: int
) -> List[Dict[str, str or int]]:
    if not subunit_repository.get_subunit_by_id(subunit_id):
        abort(404, "Subunit not found")
    end_month += 1
    if end_month > 12:
        end_year += 1
        end_month = 1
    try:
        start_date = date(start_year, start_month, 1)
        end_date = date(end_year, end_month, 1) - timedelta(days=1)
    except ValueError:
        abort(422, 'Invalid date given')
    pass


def get_feed(post_type: PostType, page: int, subunit_id: str = None) -> Dict[str, int or dict]:
    pages_count = feed_pages_count(post_type, subunit_id)
    if page <= pages_count:
        posts = prepare_posts_list(post_repository.get_feed(post_type, page, default_page_size, subunit_id))
    else:
        posts = []
    return {
        "posts": posts,
        "pages_count": pages_count
    }


def get_archived_posts(page: int) -> Dict[str, str or dict]:
    pages_count = archive_pages_count()
    if page <= pages_count:
        posts = prepare_posts_list(post_repository.get_archived_posts(page, default_page_size))
    else:
        posts = []
    return {
        "posts": posts,
        "pages_count": pages_count
    }
