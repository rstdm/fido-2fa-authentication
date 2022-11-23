import os
import string
from random import random
from random import randrange

from flask import session as flask_session

SESSION_KEY_LOGGED_IN = "loggedIn"
sessions = {}

def login(userSession: flask_session):

    sessions[userSession["id"]] = True


def logout(userSession: flask_session):
    del sessions[userSession["id"]]


def is_logged_in(userSession: flask_session):
    print ("usersession")
    print (userSession)
    if "id" in userSession:
        if userSession["id"] in sessions.keys():
            print (sessions)

    return userSession.get(SESSION_KEY_LOGGED_IN) is True

def is_id_in (userSession: flask_session):
    print (userSession)
    if "id" in userSession:
        print (userSession["id"])
        return True

    return False


def create_session_id ():
    newSessionId = randrange(100)
    sessions[newSessionId] = False
    return newSessionId

def is_session_logged_in (userSession: flask_session):
    if "id" in userSession:
        if userSession["id"] in sessions.keys():
            return sessions[userSession["id"]]
    return False