from flask import Blueprint, render_template, redirect, session, request

import session as session_util
import userManagament as userm

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
        if len (request.form) != 4:
            return render_template('register.html', error="Invalid input")
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        userName = request.form['username']
        password = request.form['password']

        serverSession = session_util.getServerSession(session)

        if not userm.userNameExists(userName):
            userm.createAndSaveUser(userName, password, None, serverSession.id, firstName, lastName)
            session_util.login(session)
            return redirect('/register-fido')
        else:
            return redirect('/register') # show error msg  # todo: redirect to fido registration

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
            if userm.checkUserPassword(userName,password):
                # login successful session is valid and logged in
                session_util.login(session)

                return redirect("/register-fido")
            else:
                return render_template("/login.html") # todo display error msg
        else:
            return render_template('login.html')

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
