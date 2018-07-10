import math
import random
from cminer.consts import COIN


class MineType:
    def __init__(self, uid, hardness, probs, item_drop_probs,
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
        return self.probs[min(pos, len(self.coin_factor) - 1)] or 0

    def hp_at_level(self, level):
        factor = random.uniform(0.9, 1.1)
        rv = 1.05 ** (level / 10) * self.hp_base * factor
        return int(rv)

    def _coin_at_level(self, level):
        pos = math.floor(level / 100)
        factor = self.coin_factor[min(pos, len(self.coin_factor) - 1)]
        rv = factor * self.hp_at_level(level)
        return int(rv)

    def award_at_level(self, level, lucky):
        rv = dict()
        for item in self.item_drop_probs:
            if random.random() > item[2] + lucky:
                continue
            if rv.get(item[0]):
                rv[item[0]] += item[1]
            else:
                rv[item[0]] = item[1]
        coins = self._coin_at_level(level=level)
        # 40% probability drop 10% more coin
        if random.random() < 0.4 + lucky:
            coins = int(coins * 1.1)
        rv[COIN] = coins
        return rv

    def new(self, level, lucky):
        return Mine(self, level, lucky)


class MineStatus:
    def __init__(self, hp):
        self.hp = hp
        self.hp_now = hp


class Mine:
    def __init__(self, model, level, lucky):
        self.model = model
        self.award = model.award_at_level(level, lucky)
        hp = model.hp_at_level(level)
        self.status = MineStatus(hp)

    def __repr__(self):
        from cminer.system import System
        return System.i18n(self.model.uid)
