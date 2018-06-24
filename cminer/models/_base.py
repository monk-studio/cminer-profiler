class ItemType:
    def __init__(self, uid, volume):
        self.uid = uid
        self.volume = volume

    def new(self):
        raise NotImplemented

    def __repr__(self):
        return self.uid


class ItemStatus:
    pass


class Item:
    model: ItemType

    def __hash__(self):
        return hash(self.model.uid)

    def __repr__(self):
        from cminer.system import System
        return System.i18n(self.model.uid)
