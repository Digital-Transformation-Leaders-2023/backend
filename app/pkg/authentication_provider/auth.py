from app.pkg.authentication_provider import SECRET_KEY, ALGORITHM
from passlib.context import CryptContext


class AuthProvider:
    def __init__(self):
        self.__secret_key = SECRET_KEY
        self.__algorithm = ALGORITHM
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password: str, hash: str) -> bool:
        return self.pwd_context.verify(plain_password, hash)

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
