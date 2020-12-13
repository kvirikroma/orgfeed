from typing import List, Iterable

from . import db, Employee
from models.employee_model import EmployeeType


def add_or_edit_employee(employee: Employee) -> Employee:
    db.session.merge(employee)
    db.session.commit()
    return employee


def get_employee_by_id(employee_id: str) -> Employee:
    return db.session.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_id_list(employee_ids: Iterable[str]) -> List[Employee]:
    return db.session.query(Employee).filter(Employee.id.in_(employee_ids)).all()


def get_employee_by_email(email: str) -> Employee:
    return db.session.query(Employee).filter(Employee.email == email).first()


def delete_employee(employee: Employee) -> None:
    db.session.delete(employee)
    db.session.commit()


def fired_users_of_subunit(subunit_id: str, types: Iterable[EmployeeType]) -> List[Employee]:
    return db.session.query(Employee).\
        filter(Employee.subunit == subunit_id).\
        filter(Employee.user_type.in_(e_type.value for e_type in types)).\
        filter(Employee.fired).\
        all()
