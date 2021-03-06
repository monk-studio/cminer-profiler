import pickle
import re

import json

import pygsheets

from cminer.models import MineType, ToolType, MaterialType, FoodType
from cminer.models import Recipe, Player, Utility
from settings import SHEET_URL
from .consts import (
    SOURCE_MINES, SOURCE_RECIPES, SOURCE_TOOLS, SOURCE_MATERIALS, SOURCE_I18N,
    SOURCE_PLAYER, SOURCE_FOOD, SOURCE_UTILITY
)
from .logger import logger
from cminer.db import session_maker, Item, Mine, Utilities, RecipeD

DROP_PROB_FACTORS = [1, 0.8, 0.6, 0.4, 0.2, 0.05, 0.01]


def run():
    session = session_maker()

    gc = pygsheets.authorize()
    sheet = gc.open_by_url(SHEET_URL)

    id_data = sheet.worksheet_by_title('ID').range('A2:B200')
    name_id_map = dict([(x[1].value, x[0].value)
                        for x in id_data if x[0].value])
    # key: ID, value: 中文
    i18n = dict([(x[0].value, x[1].value)
                 for x in id_data if x[0].value])
    reversed_i18n = {v: k for k, v in i18n.items()}
    _save(i18n, SOURCE_I18N)
    logger.info(f'Synced {len(i18n)} nouns')

    mine_data = sheet.worksheet_by_title('矿山')
    mines_data2 = sheet.worksheet_by_title('矿山血量&金币掉落')
    hp_base_list = [int(x[0].value) for x in mines_data2.range('B2:B20')]
    coin_factor = [float(x.value) for x in mines_data2.range('P27:AB27')[0]]
    utility_ = Utilities(
        id="coin_factor",
        data=json.dumps(coin_factor),
    )
    # session.add(utility_)
    mines = list()
    for idx, row in enumerate(mine_data.range('A2:V20')):
        name = row[0].value
        uid = name_id_map[name]
        hardness = int(row[1].value)
        probs = [int(x.value) / 100 if x.value else None for x in row[9:22]]
        drop_probs = [x.value for x in row[2: 9]]
        item_drop_probs = list()
        for (prob, group) in zip(DROP_PROB_FACTORS, drop_probs):
            items = _retrieve_items(name_id_map, group)
            item_drop_probs += [(x[0], x[1], prob) for x in items]
        mine = MineType(uid, hardness, probs, item_drop_probs,
                        hp_base_list[idx], coin_factor)
        mines.append(mine)
        mine_ = Mine(
            id=uid,
            hardness=hardness,
            probs=json.dumps(probs),
            item_drop_probs=json.dumps(item_drop_probs),
            hp_base=hp_base_list[idx],
        )
        # session.add(mine_)
    mines = dict([(x.uid, x) for x in mines])
    _save(mines, SOURCE_MINES)
    logger.info(f'Synced {len(mines)} mines')

    unlock_cost_data = sheet.worksheet_by_title('矿山解锁').range('A3:B28')
    unlock_bag_data = sheet.worksheet_by_title('人物').range('K2:L37')
    mine_unlock_costs = dict()
    bag_unlock_costs = dict()
    for row in unlock_cost_data:
        lv = int(row[0].value)
        cost = int(row[1].value)
        mine_unlock_costs[lv] = cost
    for row in unlock_bag_data:
        amount = int(row[0].value)
        cost = int(row[1].value)
        bag_unlock_costs[amount] = cost
    utility = Utility(mine_unlock_costs, bag_unlock_costs)
    _save(utility, SOURCE_UTILITY)
    utility_ = Utilities(
        id="mine_unlock_costs",
        data=json.dumps(mine_unlock_costs),
    )
    # session.add(utility_)
    utility_ = Utilities(
        id="bag_unlock_costs",
        data=json.dumps(bag_unlock_costs),
    )
    # session.add(utility_)
    logger.info('Synced utilities')

    recipe_data = sheet.worksheet_by_title('合成配方').range('A2:D19')
    inouts = [(x[0].value, x[1].value, int(x[2].value), x[3].value)
              for x in recipe_data if x[0].value]
    recipes = [Recipe(_retrieve_items(name_id_map, x[0]),
                      _retrieve_items(name_id_map, x[1]),
                      x[2], x[3]) for x in inouts]
    # _save(recipes, SOURCE_RECIPES)
    for x in inouts:
        recipe_ = RecipeD(
            id=x[3],
            inputs=json.dumps(_retrieve_items(name_id_map, x[0])),
            outputs=json.dumps(_retrieve_items(name_id_map, x[1])),
        )
        # session.add(recipe_)
    logger.info(f'Synced {len(recipes)} recipes')

    tool_data = sheet.worksheet_by_title('道具').range('A2:I100')
    tool_data = [x for x in tool_data if x[0].value]
    tools = list()
    for row in tool_data:
        uid = name_id_map[row[0].value]
        type_ = int(row[1].value)
        volume = float(row[8].value)
        hardness = int(row[4].value) if row[4].value else None
        endurance = int(row[5].value) if row[5].value else None
        base_damage = int(row[6].value) if row[6].value else None
        tool = ToolType(uid, volume, type_, hardness, endurance, base_damage)
        tools.append(tool)
        data_ = {
            "type": type_,
            "hardness": hardness,
            "endurance": endurance,
            "base_damage": base_damage,
        }
        tool_ = Item(
            id=uid, volume=volume,
            type="tool",
            data=json.dumps(data_),
            buy_price=0,
            sell_price=0,
        )
        # session.add(tool_)
    tools = dict([(x.uid, x) for x in tools])
    _save(tools, SOURCE_TOOLS)
    logger.info(f'Synced {len(tools)} tools')

    material_data = sheet.worksheet_by_title('材料').range('A2:C29')
    materials = list()
    for row in material_data:
        uid = name_id_map[row[0].value]
        volume = float(row[2].value)
        price = int(row[1].value)
        material = MaterialType(uid, volume, price)
        materials.append(material)
        material_ = Item(
            id=uid, volume=volume,
            type="material",
            data=json.dumps({}),
            buy_price=0,
            sell_price=price,
        )
        # session.add(material_)
    materials = dict([(x.uid, x) for x in materials])
    _save(materials, SOURCE_MATERIALS)
    logger.info(f'Synced {len(materials)} materials')

    food_data = sheet.worksheet_by_title('食物').range('A2:E16')
    foods = list()
    for row in food_data:
        uid = name_id_map[row[0].value]
        volume = float(row[4].value)
        energy = int(row[1].value)
        price = int(row[2].value)
        priority = int(row[3].value)
        food = FoodType(uid, volume, energy, price, priority)
        foods.append(food)
        data_ = {
            "energy": energy,
        }
        food_ = Item(
            id=uid, volume=volume,
            type="food",
            data=json.dumps(data_),
            buy_price=price,
            sell_price=0,
        )
        # session.add(food_)
    foods = dict([(x.uid, x) for x in foods])
    _save(foods, SOURCE_FOOD)
    logger.info(f'Synced {len(foods)} foods')

    # character
    character_chart = sheet.worksheet_by_title('人物')
    coins_to_upgrade = character_chart.range('B2:B100')
    coins_to_upgrade = [int(x[0].value) for x in
                        coins_to_upgrade if x[0].value]
    _save(Player(coins_to_upgrade), SOURCE_PLAYER)
    utility_ = Utilities(
        id="coins_to_upgrade",
        data=json.dumps(coins_to_upgrade),
    )
    # session.add(utility_)
    session.commit()


def _retrieve_items(ids, text):
    rv = list()
    match = re.compile(r'\d+(.*)')
    items = text.split(',')
    for item in items:
        item = item.strip()
        if not item:
            continue
        name = match.search(item).group(1)
        uid = ids[name]
        amount = int(item.rstrip(name))
        rv.append((uid, amount))
    return rv


def _save(obj, filename):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
