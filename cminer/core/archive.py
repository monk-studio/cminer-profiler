import pickle
from collections import Counter
from uuid import uuid4
from pathlib import Path
from enum import Enum
from copy import deepcopy
from cminer.logger import logger
from cminer.consts import TOOL_WOODEN_PICKAXE, COIN
from cminer.models import Tool, TOOL_TYPE_AXE
from cminer.system import System


class Location(Enum):
    camp = 1
    mine = 2


class ItemSet:
    """data: Dict(str, Item)"""
    def __init__(self, data):
        self.data = data

    def add(self, item):
        self.data[uuid4().hex] = deepcopy(item)

    def remove(self, uid):
        del self.data[uid]

    def grouped(self):
        return Counter([x.model.uid for x in self.data.values()])

    def axes(self):
        axes = filter(
            lambda x: type(x[1]) == Tool and x[1].type == TOOL_TYPE_AXE,
            self.data.items())
        axes = sorted(axes, key=lambda x: x[1].status.endurance, reverse=True)
        return list(axes)

    def clear(self):
        self.data = dict()

    def can_compose(self, recipe):
        distribution = self.grouped()
        for key, amount in recipe.inputs:
            if (distribution.get(key) or 0) < amount:
                return False
        return True

    def compose(self, recipe):
        to_remove = list()
        for key, amount in recipe.inputs:
            items = filter(lambda x: x[1].model.uid == key, self.data.items())
            to_remove += [x[0] for x in items][:amount]
        for i in to_remove:
            self.remove(i)
        for key, amount in recipe.outputs:
            for _ in range(amount):
                self.add(System.item(key))
        input_text = ', '.join([f'{amount}個{System.i18n(key)}'
                                for key, amount in recipe.inputs])
        output_text = ', '.join([f'{amount}個{System.i18n(key)}'
                                for key, amount in recipe.outputs])
        echo = f'用 {input_text}. 合成了 {output_text}'
        logger.info(echo)


class Warehouse(ItemSet):
    def __init__(self, data):
        super().__init__(data)
        self.coin = 0

    def __repr__(self):
        items = [f'{System.i18n(k)}: {v}個'
                 for k, v in self.grouped().items()]
        items = ', '.join(items + [f'金幣: {self.coin}枚'])
        return items


class Bag(Warehouse):
    def clear(self):
        super().clear()
        self.coin = 0


class MineProgress:
    def __init__(self, level=1):
        self.level = level
        self.mine = None
        self.dig_deeper(is_initial=True)

    def dig_by_axe(self, axe):
        axe_broken = False
        coin = 0
        items = dict()

        damage = axe.damage_on_hardness(self.mine.model.hardness)
        self.mine.status.hp_now -= damage
        logger.info(f'用 {axe} 造成了 {damage} 点伤害')
        axe.status.endurance -= 1

        if axe.status.endurance <= 0:
            axe_broken = True
            logger.info(f'{axe} 坏了')
        else:
            logger.info(f'{axe} 耐久 '
                        f'{axe.status.endurance}/{axe.model.endurance}')
        if self.mine.status.hp_now <= 0:
            _awards = self.mine.award
            for k, v in _awards.items():
                if k == COIN:
                    coin = v
                else:
                    items[System.item(k)] = v
            awards_text = [f'{v}个 {k}'
                           for k, v in items.items()]
            awards_text = '\n'.join(['獲得: '] + awards_text)
            awards_text += f'\n{coin}枚 金幣'
            logger.info(awards_text)
            self.dig_deeper()
        else:
            logger.info(f'{self.mine}剩餘血量 '
                        f'{self.mine.status.hp_now}/{self.mine.status.hp}')
        return dict(
            axe_broken=axe_broken,
            awards=dict(
                coin=coin,
                items=items,
            )
        )

    def dig_deeper(self, is_initial=False):
        if not is_initial:
            self.level += 1
        self.mine = System.mine_at_level(self.level)
        logger.info(f'到达{self.level}层, 发现 {self.mine}, '
                    f'血量: {self.mine.status.hp}')


class Archive:
    root = Path.home() / '.cminer/archives'
    location = None
    mine_progress = None

    def __init__(self, name):
        self.name = name
        self.bag = Bag({})
        self.warehouse = Warehouse({})
        if not self.load():
            self.location = Location.camp
            for _ in range(10):
                item = System.item(TOOL_WOODEN_PICKAXE)
                self.warehouse.add(item)

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
