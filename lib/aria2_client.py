# aria2 client
# 2023 7 4
from typing import Any

import requests


class Client(object):
    """
    aria2 client
    参考：https://aria2.github.io/manual/en/html/aria2c.html#methods
    https://github.com/pawamoy/aria2p/blob/master/src/aria2p/client.py
    """

    def __init__(self, host: str, port: int = 6800, secret: str = ""):
        self.host = host
        self.port = port
        self.secret = secret

    @property
    def server_addr(self) -> str:
        return f"{self.host}:{self.port}/jsonrpc"

    def call(self, method: str,
             params: str = None,
             msg_id: str = None,
             need_secret: bool = True) -> dict:
        params = params or []
        if need_secret:
            params.insert(0, f"token: {self.secret}")

        payload = self.make_payload(method, params, msg_id)
        resp = self._post(payload)
        return resp

    def _post(self, payload: dict):
        resp = requests.post(self.server_addr, json=payload).json()
        return resp

    @staticmethod
    def make_payload(method: str, parmas: list = None,
                     msg_id: str = None) -> dict[str: Any]:
        payload = {"jsonrpc": 2.0, "method": method}
        if msg_id:
            payload['id'] = msg_id
        else:
            payload['id'] = "-1"
        if parmas:
            payload['params'] = parmas

        return payload

    def list_methods(self):
        method = "system.listmethods"
        r = self.call(method)
        return r
