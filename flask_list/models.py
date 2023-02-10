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

from flask_list import database


class SqliteNumeric(types.TypeDecorator):
    impl = types.String(1000)

    def process_bind_param(self, value, dialect):
        return str(value)

    def process_result_value(self, value, dialect):
        return Decimal(value if value is not None else "0")


class User(database.Model, UserMixin):
    user_id = database.Column(
        database.Integer, nullable=False, unique=True, index=True, primary_key=True
    )
    email = database.Column(
        database.String(1000), nullable=False, unique=True, index=True
    )
    password_hash = database.Column(database.String(128), nullable=False)
    active = database.Column(database.Boolean(), nullable=False)
    updated_on = database.Column(
        database.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
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

    def get_token(self, subject, expires_in=3600):
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

    def has_access(self, object_):
        return (
            (object_.private is False or object_.created_by == self.user_id)
            if isinstance(object_, List)
            else False
        )


class List(database.Model):
    list_id = database.Column(
        database.Integer, nullable=False, unique=True, index=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), nullable=False, unique=True, index=True
    )
    created_by = database.Column(database.Integer, nullable=False)
    private = database.Column(database.Boolean(), nullable=False)
    version_id = database.Column(database.String(32), nullable=False)

    # one to many: list <-> categories
    categories = database.relationship("Category", back_populates="list_")

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<List id: {self.list_id} name: {self.name}>"


class Category(database.Model):
    category_id = database.Column(
        database.Integer, nullable=False, unique=True, index=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), nullable=False, index=True  # unique per list
    )
    version_id = database.Column(database.String(32), nullable=False)

    # one to many: list <-> categories
    list_ = database.relationship("List", back_populates="categories")
    list_id = database.Column(
        database.Integer,
        database.ForeignKey("list.list_id"),
        nullable=False,
        index=True,
    )

    # one to many: category <-> items
    items = database.relationship(
        "Item", back_populates="category", cascade="all, delete-orphan"
    )

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = (
        database.UniqueConstraint("list_id", "name"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Category id: {self.category_id} name: {self.name}>"


class ItemType(enum.Enum):
    selection = 0
    number = 1
    text = 2


class Item(database.Model):
    item_id = database.Column(
        database.Integer, nullable=False, unique=True, index=True, primary_key=True
    )
    name = database.Column(
        database.String(1000), nullable=False, index=True  # unique per category
    )
    type_ = database.Column("type", database.Enum(ItemType), nullable=False)
    selection = database.Column(database.Boolean, nullable=False)
    # number = database.Column(database.Numeric, nullable=False)
    number = database.Column(SqliteNumeric, nullable=False)
    text = database.Column(database.String(1000), nullable=False)
    version_id = database.Column(database.String(32), nullable=False)

    # one to many: category <-> items
    category = database.relationship("Category", back_populates="items")
    category_id = database.Column(
        database.Integer,
        database.ForeignKey("category.category_id"),
        nullable=False,
        index=True,
    )

    __mapper_args__ = {
        "version_id_col": version_id,
        "version_id_generator": lambda version: uuid.uuid4().hex,
    }
    __table_args__ = (
        database.UniqueConstraint("category_id", "name"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Item id: {self.item_id} name: {self.name}>"
