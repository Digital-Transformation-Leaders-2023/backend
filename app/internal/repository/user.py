from app.internal.model.user import User


class UserRepository:
    def __init__(self):
        self.curr_id = 2
        self.inner_db = {
            1: {
                "username": "mayatinalex",
                "name": "Маятин Алексанр",
                "password_hash": "string",
                "email": "mayatin@gmail.com"
            }
        }

    def get_user_by_id(self, id: int):
        return self.inner_db[id]

    def get_user_by_username(self, username: str):
        return [e for e in self.inner_db.values() if e["username"] == username][0]

    def add_user(self, user: User):
        self.inner_db[self.curr_id] = user
