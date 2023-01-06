import dataclasses
import hashlib
import uuid

import flask_login
import tinydb.table
from tinydb import TinyDB, Query
from dataclasses import dataclass

db = TinyDB('userContainer.json')


class UsernameAlreadyExistsException(Exception):
    pass


@dataclass
class User(flask_login.UserMixin):
    user_id: int = None
    username: str = None
    firstname: str = None
    lastname: str = None

    hashed_password: str = None
    password_salt: str = None
    fido_info: str = None

    def get_id(self): # this function is required by flask_login
        return self.user_id


def create_user(username: str, firstname: str, lastname: str, password: str) -> User:
    existing_user = load_user(username=username)
    if existing_user is not None:
        raise UsernameAlreadyExistsException

    password_salt = uuid.uuid4().hex
    hashed_password = hash_password(password, password_salt)

    # we can specify 0 as user_id because we don't store the user_id by ourselves. it's managed by the database
    user = User(0, username, firstname, lastname, hashed_password, password_salt, fido_info='')
    user = dataclasses.asdict(user)
    del user['user_id']  # the database manages the userid for us

    db.insert(user)

    return load_user(username=username)


def hash_password(password: str, salt: str):
    return hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()


def load_user(username: str = '', user_id: int = -1) -> User | None:
    if username == '' and user_id < 0:
        raise ValueError('username or user_id must be specified to retrieve a user')

    if user_id >= 0:
        user = db.get(doc_id=user_id)
        user = db_entry_to_user(user)

        if username != '' and username != user.username:
            return None
        return user

    user = db.get(Query().username == username)
    user = db_entry_to_user(user)

    return user


def authenticate_user(username: str, password: str) -> User | None:
    user = db.get(Query().username == username)
    if user is None:
        return None

    persisted_salt = user['password_salt']
    persisted_hash = user['hashed_password']
    provided_hash = hash_password(password, persisted_salt)

    if persisted_hash != provided_hash:
        return None

    return db_entry_to_user(user)


def db_entry_to_user(user_entry: tinydb.table.Document) -> User | None:
    if user_entry is None:
        return None

    user = User(**user_entry)
    user.user_id = user_entry.doc_id

    return user
