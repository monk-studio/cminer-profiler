import logging
from settings import LOG_LEVEL


_format = '%(message)s'
_name = 'profiler'

formatter = logging.Formatter(_format)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(_name)
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)
