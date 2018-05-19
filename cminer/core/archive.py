import pickle
from pathlib import Path
from enum import Enum
from cminer.logger import logger
from cminer.consts import TOOL_WOODEN_PICKAXE
from .system import System


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
