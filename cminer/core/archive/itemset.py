from copy import deepcopy
from uuid import uuid4
from collections import Counter
from cminer.models import Tool, TOOL_TYPE_AXE, Food
from cminer.consts import MATERIAL_WOOD
from cminer.system import System
from cminer.logger import logger


class ItemSet:
    capacity = 99999999

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
        axes = sorted(axes, key=lambda x: x[1].model.endurance, reverse=True)
        return list(axes)

    def foods(self):
        foods = filter(
            lambda x: type(x[1]) == Food,
            self.data.items())
        return list(foods)

    def wood_num(self):
        return self.grouped().get(MATERIAL_WOOD) or 0

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

    def transfer_axes_to(self, target):
        uids = [x[0] for x in self.axes()[:10]]
        for uid in uids:
            target.add(self.data[uid])
            """tool volume 1"""
            target.volume -= 1
        for uid in uids:
            self.remove(uid)

    def dump_to(self, target):
        [target.add(x) for x in self.data.values()]
        self.clear()

    def transfer_foods_to(self, target):
        """food volume 0.08"""
        left_volume = int(target.volume / 0.08)
        uids = [x[0] for x in self.foods()[:left_volume]]
        for uid in uids:
            target.add(self.data[uid])
        for uid in uids:
            self.remove(uid)
