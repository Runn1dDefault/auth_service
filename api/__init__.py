import falcon

from api.middleware import AuthMiddleware, VerifyEmailAuthMiddleware
from api.resource import (
    AuthResource, RegisterResource, UserInfoResource, ForgotPasswordResource, UpdatePasswordResource,
    VerifyEmailResource
)


def create():
    return falcon.App(middleware=[AuthMiddleware()])


app = create()
# user resources
app.add_route('/auth', AuthResource())
app.add_route('/register', RegisterResource())
app.add_route('/me-info', UserInfoResource())
app.add_route('/verify', VerifyEmailResource(auth_middleware=VerifyEmailAuthMiddleware))
app.add_route('/forgot-password', ForgotPasswordResource())
app.add_route('/update-password', UpdatePasswordResource(auth_middleware=VerifyEmailAuthMiddleware))
