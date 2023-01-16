import uuid

import fido2.webauthn
import flask_login
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from flask import Blueprint, jsonify, request, abort
from flask_login import login_required
from cachetools import TTLCache

import db
import fidosession
from db import User

rp = PublicKeyCredentialRpEntity(name="Demo server", id="localhost")
fido_server = Fido2Server(rp)
active_challenges = TTLCache(1000, 60)  # fido challenges expire after 60 seconds

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route("/register/begin", methods=["POST"])
@login_required
def register_begin():
    if flask_login.current_user.fido_info != "":
        return abort(400, "fido has already been activated")

    options, state = fido_server.register_begin(
        PublicKeyCredentialUserEntity(
            id=bytes (str(flask_login.current_user.user_id), 'utf-8'),
            name=flask_login.current_user.username,
            display_name=f'{flask_login.current_user.firstname} {flask_login.current_user.lastname}',
        ),
        user_verification=fido2.webauthn.UserVerificationRequirement.DISCOURAGED,
    )

    active_challenges[flask_login.current_user.user_id] = state

    return jsonify(dict(options))


@bp.route("/register/complete", methods=["POST"])
@login_required
def register_complete():
    if flask_login.current_user.fido_info != "":
        return abort(400, "fido has already been activated")

    # deleting the state from the list of active operations ensures that only one attempt to
    # beat the challenge is possible
    fido_state = active_challenges.pop(flask_login.current_user.user_id)
    if fido_state is None:
        return abort(400, 'no fido-state')

    response = request.json
    try:
        auth_data = fido_server.register_complete(fido_state, response)
    except:
        return abort(400, 'invalid payload')

    user_id = flask_login.current_user.user_id
    db.set_fido_info(user_id, auth_data.hex())

    return jsonify({"status": "OK"})


@bp.route("/authenticate/begin", methods=["POST"])
def authenticate_begin():
    user = load_user_from_fido_session()
    if user is None:
        return abort(401, "Unauthorized")

    credential_data = fido2.webauthn.AuthenticatorData.fromhex(user.fido_info).credential_data
    options, state = fido_server.authenticate_begin(
        credentials=[
            credential_data
        ],
        user_verification=fido2.webauthn.UserVerificationRequirement.DISCOURAGED
    )

    active_challenges[user.user_id] = state

    return jsonify(dict(options))


@bp.route("/authenticate/complete", methods=["POST"])
def authenticate_complete():
    user = load_user_from_fido_session()
    if user is None:
        return abort(401, "Unauthorized")

    # deleting the state from the list of active operations ensures that only one attempt to
    # beat the challenge is possible
    fido_state = active_challenges.pop(user.user_id, None)
    if fido_state is None:
        return abort(400, 'no fido-state')

    credential_data = fido2.webauthn.AuthenticatorData.fromhex(user.fido_info).credential_data
    try:
        fido_server.authenticate_complete(
            fido_state,
            [credential_data],
            request.json,
        )
    except:
        return abort(400, 'invalid payload')

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
