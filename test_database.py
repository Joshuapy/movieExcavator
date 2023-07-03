# 测试数据库操作方法


from logger import init_logger
from database import init_table, modified_db, query_db, TABLE_NAME_OF_MOVIE

init_logger()


class TestDatabase(object):

    def test_init_table(self):
        init_table()
        assert 2 > 1

    def test_insert_db(self):
        sql = '''INSERT INTO movie (hash, title, addr) VALUES (?, ?, ?);'''
        changes = modified_db(sql, parameters=('123', '电影x', 'https://xx.com'))
        print(changes)
        assert changes != 0

    def test_query(self):
        sql = "select * from movie where hash = ?;"
        rows = query_db(sql, parameters=('123',))
        print(rows)
        assert len(rows) > 0

    def test_delete(self):
        sql = "delete from movie where hash = ?;"
        changes = modified_db(sql, parameters=('123',))
        print(changes)
        assert changes > 0
