from api.resource.base_verify import BaseVerifyResource
from config import REDIRECT_UPDATE_PWD_URL


class ForgotPasswordResource(BaseVerifyResource):
    VERIFY_REDIRECT_URL = REDIRECT_UPDATE_PWD_URL
