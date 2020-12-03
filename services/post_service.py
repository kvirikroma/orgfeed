from typing import List, Dict
from datetime import date

from flask import abort

from repositories import post_repository, Post
from models.post_model import PostStatus, PostType
from . import attachment_service, any_non_nones


def prepare_post(post: Post) -> dict:
    result = post.__dict__
    result['post_type'] = PostType(post.type).name
    result['status'] = PostStatus(post.status).name
    result['attachments'] = [attachment_service.prepare_attachment(attachment) for attachment in post.attachments]
    return result


def calculate_post_size(post: Post) -> int:
    pass


def get_post(post_id: str) -> dict:
    pass


def edit_post(editor_id: str, post_id: str, title: str, body: str, post_type: str, attachments: List[str], **kwargs) -> dict:
    pass


def create_post(creator_id: str, title: str, body: str, post_type: str, attachments: List[str], **kwargs) -> dict:
    pass


def set_post_status(setter_id: str, post_id: str, status: PostStatus) -> dict:
    pass


def delete_post(deleter_id: str, post_id: str) -> None:
    pass


def get_biggest_post(day: date, include_archived: bool) -> dict:
    pass


def get_statistics(
        subunit_id: str, start_year: int, start_month: int, end_year: int, end_month: int
) -> List[Dict[str, str or int]]:
    pass


def get_feed(post_type: PostType, page: int, subunit_id: str = None) -> Dict[str, int or dict]:
    pass
