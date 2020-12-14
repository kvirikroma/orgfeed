from typing import List

from . import db, Subunit


def add_or_edit_subunit(subunit: Subunit) -> Subunit:
    db.session.merge(subunit)
    db.session.commit()
    return subunit


def get_subunit_by_id(subunit_id: str) -> Subunit:
    return db.session.query(Subunit).filter(Subunit.id == subunit_id).first()


def get_subunit_by_email(email: str) -> Subunit:
    return db.session.query(Subunit).filter(Subunit.email == email).first()


def get_subunit_by_name(name: str) -> Subunit:
    return db.session.query(Subunit).filter(Subunit.name == name).first()


def delete_subunit(subunit: Subunit) -> None:
    db.session.delete(subunit)
    db.session.commit()


def get_subunits(subunit_ids: List[str] = None) -> List[Subunit]:
    base_request = db.session.query(Subunit)
    if subunit_ids:
        base_request = base_request.filter(Subunit.id.in_(subunit_ids))
    return base_request.all()
