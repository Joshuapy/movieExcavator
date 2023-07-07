
# 电影对象模型
from typing import Sequence

from database import query_db, modified_db


class Movie(object):
    status_dict = {
        0: "待评估",
        1: "不喜欢",
        2: "下载中",
        3: "下载完成"
    }

    def __init__(self, status: int = 0):
        self.title = None           # 电影名
        self.hash = None            # 唯一标识
        self.addr = None            # 下载地址
        self.release_time = None    # 发布时间
        self.cover_addr = None      # 封面url
        self.cover_path = None      # 封面本地路径
        self.tags = None            # 类型标签
        self.show_time = None       # 上映时间
        self.score = None           # 机构评分
        self.description = None     # 简介
        self.area = None            # 产地
        self.status = status        # 下载状态


class MoviveDbManager(object):
    """
    数据库交互收敛到此类
    """
    DDL = '''CREATE TABLE if not exists movie (
                hash TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                release_time TEXT,
                cover_addr TEXT,
                cover_path TEXT,
                tags TEXT,
                show_time TEXT,
                score REAL,
                description TEXT,
                addr TEXT NOT NULL,
                area TEXT,
                status INTEGER);'''
    # _table_name = "movie"
    _model = Movie

    @staticmethod
    def query_by_hash(hash_id: str) -> list:
        sql = "select * from movie where hash = ? ;"
        row = query_db(sql, parameters=(hash_id, ))
        return row

    @staticmethod
    def query_status(status: int = 0):
        sql = "select * from movie where status = ? ;"
        row = query_db(sql, parameters=(status,))
        return row

    @staticmethod
    def is_exists(hash_id: str) -> bool:
        sql = "SELECT hash FROM movie WHERE hash = ? ;"
        parameters = (hash_id, )
        rows = query_db(sql, parameters)
        return len(rows) > 0

    @staticmethod
    def save(data: Sequence[Movie]) -> int:
        """
        保存记录到db
        :data: list of Movie
        :return:
        """
        sql = '''INSERT INTO movie (hash, title, release_time,
        cover_addr, cover_path, tags, show_time, score,
        description, addr, area, status) 
        VALUES (:hash,:title,:release_time,:cover_addr,:cover_path,:tags,
        :show_time, :score, :description, :addr, :area, :status);'''
        _data = (m.__dict__ for m in data)
        count = modified_db(sql, _data, many=True)
        return count
