import falcon

from api.utils.hashers import get_hashed_password
from api.queries import create_client
from api.utils.validators import check_required_fields, PasswordValidator, EmailValidator


class RegisterResource:
    REQUIRED_FIELDS = ('email', 'password', 'full_name')

    def on_post(self, req, resp):
        data = req.get_media()

        not_found_fields = check_required_fields(data, self.REQUIRED_FIELDS)
        if not_found_fields:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = not_found_fields
            return

        email = data['email'] or ""
        validator = EmailValidator(email=email)
        email_error_msgs = validator.validate()
        if email_error_msgs:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = {"email": email_error_msgs}
            return

        password = data['password']
        pwd_validator = PasswordValidator(password)
        pwd_error_msgs = pwd_validator.validate()
        if pwd_error_msgs:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.media = {"password": email_error_msgs}
            return

        token = create_client(
            email=email,
            password=get_hashed_password(password),
            full_name=data['full_name']
        )
        resp.status = falcon.HTTP_OK
        resp.media = {'token': token}
