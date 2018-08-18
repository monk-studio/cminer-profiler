import os
from pathlib import Path

from dotenv import load_dotenv

_here = os.path.abspath(os.path.dirname(__file__))
_db_path = os.path.join(_here, './store.sqlite')

load_dotenv(Path('.') / '.env')

LOG_LEVEL = os.getenv('LOG_LEVEL')
SHEET_URL = os.getenv('SHEET_URL')
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(_db_path)
