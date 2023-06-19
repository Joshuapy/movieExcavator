

from bs4 import BeautifulSoup
from gather import DYTTgather


class TestGather(object):

    def test_href_suffix(self):
        tag = BeautifulSoup("<a href='xx/321x.html'></a>", "html.parser").a
        d = DYTTgather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is False

    def test_href_suffix2(self):
        tag = BeautifulSoup("<a href='xx/321.html'></a>", "html.parser").a
        d = DYTTgather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is True

    def test_href_suffix3(self):
        tag = BeautifulSoup("<p class='some'></a>", "html.parser").p
        d = DYTTgather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is False
