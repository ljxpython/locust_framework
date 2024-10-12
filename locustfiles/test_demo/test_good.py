"""

这是一个demo,假如我们有一个获取good的场景需要压测


"""

import logging
import random
import sys
import time

from locust import HttpUser, between, task
from loguru import logger

from src.utils.locust_report import manual_report, measure


class QuickstartUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:5001"

    @task
    def world(self):
        # resp = self.client.get("/api/auto_pytest/get_suite_list")
        logger.info(
            "this log message will go wherever the other locust log messages go"
        )
        # logging.info(resp.text)
        with manual_report("world"):
            logger.info(f"请求路径: /api/auto_pytest/get_suite_list,")
            time.sleep(random.randint(1, 3))
