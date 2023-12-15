from logging import getLogger
from typing import Any, Iterable

from sqlalchemy import delete, update, exists
from sqlalchemy.orm import load_only

from .connections import get_session_factory
from .models import Base, User


class BaseController:
    model = None

    def __init__(self, session=None):
        assert issubclass(self.model, Base), "%s it must be inherited from %s" % (self.model.__name__, Base.__name__)
        self.logger = getLogger(self.__class__.__name__)
        self.session = get_session_factory()() if not session else session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.session.close()

    def _get_model_fields(self, fields: Iterable[str]):
        return [getattr(self.model, field) for field in fields or []]

    def get_all(self, fields: Iterable[str] = None) -> list:
        query = self.session.query(self.model)
        if fields:
            model_fields = self._get_model_fields(fields)
            query = query.options(load_only(*model_fields))
        return query.all()

    def _get(self, by_field: str, value: Any, fields: Iterable[str] = None):
        query = self.session.query(self.model).filter(getattr(self.model, by_field) == value)
        if fields:
            model_fields = self._get_model_fields(fields)
            query = query.options(load_only(*model_fields))
        return query.first()

    def get_by_id(self, _id, fields: Iterable[str] = None):
        return self._get("id", _id, fields)

    def delete(self, _id) -> None:
        try:
            self.session.execute(
                delete(self.model)
                .where(self.model.id == _id)
            )
            self.session.commit()
        except Exception as e:
            self.logger.exception(e)
            self.session.rollback()

    def create(self, entity):
        try:
            self.session.add(entity)
            self.session.commit()
            return True
        except Exception as e:
            self.logger.exception(e)
            self.session.rollback()
            return False

    def update(self, _id, values: dict[str, Any]) -> bool:
        try:
            values = {getattr(self.model, key): value for key, value in values.items()}
            print(values)
            self.session.execute(
                update(self.model)
                .where(self.model.id == _id)
                .values(values)
            )
            self.session.commit()
            return True
        except Exception as e:
            self.logger.exception(e)
            self.session.rollback()
            return False

    def exists(self, _id) -> bool:
        return self.session.query(exists().where(self.model.id == _id)).scalar()


class UserController(BaseController):
    model = User

    def get_user_by_email(self, email: str, fields: Iterable[str] = None) -> User | None:
        return self._get('email', email, fields)

    def email_exists(self, email: str) -> bool:
        return self.session.query(exists().where(self.model.email == email)).scalar()
