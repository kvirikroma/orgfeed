from typing import List
from datetime import date, datetime

from sqlalchemy import func, distinct

from models.post_model import PostType, PostStatus
from . import db, Post, Subunit, Employee
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


def base_archive_request():
    return db.session.query(Post).filter(Post.status == PostStatus.archived.value)


def base_feed_request(posts_type: PostType):
    return db.session.query(Post).\
        filter(Post.status == PostStatus.posted.value).\
        filter(Post.type == posts_type.value)


def get_archived_posts(page: int, page_size: int) -> List[Post]:
    return base_archive_request().\
        limit(page_size).offset(page * page_size).\
        all()


def count_archived_posts() -> int:
    return base_archive_request().count()


def get_posts_by_date(day: date, include_archived: bool) -> List[Post]:
    base_request = db.session.query(Post).\
        filter(Post.published_on.date() == day)
    if include_archived:
        base_request = base_request.filter(Post.status.in_(PostStatus.archived.value, PostStatus.posted.value))
    else:
        base_request = base_request.filter(Post.status == PostStatus.posted.value)
    return base_request.all()


def get_posts_of_employee(employee_id: str) -> List[Post]:
    return db.session.query(Post).\
        filter(Post.author == employee_id).\
        all()


def get_feed(posts_type: PostType, page: int, page_size: int, subunit_id: str = None) -> List[Post]:
    base_request = base_feed_request(posts_type)
    if subunit_id is not None:
        base_request = base_request.filter(Post.creator.subunit == subunit_id)
    return base_request.limit(page_size).offset(page * page_size).all()


def feed_count(posts_type: PostType, subunit_id: str = None) -> int:
    base_request = base_feed_request(posts_type)
    if subunit_id is not None:
        base_request = base_request.filter(Post.creator.subunit == subunit_id)
    return base_request.count()


def get_posts_by_period(start: date, end: date, page: int, page_size: int) -> List:
    return db.session.query(Post).\
        filter(Post.status == PostStatus.posted.value).\
        filter(Post.published_on >= start).\
        filter(Post.published_on <= end).\
        limit(page_size).offset(page * page_size).\
        all()


def archive_expired_posts() -> None:
    with get_current_app().app_context():
        db.session.query(Post).\
            filter(Post.status != PostStatus.archived.value).\
            filter(Post.archived_on < datetime.utcnow()).\
            update({"status": PostStatus.archived.value}, synchronize_session='fetch')
