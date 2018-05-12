import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path('.') / '.env')

SHEET_ID = os.getenv('SHEET_ID')
