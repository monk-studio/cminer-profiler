import pickle
from pathlib import Path

from aenum import Enum, MultiValueEnum

from ._logger import logger
from .consts import (
    SOURCE_I18N, SOURCE_TOOLS, SOURCE_RECIPES, SOURCE_MINES
)
from .consts import TOOL_WOODEN_PICKAXE


def _load(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


class System:
    i18n = _load(SOURCE_I18N)
    mines = _load(SOURCE_MINES)
    tools = _load(SOURCE_TOOLS)
    recipes = _load(SOURCE_RECIPES)


class Archive:
    root = Path.home() / '.cminer/archives'
    location = None
    warehouse = dict()
    bag = dict()

    def __init__(self, name):
        self.name = name
        if not self.load():
            self.location = Location.camp
            self.warehouse = {System.tools[TOOL_WOODEN_PICKAXE]: 10}

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
                return True
        except FileNotFoundError:
            return False

    @staticmethod
    def list():
        Archive.root.mkdir(parents=True, exist_ok=True)
        return [Path(f).name.split('.')[0]
                for f in Archive.root.glob('*.pkl')]


class Action(MultiValueEnum):
    buy_wood = 1, '买木头'
    make_pickaxe = 2, '做稿子'
    go_mining = 3, '去挖矿'
    mine = 4, '往下挖'
    go_camp = 5, '回到营地'
    show_warehouse = 6, '显示仓库'
    show_bag = 7, '显示背包'


class Location(Enum):
    camp = 1
    mine = 2


class MiningProgress:
    def __init__(self, level=1, items=None):
        self.level = level
        self.items = items or dict()


class Game:
    def __init__(self, archive):
        self.archive = archive

    def echo(self):
        if self.archive.location == Location.camp:
            cmds = [
                Action.show_warehouse,
                Action.buy_wood, Action.make_pickaxe, Action.go_mining,
            ]
        elif self.archive.location == Location.mine:
            cmds = [
                Action.show_bag,
                Action.mine, Action.go_camp
            ]
        else:
            return dict()
        cmds = [(idx, x) for idx, x in enumerate(cmds)]
        cmds_text = '\n'.join([f'{idx}: {x.values[1]}' for idx, x in cmds])
        logger.info(cmds_text)
        return dict(cmds)

    def execute(self, action):
        if action == Action.show_warehouse:
            # todo: interactive ui for bag.
            items = [f'{System.i18n[k.uid]}: {v}個'
                     for k, v in self.archive.warehouse.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.show_bag:
            items = [f'{System.i18n[k.uid]}: {v}個'
                     for k, v in self.archive.bag.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.go_mining:
            # todo: bag should has limited space
            self.archive.bag = self.archive.warehouse
            self.archive.warehouse = dict()
            self.archive.location = Location.mine
        if action == Action.go_camp:
            self.archive.warehouse = self.archive.bag
            self.archive.bag = dict()
            self.archive.location = Location.camp
        if action == Action.mine:
            # todo: use best axe to mine to next level
            pass
        self.archive.save()
