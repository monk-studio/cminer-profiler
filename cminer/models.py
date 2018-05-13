import math
import random
from collections import namedtuple
from .consts import COIN


Food = namedtuple('Level', ['name', 'hp'])
Material = namedtuple('Material', ['sdf'])


class Tool:
    TYPE_AXE = 0
    TYPE_BOMB = 1
    TYPE_OTHERS = 9

    def __init__(self, uid, type_, hardness, endurance, base_damage):
        self.uid = uid
        self.type = type_
        self.hardness = hardness
        self.endurance = endurance
        self.base_damage = base_damage

    def damage_on_hardness(self, hardness):
        offset = hardness - self.hardness
        rv = self.base_damage
        if offset == 1:
            rv *= 0.7
        elif offset >= 2:
            rv *= 0.4
        elif offset == -1:
            rv *= 1.2
        elif offset <= -2:
            rv *= 1.5
        return int(rv)

    def __repr__(self):
        return self.uid


class Recipe:
    def __init__(self, inputs, outputs):
        # [('MATERIAL_STONE', 3), ('MATERIAL_WOOD', 1)]
        self.inputs = inputs
        # [('TOOL_STONE_PICKAXE', 1)]
        self.outputs = outputs

    def __repr__(self):
        return repr(self.inputs) + ': ' + repr(self.outputs)


class Mine:
    def __init__(self, uid, probs, item_drop_probs, hardness,
                 hp_base, coin_factor):
        self.uid = uid
        self.hardness = hardness
        self.probs = probs
        # [(MATERIAL_IRON, 2, 0.4), ...], <= [(id, num, prob)]
        self.item_drop_probs = item_drop_probs
        self.hp_base = hp_base
        self.coin_factor = coin_factor

    def prob_at_level(self, level):
        pos = math.floor(level / 100)
        return self.probs[min(pos, len(self.coin_factor) - 1)]

    def hp_at_level(self, level):
        return 1.05 ** (level / 10) * self.hp_base

    def coin_at_level(self, level):
        pos = math.floor(level / 100)
        factor = self.coin_factor[min(pos, len(self.coin_factor) - 1)]
        rv = factor * self.hp_at_level(level)
        return int(rv)

    def drops_at_level(self, level):
        rv = dict()
        for item in self.item_drop_probs:
            if random.random() > item[2]:
                continue
            if rv.get(item[0]):
                rv[item[0]] += item[1]
            else:
                rv[item[0]] = item[1]
        coins = self.coin_at_level(level=level)
        # 40% probability drop 10% more coin
        if random.random() < 0.4:
            coins = int(coins * 1.1)
        rv[COIN] = coins
        return rv

    def __repr__(self):
        return self.uid