"""
This module configures flask and launches the server. The application logic is implemented in the other modules.
"""

from flask import Flask
from flask_login import LoginManager

import pyfiglet
import os
import fido2.features

import api
import db
import frontend

# configure the fido library
fido2.features.webauthn_json_mapping.enabled = True  # this simplifies the conversion from and to json

# configure flask
app = Flask(__name__, static_url_path="")
app.secret_key = os.urandom(32)  # Used for session.

# add http routes / endpoints
app.register_blueprint(api.bp)
app.register_blueprint(frontend.bp)

# configure flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "frontend.login"

# update the flask configuration
app.config.update(
    # tell flask to use secure cookies
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='strict',

    # tell flask-login to store its state in the session (and not in the url)
    USE_SESSION_FOR_NEXT=True
)


@app.after_request
def apply_caching(response):
    """This function adds security headers to every response that is sent to the client. The security headers are
    based on the recommendations of owasp (see https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)"""

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Resource-Policy"] = "same-site"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"

    # we have to allow the "data" scheme for images because bootstrap uses some CSS rules that look like this:
    # background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='-4 -4 8 8'%3e%3ccircle r='2' fill='%23fff'/%3e%3c/svg%3e");
    response.headers["Content-Security-Policy"] = "default-src 'none'; " \
                                                  "script-src 'self'; " \
                                                  "connect-src 'self'; " \
                                                  "img-src 'self' data:; " \
                                                  "style-src 'self'; " \
                                                  "form-action 'self'; " \
                                                  "upgrade-insecure-requests; " \
                                                  "frame-ancestors 'none'; " \
                                                  "base-uri 'self';"
    # Strict-Transport-Security can be enabled as soon as this website has a valid certificate

    return response


@login_manager.user_loader
def load_user(user_id):
    """This function is used by flask-login to load the user. flask-login stores only the user_id in the session."""
    return db.load_user(user_id=user_id)


def main():
    helpinfo = 'localhost'
    ascii_banner = pyfiglet.figlet_format(helpinfo)
    print(ascii_banner)
    app.run(host="0.0.0.0", port=5000, ssl_context="adhoc", debug=True)


if __name__ == "__main__":
    main()
