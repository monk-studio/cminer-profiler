import json

from .player import Player, PlayerPresets

PLAYER_PRESETS = PlayerPresets(
    hp_init=30,
    hp_growth=5,
    crit_damage_init=1.1,
    crit_damage_growth=0.01,
    crit_prob_init=0.05,
    crit_prob_growth=0.005,
    lucky_prob_init=0,
    lucky_prob_growth=0.002,
    points_per_level=10,
)

PLAYER_INIT = Player(
    level=1, points=0,
    hp=PLAYER_PRESETS.hp_init,
    crit_damage=PLAYER_PRESETS.crit_damage_init,
    crit_prob=PLAYER_PRESETS.crit_prob_init,
    lucky_prob=PLAYER_PRESETS.lucky_prob_init,
    status=json.dumps({}),
    highest_mine_level=0,
    unlock_mine_level=0,
    cumulative_compose_times=0,
    cumulated_coin=0,
)
