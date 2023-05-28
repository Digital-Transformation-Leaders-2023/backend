from app.internal.repository import mongo_db_client, engine

database_name = "reports"


class MkbRepository:
    def __init__(self):
        self.__engine = engine

    def GetMkbWithServicesCodes(self, mkb):
        ...
