from typing import List

from . import db, Employee


def add_employee(employee: Employee) -> Employee:
    db.session.add(employee)
    db.session.commit()
    return employee


def get_employee_by_id(employee_id: str) -> Employee:
    return db.session.query(Employee).filter(Employee.id == employee_id).first()


def get_employees() -> List[Employee]:
    pass
