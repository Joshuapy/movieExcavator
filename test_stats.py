

from logger import init_logger
from model.movie import MovieDbManager
from stats import asker

logger = init_logger()

class TestJudgment(object):

    def test_download_status(self):
        data = [
            {"hash": "63922",
             "status": 3,
             "cover_path": "xxx",
             "movie_path": "yyy"}
        ]
        manager = MovieDbManager()
        c = manager.update_download_stats(data)
        assert c > 0

class TestAsker():
    def test_asker(self):
        data = asker()
        print(data[0])
        assert data
