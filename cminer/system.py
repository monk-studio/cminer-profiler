import pickle
import random

from cminer.consts import (
    SOURCE_I18N, SOURCE_TOOLS, SOURCE_MATERIALS, SOURCE_RECIPES, SOURCE_MINES,
    SOURCE_PLAYER, SOURCE_FOOD, SOURCE_UTILITY
)


def _load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class System:
    _i18n = _load(SOURCE_I18N)
    mines = _load(SOURCE_MINES)
    tools = _load(SOURCE_TOOLS)
    materials = _load(SOURCE_MATERIALS)
    recipes = _load(SOURCE_RECIPES)
    player = _load(SOURCE_PLAYER)
    foods = _load(SOURCE_FOOD)
    utility = _load(SOURCE_UTILITY)

    @classmethod
    def mine_at_level(cls, level, lucky):
        mines = list(cls.mines.values())
        return random.choices(
            mines,
            [x.prob_at_level(level) for x in mines],
            k=1,
        )[0].new(level, lucky)

    @classmethod
    def i18n(cls, uid):
        return cls._i18n.get(uid) or uid

    @classmethod
    def item(cls, uid):
        rv = cls.tools.get(uid) or cls.materials.get(uid) or cls.foods.get(uid)
        return rv.new()
