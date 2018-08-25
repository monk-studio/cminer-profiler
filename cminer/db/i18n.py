from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class I18n(Base):
    __tablename__ = 'i18n'
    id = Column(String, primary_key=True)
    name = Column(String)
