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
    userName  = None
    password = None
    passwordSalt = None
    fidoInfo = None
    sessionID = None
    firstName = None
    lastName = None

    def __init__(self, userName, password, passwordSalt, fidoInfo, sessionID, firstName, lastName):
        self.userName = userName
        self.password = password
        self.passwordSalt = passwordSalt
        self.fidoInfo = fidoInfo
        self.sessionID = sessionID
        self.firstName = firstName
        self.lastName = lastName

    def __cmp__(self, other):
        return self.userName == other.userName

    def __repr__(self):
        return f"userName: {self.userName}, password: {self.password}, passwordSalt: {self.passwordSalt}, fidoInfo: {self.fidoInfo}, sessionID: {self.sessionID}, firstName: {self.firstName}, lastName: {self.lastName}"

    def __str__(self):
        return f"userName: {self.userName}, password: {self.password}, passwordSalt: {self.passwordSalt}, fidoInfo: {self.fidoInfo}, sessionID: {self.sessionID}, firstName: {self.firstName}, lastName: {self.lastName}"

    def __eq__(self, other):
        return self.userName == other.userName


    def __hash__(self):
        return hash(self.userName)

    def __ne__(self, other):
        return not self.__eq__(other)


def createUser(userName, password, fidoInfo, sessionID, firstName, lastName):
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()

    user = User(userName, hashed_password, salt, fidoInfo, sessionID, firstName, lastName)

    print(f"        sessionID: {sessionID}")
    print(f"        hashed_password: {hashed_password}")
    print(f"        salt: {salt}")
    print(f"        fidoInfo: {fidoInfo}")
    userContainer[user.userName] = user

    return user


def getUser(userName):
    return userContainer[userName]

def getUserBySessionID(sessionID):
    for user in userContainer.values():
        if user.sessionID == sessionID:
            return user
    return None


def checkPassword(user, given_password):
    existing_password = user.password
    salt = user.passwordSalt
    hashed_password = hashlib.sha512(given_password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
    return hashed_password == existing_password

def checkPassword2(password, passwordSalt, hashed_password) -> bool:
    #print(f"        password: {password}")
    #print(f"        passwordSalt: {passwordSalt}")
    control_hashed_password = hashlib.sha512(password.encode('utf-8') + passwordSalt.encode('utf-8')).hexdigest()
    #print(f"        hashed_password: {control_hashed_password}")
    return control_hashed_password == hashed_password


def  registerUser(user, sessionID) -> bool:
    user.sessionID = sessionID
    # check if user already exists
    for userInContainer in userContainer.values():
        if userInContainer == user:
            return False
    userContainer[user.userName] = user
    return True




