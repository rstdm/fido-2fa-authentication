"""This module contains the api endpoints that are related to fido. It also contains the fido related application logic."""

import uuid

import fido2.webauthn
import flask_login
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required
from cachetools import TTLCache

import app.db as db
from app.db import User
import app.fidosession as fidosession

# This information is sent to the client (browser + fido-token). The browser verifies that the id matches the domain of
# the webpage.
rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
fido_server = Fido2Server(rp)

# Fido is a challenge-response authentication mechanism. To ensure that every challenge is only used once we store the
# challenges on the server (and not e.g. in a cookie). The TTLCache automatically removes all challenges that are older
# than 60 seconds. This reduces the amount of time that attackers have to provide a valid response.
active_challenges = TTLCache(1000, 60)

# The api endpoints are added to this blueprint. The server module adds this blueprints and the associated endpoints to
# flask.
bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
@login_required
def register_begin():
    """Clients call this endpoint to register a new fido token. The endpoint returns a challenge which is then processed
    by the fido token. The client uses the register_complete endpoint to send the signed challenge back to the server.
    flask-login ensures that this endpoint can only be accessed by authenticated users."""

    # Although technically possible this application only allows one fido token per user.
    if flask_login.current_user.fido_info != "":
        return abort(400, "fido has already been activated")

    # create a challenge for the client
    options, state = fido_server.register_begin(
        PublicKeyCredentialUserEntity(
            # according to the documentation the id should be unique and shouldn't contain user related information
            id=uuid.uuid4().bytes,
            # the client might present these fields to the user
            name=flask_login.current_user.username,
            display_name=f'{flask_login.current_user.firstname} {flask_login.current_user.lastname}',
        ),
        # The token shouldn't ask the user to verify his identity (e.g. using a PIN). This would be redundant because
        # the user already verified his identity during the first login step (by providing his username and password).
        user_verification=fido2.webauthn.UserVerificationRequirement.DISCOURAGED,
    )

    # store some information (e.g. the challenge that was just send to the client) on the server. The register_complete
    # endpoint needs it to verify the response of the client.
    active_challenges[flask_login.current_user.user_id] = state

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
@login_required
def register_complete():
    """This endpoint is called by the client to register a new fido token. The client first retrieves a challenge from
    register_begin which is then processed by the token. The final result is sent back to this api endpoint which
    validates it and persists it in the database. flask-login ensures that this endpoint can only be accessed by
    authenticated users."""

    if flask_login.current_user.fido_info != "":
        return abort(400, "fido has already been activated")

    # The register_begin endpoint created a challenge and persisted it on the server. This retrieves the challenge and
    # then deletes it from the cache. This ensures that an attacker has only one attempt per challenge to provide
    # valid information.
    fido_state = active_challenges.pop(flask_login.current_user.user_id)
    if fido_state is None:
        return abort(400, 'no fido-state')

    # validate that the client sent valid information
    try:
        auth_data = fido_server.register_complete(fido_state, request.json)
    except:
        return abort(400, 'invalid payload')

    # persist the information that we received from the client. This includes the public key of the token.
    user_id = flask_login.current_user.user_id
    db.set_fido_info(user_id, auth_data.hex())

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    """This endpoint is called by the client to perform the second factor login. The endpoint creates a challenge which
    is sent to the client. The client sends it to the fido token which signs it. The client then sends the signed
    challenge to the authenticate_complete endpoint. This endpoint can only be accessed if the user has already provided
    valid credentials (username and password)."""

    # which user is trying to log in? Is the user even logged in?
    user = load_user_from_fido_session()
    if user is None:
        return abort(401, "Unauthorized")

    # load the information about the token (they were persisted when the token was registered)
    credential_data = fido2.webauthn.AuthenticatorData.fromhex(user.fido_info).credential_data

    # create a new challenge
    options, state = fido_server.authenticate_begin(
        credentials=[
            credential_data
        ],
        # The token shouldn't ask the user to verify his identity (e.g. using a PIN). This would be redundant because
        # the user already verified his identity during the first login step (by providing his username and password).
        user_verification=fido2.webauthn.UserVerificationRequirement.DISCOURAGED
    )

    # store some information (e.g. the challenge that was just send to the client) on the server. The
    # authenticate_complete endpoint needs it to verify the response of the client.
    active_challenges[user.user_id] = state

    # send the challenge to the client
    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    """This endpoint is called by the client when the fido token has processed the challenge. The endpoint creates a
    new session for the user if the challenge has been signed correctly. The endpoint can only
    be accessed if the user has already provided his username and password. """

    # which user is trying to log in? Is the user even logged in?
    user = load_user_from_fido_session()
    if user is None:
        return abort(401, "Unauthorized")

    # The authenticate_begin endpoint created a challenge and persisted it on the server. This retrieves the challenge
    # and then deletes it from the cache. This ensures that an attacker has only one attempt per challenge to provide
    # valid information.
    fido_state = active_challenges.pop(user.user_id, None)
    if fido_state is None:
        return abort(400, 'no fido-state')

    # load the information about the token (they were persisted when the token was registered)
    credential_data = fido2.webauthn.AuthenticatorData.fromhex(user.fido_info).credential_data

    # ensure that the client signed the challenge correctly
    try:
        fido_server.authenticate_complete(
            fido_state,
            [credential_data],
            request.json,
        )
    except:
        return abort(400, 'invalid payload')

    # The fido session is only needed if the user 1) has already provided his username and password and 2) hasn't yet
    # authenticated himself using fido. We can close the fido session and create a "real" flask-login session.
    fidosession.close_fido_session()
    flask_login.login_user(user)
    return jsonify({"status": "OK"})


def load_user_from_fido_session() -> User:
    user_id = fidosession.get_user_id()
    if user_id is None:
        return None

    user = db.load_user(user_id=user_id)
    if user is None:
        return None

    return user
