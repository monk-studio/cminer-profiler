from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class Warehouse(Base):
    __tablename__ = 'warehouse'
    id = Column(String, primary_key=True, autoincrement=True)
    size = Column(Integer)
