# 数据库Sqlite3 操作  -  函数编程

import logging
import os.path
import sqlite3
from contextlib import closing

logger = logging.getLogger(__name__)


def make_connection() -> sqlite3.Connection:
    """
    创建连接
    """
    filename = "movies.db"
    db_path = os.path.join(os.path.abspath("."), "data")
    os.makedirs(db_path, exist_ok=True)
    db_file = os.path.join(db_path, filename)
    return sqlite3.connect(db_file)


def query_db(sql, parameters=()) -> list:
    """
    收敛数据库读操作
    """
    conn = make_connection()
    with closing(conn) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(sql, parameters)
            rows = cursor.fetchall()
            logger.debug("DB Query %s rows.", len(rows))
            return rows


def modified_db(sql, parameters=(), many=False) -> int:
    """
    写库操作
    """
    conn = make_connection()
    with closing(conn) as conn:
        with closing(conn.cursor()) as cursor:
            if many:
                cursor.executemany(sql, parameters)
            else:
                cursor.execute(sql, parameters)
            conn.commit()
            logger.debug("DB modified %s", conn.total_changes)
            return conn.total_changes


def init_table(tables_ddl: dict):
    """
    初始化表结构， 幂等
    """
    for name, sql in tables_ddl.items():
        changes = modified_db(sql)
        if changes:
            logger.info("Create %s table OK.", name)


