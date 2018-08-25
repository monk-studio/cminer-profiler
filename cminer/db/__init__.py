from .base import Base, session_maker, auto_commit
from .consts import PLAYER_PRESETS, PLAYER_INIT
from .player import Player, PlayerPresets
from .i18n import I18n
from .item import Item
import json


from cminer.system import System


def init_db():
    Base.metadata.create_all()
    session = session_maker()
    with auto_commit(session):
        session.add(PLAYER_PRESETS)
        session.add(PLAYER_INIT)
        for key, value in System._i18n.items():
            item_ = I18n(
                id=key,
                name=value,
            )
            session.add(item_)
        for x in System.tools:
            print(x)
            # data = {
            #     "type": type_,
            #     "hardness": hardness,
            #     "endurance": endurance,
            #     "base_damage": base_damage,
            # }
            # tool = Item(
            #     id=uid, volume=volume_,
            #     type="tool",
            #     data=json.dumps(data),
            #     buy_price=0,
            #     sell_price=0,
            # )
            # session.add(tool)
        session.commit()


def player_presets():
    session = session_maker()
    return session.query(PlayerPresets)[0]


def player():
    session = session_maker()
    return session.query(Player)[0]
