# Copyright (c) 2018 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Example demo server to use a supported web browser to call the WebAuthn APIs
to register and use a credential.

See the file README.adoc in this directory for details.

Navigate to https://localhost:5000 in a supported web browser.
"""
from fido2.webauthn import PublicKeyCredentialRpEntity, PublicKeyCredentialUserEntity
from fido2.server import Fido2Server
from flask import Flask, session, request, redirect, abort, jsonify, render_template

import os
import fido2.features

import api
import session as session_util

fido2.features.webauthn_json_mapping.enabled = True


app = Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)  # Used for session.
app.register_blueprint(api.bp)


@app.after_request
def apply_caching(response):
    # add security headers, see https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    # Strict-Transport-Security can be enabled as soon as this website has a valid certificate

    # TODO flask sets the server header: Server: Werkzeug/2.2.2 Python/3.10.6 -> remove this header

    return response


@app.route('/')
def index():
    if session_util.is_logged_in(session):
        return render_template('index_logged_in.html', is_logged_in=True)
    else:
        return render_template('index.html', is_logged_in=False)


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    if session_util.is_logged_in(session):
        return redirect("/")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session_util.logout(session)
    return redirect("/")


def main():
    print(__doc__)
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc", debug=True)


if __name__ == "__main__":
    main()
