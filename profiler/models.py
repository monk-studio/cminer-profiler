import math
import random
from collections import namedtuple
from .consts import COIN


Food = namedtuple('Level', ['name', 'effect'])
Material = namedtuple('Material', ['sdf'])


class Mine(object):
    uid = None
    name = None
    probs = None
    # [(MATERIAL_IRON, 2, 0.4), ...], <= [(id, num, prob)]
    item_drop_probs = None
    hp_base = None
    coin_factor = None

    def __init__(self, uid, name, probs, item_drop_probs,
                 hp_base, coin_factor):
        self.uid = uid
        self.name = name
        self.probs = probs
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
        return self.uid + ' ' + self.name
