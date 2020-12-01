from typing import List

from . import db, Employee
from models.employee_model import EmployeeType


def add_or_edit_employee(employee: Employee) -> Employee:
    db.session.merge(employee)
    db.session.commit()
    return employee


def get_employee_by_id(employee_id: str) -> Employee:
    return db.session.query(Employee).filter(Employee.id == employee_id).first()


def delete_employee(employee: Employee) -> None:
    db.session.delete(employee)
    db.session.commit()


def fired_moderators_of_subunit(subunit_id: str, page: int, page_size: int) -> List[Employee]:
    return db.session.query(Employee).\
        filter(Employee.subunit == subunit_id).\
        filter(Employee.user_type == EmployeeType.admin.value).\
        filter(Employee.fired).\
        limit(page_size).offset(page * page_size).\
        all()
