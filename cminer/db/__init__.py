from .base import Base, session_maker, auto_commit
from .consts import PLAYER_PRESETS, PLAYER_INIT
from .player import Player, PlayerPresets


def init_db():
    Base.metadata.create_all()
    session = session_maker()
    with auto_commit(session):
        session.add(PLAYER_PRESETS)
        session.add(PLAYER_INIT)
        session.commit()


def player_presets():
    session = session_maker()
    return session.query(PlayerPresets)[0]


def player():
    session = session_maker()
    return session.query(Player)[0]
