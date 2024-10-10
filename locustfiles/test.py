from contextlib import contextmanager
from enum import Enum
from typing import Callable, Optional

from src.utils.log_moudle import logger


# 定义报告类型
class ReportType(Enum):
    ALL_THREE = "all_three"
    TYPE_A = "type_a"
    TYPE_B = "type_b"


# 假设这是我们要实现的 _manual_report 函数
def _manual_report(name: str, report_type: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # 在这里可以执行一些报告相关的逻辑
            print(f"Generating report for {name} of type {report_type}...")
            result = func(*args, **kwargs)
            # 生成报告的后续逻辑
            print(f"Report generated for {name}.")
            return result

        return wrapper

    return decorator


# 这是上下文管理器的方式
# @contextmanager
# def _manual_report(name: str, report_type: str):
#     try:
#         print(name,report_type)
#         yield name, report_type
#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         print(f"Generating report for {name} of type {report_type}...")


# 定义 manual_report 函数
def manual_report(
    name_or_func, type: Optional[ReportType] = ReportType.ALL_THREE.value
):
    if callable(name_or_func):
        return _manual_report(name_or_func.__name__, type)(name_or_func)
    else:
        return _manual_report(name_or_func, type)


# 使用 manual_report 作为装饰器
@manual_report
def my_test_function():
    print("Running the test function...")


# 使用 manual_report 作为普通函数调用
def another_test_function():
    print("Running another test function...")


# 显式生成报告
report = manual_report("another_test_function", ReportType.TYPE_A.value)
report(another_test_function)


# 使用with的上下文管理器的方式运行
# with manual_report("my_test_function", ReportType.TYPE_B.value) as f:
#     print(f)
#     pass


# # 调用装饰器
# my_test_function()
