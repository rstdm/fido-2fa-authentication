import re

from flask import Blueprint, render_template, redirect, session, request, abort
import flask_login
from flask_login import login_required

import db

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    if flask_login.current_user.is_authenticated:
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if flask_login.current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        return post_register()
    else:
        return render_template('register.html')


def post_register():
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    user_name = request.form['username']
    password = request.form['password']

    input_lengths = [len(first_name), len(last_name), len(user_name), len(password)]
    if max(input_lengths) > 100 or min(input_lengths) == 0 or re.match(r'^[a-zA-Z0-9]+$', user_name) is None:
        print('WARNING: Got a request with invalid input which should have been validated by the client. This '
              'might indicate that an attacker is sending manipulated requests.')

        # "nice" clients perform the validation on client side and don't send such requests
        # we don't have to provide helpful error messages to attackers
        return abort(400)

    created_user = None
    try:
        created_user = db.create_user(user_name, first_name, last_name, password)
    except db.UsernameAlreadyExistsException:
        error_msg = f'Der gewählte Nutzername "{user_name}" ist bereits vergeben. Bitte wählen Sie einen anderen Nutzernamen.'
        return render_template('register.html', error_msg=error_msg)

    flask_login.login_user(created_user)
    return redirect('/register-fido')


@bp.route('/register-fido', methods=['POST', 'GET'])
@login_required
def register_fido():
    return render_template('register_fido.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        return post_login()
    else:
        return render_template('login.html')


def post_login():
    user_name = request.form['username']
    password = request.form['password']
    if user_name == "" or password == "":
        print("WARNING: Got a request with invalid input which should have been validated by the client. This ")
        return render_template('login.html', error="Invalid input")

    # if userm.checkUserPassword(user_name, password):
    # login successful session is valid and logged in
    #   user = userm.getUserByUsername(user_name)

    #    return redirect("/register-fido")
    else:
        error_msg = "Ungültige Zugangsdaten."
        return render_template("/login.html", error_msg=error_msg)


@bp.route('/login-fido')
def login_fido():
    if flask_login.current_user.is_authenticated:
        return redirect('/')
    return render_template('login_fido.html')


@bp.route('/logout', methods=["POST"])
def logout():
    # we don't have to check weather the user is logged in or not
    # if the user thinks he is logged in but he is no longer logged in (e.g. because his session expired) this route
    # will be called. We want to redirect all users to the landing page
    flask_login.logout_user()
    return redirect("/")
