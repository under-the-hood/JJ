from passlib.context import CryptContext


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def hashing_password(password: str):
    return pwd_context.hash(password)