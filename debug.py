
from gather import dytt_gather
from logger import init_logger
from database import init_table
from model.movie import DDL
from judgment import run


def main():
    init_logger()
    init_table(DDL)
    dytt_gather()
    run()


if __name__ == '__main__':
    main()
