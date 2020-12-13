from typing import Iterable
from uuid import UUID

from flask import abort


default_page_size = 16


def get_page(request) -> int:
    page = request.args.get("page", '')
    if not page or not page.isdigit():
        abort(400, "Page query parameter must exist and be integer")
    page = int(page) - 1
    if page < 0:
        abort(400, "Page query parameter must be >= 1")
    if page >= 2147483647:
        abort(400, "Page query parameter is too large")
    return page


def get_uuid(request, allow_empty: bool = False) -> str:
    if isinstance(request, str):
        value = request
    else:
        value = request.args.get('id', '')
    if not value and allow_empty:
        return value
    try:
        UUID(value)
    except ValueError:
        abort(400, "Incorrect ID parameter (must match UUID v4)")
    except TypeError:
        abort(400, "Cannot find ID parameter of correct type (must appear once in query)")
    return value


def any_non_nones(iterable: Iterable) -> bool:
    for i in iterable:
        if i is not None:
            return True
    return False
