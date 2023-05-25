from app.internal.model.user import UserModel
from app.internal.repository import engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.pkg.database.models import User


class UserRepository:
    # TODO: ...
    def __init__(self):
        self.__engine = engine

    def get_user_by_id(self, id: int):
        with Session(self.__engine) as session:
            result = session.query(User).filter_by(id=id).first()
            return result

    def get_user_by_username(self, username: str):
        with Session(self.__engine) as session:
            result = session.query(User).filter_by(name=username).first()
            return result

    def add_user(self, user: UserModel) -> User:
        db_user = User(email=user.email,
                       name=user.username,
                       password_hash=user.password_hash)
        with Session(self.__engine) as session:
            session.add(db_user)
            session.commit()
        return db_user
