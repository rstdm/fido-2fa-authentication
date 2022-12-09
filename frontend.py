from flask import Blueprint, render_template, redirect, session

import session as session_util

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():

    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register')
def register():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()
    return render_template('register.html')


@bp.route('/register-fido')
def register_fido():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()
    return render_template('register_fido.html')


@bp.route('/login')
def login():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return redirect("/")
    return render_template('login.html')


@bp.route('/login-fido')
def login_fido():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return redirect("/")
    return render_template('login_fido.html')


@bp.route('/logout', methods=["POST"])
def logout():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionValid(session):
        session_util.logout(session)
    return redirect("/")
