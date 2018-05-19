from ._base import ItemType, ItemStatus, Item

TOOL_TYPE_AXE = 0
TOOL_TYPE_BOMB = 1
TOOL_TYPE_OTHERS = 9


class ToolType(ItemType):
    def __init__(self, uid, type_, hardness, endurance, base_damage):
        super().__init__(uid)
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
        return max(int(rv), 1)

    def new(self):
        return Tool(self)


class ToolStatus(ItemStatus):
    def __init__(self, endurance):
        self.endurance = endurance


class Tool(Item):
    def __init__(self, model):
        self.model = model
        self.status = ToolStatus(model.endurance)

    @property
    def type(self):
        return self.model.type

    def damage_on_hardness(self, hardness):
        # todo: status would contain magic
        return self.model.damage_on_hardness(hardness)
