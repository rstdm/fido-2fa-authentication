from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from flask import Blueprint, session, jsonify, request, abort

import userManagament
import userManagament as userm

import session as session_util

rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
server = Fido2Server(rp)


# Registered credentials are stored globally, in memory only. Single user
# support, state is lost when the server terminates.
credentials = []



bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
def register_begin():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    # get user from session
    serverSession = session_util.getServerSession(session)
    user = userm.getUserBySessionID(serverSession.id)
    username = user.username
    firstname = user.firstname
    lastname = user.lastname


    options, state = server.register_begin(
        PublicKeyCredentialUserEntity(
            id=username,
            name=firstname,
            display_name=firstname + " " + lastname,
        ),
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    userManagament.saveFidoState(user, state)

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
def register_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    response = request.json
    auth_data = server.register_complete(session_util.getServerSession(session).state, response)
    credentials.append(auth_data.credential_data)
    session_util.login(session)
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
        abort(404)

    response = request.json

    server.authenticate_complete(
        session_util.getServerSession(session).state,
        credentials,
        response,
    )
    session_util.login(session)
    return jsonify({"status": "OK"})


@bp.route("/cred/print", methods=["GET"])
def printCredentials():
    return jsonify({"status": "OK"})