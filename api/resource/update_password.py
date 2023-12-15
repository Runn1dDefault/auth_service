import falcon

from api.error_msgs import INVALID_TOKEN, TRY_ANOTHER_TIME
from api.queries import update_user_pwd
from api.utils.validators import check_required_fields, PasswordValidator


class UpdatePasswordResource:
    def __init__(self, auth_middleware):
        self._auth_middleware = auth_middleware

    def on_post(self, req, resp):
        self._auth_middleware().process_request(req=req, resp=resp)
        user_id = req.context.get('user_id')
        if not user_id:
            raise falcon.HTTPUnauthorized(description=INVALID_TOKEN)

        data = req.media
        not_found_fields = check_required_fields(data, ('password',))
        if not_found_fields:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = not_found_fields
            return

        password = data['password']
        error_messages = PasswordValidator(password).validate()
        if error_messages:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = {'password': error_messages}
            return

        pwd_updated = update_user_pwd(user_id, password)
        if not pwd_updated:
            raise falcon.HTTPInternalServerError(description=TRY_ANOTHER_TIME)

        resp.status = falcon.HTTP_OK
