import pickle
from enum import Enum
from ._logger import logger
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
    location = None

    def __init__(self, name):
        self.name = name
        self.load()
        if not self.location:
            self.location = Location.camp

    @property
    def _path(self):
        return self.root / (self.name + '.pkl')

    def save(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        try:
            with open(self._path, 'rb') as f:
                data = pickle.load(f)
                for k, v in data.__dict__.items():
                    setattr(self, k, v)
        except FileNotFoundError:
            return

    @staticmethod
    def list():
        Archive.root.mkdir(parents=True, exist_ok=True)
        return [Path(f).name.split('.')[0]
                for f in Archive.root.glob('*.pkl')]


class Action(Enum):
    buy_wood = 1
    make_pickaxe = 2
    go_mining = 3
    mine = 4
    go_camp = 5


class Location(Enum):
    camp = 1
    mine = 2


class Game:
    def __init__(self, archive):
        self.system = System()
        self.archive = archive

    def echo(self):
        logger.info(f'>> {self.archive.name}')
        if self.archive.location == Location.camp:
            cmds = [
                Action.buy_wood, Action.make_pickaxe, Action.go_mining
            ]
        else:
            cmds = [
                Action.mine, Action.go_camp
            ]
        cmds = '\n'.join([f'{x.value}: {x.name}' for x in cmds])
        logger.info('Now you are in the camp, next move:')
        logger.info(cmds)

    def execute(self, cmd):
        action = Action(int(cmd))
        logger.info(f'Decide to {action.name}')
        if action == Action.go_mining:
            self.archive.location = Location.mine
        if action == Action.go_camp:
            self.archive.location = Location.camp
        self.archive.save()
        self.echo()
