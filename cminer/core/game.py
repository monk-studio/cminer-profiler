from aenum import MultiValueEnum

from cminer.logger import logger
from cminer.models import Tool
from .archive import Location, MineProgress
from .system import System


class Action(MultiValueEnum):
    buy_wood = 1, '买木头'
    make_pickaxe = 2, '做稿子'
    go_mining = 3, '去挖矿'
    mine = 4, '往下挖'
    go_camp = 5, '回到营地'
    show_warehouse = 6, '显示仓库'
    show_bag = 7, '显示背包'


class Game:
    def __init__(self, archive):
        self.archive = archive

    @property
    def v(self):
        return self.archive

    def echo(self):
        if self.v.location == Location.camp:
            cmds = [
                Action.show_warehouse,
                Action.buy_wood, Action.make_pickaxe, Action.go_mining,
            ]
        elif self.v.location == Location.mine:
            cmds = [
                Action.show_bag,
                Action.mine, Action.go_camp
            ]
        else:
            return dict()
        cmds = [(idx, x) for idx, x in enumerate(cmds)]
        cmds_text = '\n'.join([f'{idx}: {x.values[1]}' for idx, x in cmds])
        logger.info(cmds_text)
        return dict(cmds)

    def execute(self, action):
        if action == Action.show_warehouse:
            # todo: interactive ui for bag.
            items = [f'{System.i18n[k.uid]}: {v}個'
                     for k, v in self.v.warehouse.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.show_bag:
            items = [f'{System.i18n[k.uid]}: {v}個'
                     for k, v in self.v.bag.items()]
            items = '\n'.join(items)
            logger.info('-------------------')
            logger.info(items)
            logger.info('-------------------')
            return
        if action == Action.go_mining:
            # todo: bag should has limited space
            self.v.bag = self.v.warehouse
            self.v.warehouse = dict()
            self.v.mine_progress = MineProgress()
            self.v.location = Location.mine
        if action == Action.go_camp:
            self.v.warehouse = self.v.bag
            self.v.bag = dict()
            self.v.location = Location.camp
        if action == Action.mine:
            axes = filter(
                lambda x: type(x) == Tool and x.type == Tool.TYPE_AXE,
                self.v.bag.keys())
            axes = list(axes)
            if not axes:
                logger.info('没镐子可以往下挖了')
            else:
                result = self.v.mine_progress.dig_by_axe(axes[0])
                # todo result[axe_broken]
                for item, amount in result['awards'].items():
                    if self.v.bag.get(item):
                        self.v.bag[item] += amount
                    else:
                        self.v.bag[item] = 1
        self.v.save()
