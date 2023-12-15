from contextlib import contextmanager

import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import PRIMARY_DB_URI, REDIS_URI, USE_TEST, TEST_DB_URI, REDIS_TEST_URI
from dao.models import User


def get_engine():
    if USE_TEST:
        return create_engine(TEST_DB_URI)
    return create_engine(PRIMARY_DB_URI)


engine = get_engine()


def get_session_factory():
    Session = sessionmaker()
    Session.configure(binds={User: engine})
    return Session


@contextmanager
def redis_scope(db: int = 0):
    assert db < 16
    redis_client = redis.from_url(REDIS_TEST_URI if USE_TEST else REDIS_URI + f'/{db}')
    try:
        yield redis_client
    except Exception as e:
        raise e
    finally:
        redis_client.close()
