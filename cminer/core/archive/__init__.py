import pickle
from pathlib import Path

from cminer.consts import TOOL_WOODEN_PICKAXE
from cminer.system import System
from .bag import Bag
from .player import Player
from .itemset import ItemSet
from .location import Location
from .warehouse import Warehouse
from .mine_progress import MineProgress


class Archive:
    root = Path.home() / 'cminer/archives'
    location = None
    mine_progress = None

    def __init__(self, name):
        self.name = name
        self.bag = Bag({})
        self.warehouse = Warehouse({})
        self.player = Player()
        if not self.load():
            self.location = Location.camp
            for _ in range(5):
                item = System.item(TOOL_WOODEN_PICKAXE)
                self.warehouse.add(item)
            for _ in range(30):
                item = System.item('FOOD_NUTS')
                self.warehouse.add(item)

    @property
    def _path(self):
        return self.root / (self.name + '.pkl')

    def save(self):
        with open(self._path, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)

    def load(self):
        try:
            with open(self._path, 'rb') as f:
                data = pickle.load(f)
                for k, v in data.__dict__.items():
                    setattr(self, k, v)
                return True
        except FileNotFoundError:
            return False

    @staticmethod
    def list():
        Archive.root.mkdir(parents=True, exist_ok=True)
        return [Path(f).name.split('.')[0]
                for f in Archive.root.glob('*.pkl')]
