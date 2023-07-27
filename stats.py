# 描述：状态管理,包括提交下载，查询下载状态，更新状态信息到数据库等
# 时间：23.7.19

import logging
import time

from lib.aria2_client import Aria2Client
from model.movie import (MovieDbManager, MOVIE_ST_DOWNLOADING)
from config import aria2_host, aria2_secret

logger = logging.getLogger(__name__)


class MovieLink(object):
    """
    用于下载的结构体
    """
    def __init__(self, hash_id, title, cover_addr, addr):
        self.hash = hash_id
        self.title = title
        self.cover_addr = cover_addr
        self.addr = addr
        self.cover_path = None
        self.movie_path = None
        self.status = None


class StatsUpdater(object):
    def __init__(self):
        self.movies = None
        self.client = Aria2Client(host=aria2_host, secret=aria2_secret)

    def get_movies(self):
        """
        查询待评审的电影条目（status=0）
        return: list of SimpleMovie
        """
        manager = MovieDbManager()
        rows = manager.query_liked_movies()
        logger.info("Got liked movies %s.", len(rows))
        self.movies = [MovieLink(*item) for item in rows]

    def download_source(self):
        """
        提交下载
        """
        for movie in self.movies:
            if movie.cover_addr:
                try:
                    # 将任务ID暂存在path字段中
                    movie.cover_path = self.client.add_uri(movie.cover_addr)
                    logger.info("submitted cover downlaod task: %s", movie.title)
                except Exception as e:
                    logger.exception("Submit cover task for: %s  error: %s", movie.title, e)
            else:
                logger.info("Cover of %s is None.", movie.title)

            if movie.addr:
                try:
                    # 将任务ID暂存在path字段中
                    movie.movie_path = self.client.add_uri(movie.addr)
                    logger.info("submitted movie downlaod task: %s", movie.title)
                except Exception as e:
                    logger.exception("Submit movie task for: %s error: %s", movie.title, e)
            else:
                logger.info("Addr of %s is None.", movie.title)

            if movie.cover_path or movie.movie_path:
                movie.status = MOVIE_ST_DOWNLOADING

    def update_stats(self):
        """
        更新下载的电影
        """
        available_movies = [item.__dict__ for item in self.movies if item.status]
        if available_movies:
            manager = MovieDbManager()
            count = manager.update_download_stats(available_movies)
            logger.info("submit %s movie to download", count)

    def run(self):
        # 查询数据
        self.get_movies()
        self.download_source()
        self.update_stats()


def download_movie():
    start = time.time()
    try:
        StatsUpdater().run()
    finally:
        end = time.time()
        logger.info("submit task use %.2s s", end - start)


def asker_cover():
    """
    检测封面下载任务是否下载完成，回写文件路劲
    """
    manager = MovieDbManager()
    rows = manager.query_downloading_movies()
    logger.info("Got downloading movies %s.", len(rows))
    client = Aria2Client(host=aria2_host, secret=aria2_secret)
    for row in rows:
        hash_id, title, cover_gid, movie_gid = row
        if cover_gid:
            result = client.tell_status(cover_gid)
            if result['status'] == "complete":
                cover_path = result['files']['path']
                print(cover_path)

