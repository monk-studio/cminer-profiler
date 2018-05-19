class Recipe:
    def __init__(self, inputs, outputs):
        # [('MATERIAL_STONE', 3), ('MATERIAL_WOOD', 1)]
        self.inputs = inputs
        # [('TOOL_STONE_PICKAXE', 1)]
        self.outputs = outputs

    def __repr__(self):
        return repr(self.inputs) + ': ' + repr(self.outputs)
