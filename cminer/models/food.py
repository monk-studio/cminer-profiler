from ._base import ItemType, ItemStatus, Item


class FoodType(ItemType):
    def __init__(self, uid, volume, energy, price, priority):
        super().__init__(uid, volume)
        self.energy = energy
        self.price = price
        self.priority = priority

    def new(self):
        return Food(self)


class FoodStatus(ItemStatus):
    pass


class Food(Item):
    def __init__(self, model):
        self.model = model
        self.status = FoodStatus()
