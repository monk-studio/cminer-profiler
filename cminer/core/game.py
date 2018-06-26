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
    buy = 8, '买东西'


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
        elif self.v.location == Location.shop:
            cmds = [
                Action.go_camp, Action.buy, Action.show_warehouse
            ]
            goods = [x for x in System.foods]
            goods_text = ','.join([f'{goods.index(x)}: {System.item(x)} (价格:{System.foods[x].price} '
                                    f'能量:{System.foods[x].energy})' for x in goods])
            logger.info(goods_text)
            logger.info(f'12: 木头(价格:5)')
            logger.info('-------------------')
        else:
            return dict()
        cmds = [(idx, x) for idx, x in enumerate(cmds)]
        cmds_text = ', '.join([f'{idx}: {x.values[1]}' for idx, x in cmds])
        logger.info(cmds_text)
        return dict(cmds)

    def execute(self, action, payload):
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
            self.v.warehouse.transfer_foods_to(self.v.bag)
            self.v.mine_progress = MineProgress()
            self.v.location = Location.mine
        if action == Action.go_camp:
            self.v.bag.dump_coin_to(self.v.warehouse)
            self.v.bag.dump_to(self.v.warehouse)
            self.v.bag.volume = self.v.bag.capacity
            self.v.location = Location.camp
            self.v.player.rest()
        if action == Action.mine:
            assert self.v.location == Location.mine
            foods = self.v.bag.foods()
            if not self.v.player.has_energy():
                if not foods:
                    return logger.info('沒體力了')
                food_id, food = foods[0]
                self.v.player.recover_energy(food.model.energy)
                self.v.bag.remove(food_id)
            axes = self.v.bag.axes()
            if not axes:
                return logger.info('没镐子可以往下挖了')
            axe_id, axe = axes[0]
            logger.debug('-------------------')
            self.v.player.hp_now -= 1
            result = self.v.mine_progress.dig_by_axe(axe)
            logger.debug('-------------------')
            if result['axe_broken']:
                self.v.bag.remove(axe_id)
            for item, amount in result['awards']['items'].items():
                for _ in range(amount):
                    self.v.bag.add(item)
            self.v.bag.coin += result['awards']['coin']
            if self.can_dig():
                self.execute(Action.mine, None)
        if action == Action.shopping:
            self.v.location = Location.shop
        if action == Action.buy:
            # todo: more goodies
            wood_unit_price = 5
            goods = [x for x in System.foods]
            good = None
            if payload is None:
                logger.info(' 请选择商品')
            if payload == 12:
                good = 'MATERIAL_WOOD'
                can_buy = self.v.warehouse.coin // wood_unit_price
            elif payload >= 0 & payload < 12:
                good = goods[payload]
                can_buy = self.v.warehouse.coin // System.foods[good].price
            else:
                return logger.info('没有该物品')

            if not can_buy:
                return logger.info(f'没钱买{System.item(good)}')

            if good == 'MATERIAL_WOOD':
                need_wood = 10 - min(self.v.warehouse.wood_num(), 10)
                buy = min(can_buy, need_wood)
                for _ in range(buy):
                    self.v.warehouse.add(System.item(MATERIAL_WOOD))
                cost = buy * wood_unit_price
            else:
                buy = min(can_buy, 12)
                for _ in range(buy):
                    self.v.warehouse.add(System.item(good))
                cost = buy * System.foods[good].price
            self.v.warehouse.coin -= cost
            logger.info(f'买了 {buy}个{System.item(good)}, 花费了 {cost}个金币')
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
