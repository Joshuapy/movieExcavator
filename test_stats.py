

from model.movie import MovieDbManager


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

