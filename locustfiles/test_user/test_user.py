"""

压测user的模块,场景为用户登录\浏览一个网页\退出这一场景


"""

import logging
import random
import sys
import time

from locust import HttpUser, between, task
from loguru import logger

from src.utils.locust_report import manual_report, measure


class QuickUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:5001"

    @task
    def hello(self):
        # resp = self.client.get("/api/auto_pytest/get_suite_list")
        logger.info(
            "this log message will go wherever the other locust log messages go"
        )
        # logging.info("this log message will go wherever the other locust log messages go")
        # logging.info(resp.text)
        with manual_report(
            "hello",
        ):
            logger.info(f"请求路径: /api/auto_pytest/get_suite_list,")
            # logging.info(f"请求路径: /api/auto_pytest/get_suite_list,")
            time.sleep(random.randint(1, 3))
