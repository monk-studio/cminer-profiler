from ._base import ItemType, ItemStatus, Item


class MaterialType(ItemType):
    def __init__(self, uid):
        super().__init__(uid)

    def new(self):
        return Material(self)


class MaterialStatus(ItemStatus):
    pass


class Material(Item):
    def __init__(self, model):
        self.model = model
        self.status = MaterialStatus()
