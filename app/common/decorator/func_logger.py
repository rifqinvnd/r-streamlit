from functools import wraps
from app.common.log import logger


def func_logger(func):
    """Function logger"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """Wrapper"""
        logger.info(f"\x1b[6;30;42m {func.__name__} \x1b[0m")
        return func(*args, **kwargs)

    return wrapper
