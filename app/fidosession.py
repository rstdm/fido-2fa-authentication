"""If a user decides to enable two factor authentication their login expires consists out of two steps
1) The user authenticates himself using his username and password
2) The user authenticates himself using fido

Step two is only allowed if step one has been executed before. After step one has successfully been completed a
fido-session is created. As long as the fido-session is valid users can perform step two. The fido session is only valid
for 5 minutes. Afterwards, the user has to provide his username and password again.

"Normal" sessions are managed by flask-login. However, flask-login does neither support two factor authentication nor
multiple sessions. Therefore we have to create our own session management class."""

from cachetools import TTLCache
from flask import session
import secrets

FIDO_SESSION_KEY = "fido-session"

cache = TTLCache(maxsize=10000, ttl=5 * 60)  # fido-sessions expire after 5 minutes


def start_fido_session(user_id: int):
    """Create a new fido-session for this user. The session will expire after 5 minutes, but it can also be
    invalidated earlier."""
    session_id = secrets.token_hex(32)
    while session_id in cache.keys():
        session_id = secrets.token_hex(32)

    cache[session_id] = user_id
    session[FIDO_SESSION_KEY] = session_id


def get_user_id() -> int:
    """Returns the id of the current user if there is an active fido-session. Returns None otherwise."""

    session_id = session.get(FIDO_SESSION_KEY, None)
    if session_id is None:
        return None

    user_id = cache.get(session_id, None)
    if user_id is None:
        del session[FIDO_SESSION_KEY]
        return None

    return user_id


def close_fido_session():
    """Invalidate the active fido-session. This function can also be called if there is no active fido-session."""

    session_id = session.get(FIDO_SESSION_KEY, None)
    if session_id is None:
        return

    del session[FIDO_SESSION_KEY]
    del cache[session_id]
