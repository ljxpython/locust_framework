"""
多渠道消息通知服务

支持飞书、钉钉、邮件、企业微信等多种通知方式
"""

import json
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MimeMultipart
from email.mime.text import MimeText
from typing import Dict, List, Optional

import requests

from conf.config import settings
from src.utils.log_moudle import logger


class NotificationChannel(ABC):
    """通知渠道抽象基类"""

    @abstractmethod
    def send_message(self, message: str, **kwargs) -> bool:
        """发送消息"""
        pass


class FeishuNotification(NotificationChannel):
    """飞书通知"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8",
        }

    def send_message(self, message: str, msg_type: str = "text", **kwargs) -> bool:
        """发送飞书消息"""
        try:
            if msg_type == "text":
                data = {"msg_type": "text", "content": {"text": message}}
            elif msg_type == "card":
                data = self._build_card_message(message, **kwargs)
            else:
                data = {"msg_type": "text", "content": {"text": message}}

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("飞书消息发送成功")
                return True
            else:
                logger.error(
                    f"飞书消息发送失败: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"发送飞书消息异常: {e}")
            return False

    def _build_card_message(self, message: str, **kwargs) -> Dict:
        """构建卡片消息"""
        card_data = {
            "msg_type": "interactive",
            "card": {
                "elements": [
                    {"tag": "div", "text": {"content": message, "tag": "lark_md"}}
                ],
                "header": {
                    "title": {
                        "content": kwargs.get("title", "性能测试通知"),
                        "tag": "plain_text",
                    }
                },
            },
        }

        # 添加额外字段
        if kwargs.get("fields"):
            for field in kwargs["fields"]:
                card_data["card"]["elements"].append({"tag": "div", "fields": field})

        return card_data


class DingTalkNotification(NotificationChannel):
    """钉钉通知"""

    def __init__(self, webhook_url: str, secret: str = None):
        self.webhook_url = webhook_url
        self.secret = secret
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    def send_message(self, message: str, msg_type: str = "text", **kwargs) -> bool:
        """发送钉钉消息"""
        try:
            if msg_type == "text":
                data = {"msgtype": "text", "text": {"content": message}}
            elif msg_type == "markdown":
                data = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": kwargs.get("title", "性能测试通知"),
                        "text": message,
                    },
                }
            else:
                data = {"msgtype": "text", "text": {"content": message}}

            # 添加@功能
            if kwargs.get("at_mobiles") or kwargs.get("at_all"):
                data["at"] = {
                    "atMobiles": kwargs.get("at_mobiles", []),
                    "isAtAll": kwargs.get("at_all", False),
                }

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("钉钉消息发送成功")
                    return True
                else:
                    logger.error(f"钉钉消息发送失败: {result}")
                    return False
            else:
                logger.error(f"钉钉消息发送失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"发送钉钉消息异常: {e}")
            return False


class EmailNotification(NotificationChannel):
    """邮件通知"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
    ):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def send_message(
        self,
        message: str,
        subject: str = "性能测试通知",
        to_emails: List[str] = None,
        **kwargs,
    ) -> bool:
        """发送邮件"""
        if not to_emails:
            logger.warning("未指定收件人邮箱")
            return False

        try:
            # 创建邮件对象
            msg = MimeMultipart()
            msg["From"] = self.username
            msg["To"] = ", ".join(to_emails)
            msg["Subject"] = subject

            # 添加邮件正文
            if kwargs.get("html", False):
                msg.attach(MimeText(message, "html", "utf-8"))
            else:
                msg.attach(MimeText(message, "plain", "utf-8"))

            # 连接SMTP服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"邮件发送成功，收件人: {to_emails}")
            return True

        except Exception as e:
            logger.error(f"发送邮件异常: {e}")
            return False


class WeChatWorkNotification(NotificationChannel):
    """企业微信通知"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json; charset=utf-8"}

    def send_message(self, message: str, msg_type: str = "text", **kwargs) -> bool:
        """发送企业微信消息"""
        try:
            if msg_type == "text":
                data = {"msgtype": "text", "text": {"content": message}}
            elif msg_type == "markdown":
                data = {"msgtype": "markdown", "markdown": {"content": message}}
            else:
                data = {"msgtype": "text", "text": {"content": message}}

            response = requests.post(
                self.webhook_url,
                headers=self.headers,
                data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                timeout=10,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("企业微信消息发送成功")
                    return True
                else:
                    logger.error(f"企业微信消息发送失败: {result}")
                    return False
            else:
                logger.error(f"企业微信消息发送失败: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"发送企业微信消息异常: {e}")
            return False


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
