#!/usr/bin/env python3
"""
基础功能示例 - HTTP测试

演示如何使用框架进行基本的HTTP性能测试
目标：Mock服务的基础API测试
"""

import random

from locust import HttpUser, between, events, task
from locust.env import Environment


class BasicUser(HttpUser):
    """基础用户类 - 演示基本HTTP测试功能"""

    wait_time = between(1, 2)  # 用户间隔1-2秒
    host = "http://localhost:5001"  # Mock服务地址

    def on_start(self):
        """测试开始时执行"""
        print(f"用户开始测试 - 目标主机: {self.host}")

    def on_stop(self):
        """测试结束时执行"""
        print("用户结束测试")

    @task(3)
    def health_check(self):
        """健康检查 - 权重3"""
        with self.client.get(
            "/health", name="健康检查", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"状态码异常: {response.status_code}")

    @task(2)
    def get_metrics(self):
        """获取系统指标 - 权重2"""
        with self.client.get(
            "/metrics", name="系统指标", catch_response=True
        ) as response:
            if response.status_code == 200 and "requests_total" in response.text:
                response.success()
            else:
                response.failure("指标数据异常")

    @task(5)
    def get_products(self):
        """获取商品列表 - 权重5"""
        page = random.randint(1, 5)
        limit = random.choice([10, 20, 50])

        with self.client.get(
            f"/api/products?page={page}&limit={limit}",
            name="商品列表",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "products" in data and "total" in data:
                        response.success()
                    else:
                        response.failure("响应格式异常")
                except Exception as e:
                    response.failure(f"JSON解析失败: {e}")
            else:
                response.failure(f"状态码异常: {response.status_code}")

    @task(3)
    def get_product_detail(self):
        """获取商品详情 - 权重3"""
        product_id = random.randint(1, 100)

        with self.client.get(
            f"/api/products/{product_id}", name="商品详情", catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "id" in data and "name" in data:
                        response.success()
                    else:
                        response.failure("商品数据格式异常")
                except Exception as e:
                    response.failure(f"JSON解析失败: {e}")
            elif response.status_code == 404:
                # 404是预期的情况（商品不存在）
                response.success()
            else:
                response.failure(f"意外状态码: {response.status_code}")

    @task(2)
    def search_products(self):
        """搜索商品 - 权重2"""
        search_terms = ["手机", "电脑", "图书", "衣服", "家具"]
        query = random.choice(search_terms)

        with self.client.get(
            f"/api/search?q={query}&sort=price", name="商品搜索", catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "products" in data and "total" in data:
                        response.success()
                    else:
                        response.failure("搜索结果格式异常")
                except Exception as e:
                    response.failure(f"JSON解析失败: {e}")
            else:
                response.failure(f"状态码异常: {response.status_code}")


# 测试事件监听器
@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始事件"""
    print("🚀 基础功能测试开始")
    print(f"目标主机: {environment.host}")
    print(
        f"用户数: {environment.parsed_options.num_users if hasattr(environment.parsed_options, 'num_users') else '未知'}"
    )


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束事件"""
    print("✅ 基础功能测试完成")

    # 输出测试统计信息
    stats = environment.stats
    print("\n📊 测试统计:")
    print(f"总请求数: {stats.total.num_requests}")
    print(f"失败请求数: {stats.total.num_failures}")
    print(
        f"错误率: {(stats.total.num_failures/max(stats.total.num_requests, 1)*100):.2f}%"
    )
    print(f"平均响应时间: {stats.total.avg_response_time:.2f}ms")
    print(f"RPS: {stats.total.current_rps:.2f}")


# 命令行参数解析器
@events.init_command_line_parser.add_listener
def _(parser):
    """添加自定义命令行参数"""
    parser.add_argument(
        "--test-mode",
        type=str,
        default="normal",
        choices=["normal", "stress", "spike"],
        help="测试模式: normal(正常), stress(压力), spike(峰值)",
    )


if __name__ == "__main__":
    print("💡 这是一个基础功能示例文件")
    print("🔧 使用方法:")
    print("   locust -f locustfiles/examples/01_basic_test.py")
    print(
        "   locust -f locustfiles/examples/01_basic_test.py --headless -u 10 -r 2 -t 60s"
    )
    print("   locust -f locustfiles/examples/01_basic_test.py --test-mode=stress")
    print("")
    print("📋 测试内容:")
    print("   - 健康检查接口")
    print("   - 系统指标接口")
    print("   - 商品列表接口")
    print("   - 商品详情接口")
    print("   - 商品搜索接口")
    print("")
    print("🎯 学习要点:")
    print("   - 基础HttpUser使用")
    print("   - @task装饰器和权重")
    print("   - catch_response错误处理")
    print("   - 事件监听器使用")
    print("   - 自定义命令行参数")
