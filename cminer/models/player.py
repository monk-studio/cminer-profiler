class Player:
    def __init__(self, coins_to_upgrade):
        self.coins_to_upgrade = coins_to_upgrade
        self.points_per_level = 10
        self.hp = 20
        self.hp_growth = 5
        self.crit_damage = 1.1
        self.crit_damage_growth = 0.001
        self.crit_prob = 0.05
        self.crit_prob_growth = 0.0001
        self.lucky_prob = 0
        self.lucky_prob_growth = 0.0001
