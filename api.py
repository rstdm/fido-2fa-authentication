from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from flask import Blueprint, session, jsonify, request, abort

import userManagament
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
    print("RegistrationResponse:", response)


    fidoState = userm.getUserBySessionID(session_util.getServerSession(session).id).fidoinfo
    auth_data = server.register_complete(fidoState, response) # todo exception handling
    state = auth_data.__str__()

    userm.saveFidoState(userm.getUserBySessionID(session_util.getServerSession(session).id), state)

    session_util.login(session)

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    getParsedFidoState = userm.getParsedFidoState(userm.getUserBySessionID(session_util.getServerSession(session).id).fidoinfo)

    if getParsedFidoState is None:
        abort(404)

    user = userm.getUserBySessionID(session_util.getServerSession(session).id)
    fidoinfo = user.fidoinfo

    options, state = server.authenticate_begin(fidoinfo)
    userManagament.saveFidoState(user, state)

    #session_util.setSessionState(session, state)

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    if not session_util.isSessionValid(session):
        session[session_util.SESSION_KEY] = session_util.createSessionId()

    if not credentials:
        abort(404) # todo exception handling?

    response = request.json

    user = userm.getUserBySessionID(session_util.getServerSession(session).id)
    fidoinfo = user.fidoinfo

    print("AuthenticationResponse:", response)
    server.authenticate_complete( # todo exception handling
        fidoinfo,
        credentials,
        response,
    )
    session_util.login(session)
    return jsonify({"status": "OK"})


@bp.route("/cred/print", methods=["GET"])
def printCredentials():
    return jsonify({"status": "OK"})