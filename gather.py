
# 电影信息收集器，(一个网站一个类处理独特的获取流程,需要产出相同的数据对象)

from abc import ABC

import requests
from pathlib import Path
from bs4 import BeautifulSoup

from model.movie import Movie, MoviveManager


class MovieGather(ABC):
    """
    电影元数据收集器
    """
    movies = []  # list of movie objects

    def save2db(self):
        """
        保存数据到db
        :return:
        """
        raise NotImplementedError

    def run(self):
        """
        启动入口
        :return:
        """
        raise NotImplementedError


class DYTTgather(MovieGather):
    base_host = "https://dytt8.net"

    def __init__(self):
        self._movie_hash = {}
        self.session = requests.session()

    def _http_home(self):
        """
        请求首页
        :return:
        """
        try:
            resp = self.session.get(self.base_host)
            resp.raise_for_status()
        except Exception as e:
            print("Access homepage error: %s" % e)
        else:
            return resp.text


    @staticmethod
    def _parse_hash_id(uri):
        return Path(uri).stem

    def _parse_home_bd3l(self, soup: BeautifulSoup):
        """
        解析首页左侧区域(class=bd3l)
        :return:
        """
        tag_bd3l = soup.find(name='div', attrs={'class': "bd3l"})
        if tag_bd3l is None:
            print("somthing")
            return

        for tag_a in tag_bd3l.find_all('a'):
            uri_path = tag_a.get('href')
            hash_id = self._parse_hash_id(uri_path)
            uri = self.base_host + uri_path
            self._movie_hash.setdefault(hash_id, uri)

    def run(self):
        home_text = self._http_home()
        if home_text is None:
            return

        soup = BeautifulSoup(home_text, "html.parser")
        self._parse_home_bd3l(soup)

        print(self._movie_hash)


