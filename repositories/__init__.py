import uuid
from datetime import datetime, timedelta

from injector import inject, Injector
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import (Column, String, SmallInteger, Boolean, CheckConstraint,
                        ForeignKey, DateTime, Index, Integer)


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

    subunit_ref = relationship("Subunit", back_populates='employees', foreign_keys=subunit)

    leader_in_subunit = relationship("Subunit", back_populates='leader_ref', primaryjoin="Employee.id == Subunit.leader")
    approved_posts = relationship("Post", back_populates='approver', primaryjoin="Employee.id == Post.approved_by")
    created_posts = relationship("Post", back_populates='creator', primaryjoin="Employee.id == Post.author")
    uploaded_attachments = relationship("Attachment", back_populates='author_ref', primaryjoin="Employee.id == Attachment.author")

    employees_full_name_subunit_idx = Index('employees_full_name_subunit_idx', full_name, subunit)
    employees_subunit_fired_user_type_idx = Index('employees_subunit_fired_user_type_idx', subunit, fired, user_type)


class Subunit(Base):
    __tablename__ = 'subunits'

    def __repr__(self):
        if len(self.name) > 36:
            return self.name[:36] + '…'
        return self.name

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(512), unique=True, nullable=False)
    address = Column(String(512), nullable=False)
    leader = Column(UUID(), ForeignKey('employees.id', ondelete='NO ACTION'), nullable=False)
    phone = Column(String(), nullable=False)
    email = Column(String(256), nullable=False, unique=True)

    leader_ref = relationship("Employee", back_populates="leader_in_subunit", foreign_keys=leader)

    employees = relationship("Employee", back_populates='subunit_ref', primaryjoin="Subunit.id == Employee.subunit")

    subunits_phone_check = CheckConstraint(
        '(phone >= 0 AND phone <= 999999999)', name='subunits_phone_check'
    )

    subunits_address_leader_phone_idx = Index('subunits_address_leader_phone_idx', address, leader, phone)


class Post(Base):
    __tablename__ = 'posts'

    def __repr__(self):
        if len(self.title) > 36:
            return self.title[:36] + '…'
        return self.title

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(SmallInteger(), nullable=False, default=0)
    title = Column(String(512), nullable=False)
    created_on = Column(DateTime(), nullable=False, default=datetime.utcnow)
    published_on = Column(DateTime(), nullable=True)

    # half a year after utcnow by default
    archived_on = Column(DateTime(), nullable=False, default=lambda: datetime.utcnow() + timedelta(hours=4380))

    author = Column(UUID(), ForeignKey('employees.id', ondelete='NO ACTION'), nullable=False)
    approved_by = Column(UUID(), ForeignKey('employees.id', ondelete='NO ACTION'), nullable=True)
    status = Column(SmallInteger(), nullable=False, default=0)
    body = Column(String(81920), nullable=False)

    approver = relationship("Employee", back_populates="approved_posts", foreign_keys=approved_by)
    creator = relationship("Employee", back_populates="created_posts", foreign_keys=author)

    attachments = relationship("Attachment", back_populates='post_ref', primaryjoin="Post.id == Attachment.post")

    posts_title_idx = Index("posts_title_idx", title)
    posts_status_author_published_on_created_on_idx =\
        Index("posts_status_author_published_on_created_on_idx", status, author, published_on, created_on)


class Attachment(Base):
    __tablename__ = 'attachments'

    def __repr__(self):
        _author = self.author.__repr__()
        _post = self.post.__repr__()
        if len(_author) > 16:
            _author = _author[:16] + '…'
        if len(_post) > 16:
            _post = _post[:16] + '…'
        return f"{_author}'s attachment to post \"{_post}\""

    id = Column(UUID(), nullable=False, primary_key=True, default=lambda: str(uuid.uuid4()))
    author = Column(UUID(), ForeignKey('employees.id', ondelete='NO ACTION'), nullable=False)
    post = Column(UUID(), ForeignKey('posts.id', ondelete='NO ACTION'))

    author_ref = relationship("Employee", back_populates="uploaded_attachments", foreign_keys=author)
    post_ref = relationship("Post", back_populates="attachments", foreign_keys=post)

    attachments_author_idx = Index("attachments_author_idx", author)
    attachments_post_idx = Index("attachments_post_idx", post)
