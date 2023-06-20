# 设置日志记录器


import os
import logging
from logging.handlers import RotatingFileHandler


logfilename = "app.log"


def init_logger(log_dir: str = "logs") -> logging.Logger:
    """
    设置全局logger
    :return:
    """
    level = logging.DEBUG
    os.makedirs(log_dir, exist_ok=True)
    logfile = os.path.join(log_dir, logfilename)

    msg_pattern = "%(asctime)s | %(name)s | %(levelname)s | L%(lineno)s | %(message)s"
    formatter = logging.Formatter(msg_pattern)

    handler = RotatingFileHandler(logfile, maxBytes=1024*1024*100, backupCount=5)
    handler.setLevel(level)
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.propagate = False

    logger.addHandler(handler)
    return logger
