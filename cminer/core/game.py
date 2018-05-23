from aenum import MultiValueEnum

from cminer.logger import logger
from cminer.system import System
from cminer.consts import MATERIAL_WOOD
from .archive import Location, MineProgress


class Action(MultiValueEnum):
    shopping = 1, '商店'
    compose = 2, '合成'
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
                Action.shopping, Action.compose, Action.go_mining,
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
            self.v.warehouse.transfer_axes_to(self.v.bag)
            self.v.mine_progress = MineProgress()
            self.v.location = Location.mine
        if action == Action.go_camp:
            self.v.bag.dump_coin_to(self.v.warehouse)
            self.v.bag.dump_to(self.v.warehouse)
            self.v.location = Location.camp
        if action == Action.mine:
            assert self.v.location == Location.mine
            axes = self.v.bag.axes()
            if not axes:
                logger.info('没镐子可以往下挖了')
            else:
                axe_id, axe = axes[0]
                logger.debug('-------------------')
                result = self.v.mine_progress.dig_by_axe(axe)
                logger.debug('-------------------')
                if result['axe_broken']:
                    self.v.bag.remove(axe_id)
                for item, amount in result['awards']['items'].items():
                    for _ in range(amount):
                        self.v.bag.add(item)
                self.v.bag.coin += result['awards']['coin']
            if self.can_dig():
                self.execute(Action.mine)
        if action == Action.shopping:
            assert self.v.location == Location.camp
            # todo: more goodies
            wood_unit_price = 5
            can_buy = self.v.warehouse.coin // wood_unit_price
            if not can_buy:
                return logger.info('沒錢買木頭')
            need_wood = 15 - min(self.v.warehouse.wood_num(), 15)
            buy = min(can_buy, need_wood)
            for _ in range(buy):
                self.v.warehouse.add(System.item(MATERIAL_WOOD))
            cost = buy * wood_unit_price
            self.v.warehouse.coin -= cost
            logger.info(f'買了 {buy}個木頭, '
                        f'花費 {cost}個金幣')
        if action == Action.compose:
            assert self.v.location == Location.camp
            # todo: choose with recipe to compose
            # todo: recipe unlock
            recipes = sorted(System.recipes,
                             key=lambda x: x.priority,
                             reverse=True)
            to_craft = self.v.bag.capacity
            for recipe in recipes:
                while True:
                    if self.v.warehouse.can_compose(recipe):
                        self.v.warehouse.compose(recipe)
                        to_craft -= 1
                        if to_craft == 0:
                            break
                    else:
                        break
        self.v.save()

    def can_dig(self):
        if not self.v.location == Location.mine:
            return False
        return self.v.bag.axes()
