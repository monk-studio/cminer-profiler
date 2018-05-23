from .itemset import ItemSet
from cminer.system import System


class Warehouse(ItemSet):
    def __init__(self, data):
        super().__init__(data)
        self.coin = 0

    def __repr__(self):
        items = [f'{System.i18n(k)}: {v}個'
                 for k, v in self.grouped().items()]
        items = ', '.join(items + [f'金幣: {self.coin}枚'])
        return items

    def dump_coin_to(self, target):
        target.coin += self.coin
        self.coin = 0
