import logging


_format = '%(asctime)s [%(levelname)s] [%(name)s]: %(message)s'
_name = 'profiler'

formatter = logging.Formatter(_format)

handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(_name)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
