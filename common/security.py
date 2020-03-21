import bcrypt


def hashing_password(raw_password: str) -> str:
    return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()


def check_password(raw_password: str, hashed_password) -> bool:
    return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())
