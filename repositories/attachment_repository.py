from typing import List
from os import path, listdir, removedirs, remove, makedirs

from flask import current_app
from werkzeug.datastructures import FileStorage

from . import db, Attachment


IMAGE_DEFAULT_NAME = "attachment"


def common_attachment_path():
    return path.join(current_app.config["UPLOAD_FOLDER"], "attachments")


def path_from_id(attachment_id: str) -> str:
    attachment_path_inner = str.join('/', list(attachment_id.replace('-', '')))
    return path.join(common_attachment_path(), attachment_path_inner)


def full_path_by_id(attachment_id: str, attachment_name: str) -> str:
    save_path = path_from_id(attachment_id)
    attachment_full_name = attachment_name.split('.')
    attachment_new_name = IMAGE_DEFAULT_NAME
    if len(attachment_full_name) > 1:
        attachment_new_name += f".{attachment_full_name[-1]}"
    return path.join(save_path, attachment_new_name)


def get_attachment_filename(attachment_id: str):
    attachment_path = path_from_id(attachment_id)
    if path.exists(attachment_path):
        for file in listdir(attachment_path):
            if file.startswith(IMAGE_DEFAULT_NAME):
                return file


def remove_attachment_file_by_id(attachment: str):
    attachment_path = path_from_id(attachment)
    if path.exists(attachment_path):
        for file in listdir(attachment_path):
            remove(path.join(attachment_path, file))
        removedirs(attachment_path)
        makedirs(common_attachment_path(), exist_ok=True)


def add_attachment(attachment: Attachment, file: FileStorage) -> Attachment:
    attachment_path = path_from_id(attachment.id)
    makedirs(attachment_path)
    file.save(full_path_by_id(attachment.id, file.filename))
    db.session.add(attachment)
    db.session.commit()
    return attachment


def delete_image(attachment: Attachment) -> None:
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
        order_by(Attachment.upload_time.desc()).\
        limit(page_size).offset(page * page_size).\
        all()


def get_user_attachments_count(user_id: str) -> int:
    return db.session.query(Attachment).filter(Attachment.author == user_id).count()
