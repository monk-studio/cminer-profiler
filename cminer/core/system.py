import random
import pickle
from cminer.consts import (
    SOURCE_I18N, SOURCE_TOOLS, SOURCE_RECIPES, SOURCE_MINES
)


def _load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class System:
    i18n = _load(SOURCE_I18N)
    mines = _load(SOURCE_MINES)
    tools = _load(SOURCE_TOOLS)
    recipes = _load(SOURCE_RECIPES)

    @classmethod
    def mine_at_level(cls, level):
        mines = dict([(x.prob_at_level(level), x)
                      for x in cls.mines.values()])
        rand = random.random()
        now = 0
        for prob in mines.keys():
            if now < rand <= now + prob:
                return mines[prob]
            now += prob
            continue
