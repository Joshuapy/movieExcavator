
# 23/7/3
# 读取待评估记录，根据评分和类别判断是否下载，将判断结果回写数据
# 库
# 实现方式借鉴：django.contrib.auth.authenticate方法


import logging
from collections import namedtuple

from model.movie import (MoviveDbManager, MOVIE_ST_LIKE, MOVIE_ST_DISLIKE,
                         MOVIE_ST_PAUSE)


logger = logging.getLogger(__name__)


class SimpleMovie(object):
    def __init__(self, hash_id, title, tags: str, score: float, status: int):
        self.hash = hash_id
        self.title = title
        self.tags = tags
        self.score = score
        self.status = status


class BaseBackends(object):
    def check(self, m: SimpleMovie) -> bool:
        """
        判断方法，不同的后端具体实现内容
        """
        return True


class ScoreBackends(BaseBackends):
    """
    高分电影判断
    """
    HIGH = 8.0

    def check(self, m: SimpleMovie) -> bool:
        if m.score >= self.HIGH:
            logger.info("High score movie: [%s]%s", m.hash, m.title)
            return True
        return False


class TagsBackends(BaseBackends):
    """
    根据标签，选择喜好的电影
    """
    N = 15
    tag_weight = {
        "纪录片": 10,
        "音乐": 0,
        "运动": 0,
        "西部": 0,
        "科幻": 10,
        "犯罪": 0,
        "爱情": 0,
        "灾难": 10,
        "武侠": 5,
        "歌舞": 0,
        "战争": 10,
        "惊悚": 0,
        "悬疑": 0,
        "恐怖": -10,
        "家庭": 0,
        "奇幻": 10,
        "喜剧": 0,
        "同性": -10,
        "古装": 0,
        "历史": 0,
        "动画": 5,
        "动作": 5,
        "剧情": 0,
        "冒险": 5,
        "传记": 0,
    }

    def check(self, m: SimpleMovie) -> bool:
        # TODO
        if m.tags is None:
            return False
        tag_list = m.tags.split(",")
        total_weight = self.sum_weight(tag_list)
        logger.info("total weight %s of %s", total_weight, m.title)
        return total_weight >= self.N

    def sum_weight(self, tags: list) -> int:
        total_weight = sum(self.tag_weight.get(i, 0) for i in tags)
        return total_weight


def get_movies():
    """
    查询待评审的电影条目（status=0）
    return: list of SimpleMovie
    """
    manager = MoviveDbManager()
    rows = manager.query_status(status=MOVIE_ST_PAUSE)
    logger.info("Got %s movies.", len(rows))
    return [SimpleMovie(*item) for item in rows]


def update_movie_status(movies: list) -> None:
    """
    回写选中电影的状态
    """
    manager = MoviveDbManager()
    count = manager.update_status([item.__dict__ for item in movies])
    logger.info("update %s movie status.", count)


# 判断器，注意注册顺序
JUDGEMENT_BACKENDS = [ScoreBackends, TagsBackends]


def run():
    """
    # 获得状态是「待评审」(0)的数据, 并依次判断
    """
    movies = get_movies()
    if movies:
        for movie in movies:
            for backend in JUDGEMENT_BACKENDS:
                if backend().check(movie):
                    movie.status = MOVIE_ST_LIKE
                    break
            else:
                movie.status = MOVIE_ST_DISLIKE

        update_movie_status(movies)

