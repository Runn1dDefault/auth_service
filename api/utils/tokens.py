from datetime import datetime, timedelta

import jwt

from api.error_msgs import TOKEN_HAS_EXPIRED, INVALID_TOKEN
from config import TOKEN_HASH_ALGORITHM, SECRET_KEY, VERIFY_SECRET_KEY, TOKEN_EXP_SECONDS, TOKEN_ENCODE_FIELDS_MAP


def decode_token(token, secret: str = None) -> dict:
    try:
        return jwt.decode(token, secret or SECRET_KEY, algorithms=[TOKEN_HASH_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError(TOKEN_HAS_EXPIRED)
    except jwt.InvalidTokenError as e:
        raise ValueError(INVALID_TOKEN)


def encode_token(token_payload, secret: str = None) -> str:
    return jwt.encode(token_payload, secret or SECRET_KEY, algorithm=TOKEN_HASH_ALGORITHM)


def auth_token_for_user(user) -> str:
    assert TOKEN_ENCODE_FIELDS_MAP and isinstance(TOKEN_ENCODE_FIELDS_MAP, dict)

    payload = {field: getattr(user, db_field) for field, db_field in TOKEN_ENCODE_FIELDS_MAP.items()}
    payload["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_EXP_SECONDS)
    return encode_token(payload)


def verify_token_for_user(user):
    assert TOKEN_ENCODE_FIELDS_MAP and isinstance(TOKEN_ENCODE_FIELDS_MAP, dict)

    payload = {field: getattr(user, db_field) for field, db_field in TOKEN_ENCODE_FIELDS_MAP.items()}
    payload["exp"] = datetime.utcnow() + timedelta(seconds=TOKEN_EXP_SECONDS)
    return encode_token(payload, VERIFY_SECRET_KEY)


def decode_verify_token(token):
    return decode_token(token, VERIFY_SECRET_KEY)
