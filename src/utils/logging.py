import logging

DEBUG_LEVEL = 2
'''
0 -> Error logging only
1 -> basic logging info (user state, model thinking, info, errors)
2 -> debug (basic logging info + detailed procceses)
'''

def set_logger(name):
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)

def log(message, logger, level):
    if DEBUG_LEVEL >= level:
        return logger.info(message)
