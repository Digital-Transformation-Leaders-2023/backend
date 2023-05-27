from sqlalchemy import Column, Integer, String

from app.pkg.database import Base


class MKBTable(Base):
    __tablename__ = 'mkb_table'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)