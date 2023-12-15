from falcon.errors import HTTPUnauthorized

from api.error_msgs import INVALID_TOKEN, INVALID_AUTH_HEADER
from config import TOKEN_AUTH_HEADER
from api.utils.tokens import decode_token


class AuthMiddleware:
    AUTH_HEADER = "Authorization"

    @staticmethod
    def token_decoder(token):
        return decode_token(token)

    def _get_auth_header_value(self, req):
        return req.get_header(self.AUTH_HEADER)

    @staticmethod
    def _get_token(auth_value: str):
        try:
            header, token = auth_value.split(' ')
        except ValueError:
            raise HTTPUnauthorized(description=INVALID_TOKEN)

        if header != TOKEN_AUTH_HEADER:
            raise HTTPUnauthorized(description=INVALID_AUTH_HEADER)

        return token

    def process_request(self, req, resp):
        auth_header_value = self._get_auth_header_value(req)
        if not auth_header_value:
            return

        token = self._get_token(auth_value=auth_header_value)
        try:
            decoded_data = self.token_decoder(token)
        except ValueError as e:
            raise HTTPUnauthorized(description=str(e))

        req.context.update(decoded_data)
