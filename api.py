from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from flask import Blueprint, session, jsonify, request, abort

import userManagament
import userManagament as userm

import session as session_util


rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
server = Fido2Server(rp)

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
            id=bytes(username, "utf-8"),
            name=firstname,
            display_name=firstname + " " + lastname,
        ),
        user.fidoinfo,
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    session_util.setSessionState(session, state)

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
def register_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    response = request.json
    serverSession = session_util.getServerSession(session)
    user = userm.getUserBySessionID(serverSession.id)
    fidostate = session_util.getSessionState(session)

    auth_data = server.register_complete(fidostate, response) # todo exception handling
    userm.saveFidoState(user, auth_data.credential_data)

    session_util.login(session)

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    user = userm.getUserBySessionID(session_util.getServerSession(session).id)

    if user.fidoinfo is None:
        abort(404)

    options, state = server.authenticate_begin([user.fidoinfo], user_verification="discouraged")
    session_util.setSessionState(session, state)

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    user = userm.getUserBySessionID(session_util.getServerSession(session).id)
    fidoinfo = user.fidoinfo
    state = session_util.getSessionState(session)

    if not fidoinfo:
        abort(404) # todo exception handling?

    response = request.json

    server.authenticate_complete( # todo exception handling
        state,
        [fidoinfo],
        response,
    )
    session_util.login(session)
    return jsonify({"status": "OK"})


@bp.route("/cred/print", methods=["GET"])
def printCredentials():
    return jsonify({"status": "OK"})