from typing import List
from datetime import datetime, date

from . import db, Post


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


def get_subunit_statistics(subunit_id: str, start: date, end: date) -> List:
    """get number of posts for each employee in subunit (with limiting by time)"""
    pass
