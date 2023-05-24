from app.internal.model.user import UserModel


class UserRepository:
    def __init__(self):
        self.curr_id = 2
        self.inner_db = {}

    def get_user_by_id(self, id: int) -> UserModel:
        return self.inner_db[id]

    def get_user_by_username(self, username: str) -> UserModel:
        return [e for e in self.inner_db.values() if e.username == username][0]

    def add_user(self, user: UserModel) -> UserModel:
        self.inner_db[self.curr_id] = user
        return user
