# 描述：状态管理,包括提交下载，查询下载状态，更新状态信息到数据库等
# 时间：23.7.19

import logging
import os.path
import time
from pathlib import Path
from pprint import pprint

from lib.aria2_client import Aria2Client
from model.movie import (MovieDbManager, MOVIE_ST_DOWNLOADING, MOVIE_ST_DONE)
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
        查询待下载的电影条目（status=2）
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
            # 8.30 取消封面下载，利用jellyfin搜刮功能自动下载封面
            # if movie.cover_addr:
            #     try:
            #         # 将任务ID暂存在path字段中
            #         movie.cover_path = self.client.add_uri(movie.cover_addr)
            #         logger.info("submitted cover downlaod task: %s", movie.title)
            #     except Exception as e:
            #         logger.exception("Submit cover task for: %s  error: %s", movie.title, e)
            # else:
            #     logger.info("Cover of %s is None.", movie.title)

            if movie.addr:
                try:
                    # 将任务ID暂存在path字段中
                    movie.movie_path = self.client.add_uri(movie.addr)
                    logger.info("submitted movie downlaod task: %s", movie.title)
                except Exception as e:
                    logger.exception("Submit movie task for: %s error: %s", movie.title, e)
            else:
                logger.info("Addr of %s is None.", movie.title)

            # if movie.cover_path or movie.movie_path:
            if movie.movie_path:
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


class StatsAsker(object):
    def __init__(self):
        self.movies = []
        self.client = Aria2Client(host=aria2_host, secret=aria2_secret)
        self.manager = MovieDbManager()

    def get_movies(self):
        self.movies = self.manager.query_downloading_movies()
        logger.info("Got downloading movies %s.", len(self.movies))

    def ask_cover(self):
        data = []
        for movie in self.movies:
            hash_id, title, cover_gid, _ = movie
            if cover_gid and not os.path.isabs(cover_gid):
                try:
                    result = self.client.tell_status(cover_gid)
                    status = result.get('status', 'unknown')
                    logger.info("cover Task: %s, title: %s, status is: %s", cover_gid, title, status)
                    if status == "complete":
                        cover_path = result['files'][0]['path']
                        data.append({'hash': hash_id, 'cover_path': cover_path})
                except Exception as e:
                    logger.error("get status from aria2 error: %s", e)
            else:
                logger.info("no available cover gid: %s, for titile: %s", cover_gid, title)

        if data:
            c = self.manager.update_cover_path(data)
            logger.info("update cover path: %s", c)

    def ask_movie(self):
        """
        查询电影下载状态
        """
        data = []
        for movie in self.movies:
            hash_id, title, _, movie_gid = movie
            if not movie_gid:
                logger.info("no gid for %s", title)
                continue

            try:
                result = self.client.tell_status(movie_gid)
            except Exception as e:
                logger.error("get status from aria2 error: %s", e)
            else:
                status = result.get('status', 'unknown')
                logger.info("MetaTask: %s, title: %s, status is: %s", movie_gid, title, status)

                if 'followedBy' in result:
                    gid = result.get('followedBy')[0]
                    result2 = self.client.tell_status(gid)
                    status = result2.get('status', 'unknown')
                    logger.info("MovieTask: %s, title: %s, status is: %s", gid, title, status)
                    if status == "complete":
                        movie_path = result2['files'][0]['path']
                        data.append({'hash': hash_id,
                                     'movie_path': movie_path,
                                     'title': title,
                                     'status': MOVIE_ST_DONE})
                else:
                    logger.info("not followedby, for gid: %s, title: %s", movie_gid, title)

        # 移动电影至媒体库
        if self.is_flag_file_exists():  # 判断媒体库是否挂载
            for movie_info in data:
                src = movie_info['movie_path']
                title = movie_info['title']
                try:
                    dst = self.putaway_2_media(src, title)
                except Exception as e:
                    logger.error("rename file: %s error: %s", src, e)
                else:
                    movie_info['movie_path'] = dst
                    self.manager.update_movie_done(movie_info)
        else:
            logger.info("no flag file for media.")

    @staticmethod
    def is_flag_file_exists() -> bool:
        filename = "/movies/mounted"
        return Path(filename).exists()

    @staticmethod
    def putaway_2_media(src, title: str) -> str:
        """
        将下载好的电影传输至媒体库目录, 规范电影名
        """
        dst_dir = Path("/movies")
        src_pathobj = Path(src)
        suffix = src_pathobj.suffix  # 后缀
        dst = dst_dir / f"{title}{suffix}"
        src_pathobj.rename(dst)
        return str(dst)

    def run(self):
        self.get_movies()
        # self.ask_cover()  # 8.30 取消封面下载
        self.ask_movie()


def download_movie():
    start = time.time()
    try:
        StatsUpdater().run()
    finally:
        end = time.time()
        logger.info("submit task use %.2s s", end - start)


def ask_movie_stats():
    start = time.time()
    try:
        StatsAsker().run()
    finally:
        end = time.time()
        logger.info("ask stats use %.2s s", end - start)
