import pickle
import os
from pathlib import Path
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
        pass
        # mine_list = list(self.mines.values())

    def compose(self, materials):
        pass


class Archive:
    root = Path.home() / '.cminer/archives'

    def __init__(self, name):
        self.name = name

    @property
    def _path(self):
        return Archive.root / (self.name + '.pkl')

    def save(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def list():
        Archive.root.mkdir(parents=True, exist_ok=True)
        return [Path(f).name.split('.')[0]
                for f in Archive.root.glob('*.pkl')]


class Game:
    def __init__(self, archive):
        self.system = System()
        self.archive = archive

    def execute(self, cmd):
        print('executing {}'.format(cmd))
        self.archive.save()
