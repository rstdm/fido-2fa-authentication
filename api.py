from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity, AttestedCredentialData
from flask import Blueprint, session, jsonify, request, abort

import userManagament as userm

import session as session_util

import json

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
    auth_data = server.register_complete(session_util.getServerSession(session).state, response)

    credentials.append(auth_data.credential_data)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("REGISTERED CREDENTIAL:", auth_data.credential_data)

    session_util.login(session)

    print("***********************************************************")
    print(f"curACD: {credentials}")

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    cur_aaguid = auth_data.credential_data.aaguid
    cur_credential_id = auth_data.credential_data.credential_id
    cur_public_key = auth_data.credential_data.public_key

    print(f"aaguid: {cur_aaguid}")
    print(f"credential_id: {cur_credential_id}")
    print(f"public_key: {cur_public_key}")


    #cur_aaguid_JSON = json.dumps(cur_aaguid)
    #cur_credential_id_JSON = json.dumps(cur_credential_id)
    #cur_public_key_JSON = json.dumps(cur_public_key)

    print(f"cur_aaguid_JSON: {cur_aaguid}")

    new_credential_id = bytes('b\x9ar\xf0\xf0\x98\x1f5b\x81\x0e\xc9\xfc\xafe\x88",/K\xd8X\xf4\xee\x11"Y\x92\x0fhn\xb5\x11\x0e\x85\xaf\x96\xb8\x98\xaek\x1c\xdc:\x96X\x9c\x07\xe6\xc1\x92\xbc\xe0Vk\x1b+UzT3\xa17\xe0', 'utf-8')
    


    #my_str_as_bytes = str.encode(my_str)
    #print(type(my_str_as_bytes)) # ensure it is byte representation
    #my_decoded_str = my_str_as_bytes.decode()
    #print(type(my_decoded_str)) # ensure it is string representation




    print(f"new_credential_id: {new_credential_id}")
    print(f"cur_public_key_JSON: {cur_public_key}")



    newACD = AttestedCredentialData.create(
            aaguid=bytes(cur_aaguid),
            credential_id=new_credential_id,
            public_key=cur_public_key)
    print(f"newACD: {newACD}")

    #credJSON = jsonify(auth_data.credential_data)
    #credJSON = json.dumps(credentials)
    #print(credJSON)

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
    print("AuthenticationResponse:", response)
    server.authenticate_complete(
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