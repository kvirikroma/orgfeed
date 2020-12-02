from typing import List
from datetime import datetime, date

from sqlalchemy import func, distinct

from models.post_model import PostType, PostStatus
from . import db, Post, Subunit, Employee


def add_or_edit_post(post: Post) -> Post:
    db.session.merge(post)
    db.session.commit()
    return post


def get_post_by_id(post_id: str) -> Post:
    return db.session.query(Post).filter(Post.id == post_id).first()


def delete_post(post: Post) -> None:
    db.session.delete(post)
    db.session.commit()


def get_archived_posts(page: int, page_size: int) -> List[Post]:
    return db.session.query(Post).\
        filter(Post.archived_on < datetime.utcnow()).\
        limit(page_size).offset(page * page_size).\
        all()


def get_posts_by_date(day: date) -> List[Post]:
    return db.session.query(Post).\
        filter(Post.published_on.date() == day).\
        all()


def get_feed(posts_type: PostType, page: int, page_size: int) -> List[Post]:
    return db.session.query(Post).\
        filter(Post.status == PostStatus.posted.value).\
        filter(Post.type == posts_type.value).\
        limit(page_size).offset(page * page_size).\
        all()


def get_subunit_statistics(subunit_id: str, start: date, end: date, page: int, page_size: int) -> List:
    """get number of posts for each employee in subunit (with limiting by time)"""
    return db.session.query(distinct(Post.author), func.count('*')).\
        filter(Subunit.id == subunit_id).\
        filter(Subunit.id == Employee.subunit).\
        filter(Employee.id == Post.author).\
        filter(Post.published_on >= start).\
        filter(Post.published_on <= end).\
        group_by(Post.author).\
        limit(page_size).offset(page * page_size).\
        all()
