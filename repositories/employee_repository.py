from typing import List

from sqlalchemy.sql.operators import or_

from . import db, Employee
from models.employee_model import EmployeeType


def add_or_edit_employee(employee: Employee) -> Employee:
    db.session.merge(employee)
    db.session.commit()
    return employee


def get_employee_by_id(employee_id: str) -> Employee:
    return db.session.query(Employee).filter(Employee.id == employee_id).first()


def get_employee_by_email(email: str) -> Employee:
    return db.session.query(Employee).filter(Employee.email == email).first()


def delete_employee(employee: Employee) -> None:
    db.session.delete(employee)
    db.session.commit()


def fired_moderators_of_subunit(subunit_id: str) -> List[Employee]:
    return db.session.query(Employee).\
        filter(Employee.subunit == subunit_id).\
        filter(or_(Employee.user_type == EmployeeType.admin.value, Employee.user_type == EmployeeType.moderator.value)).\
        filter(Employee.fired).\
        all()
