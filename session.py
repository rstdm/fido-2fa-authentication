from flask import session as flask_session

SESSION_KEY_LOGGED_IN = "loggedIn"


def login(session: flask_session):
    session[SESSION_KEY_LOGGED_IN] = True


def logout(session: flask_session):
    del session[SESSION_KEY_LOGGED_IN]


def is_logged_in(session: flask_session):
    return session.get(SESSION_KEY_LOGGED_IN) is True
