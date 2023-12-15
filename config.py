from pathlib import Path

from decouple import config


SECRET_KEY = config("SECRET_KEY")
VERIFY_SECRET_KEY = config("VERIFY_SECRET_KEY")

USE_TEST = config("USE_TEST", cast=bool)

# Dirs
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'static'
TEMPLATES_DIR = STATIC_DIR / 'templates'

# Postgres urls
PRIMARY_DB_URI = config("PRIMARY_DB_URI")
TEST_DB_URI = config("TEST_DB_URI")

# Redis urls
REDIS_URI = config("REDIS_URI")
REDIS_TEST_URI = config("REDIS_TEST_URI")


# Validators conf
PASSWORD_MIN_LEN = 10
ALLOWED_EMAIL_DOMAINS = ('gmail.com', 'mail.ru')


# Auth Token conf
TOKEN_HASH_ALGORITHM = 'HS256'
TOKEN_AUTH_HEADER = 'Bearer'
TOKEN_EXP_SECONDS = 43200
TOKEN_ENCODE_FIELDS_MAP = {
    "user_id": "id",
    "user_email": "email",
    "user_role": "role",
    "user_email_verified": "email_verified"
}

# Mailing
SMTP_SERVER = config("SMTP_SERVER")
SMTP_PORT = config("SMTP_PORT", cast=int)  # SMTP server port
SMTP_EMAIL = config("SMTP_EMAIL")
SMTP_PASSWORD = config("SMTP_PASSWORD")
VERIFICATION_TTL = 720
VERIFICATION_CONTEXT = {
    "subject": "Kaimono",
    "warning_text": "if it wasn't you. Please ignore this message and do not share "
                    "the code with anyone."
}
VERIFY_EMAIL_REDIRECT_URL = "http://localhost:3000/login"
REDIRECT_UPDATE_PWD_URL = "http://localhost:3000/update-password/%s"
