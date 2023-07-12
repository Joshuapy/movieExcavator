

from bs4 import BeautifulSoup
from gather import DyttGather
from model.movie import Movie


class TestGather(object):

    def test_href_suffix(self):
        tag = BeautifulSoup("<a href='xx/321x.html'></a>", "html.parser").a
        d = DyttGather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is False

    def test_href_suffix2(self):
        tag = BeautifulSoup("<a href='xx/321.html'></a>", "html.parser").a
        d = DyttGather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is True

    def test_href_suffix3(self):
        tag = BeautifulSoup("<p class='some'></a>", "html.parser").p
        d = DyttGather()
        result = d.tag_a_and_has_href_with_number(tag)
        assert result is False

    def test_parse_detail(self):
        m = Movie()
        with open('test/dytt_detail_page2.html') as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            DyttGather()._parse_detail(m, soup=soup)
            assert 1 > 0

    def test_meta_redirect(self):
        base_url = "https://dytt8.net"
        text = '<meta http-equiv="refresh" content="0;URL=index2.htm">'
        url = DyttGather.meta_redirect(base_url, text)
        print(url)
        assert url == "https://dytt8.net/index2.htm"
