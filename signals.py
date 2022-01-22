# coding=utf-8

from sqlalchemy import Column, String, Date, Integer, Numeric

from sql_base import Base


class Signal(Base):
    __tablename__ = 'signal'

    id = Column(Integer, primary_key=True)
    type = Column(String(16), primary_key=True)
    item = Column(String(16), primary_key=True)

    def __init__(self, type, item):
        self.name = name
        self.date_of_birth = date_of_birth
        self.height = height
        self.weight = weight
