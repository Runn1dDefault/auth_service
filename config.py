from pathlib import Path

from decouple import config


USE_TEST = True
TEST_DB_URI = "sqlite:///:memory:"

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'static'
TEMPLATES_DIR = STATIC_DIR / 'templates'

PRIMARY_DB_URI = config("PRIMARY_DB_URI")
REDIS_URI = config("REDIS_URI")
REDIS_TEST_URI = config("REDIS_TEST_URI")

SECRET_KEY = "foo"
VERIFY_SECRET_KEY = "foo1"

TOKEN_HASH_ALGORITHM = 'HS256'
TOKEN_AUTH_HEADER = 'Bearer'
ALLOWED_EMAIL_DOMAINS = ('gmail.com', 'mail.ru')
PASSWORD_MIN_LEN = 10
TOKEN_EXP_SECONDS = 43200

TOKEN_ENCODE_FIELDS_MAP = {
    "user_id": "id",
    "user_email": "email",
    "user_role": "role",
    "user_email_verified": "email_verified"
}


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587  # SMTP server port
SMTP_EMAIL = 'kaimono.sup@gmail.com'
SMTP_PASSWORD = 'qpxursoeoyhqtrnf'
VERIFICATION_TTL = 720
VERIFICATION_CONTEXT = {
    "subject": "Kaimono",
    "warning_text": "if it wasn't you. Please ignore this message and do not share "
                    "the code with anyone."
}
REDIRECT_UPDATE_PWD_URL = "http://localhost:3000/update-password/%s"
VERIFY_EMAIL_REDIRECT_URL = "http://localhost:3000/login"
