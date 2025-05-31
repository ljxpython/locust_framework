"""集合点
集合点的作用是当满足一定用户数量时，释放集合点，尽可能得保证用户的并发量。
使用方法 1:
```
# 创建集合点, 等待到 10 个用户时释放，如果用户等待时间超过 60s 则提前释放。
rendezvous =  Rendezvous(relase_when=10, timeout=60)
class MyUser(HttpUser):
    @task
    def my_task(self):
        # 模拟一些业务逻辑
        self.client.get("/")
        # 等待在集合点
        rendezvous.wait():
        # 当 10 个用户都到达集合点时,这里的代码才会执行
        execute_task()
```
使用方法 2:
```
# 创建集合点, 用户一直等待直到 10 个用户时释放。
rendezvous =  Rendezvous(relase_when=10)
class MyUser(HttpUser):
    @task
    def my_task(self):
        # 模拟一些业务逻辑
        self.client.get("/")
        # 等待在集合点
        with rendezvous:
            # 当 10 个用户都到达集合点时,这里的代码才会执行
            execute_task()
```
"""

# mypy: disable_error_code = import-untyped
import gevent
from gevent.lock import RLock, Semaphore


class Rendezvous:
    """
    集合点，当满足一定用户数量时，释放集合点，尽可能得保证用户的并发量。
    """

    def __init__(self, relase_when: int, timeout=None):
        self.relase_when = relase_when
        self.timeout = timeout
        self.wait_user_count = 0
        self.semaphore = Semaphore(1)
        self.__lock = RLock()

    def wait(self, timeout: float | None = None):
        """用户等待，直到满足集合点条件或超时后释放。
        Args:
            timeout (float, optional): 用户等待超时时间. 默认值 None , 无超时.
        """
        with self.__lock:
            if not timeout:
                timeout = self.timeout
            if self.semaphore.ready():
                self.semaphore.acquire()
            self.wait_user_count += 1
            if self.wait_user_count >= self.relase_when:
                self.wait_user_count = 0
                self.semaphore.release()
                gevent.sleep()
                return
        # 用户数量不足时等待
        # 用户等待超时时是释放，等待用户数减 1
        counter = self.semaphore.wait(timeout)
        if not counter and self.wait_user_count > 0:
            self.wait_user_count -= 1

    def __enter__(self):
        """上下文管理器进入"""
        self.wait(self.timeout)

    def __exit__(self, *args, **kwargs):
        """上下文管理器退出"""
