from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from flask import Blueprint, session, jsonify, request, abort

import session as session_util

rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
server = Fido2Server(rp)


# Registered credentials are stored globally, in memory only. Single user
# support, state is lost when the server terminates.
credentials = []



bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
def register_begin():
    options, state = server.register_begin(
        PublicKeyCredentialUserEntity(
            id=b"user_id",
            name="a_user",
            display_name="A. User",
        ),
        credentials,
        user_verification="discouraged",
        authenticator_attachment="cross-platform",
    )

    session["state"] = state
    print("\n\n\n\n")
    print(options)
    print (session)
    print("\n\n\n\n")

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
def register_complete():
    response = request.json
    print("RegistrationResponse:", response)
    auth_data = server.register_complete(session["state"], response)

    credentials.append(auth_data.credential_data)
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)

    session_util.login(session)

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    if not credentials:
        abort(404)

    options, state = server.authenticate_begin(credentials)
    session["state"] = state

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    if not credentials:
        abort(404)

    response = request.json
    print("AuthenticationResponse:", response)
    server.authenticate_complete(
        session.pop("state"),
        credentials,
        response,
    )
    print("ASSERTION OK")

    session_util.login(session)

    return jsonify({"status": "OK"})