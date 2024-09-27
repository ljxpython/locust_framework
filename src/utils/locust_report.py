import time
from enum import Enum

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
