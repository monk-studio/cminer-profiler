import re

import pygsheets

from settings import SHEET_URL
from ._logger import logger
from .models import Mine, Food, Recipe

DROP_PROB_FACTORS = [1, 0.8, 0.6, 0.4, 0.2, 0.05, 0.01]


def run():
    gc = pygsheets.authorize()
    sheet = gc.open_by_url(SHEET_URL)

    # ID, 矿山, 矿山血量&金币掉落, 食物, 道具, 人物,
    id_data = sheet.worksheet_by_title('ID').range('A2:B200')
    name_id_map = dict([(x[1].value, x[0].value)
                        for x in id_data if x[0].value])
    # id_name_map = dict([(x[0].value, x[1].value)
    #                     for x in id_data if x[0].value])

    mine_data = sheet.worksheet_by_title('矿山')
    mines_data2 = sheet.worksheet_by_title('矿山血量&金币掉落')
    hp_base_list = [int(x[0].value) for x in mines_data2.range('B2:B20')]
    coin_factor = [float(x[0].value) for x in mines_data2.range('P27:AB27')]

    mines = list()
    for idx, row in enumerate(mine_data.range('A2:V20')):
        name = row[0].value
        uid = name_id_map[name]
        probs = [x.value if x else None for x in row[1:14]]
        drop_probs = [x.value for x in row[14: 21]]
        item_drop_probs = list()
        for (prob, group) in zip(DROP_PROB_FACTORS, drop_probs):
            items = retrieve_items(name_id_map, group)
            item_drop_probs += [(x[0], x[1], prob) for x in items]
        mine = Mine(uid, name, probs, item_drop_probs,
                    hp_base_list[idx], coin_factor)
        mines.append(mine)

    recipe_data = sheet.worksheet_by_title('合成配方').range('A2:B200')
    inouts = [(x[0].value, x[1].value) for x in recipe_data if x[0].value]
    recipes = [Recipe(retrieve_items(name_id_map, x[0]),
                      retrieve_items(name_id_map, x[1])) for x in inouts]
    for recipe in recipes:
        logger.info(recipe)


def retrieve_items(ids, text):
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
