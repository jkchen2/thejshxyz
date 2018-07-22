import logging

def new_logger(name='Log', level=logging.DEBUG, id=None):
    logger = logging.getLogger(id)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(f'[{name}]: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(level)
    return logger
