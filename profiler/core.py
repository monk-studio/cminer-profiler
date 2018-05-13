class System:
    def __init__(self, mines, tools, recipes):
        self.mines = mines
        self.tools = tools
        self.recipes = recipes

    def mine_at_level(self, level):
        pass

    def compose(self, materials):
        pass


class Archive:
    # todo: connect to database.
    def __init__(self):
        pass


class Game:
    def __init__(self, system, archive):
        self.system = system
        self.archive = archive

    def start(self):
        pass
