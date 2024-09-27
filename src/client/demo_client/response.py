import jmespath
from requests import Response


class FlaskResponse:

    def __init__(self, resp: Response):
        self.resp = resp
        self.url = self.resp.url
        self.status_code = self.resp.status_code
        self.request_time = self.resp.elapsed
        try:
            self.json = self.resp.json()
        except:
            self.json = {}

    def search(self, expr, data, *args, **kwargs):
        return jmespath.search(expr, data, *args, **kwargs)

    def get_body_result_expression(self, expression):
        return self.search(expression, self.get_body())

    def get_body(self):
        try:
            body = self.resp.json()["data"]
        except Exception as e:
            raise Exception("data is not json\n exception:{}".format(e))
        return body
