import bcrypt


def get_hashed_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: bytes):
    return bcrypt.checkpw(plain_password.encode(), hashed_password)
