from flask import Blueprint, render_template, redirect, session, request

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
        if len (request.form) != 4:
            return render_template('register.html', error="Invalid input")
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        userName = request.form['username']
        password = request.form['password']

        serverSession = session_util.getServerSession(session)
        if serverSession is None:
            return redirect('/register')
        newUser = userm.createUser(userName, password, None, serverSession.id, firstName, lastName)
        userm.registerUser(newUser, serverSession.id)

        db.insertIntoDB(newUser)
        return redirect('/login')



    else:
        return render_template('register.html')



@bp.route('/register-fido', methods=['POST', 'GET'])
def register_fido():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        return redirect('/')

    return render_template('register_fido.html')


@bp.route('/login', methods = ['GET','POST'])
def login():
    if not session_util.isSessionValid(session):
        # is the session valid? create a new session if not
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if session_util.isSessionLoggedIn(session):
        # user is already logged in
        return redirect("/index_logged_in.html")
    else:
        if request.method == 'POST':
            if len (request.form) != 2:
                return render_template('login.html', error="Invalid input")
            userName = request.form['username']
            password = request.form['password']
            if userName == 'admin' and password == 'admin':
                print("Admin")
                # login successful
                session_util.login(session)
                return render_template("/index_logged_in.html")
            else:
                print(f"Username: {userName}, Password: {password}")
                if db.queryUserDB(userName,password):
                    return render_template("/register_fido.html")
                else:
                    return render_template("/login.html")
        else:
            return render_template('login.html')

        
        """ # user is not logged in, check credentials
        if request.method == 'POST':
            # check credentials
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
