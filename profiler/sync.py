import pygsheets
from settings import SHEET_ID


def run():
    gc = pygsheets.authorize(outh_nonlocal=False)
    grid = gc.get_range(SHEET_ID, 'A1:F')
    print(grid)
