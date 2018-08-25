from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class RecipeD(Base):
    __tablename__ = 'recipe'
    id = Column(String, primary_key=True)
    inputs = Column(String)
    outputs = Column(String)
