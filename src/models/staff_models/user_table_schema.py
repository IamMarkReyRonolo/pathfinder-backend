import sys, os, pdb, json, imp, re
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
WORKING_DIR = os.path.abspath(CURRENT_DIR)
PARENT_DIR = os.path.join(CURRENT_DIR, '..')
sys.path.append(CURRENT_DIR)
sys.path.append(PARENT_DIR)
import uuid as uuid_pkg
from sqlalchemy.dialects.postgresql import UUID
import sqlalchemy as sa
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship
from sqlmodel import Field, Relationship, SQLModel, ForeignKey, String, ARRAY
from typing import Optional, List
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime
import datetime

class utcnow(expression.FunctionElement):
    type = DateTime()
    inherit_cache = True

@compiles(utcnow, 'postgresql')
def pg_utcnow(element, compiler, **kw):
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


class User(SQLModel, table=True):
    uuid: uuid_pkg.UUID = Field(
        sa_column=sa.Column(UUID(as_uuid=True), nullable=False, default=uuid_pkg.uuid4,  unique=True, primary_key=True, index=True,))
    full_name: str
    username: str = Field(sa_column=Column("username", String, unique=True))
    password: str
    connections: List['Friend'] = Relationship(
        sa_relationship=relationship("Friend", cascade="all, delete", back_populates="user"))
    session_rooms: List['RoomSession'] = Relationship(
        sa_relationship=relationship("RoomSession", cascade="all, delete", back_populates="user"))
    

class Notification(SQLModel, table=True):
    uuid: uuid_pkg.UUID = Field(
        sa_column=sa.Column(UUID(as_uuid=True), nullable=False, default=uuid_pkg.uuid4,  unique=True, primary_key=True, index=True,))
    notification_title: str
    notification_message: str
    users_involved: Optional[List[str]] = Field(sa_column=Column(ARRAY(String)))
    code: Optional[str]
    created_at:  datetime.datetime = Field(
        sa_column=sa.Column(sa.DateTime(), nullable=False, server_default=utcnow()))

class RoomSession(SQLModel, table=True):
    uuid: uuid_pkg.UUID = Field(
        sa_column=sa.Column(UUID(as_uuid=True), nullable=False, default=uuid_pkg.uuid4,  unique=True, primary_key=True, index=True,))
    room_code: str
    users_responded: Optional[List[str]] = Field(sa_column=Column(ARRAY(String)))
    users_requested: Optional[List[str]] = Field(sa_column=Column(ARRAY(String)))
    user_id: Optional[uuid_pkg.UUID] = Field(sa_column=Column(
        UUID(as_uuid=True), ForeignKey("user.uuid", ondelete="CASCADE")))
    user: Optional[User] = Relationship(
        sa_relationship=relationship("User", back_populates="session_rooms"))

class Friend(SQLModel, table=True):
    uuid: uuid_pkg.UUID = Field(
        sa_column=sa.Column(UUID(as_uuid=True), nullable=False, default=uuid_pkg.uuid4,  unique=True, primary_key=True, index=True,))
    full_name: str
    status: str
    friend_id: uuid_pkg.UUID = Field(
        sa_column=sa.Column(UUID(as_uuid=True), nullable=False, default=uuid_pkg.uuid4))
    user_id: Optional[uuid_pkg.UUID] = Field(sa_column=Column(
        UUID(as_uuid=True), ForeignKey("user.uuid", ondelete="CASCADE")))
    user: Optional[User] = Relationship(
        sa_relationship=relationship("User", back_populates="connections"))
