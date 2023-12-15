from urllib.parse import urlparse

import falcon

from api.error_msgs import INVALID_CREDENTIALS
from api.utils.hashers import verify_password
from api.utils.tokens import auth_token_for_user
from api.utils.validators import check_required_fields
from config import TOKEN_EXP_SECONDS, TOKEN_ENCODE_FIELDS_MAP
from dao.controllers import UserController


class AuthResource:
    user_data_fields = TOKEN_ENCODE_FIELDS_MAP
    REQUIRED_FIELDS = ("email", "password")

    def on_post(self, req, resp):
        data = req.media

        not_found_fields = check_required_fields(data, self.REQUIRED_FIELDS)
        if not_found_fields:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = not_found_fields
            return

        with UserController() as Users:
            user = Users.get_user_by_email(data["email"], fields=self.user_data_fields.values())

            if not user or not verify_password(plain_password=data["password"], hashed_password=user.password):
                raise falcon.HTTPUnauthorized(description=INVALID_CREDENTIALS)

            token = auth_token_for_user(user=user)
            resp.status = falcon.HTTP_OK
            resp.media = {'token': token}

            url = urlparse(req.url)
            resp.set_cookie(
                'user_role',
                user.role,
                max_age=TOKEN_EXP_SECONDS,
                domain=url.netloc
            )
            resp.set_cookie(
                'user_email_verified',
                "1" if user.email_verified else "0",
                max_age=TOKEN_EXP_SECONDS,
                domain=url.netloc
            )
