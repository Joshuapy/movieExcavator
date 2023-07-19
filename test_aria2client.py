from pprint import pprint

from lib.aria2_client import Aria2Client

from logger import init_logger
from config import aria2_host, aria2_secret

logger = init_logger()


class TestClient(object):
    secret = "xxx"

    def test_list_method(self):
        c = Aria2Client(host=aria2_host, port=6800, secret=aria2_secret)
        r = c.list_methods()
        print(r)
        assert len(r) > 0

    def test_add_uri(self):
        # addr = "https://img9.doubanio.com/view/photo/l_ratio_poster/public/p2887641712.jpg"
        addr = "magnet:?xt=urn:btih:d384685e287bc8abb25bcadf925166417e9112ce&dn=%e7%94%b5%e5%bd%b1%e5%a4%a9%e5%a0%82dygod.org.%e9%93%83%e8%8a%bd%e4%b9%8b%e6%97%85.2022.BD.1080P.%e6%97%a5%e8%af%ad%e4%b8%ad%e8%8b%b1%e5%8f%8c%e5%ad%97.mkv&tr=udp%3a%2f%2ftracker.opentrackr.org%3a1337%2fannounce&tr=udp%3a%2f%2fexodus.desync.com%3a6969%2fannounce"
        c = Aria2Client(host=aria2_host, port=6800, secret=aria2_secret)
        r = c.add_uri(addr)
        print(r)

        result = c.tell_status(r)
        print(result)
        assert 2 > 1

    def test_tell_status(self):
        # gid = "a6b7609c9b671def"
        gid = "a6d6207bfbcbf9af"
        c = Aria2Client(host=aria2_host, port=6800, secret=aria2_secret)
        r = c.tell_status(gid)
        r.pop('bittorrent')
        pprint(r)
        assert 2 > 1
