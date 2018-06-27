from cminer.system import System


class Player:
    def __init__(self):
        self.level = 1
        self.points = 0
        self.hp = System.player.hp
        self.crit_damage = System.player.crit_damage
        self.crit_prob = System.player.crit_prob
        self.lucky_prob = System.player.lucky_prob
        self.hp_now = self.hp
        self.highest_mine_level = 0

    def level_up(self):
        self.points += System.player.points_per_level
        self.level += 1
        return System.player.coins_to_upgrade[self.level - 1]

    def skill_up(self, key):
        assert self.points > 0
        if key == 'hp':
            self.hp += System.player.hp_growth
        elif key == 'crit_damage':
            self.crit_damage += System.player.crit_damage_growth
        elif key == 'crit_prob':
            self.crit_prob += System.player.crit_prob_growth
        elif key == 'lucky_prob':
            self.lucky_prob += System.player.lucky_prob_growth
        self.points -= 1

    def has_energy(self):
        return self.hp_now > 0

    def rest(self):
        self.hp_now = self.hp

    def recover_energy(self, energy):
        self.hp_now += energy

    def can_level_up(self, coins):
        return coins >= System.player.coins_to_upgrade[self.level - 1]

    def can_skill_up(self):
        return self.points > 0
