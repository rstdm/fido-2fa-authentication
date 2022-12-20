from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from flask import Blueprint, session, jsonify, request, abort



rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
server = Fido2Server(rp)

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
def register_begin():
    username = "username" # TODO
    firstname = "firstname"
    lastname = "lastname"
    state = None


    options, state = server.register_begin(
        PublicKeyCredentialUserEntity(
            id=bytes(username, "utf-8"),
            name=firstname,
            display_name=firstname + " " + lastname,
        ),
        state,
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    #session_util.setSessionState(session, state)

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
def register_complete():
    response = request.json
    user = None
    fidostate = None # TODO

    auth_data = server.register_complete(fidostate, response) # todo exception handling
    #userm.saveFidoState(user, auth_data.credential_data)

    #session_util.login(session)

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    user = None # TODO

    options, state = server.authenticate_begin([user.fidoinfo], user_verification="discouraged")

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    user = None
    response = request.json

    #TODO
    """server.authenticate_complete( # todo exception handling 
        state,
        [fidoinfo],
        response,
    )"""
    return jsonify({"status": "OK"})
