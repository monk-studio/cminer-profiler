from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


class Player(Base):
    __tablename__ = 'player'
    id = Column(Integer, primary_key=True, autoincrement=True)
    # 屬性
    level = Column(Integer)
    points = Column(Integer)
    hp = Column(Integer)
    crit_damage = Column(Float)
    crit_prob = Column(Float)
    lucky_prob = Column(Float)
    # 狀態 JSON String <location, hp_now..>
    status = Column(String)
    # 累計的數據
    highest_mine_level = Column(Integer)
    unlock_mine_level = Column(Integer)
    cumulative_compose_times = Column(Integer)
    cumulated_coin = Column(Integer)


class PlayerPresets(Base):
    __tablename__ = 'player_presets'
    id = Column(Integer, primary_key=True, autoincrement=True)
    hp_init = Column(Integer)
    hp_growth = Column(Integer)
    crit_damage_init = Column(Float)
    crit_damage_growth = Column(Float)
    crit_prob_init = Column(Float)
    crit_prob_growth = Column(Float)
    lucky_prob_init = Column(Float)
    lucky_prob_growth = Column(Float)
    points_per_level = Column(Integer)
