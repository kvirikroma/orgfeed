import uuid
from datetime import datetime

from injector import inject, Injector
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, SmallInteger, Boolean, CheckConstraint, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


class DbGetter:
    @inject
    def __init__(self, database: SQLAlchemy):
        self.db = database


db = Injector().get(DbGetter).db
Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employees'

    def __repr__(self):
        if len(self.full_name) > 36:
            return self.full_name[:36] + '…'
        return self.full_name

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(512), nullable=False)
    email = Column(String(256), nullable=False, unique=True)
    password_hash = Column(String(64), nullable=False)
    subunit = Column(UUID(), ForeignKey('subunits.id', ondelete='NO ACTION'), nullable=False)
    user_type = Column(SmallInteger(), nullable=False, default=0)
    fired = Column(Boolean(), nullable=False, default=False)

    subunit_ref = relationship("Subunit", back_populates='employees', cascade='no action')

    employees_full_name_subunit_idx = Index('employees_full_name_subunit_idx', full_name, subunit)
    employees_subunit_fired_user_type_idx = Index('employees_subunit_fired_user_type_idx', subunit, fired, user_type)


class Subunit(Base):
    __tablename__ = 'subunits'

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))


class Post(Base):
    __tablename__ = 'posts'

    def __repr__(self):
        if len(self.title) > 36:
            return self.title[:36] + '…'
        return self.title

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    author = Column(UUID(), ForeignKey('users.id', ondelete='NO ACTION'), nullable=False)
    title = Column(String(64), nullable=False)
    body = Column(String(8192), nullable=False)
    date = Column(DateTime(), nullable=False)
    picture = Column(String(512))

    user = relationship("User", back_populates="news_posts", foreign_keys=[author])

    news_title_date_author_body_idx = Index('news_title_date_author_body_idx', title, date, author, body)
