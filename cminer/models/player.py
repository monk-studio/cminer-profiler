class Player:
    def __init__(self, coins_to_upgrade):
        self.coins_to_upgrade = coins_to_upgrade
        self.points_per_level = 10
        self.hp = 30
        self.hp_growth = 5
        self.crit_damage = 1.1
        self.crit_damage_growth = 0.01
        self.crit_prob = 0.05
        self.crit_prob_growth = 0.005
        self.lucky_prob = 0
        self.lucky_prob_growth = 0.002
