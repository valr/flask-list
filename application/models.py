from datetime import datetime
from time import time

import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from application import database

# TODO: make a script with the below commands
# export PYTHONDONTWRITEBYTECODE=1
# flask db init
# flask db migrate -m 'init db'
# flask db upgrade
# # flask db downgrade
# chown -R flask-list:root database
# chmod 700 database
# chmod 600 database/application.db
# echo '.schema' | sqlite3 database/application.db


class User(database.Model, UserMixin):
    user_id = database.Column(database.Integer, primary_key=True)
    version_id = database.Column(database.Integer, nullable=False)
    email = database.Column(
        database.String(256), nullable=False, unique=True, index=True
    )
    password_hash = database.Column(database.String(128), nullable=False)
    active = database.Column(database.Boolean(), nullable=False)
    updated_on = database.Column(
        database.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    __mapper_args__ = {"version_id_col": version_id}

    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<User {self.email}>"

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


list_category = database.Table(
    "list_category",
    database.metadata,
    database.Column(
        "list_id",
        database.Integer,
        database.ForeignKey("list.list_id"),
        nullable=False,
        index=True,
    ),
    database.Column(
        "category_id",
        database.Integer,
        database.ForeignKey("category.category_id"),
        nullable=False,
        index=True,
    ),
    database.PrimaryKeyConstraint("list_id", "category_id"),
)


list_item = database.Table(
    "list_item",
    database.metadata,
    database.Column(
        "list_id",
        database.Integer,
        database.ForeignKey("list.list_id"),
        nullable=False,
        index=True,
    ),
    database.Column(
        "item_id",
        database.Integer,
        database.ForeignKey("item.item_id"),
        nullable=False,
        index=True,
    ),
    database.PrimaryKeyConstraint("list_id", "item_id"),
)


class Category(database.Model):
    category_id = database.Column(database.Integer, primary_key=True)
    version_id = database.Column(database.Integer, nullable=False)
    name = database.Column(
        database.String(256), nullable=False, unique=True, index=True
    )

    # one to many: category <-> item
    items = database.relationship("Item", backref="category")

    # many to many: list <-> category
    lists = database.relationship("List", secondary=list_category)

    __mapper_args__ = {"version_id_col": version_id}

    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<Category {self.name}>"


class Item(database.Model):
    item_id = database.Column(database.Integer, primary_key=True)
    version_id = database.Column(database.Integer, nullable=False)
    name = database.Column(database.String(256), nullable=False, index=True)

    # one to many: category <-> item
    category_id = database.Column(
        database.Integer,
        database.ForeignKey("category.category_id"),
        nullable=False,
        index=True,
    )

    # many to many: list <-> item
    lists = database.relationship("List", secondary=list_item)

    __mapper_args__ = {"version_id_col": version_id}

    __table_args__ = (
        database.UniqueConstraint("name", "category_id"),
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<Item {self.name}>"


class List(database.Model):
    list_id = database.Column(database.Integer, primary_key=True)
    version_id = database.Column(database.Integer, nullable=False)
    name = database.Column(
        database.String(256), nullable=False, unique=True, index=True
    )

    # many to many: list <-> category
    categories = database.relationship("Category", secondary=list_category)

    # many to many: list <-> item
    items = database.relationship("Item", secondary=list_item)

    __mapper_args__ = {"version_id_col": version_id}

    __table_args__ = {"sqlite_autoincrement": True}

    def __repr__(self):
        return f"<List {self.name}>"
