from sqlalchemy import Column
from sqlalchemy import Integer, Float, String

from .base import Base


# (mine_unlock_costs, bag_unlock_costs, recipes, coin_factor, coins_to_upgrade)
class Utilities(Base):
    __tablename__ = 'utilities'
    id = Column(String, primary_key=True)
    data = Column(String)
