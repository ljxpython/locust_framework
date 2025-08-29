#!/usr/bin/env python3
"""
自定义参数示例 - 演示自定义参数和集合点功能

展示如何使用框架的自定义参数系统和集合点(Rendezvous)功能
目标：演示高级参数控制和并发同步
"""

import time

from locust import HttpUser, between, events, task
from locust.env import Environment

from src.utils.locust_report import manual_report, measure
from src.utils.rendezvous import Rendezvous


# 自定义参数转换函数
def str_to_bool(v):
    """字符串转布尔值"""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "1", "on"):
        return True
    elif v.lower() in ("no", "false", "0", "off"):
        return False
    else:
        raise ValueError(f"无法转换布尔值: {v}")


class CustomParamUser(HttpUser):
    """自定义参数用户类"""

    wait_time = between(1, 2)
    host = "http://localhost:5000"

    def on_start(self):
        """测试开始 - 获取自定义参数"""
        self.test_params = {
            "loop_num": getattr(self.environment.parsed_options, "loop_num", 1),
            "product_id": getattr(
                self.environment.parsed_options, "product_id", "test_product"
            ),
            "is_rendezvous": getattr(
                self.environment.parsed_options, "is_rendezvous", False
            ),
            "rendezvous_num": getattr(
                self.environment.parsed_options, "rendezvous_num", 1
            ),
        }

        print(f"🔧 用户参数配置: {self.test_params}")

    @task
    def custom_loop_test(self):
        """自定义循环测试"""
        loop_num = self.test_params["loop_num"]

        # 使用自定义事务报告
        with manual_report("自定义循环测试"):
            for i in range(loop_num):
                # 执行API调用
                response = self.client.get(
                    f"/api/products/{self.test_params['product_id']}",
                    name=f"循环测试-{i+1}",
                )

                # 模拟处理时间
                time.sleep(0.1)

                if response.status_code != 200:
                    break

    @task
    def rendezvous_test(self):
        """集合点测试"""
        if not self.test_params["is_rendezvous"]:
            # 非集合点模式，直接执行
            self._execute_critical_section()
            return

        # 集合点模式 - 等待其他用户到达
        rendezvous_count = self.test_params["rendezvous_num"]

        try:
            # 使用集合点等待其他用户
            with self.environment.shared:
                print(f"🚥 用户已到达集合点，等待其他 {rendezvous_count-1} 个用户...")
                # 所有用户同时执行关键业务
                self._execute_critical_section()
        except AttributeError:
            # 如果集合点未初始化，则直接执行
            print("⚠️  集合点未初始化，直接执行业务逻辑")
            self._execute_critical_section()

    def _execute_critical_section(self):
        """执行关键业务逻辑"""
        start_time = time.time()

        try:
            # 模拟关键业务：创建订单
            order_data = {
                "products": [
                    {"product_id": self.test_params["product_id"], "quantity": 1}
                ],
                "total_amount": 99.99,
            }

            # 先登录获取token
            login_response = self.client.post(
                "/auth/login",
                json={"username": "test_user", "password": "test123"},
                name="登录",
            )

            if login_response.status_code == 200:
                token = login_response.json().get("token")
                headers = {"Authorization": f"Bearer {token}"}

                # 创建订单
                order_response = self.client.post(
                    "/api/orders", json=order_data, headers=headers, name="创建订单"
                )

                # 手动记录事务时间
                measure(
                    "关键业务事务",
                    start_time,
                    exception=(
                        None
                        if order_response.status_code == 201
                        else Exception("订单创建失败")
                    ),
                )

                print(f"✅ 关键业务执行完成，状态码: {order_response.status_code}")
            else:
                measure("关键业务事务", start_time, exception=Exception("登录失败"))

        except Exception as e:
            measure("关键业务事务", start_time, exception=e)
            print(f"❌ 关键业务执行失败: {e}")

    @task
    def parameter_driven_test(self):
        """参数驱动测试"""
        # 根据产品ID参数调整测试行为
        product_id = self.test_params["product_id"]

        if product_id == "test_product":
            # 测试模式 - 访问固定商品
            self.client.get(f"/api/products/1", name="测试模式-固定商品")
        elif product_id.startswith("prod_"):
            # 生产模式 - 访问指定商品
            self.client.get(
                f"/api/products/{product_id.split('_')[1]}", name="生产模式-指定商品"
            )
        else:
            # 动态模式 - 搜索商品
            self.client.get(f"/api/search?q={product_id}", name="动态模式-搜索商品")


# 事件监听器
@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始 - 初始化集合点"""
    print("🚀 自定义参数测试开始")

    # 检查是否需要初始化集合点
    is_rendezvous = getattr(environment.parsed_options, "is_rendezvous", False)
    rendezvous_num = getattr(environment.parsed_options, "rendezvous_num", 1)

    if is_rendezvous and rendezvous_num > 1:
        # 初始化集合点
        environment.shared = Rendezvous(rendezvous_num)
        print(f"🚥 集合点已初始化，等待 {rendezvous_num} 个用户同步")

    # 打印测试参数
    print("\n📋 测试参数:")
    print(f"   循环次数: {getattr(environment.parsed_options, 'loop_num', 1)}")
    print(
        f"   产品ID: {getattr(environment.parsed_options, 'product_id', 'test_product')}"
    )
    print(f"   使用集合点: {is_rendezvous}")
    if is_rendezvous:
        print(f"   集合点用户数: {rendezvous_num}")


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束"""
    print("✅ 自定义参数测试完成")

    # 输出自定义事务统计
    print("\n📊 自定义事务统计:")
    for name, stats in environment.stats.entries.items():
        if "自定义" in name or "关键业务" in name:
            print(
                f"   {name}: 平均响应时间 {stats.avg_response_time:.2f}ms, "
                f"请求数 {stats.num_requests}, 失败数 {stats.num_failures}"
            )


# 自定义命令行参数
@events.init_command_line_parser.add_listener
def _(parser):
    """添加自定义命令行参数"""
    parser.add_argument(
        "--loop_num", type=int, default=1, help="每个测试循环的次数 (默认: 1)"
    )

    parser.add_argument(
        "--product_id",
        type=str,
        default="test_product",
        help="测试的产品ID (默认: test_product)",
    )

    parser.add_argument(
        "--is_rendezvous",
        type=str_to_bool,
        default=False,
        help="是否使用集合点同步 (默认: false)",
    )

    parser.add_argument(
        "--rendezvous_num", type=int, default=1, help="集合点等待的用户数量 (默认: 1)"
    )


if __name__ == "__main__":
    print("💡 这是一个自定义参数和集合点示例")
    print("🔧 使用方法:")
    print("   # 基础用法")
    print("   locust -f locustfiles/examples/02_custom_params.py")
    print("")
    print("   # 自定义循环次数")
    print("   locust -f locustfiles/examples/02_custom_params.py --loop_num=5")
    print("")
    print("   # 指定产品ID")
    print("   locust -f locustfiles/examples/02_custom_params.py --product_id=prod_123")
    print("")
    print("   # 使用集合点(需要多用户)")
    print(
        "   locust -f locustfiles/examples/02_custom_params.py --headless -u 5 -r 5 \\"
    )
    print("         --is_rendezvous=true --rendezvous_num=5 -t 30s")
    print("")
    print("📋 功能特性:")
    print("   - 自定义命令行参数")
    print("   - 循环控制逻辑")
    print("   - 集合点同步机制")
    print("   - 自定义事务报告")
    print("   - 参数驱动测试")
    print("")
    print("🎯 学习要点:")
    print("   - init_command_line_parser事件")
    print("   - environment.parsed_options使用")
    print("   - Rendezvous集合点实现")
    print("   - manual_report自定义事务")
    print("   - 测试逻辑的参数化")
