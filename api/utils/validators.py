import re
from abc import ABC, abstractmethod
from typing import Iterable

from api.error_msgs import REQUIRED_FIELD_MISSING, PWD_ERROR_MSGS, EMAIL_ERROR_MSGS
from api.queries import email_exists
from config import ALLOWED_EMAIL_DOMAINS, PASSWORD_MIN_LEN


def check_required_fields(data, fields: Iterable[str]) -> dict[str, str]:
    return {field: REQUIRED_FIELD_MISSING for field in fields if field not in data or not data.get(field)}


class BaseValidator(ABC):
    @abstractmethod
    def validate(self) -> list[str]:
        pass


class EmailValidator(BaseValidator):
    EMAIL_REGEX = r'^[\w.-]+@\w+[\w.-]+\w+\.\w+$'

    def __init__(self, email: str):
        self._email = email

    @property
    def is_email_string(self) -> bool:
        return bool(re.match(r'^[\w.-]+@\w+[\w.-]+\w+\.\w+$', self._email))

    @property
    def has_supported_domain(self):
        try:
            _, domain = self._email.split('@')
        except ValueError:
            return False
        return domain in ALLOWED_EMAIL_DOMAINS

    @property
    def is_exists(self):
        return email_exists(self._email)

    def validate(self) -> list[str]:
        msgs = []
        if not self.is_email_string:
            msgs.append(EMAIL_ERROR_MSGS["wrong_chars"])
        if not self.has_supported_domain:
            msgs.append(EMAIL_ERROR_MSGS["unsupported_domain"])
        if self.is_exists:
            msgs.append(EMAIL_ERROR_MSGS["already_exists"])
        return msgs


class PasswordValidator(BaseValidator):
    SPECIAL_CHAR = r'!@#$%^&*()_+{}[\]:;<>,.?~\\'

    def __init__(self, password: str, min_length: int = PASSWORD_MIN_LEN):
        self.password = password
        self.min_length = min_length

    @property
    def valid_length(self):
        return len(self.password) >= self.min_length

    @property
    def has_uppercase(self):
        return bool(re.search(r'[A-Z]', self.password))

    @property
    def has_lowercase(self):
        return bool(re.search(r'[a-z]', self.password))

    @property
    def has_digit(self):
        return bool(re.search(r'\d', self.password))

    @property
    def has_special_char(self):
        return bool(re.search(f'[{self.SPECIAL_CHAR}]', self.password))

    def validate(self):
        msgs = []
        if not self.valid_length:
            msgs.append(PWD_ERROR_MSGS['invalid_length'] % self.min_length)
        if not self.has_lowercase or not self.has_uppercase:
            msgs.append(PWD_ERROR_MSGS['has_no_different_case'])
        if not self.has_digit:
            msgs.append(PWD_ERROR_MSGS['has_no_digit'])
        if not self.has_special_char:
            msgs.append(PWD_ERROR_MSGS['has_no_special_char'] % self.SPECIAL_CHAR)
        return msgs
