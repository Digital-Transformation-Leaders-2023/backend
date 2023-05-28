from app.internal.repository import engine
from sqlalchemy.orm import Session

from app.pkg.database.models import MKBTable

database_name = "reports"


class MkbRepository:
    def __init__(self):
        self.__engine = engine
        self.__session = Session(self.__engine)

    def __del__(self):
        self.__session.close()

    def GetMkbWithServicesCodes(self, mkb: str):
        result = self.__session.query(MKBTable).filter_by(code=mkb).first()
        return result

