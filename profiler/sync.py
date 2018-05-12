import logging

import pygsheets

from settings import SHEET_ID
from ._logger import logger


def run():
    gc = pygsheets.authorize(outh_nonlocal=False)
    grid = gc.get_range(SHEET_ID, 'A2:F')
    logger.info(grid)
