import shelved_cache
import uuid
from cachetools import LRUCache
import hashlib, uuid
import session as session_util

userContainerName = 'userContainer'

userContainer = shelved_cache.PersistentCache( LRUCache, userContainerName, 500)


def randString(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


class User:
    id = None
    userName  = None
    password = None
    passwordSalt = None
    fidoInfo = None
    sessionID = None
    firstName = None
    lastName = None

    def __init__(self, id, userName, password, passwordSalt, fidoInfo, sessionID, firstName, lastName):
        self.id = id
        self.userName = userName
        self.password = password
        self.passwordSalt = passwordSalt
        self.fidoInfo = fidoInfo
        self.sessionID = sessionID
        self.firstName = firstName
        self.lastName = lastName

    def __cmp__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id}, userName: {self.userName}, password: {self.password}, passwordSalt: {self.passwordSalt}, fidoInfo: {self.fidoInfo}, sessionID: {self.sessionID}, firstName: {self.firstName}, lastName: {self.lastName}"

    def __str__(self):
        return f"id: {self.id}, userName: {self.userName}, password: {self.password}, passwordSalt: {self.passwordSalt}, fidoInfo: {self.fidoInfo}, sessionID: {self.sessionID}, firstName: {self.firstName}, lastName: {self.lastName}"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __ne__(self, other):
        return not self.__eq__(other)


def createUser(userName, password, fidoInfo, sessionID, firstName, lastName):
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    user = User(randString(), userName, hashed_password, salt, fidoInfo, sessionID, firstName, lastName)
    userContainer[user.id] = user
    return user


def getUser(id):
    return userContainer[id]

def getUserBySessionID(sessionID):
    for user in userContainer.values():
        if user.sessionID == sessionID:
            return user
    return None


def checkPassword(user, password):
    hashed_password = hashlib.sha512(password + user.passwordSalt).hexdigest()
    return hashed_password == user.password


def  registerUser(user, sessionID) -> bool:
    user.sessionID = sessionID
    # check if user already exists
    for userInContainer in userContainer.values():
        if userInContainer == user:
            return False
    userContainer[user.id] = user
    return True




