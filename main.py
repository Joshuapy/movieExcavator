# Describtion: download movies from dytt.com
# Date: 2023.6.19
# Author: joshua


from scheduler import make_scheduler
from logger import init_logger


def main():
    """
    启动定时器
    """
    logger = init_logger()
    logger.info("program started!")

    sch = make_scheduler()
    sch.start()


if __name__ == "__main__":
    main()
