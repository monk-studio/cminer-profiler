from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class Mine(Base):
    __tablename__ = 'mine_presets'
    id = Column(String, primary_key=True)
    hardness = Column(Integer)
    # 生成概率
    probs = Column(String)
    # 材料掉落概率
    item_drop_probs = Column(String)
    hp_base = Column(Integer)
