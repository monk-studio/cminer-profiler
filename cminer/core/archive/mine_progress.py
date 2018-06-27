import random

from cminer.consts import COIN
from cminer.logger import logger
from cminer.system import System


class MineProgress:
    def __init__(self, level):
        self.level = level
        self.mine = None
        self.dig_deeper(0, is_initial=True)

    def dig_by(self, axe, player):
        axe_broken = False
        coin = 0
        items = dict()

        damage = axe.damage_on_hardness(self.mine.model.hardness)
        if random.random() < player.crit_prob:
            logger.info('****** CRITICAL **')
            damage *= player.crit_damage
        self.mine.status.hp_now -= damage
        logger.debug(f'用 {axe} 造成了 {damage} 点伤害')
        axe.status.endurance -= 1

        if axe.status.endurance <= 0:
            axe_broken = True
            logger.debug(f'{axe} 坏了')
        else:
            logger.debug(f'{axe} 耐久 '
                         f'{axe.status.endurance}/{axe.model.endurance}')
        if self.mine.status.hp_now <= 0:
            _awards = self.mine.award
            for k, v in _awards.items():
                if k == COIN:
                    coin = v
                else:
                    items[System.item(k)] = v
            awards_text = [f'{v}个 {k}'
                           for k, v in items.items()]
            awards_text += [f'{coin}枚 金幣']
            awards_text = '獲得: ' + ', '.join(awards_text)
            logger.info(awards_text)
            self.dig_deeper(player.lucky_prob)
        else:
            logger.debug(f'{self.mine}剩餘血量 '
                         f'{self.mine.status.hp_now}/{self.mine.status.hp}')
        return dict(
            axe_broken=axe_broken,
            awards=dict(
                coin=coin,
                items=items,
            ),
            mine_level=self.level
        )

    def dig_deeper(self, lucky, is_initial=False):
        if not is_initial:
            self.level += 1
        self.mine = System.mine_at_level(self.level, lucky)
        logger.info(f'到达{self.level}层, 发现 {self.mine}, '
                    f'血量: {self.mine.status.hp}')
        return self.level

