from sqlalchemy import Integer, String, Column

from app.pkg.database import Base


class ServiceCodeTable(Base):
    __tablename__ = 'service_code_table'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)
