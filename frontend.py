import re

from flask import Blueprint, render_template, redirect, session, request, abort

import db

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    is_logged_in = True  # TODO
    if is_logged_in:
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    # if session_util.isSessionLoggedIn(session): # TODO
    #    return redirect('/')

    if request.method == 'POST':
        return post_register()
    else:
        return render_template('register.html')


def post_register():
    # register user
    # validate input
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

    # todo login
    # if not userm.userNameExists(user_name):
    #    userm.createAndSaveUser(user_name, password, None, serverSession.id, first_name, last_name)
    return redirect('/register-fido')
    # else:


@bp.route('/register-fido', methods=['POST', 'GET'])
def register_fido():
    return render_template('register_fido.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # if session_util.isSessionLoggedIn(session): # TODO
    #    # user is already logged in
    #    return redirect("/")

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
    return render_template('login_fido.html')


@bp.route('/logout', methods=["POST"])
def logout():
    # TODO logout
    return redirect("/")
