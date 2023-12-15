from dao.connections import engine
from dao.models import User


def initialize_models():
    User.metadata.create_all(engine)
