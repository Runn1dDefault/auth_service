import falcon

from api.middleware.authentication import AuthMiddleware
from api.utils.tokens import decode_verify_token


class VerifyEmailAuthMiddleware(AuthMiddleware):
    AUTH_HEADER = "X-VERIFY-TOKEN"

    @staticmethod
    def token_decoder(token):
        return decode_verify_token(token)

    def _get_auth_header_value(self, req):
        value = super()._get_auth_header_value(req=req)
        if not value:
            raise falcon.HTTPUnauthorized()
        return value
