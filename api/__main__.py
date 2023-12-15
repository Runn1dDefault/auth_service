from wsgiref import simple_server

from api import app
from dao.operations import initialize_models


if __name__ == '__main__':
    initialize_models()
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
