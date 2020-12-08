from typing import List, Dict
from math import ceil
from uuid import uuid4

from flask import abort, Response, send_from_directory
from werkzeug.datastructures import FileStorage

from models.employee_model import EmployeeType
from repositories import attachment_repository, employee_repository, Attachment
from . import default_page_size
from .employee_service import prepare_employee


def prepare_attachment(attachment: Attachment) -> dict:
    result = attachment.__dict__.copy()
    result["author"] = prepare_employee(attachment.author_ref)
    result["size"] = attachment_repository.get_attachment_size(attachment.id)
    result["filename"] = attachment_repository.get_attachment_path_and_filename(attachment.id)[1]
    result["post"] = attachment.post
    result["id"] = attachment.id
    return result


def save_attachment(employee_id: str, attachment_file: FileStorage) -> dict:
    attachment = Attachment()
    attachment.author = employee_id
    attachment.post = None
    attachment.id = str(uuid4())
    return prepare_attachment(attachment_repository.add_attachment(attachment, attachment_file))


def get_attachment(attachment_id: str) -> Response:
    if not attachment_repository.get_attachment_by_id(attachment_id):
        abort(404, "Attachment not found")
    return send_from_directory(
        attachment_repository.path_from_id(attachment_id),
        attachment_repository.get_attachment_path_and_filename(attachment_id)[1],
        as_attachment=True
    )


def delete_attachment(employee_id: str, attachment_id: str) -> None:
    attachment = attachment_repository.get_attachment_by_id(attachment_id)
    if not attachment:
        abort(404, "Attachment not found")
    if attachment.author != employee_id:
        employee = employee_repository.get_employee_by_id(employee_id)
        if not employee or employee.user_type != EmployeeType.admin.value:
            abort(403, "You can not remove attachments of other users")
    attachment_repository.delete_attachment(attachment)


def attachments_pages_count(employee_id: str) -> int:
    return ceil(attachment_repository.get_user_attachments_count(employee_id) / default_page_size)


def get_all_attachments(employee_id: str, page: int) -> Dict[str, List[Dict] or int]:
    if not employee_repository.get_employee_by_id(employee_id):
        abort(404, "Employee not found")
    pages_count = attachments_pages_count(employee_id)
    if page <= pages_count:
        attachments = attachment_repository.get_user_attachments(employee_id, page, default_page_size)
    else:
        attachments = []
    return {
        "attachments": [prepare_attachment(attachment) for attachment in attachments],
        "pages_count": pages_count
    }
