import pickle
from .consts import (
    SOURCE_I18N, SOURCE_TOOLS, SOURCE_RECIPES, SOURCE_MINES
)


def _load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class System:
    def __init__(self):
        self.i18n = _load(SOURCE_I18N)
        self.mines = _load(SOURCE_MINES)
        self.tools = _load(SOURCE_TOOLS)
        self.recipes = _load(SOURCE_RECIPES)

    def mine_at_level(self, level):
        mine_list = list(self.mines.values())
        print(mine_list)

    def compose(self, materials):
        pass


class Archive:
    # todo: connect to pkl.
    def __init__(self):
        pass


class Game:
    def __init__(self, archive):
        self.system = System()
        self.archive = archive

    def start(self):
        pass
