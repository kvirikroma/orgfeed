from typing import List, Dict, Set
from datetime import date, datetime, timedelta
from uuid import uuid4
from math import ceil, floor

from flask import abort

from repositories import post_repository, attachment_repository, employee_repository, subunit_repository, Post, db
from models.post_model import PostStatus, PostType
from models.employee_model import EmployeeType
from . import attachment_service, any_non_nones, default_page_size
from .employee_service import prepare_employee


def prepare_post(post: Post, refresh: bool = True) -> dict:
    if not post:
        return {}
    if refresh:
        db.session.refresh(post)
    result = post.get_dict()
    result['post_type'] = PostType(post.type).name
    result['status'] = PostStatus(post.status).name
    result['size'] = calculate_post_size(post)
    result['attachments'] = [attachment_service.prepare_attachment(attachment) for attachment in post.attachments]
    result['author'] = prepare_employee(post.creator)
    result['approved_by'] = prepare_employee(post.approver) if post.approver else None
    return result


def prepare_posts_list(posts: List[Post]) -> List[dict]:
    return [prepare_post(post, refresh=False) for post in posts]


def calculate_post_size(post: Post) -> int:
    size = len(post.body.encode())
    size += len(post.title.encode())
    size += sum(attachment_repository.get_attachment_size(attachment.id) for attachment in post.attachments)
    return size


def archive_pages_count():
    return ceil(post_repository.count_archived_posts() / default_page_size)


def feed_pages_count(posts_type: PostType, subunit_id: str = None):
    return ceil(post_repository.get_posts_count(posts_type, {PostStatus.posted}, subunit_id) / default_page_size)


def moderation_pages_count(posts_type: PostType = None, posts_statuses: Set[PostStatus] = None, subunit_id: str = None):
    return ceil(post_repository.get_posts_count(posts_type, posts_statuses, subunit_id) / default_page_size)


def get_post(post_id: str) -> dict:
    post = post_repository.get_post_by_id(post_id)
    if not post:
        abort(404, "Post not found")
    return prepare_post(post, refresh=False)


def create_post(creator_id: str, title: str, body: str, post_type: str, attachments: List[str] = None, **kwargs) -> dict:
    if attachments and not attachment_repository.ensure_attachments_exist(attachments):
        abort(404, "Attachment not found")
    post = Post()
    post.author = creator_id
    post.type = PostType[post_type].value
    post.title = title
    post.body = body
    post.id = str(uuid4())
    creator = employee_repository.get_employee_by_id(creator_id)
    if not creator or creator.user_type == EmployeeType.user.value:
        post.status = PostStatus.under_consideration.value
    else:
        post.status = PostStatus.posted.value
        post.published_on = datetime.utcnow() + timedelta(seconds=1)
        post.approved_by = creator_id
    post_repository.add_or_edit_post(post)
    if attachments:
        attachment_repository.add_attachments_to_post(post.id, attachments)
    return get_post(post.id)


def edit_post(
        editor_id: str, post_id: str, title: str = None, body: str = None,
        post_type: str = None, attachments: List[str] = None, **kwargs
) -> dict:
    if not any_non_nones((title, body, post_type, attachments)):
        abort(422, "All fields are null")
    post = post_repository.get_post_by_id(post_id)
    if not post:
        abort(404, "Post not found")
    if post.author != editor_id:
        editor = employee_repository.get_employee_by_id(editor_id)
        if not editor or editor.user_type != EmployeeType.admin.value:
            abort(403, "Non-admins can not edit posts of other users")
    if post_type:
        try:
            post_type = PostType[post_type].value
        except KeyError:
            abort(400, "Incorrect post type")
    for existing, new in (('title', title), ('body', body), ('type', post_type)):
        setattr(post, existing, new or getattr(post, existing))
    post_repository.add_or_edit_post(post)
    if attachments is not None:
        current_attachments = [attachment.id for attachment in post.attachments]
        if current_attachments:
            attachment_repository.add_attachments_to_post(None, current_attachments)
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
        if status == PostStatus.archived:
            post.archived_on = datetime.utcnow()
        if status == PostStatus.posted:
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
    if not posts_of_day:
        abort(404, "Post not found")
    return max(posts_of_day, key=lambda post: post["size"])


def get_statistics(start_year: int, start_month: int, end_year: int, end_month: int) -> Dict[str, Dict[str, Dict[str, int]]]:
    def calculate_iso_month(day: date) -> str:
        return str.join('-', day.isoformat().split('-')[:-1])

    end_month += 1
    if end_month > 12:
        end_year += 1
        end_month = 1
    try:
        start_date = date(start_year, start_month, 1)
        end_date = date(end_year, end_month, 1)
    except ValueError:
        return abort(422, 'Invalid date given')
    months_count = (end_month - start_month) + (end_year - start_year) * 12
    if months_count <= 0:
        abort(422, "End is earlier than start")
    months_full = []
    for month in range(months_count):
        current_month = ((start_month - 1 + month) % 12) + 1
        current_year = (start_year + floor((start_month - 1 + month) / 12))
        months_full.append(date(current_year, current_month, 1))
    months = [calculate_iso_month(month) for month in months_full]
    all_posts = post_repository.get_posts_by_period(start_date, end_date)
    all_subunits = subunit_repository.get_all_subunits()
    posts_by_months = {
        month: {
            subunit.name: {
                employee.full_name: 0 for employee in subunit.employees
            } for subunit in all_subunits
        } for month in months
    }
    for post in all_posts:
        month = calculate_iso_month(post.published_on.date())
        posts_by_months[month][post.creator.subunit_ref.name][post.creator.full_name] += 1
    return posts_by_months


def get_feed(post_type: PostType, page: int, subunit_id: str = None) -> Dict[str, int or dict]:
    if (not subunit_id) and (post_type in (PostType.subunit_announcement, PostType.subunit_news)):
        abort(422, "You must specify subunit for this post type")
    pages_count = feed_pages_count(post_type, subunit_id)
    if page <= pages_count:
        posts = prepare_posts_list(
            post_repository.get_posts(page, default_page_size, post_type, {PostStatus.posted}, subunit_id)
        )
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


def get_all_posts(employee_id: str, page: int, posts_statuses: Set[PostStatus], reverse: bool = True) -> Dict[str, int or dict]:
    moderator = employee_repository.get_employee_by_id(employee_id)
    if not moderator or moderator.user_type == EmployeeType.user.value:
        abort(403, "You're not allowed to see this data")
    pages_count = moderation_pages_count(posts_statuses=posts_statuses)
    if page <= pages_count:
        posts = prepare_posts_list(post_repository.get_posts(
            page, default_page_size, post_statuses=posts_statuses, oldest_first=reverse
        ))
    else:
        posts = []
    return {
        "posts": posts,
        "pages_count": pages_count
    }
