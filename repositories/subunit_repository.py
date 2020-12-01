from typing import List

from . import db, Subunit


def add_or_edit_subunit(subunit: Subunit) -> Subunit:
    db.session.merge(subunit)
    db.session.commit()
    return subunit


def get_subunit_by_id(subunit_id: str) -> Subunit:
    return db.session.query(Subunit).filter(Subunit.id == subunit_id).first()


def delete_subunit(subunit: Subunit) -> None:
    db.session.delete(subunit)
    db.session.commit()


def get_all_subunits(page: int, page_size: int) -> List[Subunit]:
    return db.session.query(Subunit).\
        limit(page_size).offset(page * page_size).\
        all()
