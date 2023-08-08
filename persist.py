from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Apartment(Base):
    __tablename__ = 'apartments'

    id = Column(Integer, primary_key=True)
    current_date = Column(Date)
    identifier_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
