

from model.movie import MoviveDbManager, Movie
from judgment import get_movies, TagsBackends


class TestJudgment(object):

    def test_status(self):
        rows = get_movies()
        print(rows)
        assert len(rows) > 0

    def test_update_status(self):
        data = []
        manager = MoviveDbManager()
        manager.update_status(data)

    def test_tagsbackend(self):
        # tags = ["动作", "科幻"]
        tags = ["动作", "犯罪"]
        w = TagsBackends().sum_weight(tags)
        print(w)
        assert w >= 15


