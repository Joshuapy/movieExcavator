# 电影信息收集器，(一个网站一个类处理独特的获取流程,需要产出相同的数据对象)

import re
import logging
import time
from pprint import pprint
from urllib.parse import urljoin

import bs4
import requests
from pathlib import Path
from bs4 import BeautifulSoup

from model.movie import Movie, MoviveDbManager

logger = logging.getLogger(__name__)


class ParseError(Exception):
    pass


class BaseGather(object):
    """
    通用方法收敛
    数据库交互都在本抽象类种收敛和规范
    """
    def __init__(self):
        self.movies = []  # list of Movie obj
        self._movie_dbmanager = MoviveDbManager()

    def _add_movie(self, m: Movie):
        if m.title and m.hash and m.addr:
            self.movies.append(m)
        else:
            logger.warning("Incomplete Movie: %s", m.__dict__)

    def save2db(self):
        """
        电影信息写库
        每个线程独立db连接，保持独立。
        写库操作收敛至此，写完之后断开连接。
        :return:
        """
        try:
            c = self._movie_dbmanager.save(data=self.movies)
            logger.info("Save %s rows to db.", c)
        except Exception as e:
            logger.exception("Save rows to db error: %s", e)


class DyttGather(BaseGather):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://www.baidu.com/link?url=u5csmrd0v3OeGNX4MLsOKS6_jZzFV2qsaJyK1Vhvqk3&wd=&eqid=b3b7b46b0002d25200000003649163c7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }

    def __init__(self):
        super().__init__()
        self.base_host = "https://dytt8.net"
        self.pattern = re.compile(r"\d+\.html")  # 数字.html
        self._movie_hash = {}
        self.session = requests.session()
        self.session.headers.update(self.headers)

    def _http_detail(self, hash_id, uri: str):
        """
        请求详情页+解析
        :return:
        """
        header = {'Referer': self.base_host}
        try:
            resp = self.session.get(uri, headers=header)
            resp.encoding = resp.apparent_encoding
        except Exception as e:
            logger.error("Access detail [%s] error: %s", uri, e)
        else:
            m = Movie()
            m.hash = hash_id
            soup = BeautifulSoup(resp.text, "html.parser")
            self._parse_detail(m, soup)

    @staticmethod
    def _parse_line(m: Movie, tokens: list):
        if not tokens:
            return
        token_string = " ".join(tokens)
        attr_pattern_dict = {
            'show_time': r'^◎上映日期\s*(.*)',
            'release_time': r'^◎年\s*代\s*(.*)',
            'area': r'^◎产\s*地\s*(.*)',
            'description': r'^◎简\s*介\s*(.*)',
            'tags': r'^◎类\s*别\s*(.*)',
            'score': r'^◎豆瓣评分\s*(.*)\/10\s*from.*',
        }
        for attr, p in attr_pattern_dict.items():
            match_result = re.match(p, token_string)
            if match_result:
                value = match_result.group(1)
                if attr == "score":
                    try:
                        value = float(value)
                    except:
                        value = 0.0
                if attr == "tags":
                    value = ",".join(i.strip() for i in value.split('/'))

                m.__setattr__(attr, value)
        if m.score is None:
            m.score = 0.0

    def _parse_detail(self, m: Movie, soup: BeautifulSoup):
        """
        解析详情页
        1. 内容最近包 div.co_content8
        :return:
        """
        tag_content = soup.find('div', attrs={'class': "co_content8"})
        if tag_content is None:
            raise ParseError("Can not fond tag: co_content8!")

        # 字段必填,解析失败直接退出
        # 下载地址 + 电影名
        tag_a = tag_content.find('a')
        if tag_a:
            m.addr = tag_a.get('href')  # 下载地址
            _title = tag_a.find('font', string=re.compile(r"点击下载|磁力链")).string
            m.title = _title.split()[1]
        else:
            raise ParseError("Can not fond tag <a> of download addr!")

        tag_img = tag_content.find('img')
        m.cover_addr = tag_img.get('src')  # 封面地址

        tag_td = tag_img.parent
        token = []
        for line in tag_td.contents[:-1]:
            if line.string and str(line.string).strip():
                _content = str(line.string).strip()
                logger.debug("%s", _content)
                if _content[0] == '◎':
                    self._parse_line(m, token)
                    token = []
                    token.append(_content)
                else:
                    token.append(_content)
        if token:
            self._parse_line(m, token)

        self._add_movie(m)

    @staticmethod
    def meta_redirect(original_url, text):
        soup = BeautifulSoup(text, "html.parser")
        result = soup.find("meta", attrs={"http-equiv": "refresh"})
        if result:
            wait, content = result["content"].split(";")
            if content.strip().lower().startswith("url="):
                url = content.strip()[4:]
                if not url.startswith("http"):
                    url = urljoin(original_url, url)
                logger.debug("Meta redirect: %s", url)
                return url
        return None

    def _http_home(self, url: str = None):
        """
        请求首页
        :return:
        """
        home_url = url or self.base_host
        try:
            resp = self.session.get(home_url)
            resp.raise_for_status()
            logger.info("Access homepage: %s", resp.status_code)
        except Exception as e:
            logger.error("Access homepage error: %s", e)
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

    def tag_a_and_has_href_with_number(self, tag: BeautifulSoup):
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
            logger.warning("Parse Failed at 左区-最新电影更新")
            return

        c = 0
        for tag_a in tag_bd3l.find_all(self.tag_a_and_has_href_with_number):
            self._add_tag_a_hash(tag_a)
            c += 1
        logger.info("Parse %s uri at 左区-最新电影更新", c)

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
            logger.warning("Parse failed at 中区-新片")
            return

        # 最新电影
        tag_bd3rl = tag_bd3r.find(name='div', attrs={'class': "bd3rl"})
        # 遍历前两个电影列表块(每个块是一个table)
        c = 0
        if tag_bd3rl:
            top_area2_of_bd3rl = tag_bd3rl.find_all(name='div', attrs={'class': "co_area2"}, limit=2)
            for area in top_area2_of_bd3rl:
                for tag_a in area.find_all(self.tag_a_and_has_href_with_number):
                    self._add_tag_a_hash(tag_a)
                    c += 1
            logger.info("Parse %s uri at 中区-最新精品", c)
        else:
            logger.warning("bd3rl is None")

        # 经典推荐
        c = 0
        tag_bd3rr = tag_bd3r.find(name='div', attrs={'class': "bd3rr"})
        if tag_bd3rr:
            for area in tag_bd3rr.find_all(name='div', attrs={'class': "co_area2"}, limit=2):
                for tag_a in area.find_all(self.tag_a_and_has_href_with_number):
                    self._add_tag_a_hash(tag_a)
                    c += 1
            logger.info("Parse %s uri at 右区-经典推荐", c)

        else:
            logger.warning("bd3rr is None")

    def run(self):
        home_text = self._http_home()
        if home_text is None:
            return
        # 处理 meta refrash tag
        url = self.meta_redirect(self.base_host, home_text)
        while url:
            home_text = self._http_home(url)
            url = self.meta_redirect(url, home_text)

        # 首页采集最新电影地址
        soup = BeautifulSoup(home_text, "html.parser")
        self._parse_home_bd3l(soup)
        self._parse_new_movie(soup)

        logger.info("Fetch %s uri from homepage.", len(self._movie_hash))

        if self._movie_hash:
            # TODO: 暂时用循环,后续改成并发
            for hash_id, uri in self._movie_hash.items():
                # 判断数据库是否已存在,如果存在则忽略
                if self._movie_dbmanager.is_exists(hash_id):
                    continue
                try:
                    self._http_detail(hash_id, uri)
                except ParseError as e:
                    logger.warning(
                        "Parse DetailPage: [%s] error: %s",
                        hash_id, e)
                except AttributeError as e:
                    logger.error(
                        "Access or Parse DetailPage error: hash_id: %s. msg: %s",
                        hash_id, e)
                except Exception as e:
                    logger.exception(
                        "Access or Parse DetailPage error: hash_id: %s. msg: %s",
                        hash_id, e)
        if self.movies:
            self.save2db()


def dytt_gather():
    start = time.time()
    try:
        DyttGather().run()
    finally:
        end = time.time()
        logger.info("fetch dytt use %.2s s", end - start)
