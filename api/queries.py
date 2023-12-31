from typing import Any

import falcon

from api.enums import Role
from api.error_msgs import TRY_ANOTHER_TIME, INVALID_CREDENTIALS
from api.utils.hashers import get_hashed_password, verify_password
from api.utils.tokens import auth_token_for_user, verify_token_for_user
from dao.controllers import UserController


def email_exists(email: str) -> bool:
    with UserController() as Users:
        return Users.email_exists(email=email)


def create_client(**client_data) -> str:
    client_data['role'] = Role.client.value
    with UserController() as Users:
        new_user = Users.model(**client_data)
        created = Users.create(new_user)
        if not created:
            raise falcon.HTTPInternalServerError(description=TRY_ANOTHER_TIME)
        return auth_token_for_user(new_user)


def update_user_pwd(user_id, plain_pwd):
    with UserController() as Users:
        user = Users.get_by_id(user_id)
        user.password = get_hashed_password(plain_pwd)
        return Users.commit()


def collect_user_data(user):
    return {
        "email": user.email,
        "full_name": user.full_name
    }


def get_user_data(user_id) -> dict | None:
    with UserController() as Users:
        user = Users.get_by_id(user_id, fields=("email", "full_name"))
        if user:
            return collect_user_data(user)


def update_user_data(user_id, password: str, updates: dict[str, Any]) -> bool:
    if not updates:
        return False

    if "password" in updates:
        raise ValueError("updates cannot have a key password!")

    with UserController() as Users:
        user = Users.get_by_id(_id=user_id)
        if not user:
            raise falcon.HTTPNotFound()

        if not verify_password(plain_password=password, hashed_password=user.password):
            raise falcon.HTTPUnauthorized(description=INVALID_CREDENTIALS)

        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return Users.commit()


def verify_token_by_email(email) -> str | None:
    with UserController() as Users:
        user = Users.get_user_by_email(email=email)
        if not user:
            return
        return verify_token_for_user(user=user)
