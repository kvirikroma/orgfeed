from typing import List, Set
from datetime import date, datetime

from sqlalchemy import Date
from flask_sqlalchemy import BaseQuery

from models.post_model import PostType, PostStatus
from . import db, Post, Employee
from utils import get_current_app


def add_or_edit_post(post: Post) -> Post:
    db.session.merge(post)
    db.session.commit()
    return post


def get_post_by_id(post_id: str) -> Post:
    return db.session.query(Post).filter(Post.id == post_id).first()


def delete_post(post: Post) -> None:
    db.session.delete(post)
    db.session.commit()


def base_archive_request() -> BaseQuery:
    return db.session.query(Post).filter(Post.status == PostStatus.archived.value)


def base_posts_request_for_subunit(base_request: BaseQuery, subunit_id: str) -> BaseQuery:
    return base_request.\
        filter(Employee.subunit == subunit_id).\
        filter(Post.author == Employee.id)


def get_archived_posts(page: int, page_size: int) -> List[Post]:
    return base_archive_request().\
        limit(page_size).offset(page * page_size).\
        all()


def count_archived_posts() -> int:
    return base_archive_request().count()


def get_posts_by_date(day: date, include_archived: bool) -> List[Post]:
    base_request = db.session.query(Post).\
        filter(Post.published_on.cast(Date) == day)
    if include_archived:
        base_request = base_request.filter(Post.status.in_((PostStatus.archived.value, PostStatus.posted.value)))
    else:
        base_request = base_request.filter(Post.status == PostStatus.posted.value)
    return base_request.all()


def get_posts_of_employee(employee_id: str) -> List[Post]:
    return db.session.query(Post).\
        filter(Post.author == employee_id).\
        all()


def base_posts_request(posts_type: PostType, subunit_id: str or None, post_statuses: Set[PostStatus]) -> BaseQuery:
    post_statuses_int = [status.value for status in post_statuses]
    base_request = db.session.query(Post).\
        filter(Post.status.in_(post_statuses_int)).\
        filter(Post.type == posts_type.value)
    if subunit_id:
        return base_posts_request_for_subunit(base_request, subunit_id)
    return base_request


def get_posts(
        posts_type: PostType, page: int, page_size: int, post_statuses: Set[PostStatus],
        subunit_id: str = None, oldest_first: bool = False
) -> List[Post]:
    base_request = base_posts_request(posts_type, subunit_id, post_statuses)
    if oldest_first:
        base_request = base_request.order_by(Post.created_on.asc())
    else:
        base_request = base_request.order_by(Post.created_on.desc())
    return base_request.limit(page_size).offset(page * page_size).all()


def get_posts_count(posts_type: PostType, post_statuses: Set[PostStatus], subunit_id: str = None) -> int:
    base_request = base_posts_request(posts_type, subunit_id, post_statuses)
    return base_request.count()


def get_posts_by_period(start: date, end: date) -> List:
    return db.session.query(Post).\
        filter(Post.status.in_((PostStatus.posted.value, PostStatus.archived.value))).\
        filter(Post.published_on >= start).\
        filter(Post.published_on < end).\
        all()


def archive_expired_posts() -> None:
    with get_current_app().app_context():
        db.session.query(Post).\
            filter(Post.status != PostStatus.archived.value).\
            filter(Post.archived_on < datetime.utcnow()).\
            update({"status": PostStatus.archived.value}, synchronize_session='fetch')
