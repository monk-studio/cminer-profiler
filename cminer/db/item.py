from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class Item(Base):
    __tablename__ = 'item_presets'
    id = Column(String, primary_key=True, autoincrement=True)
