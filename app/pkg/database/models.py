from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.pkg.database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    password_hash = Column(String)


class ServiceCodeTable(Base):
    __tablename__ = 'service_code_table'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)

    courses = relationship("TreatmentCourse", back_populates="service_code")


class MKBTable(Base):
    __tablename__ = 'mkb_table'

    id = Column(Integer, primary_key=True)
    code = Column(String)
    description = Column(String)

    courses = relationship("TreatmentCourse", back_populates="mkb")


class TreatmentCourse(Base):
    __tablename__ = 'treatment_course'

    id = Column(Integer, primary_key=True)

    mkb_id = Column(Integer, ForeignKey('mkb_table.id'))
    mkb = relationship("MKBTable", back_populates="courses")

    service_code_id = Column(Integer, ForeignKey('service_code_table.id'))
    service_code = relationship("ServiceCodeTable", back_populates="courses")

    weight = Column(Float)
