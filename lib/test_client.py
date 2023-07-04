

from aria2_client import Client


class TestClient(object):
    secret = "jsohua2022"

    def test_list_method(self):
        msg_id = "listmethods"
        method = "system.listMethods"
        c = Client(host="host://ariang.joshua.com", port=6800, secret=self.secret)
        r = c.call(method, msg_id=msg_id, need_secret=False)
        print(r)
        assert r['id'] == msg_id
