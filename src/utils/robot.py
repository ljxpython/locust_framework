"""
飞书或者其他的消息

"""

import json

import requests

custom_robot_url = "this is web hook url"

data = '{"msg_type":"text","content":{"text":"request example"}}'

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
    "Content-Type": "application/json; charset=utf-8",
}


## 普通文本
"""
格式：
{
    "receive_id": "ou_7d8a6e6df7621556ce0d21922b676706ccs",
    "content": "{\"text\":\" test content\"}",
    "msg_type": "text"
}
如果需要文本中进行换行，需要增加转义
{
    "receive_id": "oc_xxx",
    "content": "{\"text\":\"firstline \\n second line  \"}",
    "msg_type": "text"
}
"""


## 富文本


## 卡片消息
"""

参数：

## 通用的卡片类型
{

}


## 消息卡片中艾特其他人
// at 指定用户
	<at id=ou_xxx></at> //使用open_id at指定人
	<at id=b6xxxxg8></at> //使用user_id at指定人
	<at email=test@email.com></at> //使用邮箱地址 at指定人
// at 所有人
	<at id=all></at>

"""

## 正文

data_format = {
    "msg_type": "interactive",
    "card": {
        "elements": [],
        "header": {},
        "config": {"wide_screen_mode": True},
    },
}


class CustomRobotMessage(object):
    def __init__(self, url, data_format):
        self.url = url
        self.data_format = data_format
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8",
        }
        self.elements: list = self.data_format["card"]["elements"]
        self.content_header: dict = self.data_format["card"]["header"]
        """
        需提供一个地址，一个
        """
        pass

    def send_message(self):
        r = requests.post(
            self.url, headers=self.headers, data=json.dumps(self.data_format)
        )
        self.clear_message()
        return r

    def clear_message(self):
        self.data_format["card"]["elements"] = []
        self.data_format["card"]["header"] = {}
        pass

    def write_title(self, content: str = None, type: str = "green"):
        """
        支持markdown语法
        :param content:
        :return:
        """
        title_style = {
            "template": type,
            "title": {"content": content, "tag": "plain_text"},
        }
        self.data_format["card"]["header"] = title_style

    def write_title_warning(self, content: str = None):
        return self.write_title(content=content, type="red")

    def write_title_pass(self, content: str = None):
        return self.write_title(content=content, type="green")

    def write_body(self, content):
        """
        正文
        :param content:
        :return:
        """
        body_style = {
            "tag": "markdown",
            "content": content,
        }
        self.data_format["card"]["elements"].append(body_style)

    def write_body_sendmessage(self, content):
        """
        正文
        :param content:
        :return:
        """
        body_style = {
            "tag": "markdown",
            "content": content,
        }
        self.data_format["card"]["elements"].append(body_style)
        self.send_message()

    def write_line(self):
        """
        写入下划线
        :return:
        """
        self.elements.append({"tag": "hr"})

    def write_picture(self, content, token):
        """
        写入图片
        传入的参数为图片地址和描述文字

        :return:
        """
        picture_style = {
            "alt": {"content": content, "tag": "plain_text"},
            "img_key": token,
            "tag": "img",
        }
        self.data_format["card"]["elements"].append(picture_style)

    def write_link(self, content: str = "跳转按钮", url: str = "https://baidu.cn"):
        """
        一个button，里面有地址
        :param url:
        :return:
        """
        link_style = {
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": content},
                    "type": "primary",
                    "url": url,
                }
            ],
        }
        self.data_format["card"]["elements"].append(link_style)


robot = CustomRobotMessage(url=custom_robot_url, data_format=data_format)


if __name__ == "__main__":

    pass
