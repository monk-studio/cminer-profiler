from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class Item(Base):
    __tablename__ = 'item_presets'
    id = Column(String, primary_key=True)
    volume = Column(Float)
    type = Column(String)
    # food(补充体力）, tool（硬度，耐久，属性）,material（硬度，属性）
    data = Column(String)
    buy_price = Column(Integer)
    sell_price = Column(Integer)
