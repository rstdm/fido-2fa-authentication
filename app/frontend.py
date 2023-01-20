import re

from flask import Blueprint, render_template, redirect, request, abort, flash
import flask_login
from flask_login import login_required

import db
import fidosession

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    """This route returns the landing page. The returned page depends on weather the user is logged in or not."""
    if flask_login.current_user.is_authenticated:
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    """This route is used to register new users. GET returns the HTML, POST is used to create a new user."""

    # this route must not be used by logged-in users
    if flask_login.current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        return post_register()
    else:
        return render_template('register.html')


def post_register():
    # extract form fields
    first_name = request.form['firstname']
    last_name = request.form['lastname']
    user_name = request.form['username']
    password = request.form['password']

    # validate input
    input_lengths = [len(first_name), len(last_name), len(user_name), len(password)]
    if max(input_lengths) > 100 or min(input_lengths) == 0 or re.match(r'^[a-z0-9]+$', user_name) is None:
        print('WARNING: Got a request with invalid input which should have been validated by the client. This '
              'might indicate that an attacker is sending manipulated requests.')

        # "nice" clients perform the validation on client side and don't send such requests
        # we don't have to provide helpful error messages to attackers
        return abort(400)

    # create a new user
    try:
        created_user = db.create_user(user_name, first_name, last_name, password)
    except db.UsernameAlreadyExistsException:
        error_msg = f'Der gewählte Nutzername "{user_name}" ist bereits vergeben. ' \
                    f'Bitte wählen Sie einen anderen Nutzernamen.'
        flash(error_msg)
        return redirect('/register')

    # create a new session for the user
    flask_login.login_user(created_user)

    # ask the user weather he wants to set up fido or not
    return redirect('/register-fido')


@bp.route('/register-fido', methods=['POST', 'GET'])
@login_required
def register_fido():
    """This route is only accessible for authenticated users and returns the HTML page to optionally setup fido. The
    HTML page loads some JavaScript which interacts with the endpoints in the api module to perform the actual fido
    set up."""
    return render_template('register_fido.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """This route is used to log in with username and password."""

    # logged-in users don't have to log in
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        return post_login()
    else:
        return render_template('login.html')


def post_login():
    # extract form fields
    user_name = request.form['username']
    password = request.form['password']

    # validate input
    if user_name == "" or password == "":
        print("WARNING: Got a request with invalid input which should have been validated by the client. This "
              'might indicate that an attacker is sending manipulated requests.')
        return render_template('login.html', error="Invalid input")

    # load user and check credentials
    user = db.authenticate_user(user_name, password)
    if user is None:
        error_msg = "Ungültige Zugangsdaten."
        flash(error_msg)
        return redirect('/login')

    # is fido enabled?
    if user.fido_info == "":
        # fido is not enabled. Create a new session and ask the user if he wants to enable fido
        flask_login.login_user(user)
        return redirect('/register-fido')
    else:
        # fido is enabled. Start a temporary fido-session and redirect the user to the fido-login page.
        # (The fidosession module describes why the fido-session is necessary)
        fidosession.start_fido_session(user.user_id)
        return redirect('/login-fido')


@bp.route('/login-fido')
def login_fido():
    """This route returns the HTML for the fido-login page. This page can only be accessed if the user has a valid
    fido-session."""

    # logged-in users don't have to log in
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    # check if there is a fido-session
    user_id = fidosession.get_user_id()
    if user_id is None:
        return redirect('/login')

    return render_template('login_fido.html')


@bp.route('/logout', methods=["POST"])
def logout():
    # we don't have to check weather the user is logged in or not
    # if the user thinks he is logged in but he is no longer logged in (e.g. because his session expired) this route
    # will be called. We want to redirect all users to the landing page
    flask_login.logout_user()
    return redirect("/")
