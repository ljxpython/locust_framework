"""

这是一个demo,假如我们有一个获取good的场景需要压测


"""

import time
from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:5001"

    @task
    def hello_world(self):
        self.client.get("/api/auto_pytest/get_project_list")
