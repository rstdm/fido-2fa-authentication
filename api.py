from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from flask import Blueprint, session, jsonify, request, abort

import userManagament as userm

import session as session_util

rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
server = Fido2Server(rp)


# Registered credentials are stored globally, in memory only. Single user
# support, state is lost when the server terminates.
credentials = [] # todo this information must be unique for each user and has to be retrieved from the database



bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
def register_begin():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    #if request.method == 'POST':
        # register user
        # validate input
        #firstName = request.form['firstname']
        #password = request.form['passWord']
        #userName = request.form['username']
        #print("UserData")

    #user = {"id": b"user_id", "name": "A. User"}

    options, state = server.register_begin(
        PublicKeyCredentialUserEntity(
            id=b"user_id",
            name="a_user",
            display_name="A. User",

            #id=bytes(user.userName),
            #name=user.userName,
            #display_name=firstName + " " + lastName,
        ),
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    #session["state"] = state
    session_util.setSessionState(session, state)
    print("\n\n\n\n")
    print(options)
    print (f"userSession: {session}")
    print("\n\n\n\n")

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
def register_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    response = request.json
    print("RegistrationResponse:", response)
    auth_data = server.register_complete(session_util.getServerSession(session).state, response) # todo exception handling

    credentials.append(auth_data.credential_data)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)

    session_util.login(session)

    print("***********************************************************")
    print(f"{credentials}")

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if not credentials:
        abort(404)

    options, state = server.authenticate_begin(credentials)
    session_util.setSessionState(session, state)

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if not credentials:
        abort(404) # todo exception handling?

    response = request.json
    print("AuthenticationResponse:", response)
    server.authenticate_complete( # todo exception handling
        session_util.getServerSession(session).state,
        credentials,
        response,
    )
    print("ASSERTION OK")

    session_util.login(session)

    return jsonify({"status": "OK"})


@bp.route("/cred/print", methods=["GET"])
def printCredentials():
    print("--------------------------------------------------\n")
    print("Credentials:")
    print(credentials)
    print("\n--------------------------------------------------")
    return jsonify({"status": "OK"})