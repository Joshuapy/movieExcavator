
# 电影信息收集器，(一个网站一个类处理独特的获取流程,需要产出相同的数据对象)
import re
from abc import ABC
from pprint import pprint

import bs4
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

    def __init__(self):
        self.base_host = "https://dytt8.net"
        self.pattern = re.compile(r"\d+\.html")  # 数字.html
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

    def _add_tag_a_hash(self, tag_a: bs4.Tag):
        """
        拼接地址， /xx/11.html -> 11, https:xxx.com/xx/11.html
        :param tag_a:
        :return:
        """
        uri = tag_a.get('href')
        hash_id = self._parse_hash_id(uri)
        uri = self.base_host + uri
        self._movie_hash.setdefault(hash_id, uri)

    @staticmethod
    def _parse_hash_id(uri):
        """
        '/html/gndy/jddy/20160320/50523.html' -> '50523'
        """
        return Path(uri).stem

    @staticmethod
    def tag_a_and_has_href_with_number(tag: BeautifulSoup):
        """
        链接过滤器
        :param tag:
        :return:
        """
        return tag.name == "a" and tag.has_attr('href') and re.search(self.pattern, tag['href']) is not None

    def _parse_home_bd3l(self, soup: BeautifulSoup):
        """
        解析首页左侧区域(class=bd3l)   [区域1]
        :return:
        """
        tag_bd3l = soup.find(name='div', attrs={'class': "bd3l"})
        if tag_bd3l is None:
            print("somthing")
            return

        for tag_a in tag_bd3l.find_all(self.tag_a_and_has_href_with_number):
            self._add_tag_a_hash(tag_a)

    def _parse_new_movie(self, soup: BeautifulSoup):
        """
        解析首页中部和右部区域
        第一个bd3r, 包括bd3rl里的前两个co_area2(最新电影下载 + 迅雷电影下载)
        和bd3rr前两个co_area2(最新影片推荐+经典影片推荐)
        [区域2，3,4,5]
        :return:
        """
        tag_bd3r = soup.find(name='div', attrs={'class': "bd3r"})
        if tag_bd3r is None:
            print("bd3r is None")
            return

        # 最新电影
        tag_bd3rl = tag_bd3r.find(name='div', attrs={'class': "bd3rl"})
        # 遍历前两个电影列表块(每个块是一个table)
        if tag_bd3rl:
            top_area2_of_bd3rl = tag_bd3rl.find_all(name='div', attrs={'class': "co_area2"}, limit=2)
            for area in top_area2_of_bd3rl:
                for tag_a in area.find_all(self.tag_a_and_has_href_with_number):
                    self._add_tag_a_hash(tag_a)
        else:
            print("bd3rl is None")

        print("*"*100)
        # 经典推荐
        tag_bd3rr = tag_bd3r.find(name='div', attrs={'class': "bd3rr"})
        if tag_bd3rr:
            for area in tag_bd3rr.find_all(name='div', attrs={'class': "co_area2"}, limit=2):
                for tag_a in area.find_all(self.tag_a_and_has_href_with_number):
                    self._add_tag_a_hash(tag_a)

        else:
            print("bd3rr is None")

    def run(self):
        home_text = self._http_home()
        if home_text is None:
            return

        soup = BeautifulSoup(home_text, "html.parser")
        self._parse_home_bd3l(soup)
        self._parse_new_movie(soup)

        pprint(self._movie_hash)
        pprint(len(self._movie_hash))


