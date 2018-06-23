from ._base import ItemType, ItemStatus, Item


class MaterialType(ItemType):
    def __init__(self, uid, price):
        super().__init__(uid)
        self.price = price

    def new(self):
        return Material(self)


class MaterialStatus(ItemStatus):
    pass


class Material(Item):
    def __init__(self, model):
        self.model = model
        self.status = MaterialStatus()
