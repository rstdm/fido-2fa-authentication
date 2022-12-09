import shelved_cache
import uuid
from cachetools import LRUCache


userContainerName = 'userContainer.db'

userContainer = shelved_cache.PersistentCache( LRUCache, userContainerName, 500)


def randString(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


class User:
    id = None
    name  = None
    password = None
    passwordSalt = None
    fidoInfo = None
    sessionID = None


    def __init__(self, id, name, password, fidoInfo):
        self.id = id
        self.name = name
        self.password = password
        self.passwordSalt = randString(16)
        self.fidoInfo = fidoInfo
        self.sessionID = None

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, password: {self.password}, passwordSalt: {self.passwordSalt}, fidoInfo: {self.fidoInfo}, sessionID: {self.sessionID}"

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __cmp__(self, other):
        return self.id == other.id









