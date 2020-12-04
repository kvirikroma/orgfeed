from typing import List, Iterable

import bcrypt
from flask import abort
from flask_jwt_extended import create_access_token, create_refresh_token

from repositories import employee_repository, subunit_repository, Employee
from models.employee_model import EmployeeType
from . import any_non_nones


def check_password(password: str):
    letters = bytes(range(b'a'[0], b'z'[0]+1)).decode()
    lower = False
    upper = False
    digit = False
    for letter in password:
        check = False
        if letters.find(letter) != -1:
            check = True
            lower = True
        if letters.upper().find(letter) != -1:
            check = True
            upper = True
        if "-.?!@=_^:;#$%&*()+\\<>~`/\"'".find(letter) != -1:
            check = True
        if letter.isdigit():
            check = True
            digit = True
        if not check:
            abort(422, f"Password cannot contain symbols like this: '{letter}'")
    if not lower:
        abort(422, "Password must contain at least one lowercase letter")
    if not upper:
        abort(422, "Password must contain at least one uppercase letter")
    if not digit:
        abort(422, "Password must contain at least one digit")


def prepare_employee(employee: Employee, renew: bool = False) -> dict:
    if renew:
        employee = employee_repository.get_employee_by_email(employee.email)
    result = employee.__dict__
    result["user_type"] = EmployeeType(result["user_type"]).name
    return result


def register_employee(
        registrar_id: str, email: str, full_name: str, subunit: str, user_type: int, password: str, **kwargs
) -> dict:
    check_password(password)
    registrar = employee_repository.get_employee_by_id(registrar_id)
    if not registrar or registrar.user_type != EmployeeType.admin.value:
        abort(403, "Non-admins can not register new employees")
    if employee_repository.get_employee_by_email(email):
        abort(409, "User with this email already exists")
    if not subunit_repository.get_subunit_by_id(subunit):
        abort(404, "Subunit not found")
    employee = Employee()
    employee.email = email
    employee.full_name = full_name
    employee.subunit = subunit
    employee.user_type = EmployeeType[user_type].value
    employee.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode()
    return prepare_employee(employee_repository.add_or_edit_employee(employee), renew=True)


def get_token(email: str, password: str, **kwargs):
    employee = employee_repository.get_employee_by_email(email)
    if not employee:
        abort(404, "User not found")
    if not bcrypt.checkpw(password.encode('utf-8'), employee.password_hash.encode('utf-8')):
        abort(401, "Invalid credentials given")
    return {
        "access_token": create_access_token(identity=employee.id),
        "refresh_token": create_refresh_token(identity=employee.id),
        "user_id": employee.id
    }


def get_employee(employee_id: str) -> dict:
    user = employee_repository.get_employee_by_id(employee_id)
    if not user:
        abort(404, "User not found")
    return prepare_employee(user)


def edit_employee(
        editor_id: str, employee_id: str, email: str = None,
        full_name: str = None, subunit: str = None,
        user_type: int = None, fired: bool = None, **kwargs
) -> dict:
    if not any_non_nones((email, full_name, subunit, fired, user_type)):
        abort(422, "You must specify at least one field to edit")
    editor = employee_repository.get_employee_by_id(editor_id)
    if not editor or editor.user_type != EmployeeType.admin.value:
        abort(403, "Non-admins can not edit employees")
    if subunit and not subunit_repository.get_subunit_by_id(subunit):
        abort(404, "Subunit not found")
    employee = employee_repository.get_employee_by_id(employee_id)
    if not employee:
        abort(404, "Can not found an employee to edit")
    if email and email != employee.email and employee_repository.get_employee_by_email(email):
        abort(409, "User with this email already exists")
    for existing, new in (('email', email), ('full_name', full_name), ('subunit', subunit)):
        setattr(employee, existing, new or getattr(employee, existing))
    if user_type is not None:
        employee.user_type = EmployeeType[user_type].value
    if fired is not None:
        employee.fired = fired
    return prepare_employee(employee_repository.add_or_edit_employee(employee))


def get_fired_moderators(subunit_id: str) -> List[dict]:
    if not subunit_repository.get_subunit_by_id(subunit_id):
        abort(404, "Subunit not found")
    return [prepare_employee(employee) for employee in employee_repository.fired_moderators_of_subunit(subunit_id)]


def get_multiple_employees(employee_ids: Iterable[str]) -> List[dict]:
    return [prepare_employee(employee) for employee in employee_repository.get_employee_by_id_list(employee_ids)]
