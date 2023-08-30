
# 电影对象模型
from typing import Sequence
import datetime

from database import query_db, modified_db

MOVIE_ST_PAUSE = 0
MOVIE_ST_DISLIKE = 1
MOVIE_ST_LIKE = 2
MOVIE_ST_DOWNLOADING = 3
MOVIE_ST_DONE = 4


class Movie(object):
    status_dict = {
        MOVIE_ST_PAUSE: "待评估",
        MOVIE_ST_DISLIKE: "不喜欢",
        MOVIE_ST_LIKE: "想看",
        MOVIE_ST_DOWNLOADING: "下载中",
        MOVIE_ST_DONE: "下载完成"
    }

    def __init__(self, status: int = MOVIE_ST_PAUSE):
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
        self.create_time = None     # 抓取日期

    @classmethod
    def create(cls, hash_id, title, **kwargs):
        m = cls()
        m.hash = hash_id
        m.title = title
        for key, value in kwargs.items():
            m.__setattr__(key, value)
        return m

    @staticmethod
    def format_today():
        return str(datetime.date.today())

    def dump_2_dict(self):
        """
        额外的填充操作可以放在这里
        """
        self.create_time = self.format_today()
        return self.__dict__


class MovieDbManager(object):
    """
    数据库交互收敛到此类
    """
    DDL = '''CREATE TABLE if not exists movie (
                hash TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                tags TEXT,
                release_time TEXT,
                cover_addr TEXT,
                cover_path TEXT,
                movie_path TEXT,
                show_time TEXT,
                score REAL,
                description TEXT,
                addr TEXT NOT NULL,
                area TEXT,
                status INTEGER,
                create_time TEXT);'''
    # _table_name = "movie"
    _model = Movie

    @staticmethod
    def query_by_hash(hash_id: str) -> list:
        sql = "select * from movie where hash = ? ;"
        row = query_db(sql, parameters=(hash_id, ))
        return row

    @staticmethod
    def query_status(status: int = MOVIE_ST_PAUSE) -> list:
        sql = """SELECT hash, title, tags, score, status FROM movie
         where status = ? order by score;"""
        rows = query_db(sql, parameters=(status,))
        return rows

    @staticmethod
    def query_liked_movies(status: int = MOVIE_ST_LIKE) -> list:
        sql = """SELECT hash, title, cover_addr, addr FROM movie
         where status = ? ;"""
        rows = query_db(sql, parameters=(status,))
        return rows

    @staticmethod
    def query_downloading_movies(status: int = MOVIE_ST_DOWNLOADING) -> list:
        sql = """SELECT hash, title, cover_path, movie_path FROM movie
         where status = ? ;"""
        rows = query_db(sql, parameters=(status,))
        return rows

    @staticmethod
    def update_status(movies: list) -> int:
        sql = """
        UPDATE movie SET status = :status where hash = :hash; """
        count = modified_db(sql, movies, many=True)
        return count

    @staticmethod
    def update_download_stats(movies: list) -> int:
        sql = """
        UPDATE movie SET cover_path = :cover_path, movie_path = :movie_path,
        status = :status where hash = :hash; """
        count = modified_db(sql, movies, many=True)
        return count

    @staticmethod
    def update_cover_path(movies: list) -> int:
        sql = """
        UPDATE movie SET cover_path = :cover_path where hash = :hash; """
        count = modified_db(sql, movies, many=True)
        return count

    @staticmethod
    def update_movie_path(movies: list) -> int:
        sql = """
        UPDATE movie SET movie_path = :movie_path, status = :status where hash = :hash; """
        count = modified_db(sql, movies, many=True)
        return count

    @staticmethod
    def update_movie_done(movie_ifo: dict) -> int:
        sql = """
        UPDATE movie SET movie_path = :movie_path, status = :status where hash = :hash; """
        count = modified_db(sql, movie_ifo)
        return count

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
        description, addr, area, status, create_time) 
        VALUES (:hash,:title,:release_time,:cover_addr,:cover_path,:tags,
        :show_time, :score, :description, :addr, :area, :status,
        :create_time);'''
        _data = (m.dump_2_dict() for m in data)
        count = modified_db(sql, _data, many=True)
        return count


DDL = {
    "movie": MovieDbManager.DDL,
}
