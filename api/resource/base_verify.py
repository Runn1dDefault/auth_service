import logging
from copy import deepcopy

import falcon

from api.error_msgs import TRY_ANOTHER_TIME, EMAIL_TTL_ERROR
from api.queries import email_exists, verify_token_by_email
from api.utils import verification_cache_key
from api.utils.send_email import send_mail_html
from config import VERIFICATION_TTL, VERIFICATION_CONTEXT
from dao.connections import redis_scope


class BaseVerifyResource:
    VERIFY_REDIRECT_URL = None

    def __init__(self, redis_db: int = 0):
        assert self.VERIFY_REDIRECT_URL
        self._redis_db = redis_db

    def on_get(self, req, resp, email):
        if not email_exists(email):
            raise falcon.HTTPNotFound()

        cache_key = verification_cache_key(email)
        with redis_scope(self._redis_db) as cache:
            ttl_seconds = cache.ttl(cache_key)

        match ttl_seconds:
            case -2:
                token = verify_token_by_email(email)
                if not token:
                    raise falcon.HTTPNotFound()

                context = deepcopy(VERIFICATION_CONTEXT)
                context["url"] = self.VERIFY_REDIRECT_URL % token

                try:
                    # TODO: task
                    send_mail_html(
                        email=email,
                        subject="Verify your email",
                        template_name="verify_email.html",
                        context=context
                    )
                except Exception as e:
                    logging.exception(e)
                    raise falcon.HTTPInternalServerError(description=TRY_ANOTHER_TIME)

                with redis_scope(self._redis_db) as cache:
                    cache.setex(cache_key, VERIFICATION_TTL, "1")

                resp.status = falcon.HTTP_OK
            case -1:
                logging.exception("% Key exists in Redis and has no TTL (it never expires).", req.uri())
                raise falcon.HTTPInternalServerError(description=TRY_ANOTHER_TIME)
            case _:
                raise falcon.HTTPBadRequest(
                    title="error",
                    description=EMAIL_TTL_ERROR % ttl_seconds
                )
