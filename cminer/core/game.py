from aenum import MultiValueEnum

from cminer.logger import logger
from .archive import Location, MineProgress


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
        cmds_text = ', '.join([f'{idx}: {x.values[1]}' for idx, x in cmds])
        logger.info(cmds_text)
        return dict(cmds)

    def execute(self, action):
        if action == Action.show_warehouse:
            # todo: interactive ui for bag.
            logger.info('-------------------')
            logger.info(self.v.warehouse)
            logger.info('-------------------')
            return
        if action == Action.show_bag:
            logger.info('-------------------')
            logger.info(self.v.bag)
            logger.info('-------------------')
            return
        if action == Action.go_mining:
            # todo: bag should has limited space
            self.v.bag.data = self.v.warehouse.data
            self.v.warehouse.clear()
            self.v.mine_progress = MineProgress()
            self.v.location = Location.mine
        if action == Action.go_camp:
            self.v.warehouse.data = self.v.bag.data
            self.v.warehouse.coin += self.v.bag.coin
            self.v.bag.clear()
            self.v.location = Location.camp
        if action == Action.mine:
            axes = self.v.bag.axes()
            if not axes:
                logger.info('没镐子可以往下挖了')
            else:
                axe_id, axe = axes[0]
                logger.info('-------------------')
                result = self.v.mine_progress.dig_by_axe(axe)
                logger.info('-------------------')
                if result['axe_broken']:
                    self.v.bag.remove(axe_id)
                for item, amount in result['awards']['items'].items():
                    for _ in range(amount):
                        self.v.bag.add(item)
                self.v.bag.coin += result['awards']['coin']
        self.v.save()
