from typing import List, Tuple
from os import path, listdir, removedirs, remove, makedirs, stat

from flask import current_app
from werkzeug.datastructures import FileStorage

from . import db, Attachment


def common_attachment_path():
    return path.join(current_app.config["UPLOAD_FOLDER"], "attachments")


def path_from_id(attachment_id: str) -> str:
    attachment_path_inner = str.join('/', list(attachment_id.replace('-', '')))
    return path.join(common_attachment_path(), attachment_path_inner)


def full_path_by_id(attachment_id: str, attachment_name: str) -> str:
    save_path = path_from_id(attachment_id)
    return path.join(save_path, attachment_name)


def get_attachment_path_and_filename(attachment_id: str) -> Tuple[str, str] or Tuple[None]:
    attachment_path = path_from_id(attachment_id)
    if path.exists(attachment_path):
        for file in listdir(attachment_path):
            return attachment_path, file
    return None, None


def remove_attachment_file_by_id(attachment: str):
    attachment_path = path_from_id(attachment)
    if path.exists(attachment_path):
        for file in listdir(attachment_path):
            remove(path.join(attachment_path, file))
        removedirs(attachment_path)
        makedirs(common_attachment_path(), exist_ok=True)


def get_attachment_size(attachment_id: str) -> int:
    attachment_path, filename = get_attachment_path_and_filename(attachment_id)
    if not filename:
        return 0
    return stat(path.join(attachment_path, filename)).st_size


def add_attachment(attachment: Attachment, file: FileStorage) -> Attachment:
    attachment_path = path_from_id(attachment.id)
    makedirs(attachment_path)
    file.save(full_path_by_id(attachment.id, file.filename))
    db.session.add(attachment)
    db.session.commit()
    return attachment


def edit_attachment(attachment: Attachment):
    db.session.merge(attachment)
    db.session.commit()


def delete_attachment(attachment: Attachment) -> None:
    remove_attachment_file_by_id(attachment.id)
    db.session.delete(attachment)
    db.session.commit()


def get_attachment_by_id(attachment_id: str) -> Attachment:
    return db.session.query(Attachment).filter(Attachment.id == attachment_id).first()


def delete_attachment_by_id(attachment_id: str) -> None:
    remove_attachment_file_by_id(attachment_id)
    db.session.query(Attachment).filter(Attachment.id == attachment_id).delete()
    db.session.commit()


def get_user_attachments(user_id: str, page: int, page_size: int) -> List[Attachment]:
    return db.session.query(Attachment).\
        filter(Attachment.author == user_id).\
        limit(page_size).offset(page * page_size).\
        all()


def get_user_attachments_count(user_id: str) -> int:
    return db.session.query(Attachment).filter(Attachment.author == user_id).count()


def ensure_attachments_exist(attachment_ids: List[str]) -> bool:
    real_count = db.session.query(Attachment).filter(Attachment.id.in_(attachment_ids)).count()
    if real_count != len(attachment_ids):
        return False
    return True


def add_attachments_to_post(post_id: str or None, attachment_ids: List[str]) -> None:
    db.session.query(Attachment).\
        filter(Attachment.id.in_(attachment_ids)).\
        update({"post": post_id}, synchronize_session='fetch')
    db.session.commit()
