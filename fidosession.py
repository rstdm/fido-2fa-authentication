from cachetools import TTLCache
from flask import session
import secrets

FIDO_SESSION_KEY = "fido-session"

cache = TTLCache(maxsize=10000, ttl=5 * 60)  # fido-sessions expire after 5 minutes


def start_fido_session(user_id: int):
    session_id = secrets.token_hex(32)
    while session_id in cache.keys():
        session_id = secrets.token_hex(32)

    cache[session_id] = user_id

    session[FIDO_SESSION_KEY] = session_id


def get_user_id() -> int | None:
    session_id = session.get(FIDO_SESSION_KEY, None)
    if session_id is None:
        return None

    user_id = cache.get(session_id, None)
    if user_id is None:
        del session[FIDO_SESSION_KEY]
        return None

    return user_id


def close_fido_session():
    session_id = session.get(FIDO_SESSION_KEY, None)
    if session_id is None:
        return

    del session[FIDO_SESSION_KEY]
    del cache[session_id]
