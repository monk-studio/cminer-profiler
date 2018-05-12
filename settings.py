import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path('.') / '.env')

LOG_LEVEL = os.getenv('LOG_LEVEL')
SHEET_URL = os.getenv('SHEET_URL')
