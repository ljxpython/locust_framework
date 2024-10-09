


from locust import HttpUser, task, between
from loguru import logger
import sys
import logging

# 配置 Loguru
logger.remove()  # 移除默认处理器
logger.add(sys.stdout, level="INFO", format="{time} {level} {message}")  # 输出到控制台

# 添加自定义的日志处理程序到 Locust
def loguru_handler(message):
    logger.log(message.levelname, message.getMessage())

# 配置 Locust 的日志
logging.basicConfig(level=logging.INFO)
logging.getLogger("locust").addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger("locust").setLevel(logging.INFO)

# class MyUser(HttpUser):
#     wait_time = between(1, 5)
#
#     @task
#     def my_task(self):
#         logger.info("执行 my_task")
#         response = self.client.get("/path")  # 替换为实际路径
#         logger.info(f"请求路径: /path, 状态码: {response.status_code}")
#
#         if response.status_code == 200:
#             logger.success("请求成功")
#         else:
#             logger.error(f"请求失败，状态码: {response.status_code}")


class QuickUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:5001"

    @task
    def hello_world(self):
        resp = self.client.get("/api/auto_pytest/get_suite_list")
        logger.info("this log message will go wherever the other locust log messages go")
        # logging.info(resp.text)
