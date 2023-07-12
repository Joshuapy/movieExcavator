# Describtion: download movies from dytt.com
# Date: 2023.6.19
# Author: joshua


from scheduler import make_scheduler
from logger import init_logger
from database import init_table
from model.movie import DDL


def main():
    """
    启动定时器
    """
    logger = init_logger()
    logger.info("program started!")
    init_table(DDL)

    sch = make_scheduler()
    sch.start()


if __name__ == "__main__":
    main()
