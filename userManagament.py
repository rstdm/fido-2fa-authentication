import shelved_cache
import uuid
from cachetools import LRUCache
import hashlib, uuid
import session as session_util
from tinydb import TinyDB, Query

userContainerName = 'userContainer.json'
db = TinyDB(userContainerName)

def randString(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


class User:
    username  = None
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
    db.insert(user.__dict__)

def userNameExists(username) -> bool:
    user_query = Query()
    user = db.search(user_query.username == username)
    if len(user) == 1:
        return True
    else:
        return False

def userExists(user) -> bool:
    return userNameExists(user.username)

def checkUserPassword(username, password) -> bool:
    user_query = Query()
    users = db.search(user_query.username == username)
    if len(users) != 1:
        return False
    user = User(**users[0])
    hashed_password = hashlib.sha512(password.encode('utf-8') + user.passwordsalt.encode('utf-8')).hexdigest()
    if user.password == hashed_password:
        return True
    else:
        return False

def deleteUserByName(username):
    user_query = Query()
    db.remove(user_query.username == username)

def createAndSaveUser(userName, password, fidoInfo, sessionID, firstName, lastName):
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    user = User(userName, hashed_password, salt, fidoInfo, sessionID, firstName, lastName)
    saveUser(user)
    return user


def getUserBySessionID(sessionid):
    user_query = Query()
    user = db.search(user_query.sessionid == sessionid)
    if user is None:
        return None
    else:
        return User(**user).sessionid

def  setNewSessionId(username):
    user_query = Query()
    user = db.search(user_query.username == username)
    user = User(**user)
    user.sessionid = session_util.createSessionId()
    db.remove(user_query.username == username)
    saveUser(user)
    return user.sessionid



