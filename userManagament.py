import shelved_cache
import uuid
from cachetools import LRUCache
import hashlib, uuid
import types
from fido2.webauthn import AttestedCredentialData

import session as session_util
from tinydb import TinyDB, Query

userContainerName = 'userContainer.json'
db = {}

def randString(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


class User:
    username = None
    password = None
    passwordsalt = None
    fidoinfo = None

    sessionid = None
    firstname = None
    lastname = None

    def __init__(self, username, password, passwordsalt, fidoinfo, sessionid, firstname, lastname):
        self.username = username
        self.password = password
        self.passwordsalt = passwordsalt
        self.fidoinfo = fidoinfo
        self.sessionid = sessionid
        self.firstname = firstname
        self.lastname = lastname



def saveUser(user):
    # insert dict db
    db[user.username] = user

    db
def userNameExists(username) -> bool:
    if username in db.keys():
        return True
    else:
        return False


def userExists(user) -> bool:
    return userNameExists(user.username)

def checkUserPassword(username, password) -> bool:
    user = getUserByUsername(username)
    if user is None:
        return False
    hashed_password = hashlib.sha512(password.encode('utf-8') + user.passwordsalt.encode('utf-8')).hexdigest()
    if user.password == hashed_password:
        return True
    else:
        return False

def deleteUserByName(username):
    db[username] = None

def createAndSaveUser(userName, password, fidoInfo, sessionID, firstName, lastName):
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    user = User(userName, hashed_password, salt, fidoInfo, sessionID, firstName, lastName)
    saveUser(user)
    return user


def getUserByUsername (username):
    for user in db.values():
        userName = user.username
        if user.username == username:
            return user
    return None

def getUserBySessionID(sessionid):
    user = None
    for key in db:
        if db[key].sessionid == sessionid:
            user = db[key]
            break
    return user

def  setNewSessionId(username):
    user = getUserByUsername(username)
    user.sessionid = session_util.createSessionId()
    saveUser(user)
    return user.sessionid

def saveFidoState(user, fidoState):
    user.fidoinfo = fidoState
    saveUser(user)

def refrechSession(user, sessionid):
    user.sessionid = sessionid
    saveUser(user)
    return user