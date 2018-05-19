RECIPE_TYPE_AXE = 1


class Recipe:
    def __init__(self, inputs, outputs, priority):
        # [('MATERIAL_STONE', 3), ('MATERIAL_WOOD', 1)]
        self.inputs = inputs
        # [('TOOL_STONE_PICKAXE', 1)]
        self.outputs = outputs
        self.priority = priority

    def __repr__(self):
        return repr(self.inputs) + ': ' + repr(self.outputs)
