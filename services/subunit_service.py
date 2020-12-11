from typing import List

from flask import abort

from repositories import subunit_repository, employee_repository, Subunit
from models.employee_model import EmployeeType
from . import any_non_nones
from .employee_service import prepare_employee


def prepare_subunit(subunit: Subunit) -> dict:
    result = subunit.get_dict()
    result['employees'] = [prepare_employee(employee, renew=False) for employee in subunit.employees]
    return result


def subunit_write_access(writer_id: str, leader_id: str) -> None:
    writer = employee_repository.get_employee_by_id(writer_id)
    if not writer or writer.user_type != EmployeeType.admin.value:
        abort(403, "Non-admins can not create new subunits or edit existing ones")


def create_subunit(creator_id: str, name: str, address: str, leader: str, phone: str, email: str, **kwargs) -> dict:
    subunit_write_access(creator_id, leader)
    if not employee_repository.get_employee_by_id(leader):
        abort(404, "Leader not found")
    if subunit_repository.get_subunit_by_email(email):
        abort(409, "Subunit with this email already exists")
    if subunit_repository.get_subunit_by_name(name):
        abort(409, "Subunit with this name already exists")
    subunit = Subunit()
    subunit.name = name
    subunit.address = address
    subunit.leader = leader
    subunit.phone = phone
    subunit.email = email
    subunit_repository.add_or_edit_subunit(subunit)
    return prepare_subunit(subunit_repository.get_subunit_by_email(email))  # re-getting object to fill the ID field


def edit_subunit(
        editor_id: str, subunit_id: str, name: str = None, address: str = None,
        leader: str = None, phone: str = None, email: str = None, **kwargs
) -> dict:
    subunit_write_access(editor_id, leader)
    subunit = subunit_repository.get_subunit_by_id(subunit_id)
    if not subunit:
        abort(404, "Subunit not found")
    if leader and not employee_repository.get_employee_by_id(leader):
        abort(404, "Leader not found")
    if email and subunit.email != email and subunit_repository.get_subunit_by_email(email):
        abort(409, "Subunit with this email already exists")
    if name and subunit.name != name and subunit_repository.get_subunit_by_name(name):
        abort(409, "Subunit with this name already exists")
    if not any_non_nones((name, address, leader, phone, email)):
        abort(422, "You must specify at least one field to edit")
    for existing, new in (('name', name), ('address', address), ('leader', leader), ('phone', phone), ('email', email)):
        setattr(subunit, existing, new or getattr(subunit, existing))
    return prepare_subunit(subunit_repository.add_or_edit_subunit(subunit))


def get_subunit(subunit_id: str) -> dict:
    subunit = subunit_repository.get_subunit_by_id(subunit_id)
    if not subunit:
        abort(404, "Subunit not found")
    return prepare_subunit(subunit)


def get_all_subunits() -> List[dict]:
    return [prepare_subunit(subunit) for subunit in subunit_repository.get_all_subunits()]
