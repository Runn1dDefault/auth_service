from urllib.parse import urlparse

import falcon

from api.error_msgs import INVALID_TOKEN, INVALID_CREDENTIALS
from api.queries import email_exists
from api.resource.base_verify import BaseVerifyResource
from api.utils.hashers import verify_password
from api.utils.validators import check_required_fields
from config import TOKEN_EXP_SECONDS, VERIFY_EMAIL_REDIRECT_URL
from dao.controllers import UserController


class VerifyEmailResource(BaseVerifyResource):
    VERIFY_REDIRECT_URL = VERIFY_EMAIL_REDIRECT_URL

    def __init__(self, auth_middleware, **kwargs):
        super().__init__(**kwargs)
        self._auth_middleware = auth_middleware

    def on_post(self, req, resp, email):
        if not email_exists(email=email):
            raise falcon.HTTPNotFound()

        self._auth_middleware().process_request(req=req, resp=resp)
        user_id = req.context.get('user_id')
        if not user_id:
            raise falcon.HTTPUnauthorized(description=INVALID_TOKEN)

        data = req.media
        not_found_fields = check_required_fields(data, ('password',))
        if not_found_fields:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.context.result = not_found_fields
            return

        with UserController() as Users:
            user = Users.get_by_id(user_id)
            if not verify_password(plain_password=data["password"], hashed_password=user.password):
                raise falcon.HTTPBadRequest(
                    description=INVALID_CREDENTIALS
                )

            user.email_verified = True
            Users.session.commit()

        resp.status = falcon.HTTP_OK
        resp.set_cookie(
            'user_email_verified',
            "1",
            max_age=TOKEN_EXP_SECONDS,
            path=urlparse(req.url).netloc
        )
