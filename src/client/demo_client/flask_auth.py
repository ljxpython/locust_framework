"""
一个auth的demo


"""

from requests.auth import AuthBase


class ClientAuth(AuthBase):

    def __init__(self, ak: str, sk: str):
        self.ak = ak
        self.sk = sk

    def __call__(self, r):
        r.headers["test-ak"] = self.ak
        return r
