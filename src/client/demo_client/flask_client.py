import jmespath
import requests
from locust import HttpUser
from locust.clients import HttpSession, Response
from loguru import logger
from requests import Session

from conf.config import settings
from src.client.demo_client.flask_auth import ClientAuth
from src.client.demo_client.response import FlaskResponse

config = settings.flaskclient


class FlaskClient(object):
    """可以根据client适配基于locust框架及原requests框架的http请求"""

    def __init__(self, client: Session, base_url, ak, sk):
        self.client = client
        self.base_url = base_url
        self.client.auth = ClientAuth(ak, sk)
        self.ak = ak
        self.sk = sk
        self.resp: Response

    def request(self, method, path, **kwargs):
        # 处理请求
        url = self.base_url + path
        resp = self.client.request(method=method, url=url, **kwargs)
        self.resp = FlaskResponse(resp)
        return self.resp

    def get(self, path, params=None, **kwargs):
        return self.request("GET", path, params=params, **kwargs)

    def post(self, path, data=None, json=None, **kwargs):
        return self.request("POST", path, data=data, json=json, **kwargs)

    def __enter__(self):
        return self.client

    def __exit__(self, *args):
        self.client.close()


class SaturnLocustUser(HttpUser):
    """locust框架下的client"""

    abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = HttpSession(
            base_url=config.url,
            request_event=self.environment.events.request,
            user=self,
            pool_manager=self.pool_manager,
        )
        self.client = FlaskClient(
            self.client,
            config.url,
            config.ak,
            config.sk,
        )

    # 举一个例子,比如通过接口获取region
    def get_region(self):
        return self.client.get("/region", name="/get_region")
