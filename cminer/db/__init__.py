from .base import Base
from .player import Player, PlayerPresets


def init_db():
    Base.metadata.create_all()
