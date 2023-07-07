# aria2 client
# 2023 7 4
import time
from pprint import pprint
from typing import Any

import requests


class Client(object):
    """
    aria2 client
    参考：https://aria2.github.io/ma
    nual/en/html/aria2c.html#methods
    https://github.com/pawamoy/aria2p/blob/master/src/aria2p/client.py
    """

    def __init__(self, host: str, port: int = 6800, secret: str = ""):
        self.host = host
        self.port = port
        self.secret = secret

    @property
    def server_addr(self) -> str:
        return f"{self.host}:{self.port}/jsonrpc"

    def call(self, method: str, params: list = None, msg_id: str = None, need_secret: bool = True) -> dict:
        params = params or []
        if need_secret:
            params.insert(0, f"token:{self.secret}")

        payload = self.make_payload(method, params, msg_id)
        pprint(payload)
        resp = self._post(payload)
        return resp

    def _post(self, payload: dict):
        resp = requests.post(self.server_addr, json=payload).json()
        if 'error' in resp:
            print(resp)
            raise Exception("Error code:{code} {message}".format(**resp['error']))
        return resp['result']

    @staticmethod
    def make_payload(method: str, params: list = None, msg_id: str = None) -> dict:
        payload = {"jsonrpc": '2.0', "method": method}
        if msg_id:
            payload['id'] = msg_id
        else:
            payload['id'] = "-1"
        if params:
            payload['params'] = params

        return payload

    def list_methods(self):
        method = "system.listMethods"
        r = self.call(method)
        return r

    def add_uri(self, addr):
        """
        添加单个下载任务
        """
        method = "aria2.addUri"
        params = [[addr]]
        msg_id = "msg"
        r = self.call(method, params=params, msg_id=msg_id, need_secret=True)
        return r

    def tell_status(self, gid: str) -> dict:
        method = "aria2.tellStatus"
        params = [gid]
        msg_id = "myid"
        r = self.call(method, params, msg_id, need_secret=True)
        return r
