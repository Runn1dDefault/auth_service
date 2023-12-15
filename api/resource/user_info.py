import falcon

from api.error_msgs import MISSING_FIELDS_FOR_UPDATE, TRY_ANOTHER_TIME
from api.queries import get_user_data, update_user_data
from api.utils.validators import EmailValidator


class UserInfoResource:
    UPDATE_FIELDS = ("email", "full_name",)

    @staticmethod
    def on_get(req, resp):
        user_id = req.context.get("user_id")
        if not user_id:
            raise falcon.HTTPUnauthorized()

        user_data = get_user_data(user_id)
        if not user_data:
            raise falcon.HTTPNotFound()

        resp.media = user_data

    @staticmethod
    def on_patch(req, resp):
        user_id = req.context.get("user_id")
        if not user_id:
            raise falcon.HTTPUnauthorized()

        data = req.get_media()

        collected_update_fields = {}
        email = data.get("email")
        full_name = data.get("full_name")

        if email:
            validator = EmailValidator(email=email)
            email_error_msgs = validator.validate()
            if email_error_msgs:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.media = {"email": email_error_msgs}
                return

            collected_update_fields["email"] = email
            # TODO: send verification message to email

        if full_name:
            collected_update_fields["full_name"] = full_name

        if not collected_update_fields:
            raise falcon.HTTPBadRequest(
                title="error",
                description=MISSING_FIELDS_FOR_UPDATE
            )

        if not update_user_data(user_id, collected_update_fields):
            raise falcon.HTTPInternalServerError(description=TRY_ANOTHER_TIME)

        resp.status = falcon.HTTP_OK
        resp.media = get_user_data(user_id)
