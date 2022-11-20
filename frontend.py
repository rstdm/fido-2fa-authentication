from flask import Blueprint, render_template, redirect, session

import session as session_util

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    if session_util.is_logged_in(session):
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register')
def register():
    return render_template('register.html')


@bp.route('/login')
def login():
    if session_util.is_logged_in(session):
        return redirect("/")

    return render_template('login.html')


@bp.route('/logout')
def logout():
    session_util.logout(session)
    return redirect("/")