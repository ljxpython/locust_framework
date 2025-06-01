import asyncio
import os
import time
from datetime import datetime

from locust import HttpUser, between, events, run_single_user, task
from locust.runners import WorkerRunner

from src.utils.locust_report import manual_report, measure
from src.utils.rendezvous import Rendezvous

num = 0
lock = asyncio.Lock()


def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {"true", "yes", "1"}:
        return True
    elif value.lower() in {"false", "no", "0"}:
        return False
    raise ValueError(f"Invalid boolean value: {value}")


@events.init_command_line_parser.add_listener
def _(parser):
    parser.add_argument(
        "--product_id",
        type=str,
        env_var="product_id",
        default="1925511528732168192",
        help="测试业务",
    )
    parser.add_argument(
        "--node_num", type=int, env_var="node_num", default=1, help="测试的node数量"
    )
    parser.add_argument(
        "--pod_num", type=int, env_var="pod_num", default=1, help="测试的pod数量"
    )
    parser.add_argument(
        "--loop_num", type=int, env_var="loop_num", default=1, help="执行的轮数"
    )
    parser.add_argument(
        "--is_rendezvous", type=str_to_bool, default=False, help="是否使用集合点"
    )
    parser.add_argument(
        "--rendezvous_num",
        type=int,
        env_var="rendezvous_num",
        default=1,
        help="集合点的数量",
    )


@events.test_start.add_listener
def _(environment, **kw):
    print(f"Custom argument supplied: {environment.parsed_options.product_id}")
    # # 集合点
    # rendezvous = Rendezvous(relase_when=environment.parsed_options.rendezvous_num)


@events.test_start.add_listener
def init_shared_service(environment, **kwargs):
    # 仅在Master节点或独立运行模式初始化
    if not isinstance(environment.runner, WorkerRunner):
        environment.shared = Rendezvous(environment.parsed_options.rendezvous_num)
        print("实例化集合点")


@events.test_start.add_listener
def set_report_name(environment, **kwargs):
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    params = f"pid{environment.parsed_options.product_id}_loop{environment.parsed_options.loop_num}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    environment.parsed_options.csv = f"{script_name}_{params}_{timestamp}"
    environment.parsed_options.html = f"{script_name}_report_{timestamp}.html"


class WebsiteUser(HttpUser):
    host = "127.0.0.1"

    @task
    def my_task(self):
        global num
        print("test")
        num += 1
        print(f"num:{num}")
        time.sleep(1)
        loop_num = self.environment.parsed_options.loop_num
        print(f"loop_num:{loop_num}")
        print(f"is_rendezvous:{self.environment.parsed_options.is_rendezvous}")
        print(type(self.environment.parsed_options.is_rendezvous))
        with manual_report("my_task"):
            time.sleep(1)
        # 使用measure更加灵活
        # measure(name="order", start_time=start_time,end_time=status['time'],exception=LocustError(f"host_id: {host} 订购失败"))
        if self.environment.parsed_options.is_rendezvous:
            with self.environment.shared:
                with manual_report("my_task"):
                    time.sleep(1)
        if loop_num < num:
            self.environment.runner.quit()  # 强制停止所有虚拟用户

            print(f"my_argument={self.environment.parsed_options.my_argument}")
            print(
                f"my_ui_invisible_argument={self.environment.parsed_options.my_ui_invisible_argument}"
            )
        time.sleep(1)


if __name__ == "__main__":
    run_single_user(WebsiteUser)
