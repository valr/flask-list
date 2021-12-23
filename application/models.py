import enum
import uuid
from datetime import datetime
from decimal import Decimal
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import types
from werkzeug.security import check_password_hash, generate_password_hash

from application import database

# TODO: make a script with the below commands
# export PYTHONDONTWRITEBYTECODE=1
# flask db init
# flask db migrate -m 'init db' (or any other change after init)
# flask db upgrade (flask db downgrade)
# echo '.schema' | sqlite3 database/application.db > database/database.sql
# chown -R flask-list:root database
# chmod 700 database
# chmod 600 database/application.db


class SqliteNumeric(types.TypeDecorator):
    impl = types.String(1000)

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Decimal(value if value is not None else "0")


class User(database.Model, UserMixin):
    user_id = database.Column(
        database.Integer, index=True, nullable=False, unique=True, primary_key=True
    )
    email = database.Column(
        database.String(1000), index=True, nullable=False, unique=True
    )
    password_hash = database.Column(database.String(128), nullable=False)
    active = database.Column(database.Boolean(), nullable=False)
    updated_on = database.Column(
        database.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    filter_ = database.Column(database.String(1000))
    version_id = database.Column(database.String(32), nullable=False)

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<User id: {self.user_id} email: {self.email}>"

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_token(self, subject, expires_in=600):
        claims = {"sub": subject, "id": self.user_id, "exp": time() + expires_in}
        key = current_app.config["SECRET_KEY"]

        return jwt.encode(claims, key, algorithm="HS256")

    @staticmethod
    def verify_token(token, subject):
        try:
            key = current_app.config["SECRET_KEY"]
            claims = jwt.decode(token, key, algorithms=["HS256"])

            user_id = claims.get("id") if claims.get("sub") == subject else None
            if not user_id:
                return
        except jwt.InvalidTokenError:
            return

        return User.query.get(user_id)


class Category(database.Model):
    category_id = database.Column(
        database.Integer, index=True, nullable=False, unique=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), index=True, nullable=False, unique=True
    )
    filter_ = database.Column(database.String(1000), index=True, nullable=False)
    version_id = database.Column(database.String(32), nullable=False)

    # one to many: category <-> item
    items = database.relationship("Item", back_populates="category")

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<Category id: {self.category_id} name: {self.name}>"


class Item(database.Model):
    item_id = database.Column(
        database.Integer, index=True, nullable=False, unique=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), index=True, nullable=False  # not unique
    )
    version_id = database.Column(database.String(32), nullable=False)

    # one to many: category <-> item
    category = database.relationship("Category", back_populates="items")
    category_id = database.Column(
        database.Integer,
        database.ForeignKey("category.category_id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    # many to many: list <-> item
    lists = database.relationship(
        "ListItem",
        back_populates="item",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = (
        database.UniqueConstraint("name", "category_id"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Item id: {self.item_id} name: {self.name}>"


class List(database.Model):
    list_id = database.Column(
        database.Integer, index=True, nullable=False, unique=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), index=True, nullable=False, unique=True
    )
    version_id = database.Column(database.String(32), nullable=False)

    # many to many: list <-> item
    items = database.relationship(
        "ListItem",
        back_populates="list_",
        cascade="save-update, merge, delete",
        passive_deletes=True,
    )

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<List id: {self.list_id} name: {self.name}>"


class ListItemType(enum.Enum):
    none = 0
    selection = 1
    number = 2
    text = 3

    def next(self):
        return ListItemType((self.value + 1) % 4)


class ListItem(database.Model):
    list_id = database.Column(
        database.Integer,
        database.ForeignKey("list.list_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        primary_key=True,
    )
    item_id = database.Column(
        database.Integer,
        database.ForeignKey("item.item_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        primary_key=True,
    )
    type_ = database.Column("type", database.Enum(ListItemType), nullable=False)
    selection = database.Column("selection", database.Boolean, nullable=False)
    # number = database.Column("number", database.Numeric, nullable=False)
    number = database.Column("number", SqliteNumeric, nullable=False)
    text = database.Column("text", database.String(1000), nullable=False)
    version_id = database.Column(database.String(32), nullable=False)

    list_ = database.relationship("List", back_populates="items")
    item = database.relationship("Item", back_populates="lists")

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = (
        database.PrimaryKeyConstraint("list_id", "item_id"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<ListItem list: {self.list_id} item: {self.item_id}>"
