import re
import pickle
import pygsheets

from settings import SHEET_URL
from ._logger import logger
from .models import Mine, Recipe, Tool
from .consts import (
    SOURCE_MINES, SOURCE_RECIPES, SOURCE_TOOLS, SOURCE_I18N
)

DROP_PROB_FACTORS = [1, 0.8, 0.6, 0.4, 0.2, 0.05, 0.01]


def run():
    gc = pygsheets.authorize()
    sheet = gc.open_by_url(SHEET_URL)

    id_data = sheet.worksheet_by_title('ID').range('A2:B200')
    name_id_map = dict([(x[1].value, x[0].value)
                        for x in id_data if x[0].value])
    i18n = dict([(x[0].value, x[1].value)
                 for x in id_data if x[0].value])
    _save(i18n, SOURCE_I18N)
    logger.info(f'Synced {len(i18n)} nouns')

    mine_data = sheet.worksheet_by_title('矿山')
    mines_data2 = sheet.worksheet_by_title('矿山血量&金币掉落')
    hp_base_list = [int(x[0].value) for x in mines_data2.range('B2:B20')]
    coin_factor = [float(x[0].value) for x in mines_data2.range('P27:AB27')]

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
        mine = Mine(uid, hardness, probs, item_drop_probs,
                    hp_base_list[idx], coin_factor)
        mines.append(mine)
    mines = dict([(x.uid, x) for x in mines])
    _save(mines, SOURCE_MINES)
    logger.info(f'Synced {len(mines)} mines')

    recipe_data = sheet.worksheet_by_title('合成配方').range('A2:B200')
    inouts = [(x[0].value, x[1].value) for x in recipe_data if x[0].value]
    recipes = [Recipe(_retrieve_items(name_id_map, x[0]),
                      _retrieve_items(name_id_map, x[1])) for x in inouts]
    _save(recipes, SOURCE_RECIPES)
    logger.info(f'Synced {len(recipes)} recipes')

    tool_data = sheet.worksheet_by_title('道具').range('A2:H100')
    tool_data = [x for x in tool_data if x[0].value]
    tools = list()
    for row in tool_data:
        uid = name_id_map[row[0].value]
        type_ = int(row[1].value)
        hardness = int(row[4].value) if row[4].value else None
        endurance = int(row[5].value) if row[5].value else None
        base_damage = int(row[6].value) if row[6].value else None
        tool = Tool(uid, type_, hardness, endurance, base_damage)
        tools.append(tool)
    tools = dict([(x.uid, x) for x in tools])
    _save(tools, SOURCE_TOOLS)
    logger.info(f'Synced {len(tools)} tools')


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
