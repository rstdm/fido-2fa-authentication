import dataclasses
import hashlib
import secrets

import flask_login
import tinydb.table
from tinydb import TinyDB, Query
from dataclasses import dataclass

db = TinyDB('userdb.json', indent=2)


class UsernameAlreadyExistsException(Exception):
    pass


@dataclass
class User(flask_login.UserMixin):
    ''' A representation of a user. It is used by flask_login to store the user in the session and FIDO-information '''
    user_id: int = None
    username: str = None
    firstname: str = None
    lastname: str = None

    hashed_password: str = None
    password_salt: str = None
    fido_info: str = None

    def get_id(self):  # this function is required by flask_login
        return self.user_id


def create_user(username: str, firstname: str, lastname: str, password: str) -> User:
    existing_user = load_user(username=username)
    if existing_user is not None:
        raise UsernameAlreadyExistsException

    password_salt = secrets.token_hex(32)
    hashed_password = hash_password(password, password_salt)

    # we can specify 0 as user_id because we don't store the user_id by ourselves. it's managed by the database
    user = User(0, username, firstname, lastname, hashed_password, password_salt, fido_info='')

    user_fields = user_to_db_entry(user)
    db.insert(user_fields)

    return load_user(username=username)


def hash_password(password: str, salt: str):
    return hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()


def load_user(username: str = '', user_id: int = -1) -> User:
    if username == '' and user_id < 0:
        raise ValueError('username or user_id must be specified to retrieve a user')

    if user_id >= 0:
        user = db.get(doc_id=user_id)
        if user is None:
            return None

        user = db_entry_to_user(user)
        if username != '' and username != user.username:
            return None

        return user

    user = db.get(Query().username == username)
    if user is None:
        return None

    user = db_entry_to_user(user)

    return user


def set_fido_info(user_id: int, fido_info: str):
    user = db.get(doc_id=user_id)
    if user is None:
        raise ValueError('user does not exist')
    user = db_entry_to_user(user)
    user.fido_info = fido_info

    user_dict = user_to_db_entry(user)
    db.update(user_dict, doc_ids=[user_id])


def authenticate_user(username: str, password: str) -> User:
    user = load_user(username=username)
    if user is None:
        return None

    provided_hash = hash_password(password, user.password_salt)

    if user.hashed_password != provided_hash:
        return None

    return user


def db_entry_to_user(user_entry: tinydb.table.Document) -> User:
    user = User(**user_entry)
    user.user_id = user_entry.doc_id

    return user


def user_to_db_entry(user) -> dict:
    user = dataclasses.asdict(user)
    del user['user_id']  # the database manages the userid for us
    return user
