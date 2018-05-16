import pickle
import random
from pathlib import Path

from aenum import Enum, MultiValueEnum

from ._logger import logger
from .consts import (
    SOURCE_I18N, SOURCE_TOOLS, SOURCE_RECIPES, SOURCE_MINES
)
from .models import Tool
from .consts import TOOL_WOODEN_PICKAXE


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
        mines = dict([(x.prob_at_level(level), x) for x in cls.mines.values()])
        rand = random.random()
        now = 0
        for prob in mines.keys():
            if now < rand <= now + prob:
                return mines[prob]
            now += prob
            continue


class Archive:
    root = Path.home() / '.cminer/archives'
    location = None
    warehouse = dict()
    bag = dict()
    mine_progress = None

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


class MineProgress:
    def __init__(self, level=1):
        self.level = level
        self.mine = None
        self.mine_hp = None
        self.dig_deeper()

    def dig_by_axe(self, axe):
        axe_broken = False
        awards = dict()

        damage = axe.damage_on_hardness(self.mine.hardness)
        self.mine_hp -= damage
        logger.info(f'用 {System.i18n[axe.uid]} 造成了 {damage} 点伤害')
        axe.endurance -= 1
        if axe.endurance <= 0:
            axe_broken = True
            logger.info(f'{System.i18n[axe.uid]} 坏了')
        if self.mine_hp <= 0:
            awards = self.mine.award_at_level(level=self.level)
            awards_text = [f'{System.i18n[k]}: {v}个'
                           for k, v in awards.items()]
            awards_text = '\n'.join(['获得:'] + awards_text)
            logger.info(awards_text)
            self.dig_deeper()
        return dict(
            axe_broken=axe_broken,
            awards=awards
        )

    def dig_deeper(self, is_initial=False):
        if not is_initial:
            self.level += 1
        self.mine = System.mine_at_level(self.level)
        self.mine_hp = self.mine.hp_at_level(self.level)
        logger.info(f'到达{self.level}层, 发现 {System.i18n[self.mine.uid]}, '
                    f'血量: {self.mine_hp}')


class Game:
    def __init__(self, archive):
        self.archive = archive

    @property
    def v(self):
        return self.archive

    def echo(self):
        if self.v.location == Location.camp:
            cmds = [
                Action.show_warehouse,
                Action.buy_wood, Action.make_pickaxe, Action.go_mining,
            ]
        elif self.v.location == Location.mine:
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
                     for k, v in self.v.warehouse.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.show_bag:
            items = [f'{System.i18n[k.uid]}: {v}個'
                     for k, v in self.v.bag.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.go_mining:
            # todo: bag should has limited space
            self.v.bag = self.v.warehouse
            self.v.warehouse = dict()
            self.v.mine_progress = MineProgress()
            self.v.location = Location.mine
        if action == Action.go_camp:
            self.v.warehouse = self.v.bag
            self.v.bag = dict()
            self.v.location = Location.camp
        if action == Action.mine:
            axes = filter(
                lambda x: type(x) == Tool and x.type == Tool.TYPE_AXE,
                self.v.bag.keys())
            axes = list(axes)
            if not axes:
                logger.info('没镐子可以往下挖了')
            else:
                result = self.v.mine_progress.dig_by_axe(axes[0])
                # todo result[axe_broken]
                for item, amount in result['awards'].items():
                    if self.v.bag.get(item):
                        self.v.bag[item] += amount
                    else:
                        self.v.bag[item] = 1
        self.v.save()
