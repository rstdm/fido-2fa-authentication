import os
import string
import uuid
from cachetools import TTLCache

from flask import session as flask_session

SESSION_KEY = "ID"
newSession = TTLCache(maxsize=500, ttl=60)
sessionIDLength = 64



def randString(string_length=10):
    random = str(uuid.uuid4())
    random = random.upper()
    random = random.replace("-","")
    return random[0:string_length]


class ServerSession:
    id = None
    logged_in = False
    state = None

    def __init__(self, id):
        self.id = id

    def __cmp__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"id: {self.id}, logged_in: {self.logged_in}, state: {self.state}"

def createSessionId():
    server_session = ServerSession(randString(sessionIDLength))
    newSession[server_session.id] = server_session
    return server_session.id
def isSessionValid (userSession: flask_session):
    if SESSION_KEY in userSession:
        return userSession[SESSION_KEY] in newSession.keys()
    else:
        return False



def getServerSession (userSession: flask_session):
    if isSessionValid(userSession):
        return newSession[userSession[SESSION_KEY]]
    else:
        return None


def login(userSession: flask_session):
    serverSession = getServerSession(userSession)
    serverSession.logged_in = True
    newSession[userSession[SESSION_KEY]] = serverSession


def logout(userSession: flask_session):
    serverSession = getServerSession(userSession)
    serverSession.logged_in = False
    newSession[serverSession.id] = serverSession

def isSessionLoggedIn(userSession: flask_session):
    serverSession = getServerSession(userSession)
    return serverSession.logged_in


def setSessionState(userSession: flask_session, state):
    serverSession = getServerSession(userSession)
    if serverSession is not None:
        serverSession.state = state
        newSession[userSession[SESSION_KEY]] = serverSession
        return True

    return False
