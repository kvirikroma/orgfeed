from uuid import UUID

from flask import abort


default_page_size = 20


def check_page(request):
    page = request.args.get("page")
    if not page or not page.isdigit():
        abort(400, "Page query parameter must exist and be integer")
    page = int(page) - 1
    if page < 0:
        abort(400, "Page query parameter must be >= 1")
    if page >= 2147483647:
        abort(400, "Page query parameter is too large")
    return page


def check_uuid(value: str) -> None:
    try:
        UUID(value)
    except ValueError:
        abort(400, "Incorrect ID parameter (must match UUID v4)")
    except TypeError:
        abort(400, "Cannot find ID parameter of correct type (must appear once in query)")
