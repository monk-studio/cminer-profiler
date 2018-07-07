from aenum import MultiValueEnum

from cminer.logger import logger
from cminer.system import System
from cminer.consts import MATERIAL_WOOD, TOOL_WOODEN_PICKAXE
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
    character = 9, '人物'
    character_up = 10, '人物升级'
    mine_level = 11, '矿山等级'
    sell = 12, '卖东西'


Character = ['升级', '体力升级', '暴击升级', '暴击率升级', '幸运值升级']


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
                Action.shopping, Action.compose, Action.go_mining, Action.character
            ]
        elif self.v.location == Location.mine:
            cmds = [
                Action.show_bag,
                Action.mine, Action.go_camp
            ]
        elif self.v.location == Location.mine_menu:
            cmds = [
                Action.show_warehouse,
                Action.mine_level, Action.go_camp, Action.show_bag
            ]
            unlock_text = f'已解锁到第{self.v.player.unlock_level} 层'
            highest_text = f'已挖到第{self.v.player.highest_mine_level}层'
            cost_text = ',\n'.join(f'{x}层: {System.utility.level_cost[x]}个金币' for x in System.utility.level_cost)
            logger.info('-------------------')
            logger.info(unlock_text)
            logger.info(highest_text)
            logger.info(cost_text)
        elif self.v.location == Location.shop:
            cmds = [
                Action.go_camp,
                Action.buy,  Action.sell,
                Action.show_warehouse
            ]
        elif self.v.location == Location.character:
            cmds = [
                Action.go_camp, Action.character_up
            ]
            logger.info('-------------------')
            logger.info('人物信息：')
            logger.info(f'等级:{self.v.player.level}  '
                        f'体力:{self.v.player.hp}  '
                        f'暴击伤害:{self.v.player.crit_damage}  '
                        f'暴击率:{self.v.player.crit_prob}  '
                        f'幸运值:{self.v.player.lucky_prob}  '
                        f'技能点:{self.v.player.points}  '
                        f'背包：{self.v.bag.capacity}   '
                        f'锻造次数：{self.v.player.compose_times}')
            logger.info('-------------------')
            logger.info('可选升级：')
            character_text = ', '.join([f'{Character.index(x)}: {x}' for x in Character])
            logger.info(character_text)
            logger.info(f'5: 背包（{System.utility.bag_cost[self.v.bag.capacity]}个金币）')
        else:
            return dict()
        cmds = [(idx, x) for idx, x in enumerate(cmds)]
        cmds_text = ', '.join([f'{idx}: {x.values[1]}' for idx, x in cmds])
        logger.info('###########################')
        logger.info(cmds_text)
        return dict(cmds)

    def execute(self, action, condition):
        axe_amount = self.v.bag.capacity - 4
        if action == Action.show_warehouse:
            # todo: interactive ui for bag.
            logger.info('-------------------')
            logger.info(self.v.warehouse)
            return
        if action == Action.show_bag:
            logger.info('-------------------')
            logger.info(self.v.bag)
            return
        if action == Action.go_mining:
            self.v.warehouse.transfer_axes_to(self.v.bag, axe_amount)
            self.v.warehouse.transfer_foods_to(self.v.bag)
            self.v.location = Location.mine_menu
        if action == Action.go_camp:
            self.v.bag.dump_coin_to(self.v.warehouse)
            self.v.bag.dump_to(self.v.warehouse)
            self.v.bag.volume = self.v.bag.capacity
            self.v.location = Location.camp
            self.v.player.rest()
        if action == Action.mine_level:
            if condition is None:
                self.v.mine_progress = MineProgress(1)
                self.v.location = Location.mine
                return
            if condition not in System.utility.level_cost:
                return logger.info('请选择开始层数')
            if condition > self.v.player.highest_mine_level:
                return logger.info('还未挖到该层')
            if condition > self.v.player.unlock_level:
                if System.utility.level_cost[condition] > self.v.warehouse.coin:
                    return logger.info('钱不够解锁存档点')
                self.v.warehouse.coin -= System.utility.level_cost[condition]
                self.v.player.unlock_level = condition
                logger.info(f'花了{System.utility.level_cost[condition]}金币，解锁了{condition}层的存档点')
            self.v.mine_progress = MineProgress(condition)
            self.v.location = Location.mine
        if action == Action.mine:
            assert self.v.location == Location.mine
            if not self.v.player.has_energy():
                foods = self.v.bag.foods()
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
            result = self.v.mine_progress.dig_by(axe, self.v.player)
            logger.debug('-------------------')
            if result['axe_broken']:
                self.v.bag.remove(axe_id)
            for item, amount in result['awards']['items'].items():
                for _ in range(amount):
                    self.v.bag.add(item)
            self.v.player.highest_mine_level = max(self.v.player.highest_mine_level, result['mine_level'])
            self.v.player.unlock_level = max(self.v.player.unlock_level, self.v.player.highest_mine_level - 200)
            self.v.bag.coin += result['awards']['coin']
            self.execute(Action.mine, None)
        if action == Action.shopping:
            self.v.location = Location.shop
        if action == Action.buy:
            # todo: more goodies
            wood_unit_price = 4
            goods = [x for x in System.foods]
            goods_text = ',\n'.join([f'{goods.index(x)}: {System.item(x)} (价格:{System.foods[x].price} '
                                     f'能量:{System.foods[x].energy})' for x in goods])
            logger.info('-------------------')
            logger.info(goods_text)
            logger.info('12: 木头(价格:4)')
            logger.info('13: 木镐(免费)')
            good = None
            if condition is None:
                return logger.info(' 请选择商品')
            elif condition == 12:
                good = 'MATERIAL_WOOD'
                can_buy = self.v.warehouse.coin // wood_unit_price
            elif 0 <= condition < 12:
                good = goods[condition]
                can_buy = self.v.warehouse.coin // System.foods[good].price
            elif condition == 13:
                for _ in range(3):
                    self.v.warehouse.add(System.item(TOOL_WOODEN_PICKAXE))
                return logger.info('领取了3个木镐')
            else:
                return logger.info('没有该物品')

            if not can_buy:
                return logger.info(f'没钱买{System.item(good)}')

            if good == 'MATERIAL_WOOD':
                buy = 5
                for _ in range(buy):
                    self.v.warehouse.add(System.item(MATERIAL_WOOD))
                cost = buy * wood_unit_price
            else:
                buy = min(can_buy, 12)
                for _ in range(buy):
                    self.v.warehouse.add(System.item(good))
                cost = buy * System.foods[good].price
            self.v.warehouse.coin -= cost
            logger.info('-------------------')
            logger.info(f'买了 {buy}个{System.item(good)}, 花费了 {cost}个金币, 还剩{self.v.warehouse.coin}个金币')
        if action == Action.sell:
            all_items = self.v.warehouse.items()
            materials = list()
            for x in all_items:
                for y in self.v.warehouse.materials():
                    if x[0] == y[1].model.uid:
                        materials.append(x)
                        break
            items_text = ',\n'.join(f'{materials.index(x)}: {System.item(x[0])}, {x[1]}个'
                                    f'(售价：{System.materials[x[0]].price}个金币）' for x in materials)
            logger.info('-------------------')
            logger.info(items_text)
            good = None
            amount = 0
            if condition is None:
                return logger.info('请选择要出售的商品')
            elif 0 <= condition <= len(materials):
                good = materials[condition][0]
                amount = materials[condition][1]
            else:
                return logger.info('请选择正确的商品')
            to_remove = list()
            items = filter(lambda x: x[1].model.uid == good, self.v.warehouse.materials())
            to_remove += [x[0] for x in items][:amount]
            for i in to_remove:
                self.v.warehouse.remove(i)
            reward = System.materials[good].price * amount
            self.v.warehouse.coin += reward
            logger.info('-------------------')
            logger.info(f'卖了{amount}个{System.item(good)}, 赚了{reward}个金币，现有{self.v.warehouse.coin}个金币')
        if action == Action.compose:
            assert self.v.location == Location.camp
            # todo: choose with recipe to compose
            # todo: recipe unlock
            if condition is None:
                recipes = sorted(System.recipes,
                                 key=lambda x: x.priority,
                                 reverse=True)
                recipes = filter(lambda x: x.priority > 0, recipes)
                to_craft = axe_amount - len(self.v.warehouse.axes())
                for recipe in recipes:
                    while True:
                        if self.v.warehouse.can_compose(recipe):
                            self.v.warehouse.compose(recipe)
                            self.v.player.compose_times += 1
                            to_craft -= 1
                            if to_craft <= 0:
                                break
                        else:
                            break
            elif condition == 1:
                recipe_id = 'RECIPE_CHARCOAL'
                recipe = None
                for x in System.recipes:
                    if x.id_ == recipe_id:
                        recipe = x
                if self.v.warehouse.can_compose(recipe):
                    self.v.warehouse.compose(recipe)
                    self.v.player.compose_times += 1

        if action == Action.character:
            self.v.location = Location.character
        if action == Action.character_up:
            assert self.v.location == Location.character
            if condition is None:
                return logger.info('请选择升级内容')
            if condition == 0:
                if not self.v.player.can_level_up(self.v.warehouse.coin):
                    return logger.info('钱不够升级')
                cost = self.v.player.level_up()
                self.v.warehouse.coin -= cost
                logger.info(f'升了一级，花费了{cost}金币，还剩{self.v.warehouse.coin}金币')
            if 0 < condition < 5:
                if not self.v.player.can_skill_up():
                    return logger.info('点数不够升级')
                key = None
                if condition == 1:
                    key = 'hp'
                elif condition == 2:
                    key = 'crit_damage'
                elif condition == 3:
                    key = 'crit_prob'
                elif condition == 4:
                    key = 'lucky_prob'
                else:
                    return logger.info('指令错误')
                self.v.player.skill_up(key)
                logger.info(f'{Character[condition]}了，还剩{self.v.player.points}个技能点')
            if condition == 5:
                cost = System.utility.bag_cost[self.v.bag.capacity]
                if cost > self.v.warehouse.coin:
                    return logger.info('钱不够解锁背包')
                self.v.bag.capacity += 1
                self.v.bag.volume = self.v.bag.capacity
                self.v.warehouse.coin -= cost
                logger.info(f'现背包容量为{self.v.bag.capacity}, 花了{cost}个金币, 还剩{self.v.warehouse.coin}金币')
            if condition > 5:
                logger.info('指令错误')
        self.v.save()
