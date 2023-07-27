# aria2 client
# 2023 7 4
import logging
import time

import requests


logger = logging.getLogger(__name__)


class Aria2Client(object):
    """
    aria2 client
    参考：https://aria2.github.io/manual/en/html/aria2c.html#methodshttps://github.com/pawamoy/aria2p/blob/master/src/aria2p/client.py
    """

    def __init__(self, host: str, port: int = 6800, secret: str = None):
        self.host = host
        self.port = port
        self.secret = secret
        self.session = requests.session()

    @property
    def server_addr(self) -> str:
        """
        例如：http://ariang.joshua.com:6800/jsonrpc
        """
        return f"{self.host}:{self.port}/jsonrpc"

    def call(self, method: str, params: list = None, msg_id: str = None,
             need_secret: bool = True) -> dict:
        params = params or []
        if need_secret:
            params.insert(0, f"token:{self.secret}")

        payload = self.make_payload(method, params, msg_id)
        logger.debug("payload: %s", payload)
        resp = self._post(payload)
        return resp

    def _post(self, payload: dict):
        resp = self.session.post(self.server_addr, json=payload).json()
        logger.debug("response: %s", resp)
        if 'error' in resp:
            raise Exception("Error code:{code} {message}".format(**resp['error']))
        return resp['result']

    @staticmethod
    def make_payload(method: str, params: list = None, msg_id: str = None) -> dict:
        payload = {"jsonrpc": '2.0', "method": method}
        if msg_id:
            payload['id'] = msg_id
        else:
            payload['id'] = str(int(time.time() * 1000))
        if params:
            payload['params'] = params

        return payload

    def list_methods(self):
        method = "system.listMethods"
        r = self.call(method)
        return r

    def add_uri(self, addr) -> str:
        """
        添加单个下载任务
        return: aria2 任务ID gid
        """
        method = "aria2.addUri"
        params = [[addr]]
        r = self.call(method, params=params, need_secret=True)
        return r

    def tell_status(self, gid: str) -> dict:
        """
        :return:
        {'bitfield': 'f0',
         'completedLength': '65536',
         'connections': '0',
         'dir': '/downloads',
         'downloadSpeed': '0',
         'files': [{'completedLength': '65536',
                    'index': '1',
                    'length': '79574',
                    'path': '[METADATA]阳光电影www.ygdy8.com.门徒.2007.1080p.国粤双语中字.mkv',
                    'selected': 'true',
                    'uris': []}],
         'gid': '4312f93e75f4fb13',
         'infoHash': 'e5839d842fa369b53c40e519441415bef1312545',
         'numPieces': '5',
         'numSeeders': '0',
         'pieceLength': '16384',
         'seeder': 'false',
         'status': 'active',
         'totalLength': '79574',
         'uploadLength': '0',
         'uploadSpeed': '0'}
        """
        method = "aria2.tellStatus"
        # params = [gid, ['gid', 'status', 'errorMessage']]
        params = [gid]
        r = self.call(method, params, need_secret=True)
        return r
