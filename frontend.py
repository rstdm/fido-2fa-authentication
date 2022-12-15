import re

from flask import Blueprint, render_template, redirect, session, request, abort

import session as session_util
import userManagament as userm
import dbtry as db

bp = Blueprint('frontend', __name__)


@bp.route('/')
def index():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return redirect('/')

    if request.method == 'POST':
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

        serverSession = session_util.getServerSession(session)
        newUser = userm.createUser(user_name, password, None, serverSession.id, first_name, last_name)

        if not db.userExists(user_name):
            db.insertIntoDB(newUser)
            session_util.login(session)
            return redirect('/register-fido')
        else:
            return redirect('/register') # todo user name already exists -> display error message

    else:
        return render_template('register.html')



@bp.route('/register-fido', methods=['POST', 'GET'])
def register_fido():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    return render_template('register_fido.html')


@bp.route('/login', methods = ['GET','POST'])
def login():
    sessionId = None
    if not session_util.isSessionValid(session):
        # is the session valid? create a new session if not
        sessionId = session_util.createSessionId()
        session[session_util.SESSION_KEY] = sessionId
    else:
        sessionId = session[session_util.SESSION_KEY]

    if session_util.isSessionLoggedIn(session):
        # user is already logged in
        return redirect("/")
    else:
        if request.method == 'POST':
            if len (request.form) != 2:
                return render_template('login.html', error="Invalid input")
            userName = request.form['username']
            password = request.form['password']
            print(f"Username: {userName}, Password: {password}")
            if db.queryUserDB(userName,password):
                # login successful session is valid and logged in
                session_util.login(session)

                return redirect("/register-fido")
            else:
                return render_template("/login.html") # todo incorrect username / password -> display error message
        else:
            return render_template('login.html')

        # todo remove?
        """ # user is not logged in, check credentials
        if request.method == 'POST':
            # check credentials
            username = request.form['username']
            password = request.form['password']

            user = userm.getUser(username)

            if user is not None:
                if userm.checkPassword(user, password):
                    session_util.login(session)
                    return render_template('/index_logged_in.html')
                else:
                    return render_template('login.html', error="Invalid credentials")

            if request.form['username'] == 'admin' and request.form['password'] == 'admin':
                # login successful
                session_util.login(session)
                return render_template("/index_logged_in.html")
            else:
                # login failed
                return render_template('login.html', is_logged_in=False, login_failed=True) """
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
