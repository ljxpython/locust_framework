"""
自定义事务指标统计
Example of a manual_report() function that can be used either as a context manager
(with statement), or a decorator, to manually add entries to Locust's statistics.

Usage as a context manager:

    with manual_report("stats entry name"):
        # Run time of this block will be reported under a stats entry called "stats entry name"
        # do stuff here, if an Exception is raised, it'll be reported as a failure

Usage as a decorator:

    @task
    @manual_report
    def my_task(self):
       # The run time of this task will be reported under a stats entry called "my task" (type "Transaction").
       # If an Exception is raised, it'll be reported as a failure


Useage measure:

    start_time = time.time()
    # do stuff here
    measure("my task", start_time)
    # or with  exception
    measure("my task", start_time, ex)
"""

import time
from contextlib import contextmanager
from enum import Enum
from typing import Callable

from locust import events


class ReportStrategy(Enum):
    """报告策略"""

    COMBINE = 1  # 成功失败合并成一条记录
    SEPARATE = 2  # 成功失败分开记录
    ALL = 3  # 三条记录，成功，失败，成功&失败


def measure(
    name: str,
    start_time: int | float,
    exception: Exception | None = None,
    end_time: int | float = 0,
    request_type: str = "Transaction",
    context: dict | None = None,
    response_length: int = 0,
    strategy: ReportStrategy = ReportStrategy.ALL,
):
    """自定义事务指标统计

    Args:
        name (str): 指标名称
        start_time (int | float): 事务开始时间
        end_time (int | float, optional): 事务结束时间. Defaults to time.time().
        exception (Exception | None, optional): 事务异常. Defaults to None.
        request_type (str, optional): 请求类型. Defaults to "Transaction".
        response_length (int, optional): 请求长度. Defaults to 0.
        strategy (ReportStrategy, optional): 指标记录策略. Defaults to ReportStrategy.ALL.
        context (dict | None, optional): 上下文. Defaults to None.
    """
    if not end_time:
        end_time = time.time()
    response_time = (end_time - start_time) * 1000
    request_meta = {
        "request_type": request_type,
        "name": name,
        "response_length": response_length,
        "context": context or {},
        "exception": exception,
        "start_time": start_time,
        "response_time": response_time,
    }

    if strategy in [ReportStrategy.ALL, ReportStrategy.COMBINE]:
        events.request.fire(**request_meta)
    if strategy in [ReportStrategy.ALL, ReportStrategy.SEPARATE]:
        request_meta["name"] = name + "[SUCCESS]"
        if exception:
            request_meta["name"] = name + "[FAILURE]"
        events.request.fire(**request_meta)


@contextmanager
def manual_report(name: str, strategy: ReportStrategy = ReportStrategy.ALL):
    start_time = time.time()
    exception = None
    try:
        yield
    except Exception as ex:  # pylint: disable=broad-exception-caught
        # 已知问题: 如果在方法内使用了 ResponseContextManager 且调用了 response.success() 或者 response.failure() 或者抛出了 Response 异常
        # ResponseContextManager 会处理异常，并不会传递出来，导致无法识别到失败，被统计为成功。
        # 例如:
        # with self.client.get(f"/get", catch_response=True) as resp:
        #   if resp.status >= 400:
        #       resp.failure(f"{resp.status=}")
        #       raise ResponseError(f"ERROR {resp.status=}")
        # 解决： 要正确统计，需要避免使用 ResponseContextManager 或者抛出非 ResponseError 异常
        exception = ex
        raise
    finally:
        measure(
            name=name, start_time=start_time, exception=exception, strategy=strategy
        )
