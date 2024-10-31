"""

压测user的模块,场景为用户登录\浏览一个网页\退出这一场景


"""

import logging
import random
import sys
import time

from locust import HttpUser, between, task,events
from loguru import logger

from src.utils.locust_report import manual_report, measure

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    # 获取并发大小
    num = environment.parsed_options.num_users
    logger.info(f"并发数: {num}")
    # 如果并发数大于10,将其修改为10
    if num > 10:
        environment.parsed_options.num_users = 10
    # 打印修改后的压测数
    logger.info(f"修改后的压测数{environment.parsed_options.num_users}")

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
            current_users = self.environment.runner.user_count
            logger.info(self.environment.runner)
            # 打印当前的测试并发量
            logger.info(f"当前并发量: {current_users}")
