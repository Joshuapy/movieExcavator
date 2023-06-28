
# 电影对象模型


class Movie(object):
    status_dict = {
        0: "待评估",
        1: "不喜欢",
        2: "下载中",
        3: "下载完成"
    }

    def __init__(self):
        self.db_id = None
        self.title = None                   # 电影名
        self.hash = None                    # 唯一标识
        self.release_time = None            # 发布时间
        self.cover_addr = None              # 封面url
        self.cover_path = None              # 封面本地路径
        self.tags = None                    # 类型标签
        self.show_time = None               # 上映时间
        self.score = None                   # 机构评分
        self.describtion = None             # 简介
        self.addr = None                    # 下载地址
        self.area = None                    # 产地
        self.status = None                  # 下载状态


class MoviveManager(object):
    """
    数据库交互收敛到此类
    """
    def __init__(self, db: str):
        self._db = db

    def query_by_hash(self, hash: str) -> Movie:
        sql = f'''select * from xx where hash = '{hash}';'''
        return Movie(title="xxx")

    def save(self):
        """
        保存记录到db
        :return:
        """
        pass