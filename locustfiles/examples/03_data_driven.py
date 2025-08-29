#!/usr/bin/env python3
"""
数据驱动测试示例

演示如何使用框架的数据管理功能进行数据驱动测试
目标：展示数据生成器和数据提供者的使用
"""

import json
import random

from locust import HttpUser, between, events, task
from locust.env import Environment

from src.data_manager.data_generator import DataGenerator
from src.data_manager.data_provider import DataProvider


class DataDrivenUser(HttpUser):
    """数据驱动用户类"""

    wait_time = between(1, 2)
    host = "http://localhost:5000"

    def on_start(self):
        """测试开始 - 初始化数据"""
        # 获取共享的数据提供者
        self.data_provider = getattr(self.environment, "data_provider", None)

        if self.data_provider is None:
            print("⚠️  数据提供者未初始化")
            return

        print("✅ 数据驱动用户启动成功")

    @task(3)
    def test_with_generated_users(self):
        """使用生成用户数据进行测试"""
        if not self.data_provider:
            return

        # 获取下一个用户数据
        user_data = self.data_provider.get_next_data("users")
        if not user_data:
            print("⚠️  用户数据已用完")
            return

        # 使用用户数据进行登录测试
        login_data = {
            "username": user_data["username"],
            "password": "test123",  # 统一测试密码
        }

        with self.client.post(
            "/auth/login",
            json=login_data,
            name="数据驱动-用户登录",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    token_data = response.json()
                    if "token" in token_data:
                        response.success()

                        # 使用token获取用户信息
                        headers = {"Authorization": f'Bearer {token_data["token"]}'}
                        self.client.get(
                            "/auth/profile",
                            headers=headers,
                            name="数据驱动-获取用户信息",
                        )
                    else:
                        response.failure("登录响应缺少token")
                except Exception as e:
                    response.failure(f"JSON解析失败: {e}")
            else:
                response.failure(f"登录失败: {response.status_code}")

    @task(4)
    def test_with_generated_products(self):
        """使用生成商品数据进行测试"""
        if not self.data_provider:
            return

        # 获取下一个商品数据
        product_data = self.data_provider.get_next_data("products")
        if not product_data:
            print("⚠️  商品数据已用完")
            return

        # 使用商品数据进行搜索测试
        search_query = product_data["name"].split()[0]  # 取商品名称的第一个词

        with self.client.get(
            f"/api/search?q={search_query}",
            name="数据驱动-商品搜索",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                try:
                    search_result = response.json()
                    if "products" in search_result:
                        response.success()
                        print(
                            f"🔍 搜索 '{search_query}' 找到 {search_result.get('total', 0)} 个商品"
                        )
                    else:
                        response.failure("搜索结果格式异常")
                except Exception as e:
                    response.failure(f"JSON解析失败: {e}")
            else:
                response.failure(f"搜索失败: {response.status_code}")

    @task(2)
    def test_with_random_data(self):
        """使用随机数据进行测试"""
        if not self.data_provider:
            return

        # 获取随机用户数据
        random_users = self.data_provider.get_random_data("users", count=2)
        if not random_users:
            return

        user = random_users[0]

        # 使用随机数据添加商品到购物车
        cart_data = {
            "product_id": str(random.randint(1, 100)),
            "quantity": random.randint(1, 3),
        }

        with self.client.post(
            "/api/cart/add",
            json=cart_data,
            name="数据驱动-添加购物车",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                response.success()
                print(
                    f"🛒 用户 {user['name']} 添加商品 {cart_data['product_id']} 到购物车"
                )
            else:
                response.failure(f"添加购物车失败: {response.status_code}")

    @task(1)
    def test_data_statistics(self):
        """测试数据统计功能"""
        if not self.data_provider:
            return

        # 获取数据统计信息
        user_stats = self.data_provider.get_data_stats("users")
        product_stats = self.data_provider.get_data_stats("products")

        print(
            f"📊 数据统计 - 用户: {user_stats.get('total_records', 0)}, "
            f"商品: {product_stats.get('total_records', 0)}"
        )

        # 简单的健康检查
        self.client.get("/health", name="数据统计-健康检查")


# 事件监听器
@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始 - 初始化数据"""
    print("🚀 数据驱动测试开始")
    print("🔄 正在生成测试数据...")

    # 初始化数据生成器
    generator = DataGenerator(locale="zh_CN", seed=12345)  # 使用固定种子确保可重复性

    # 生成用户数据
    print("👥 生成用户数据...")
    users_data = []
    for i in range(100):  # 生成100个用户
        user = generator.generate_user_profile(include_avatar=True)
        users_data.append(user)

    # 生成商品数据
    print("📦 生成商品数据...")
    products_data = []
    categories = ["electronics", "clothing", "books", "home", "sports"]
    for category in categories:
        for i in range(20):  # 每个类别20个商品
            product = generator.generate_product_info(category=category)
            products_data.append(product)

    # 初始化数据提供者
    data_provider = DataProvider()

    # 将生成的数据加载到数据提供者
    # 这里我们手动加载数据，实际使用中可以从CSV文件加载
    data_provider._load_data_from_list("users", users_data, "round_robin")
    data_provider._load_data_from_list("products", products_data, "random")

    # 将数据提供者附加到环境
    environment.data_provider = data_provider

    print("✅ 测试数据生成完成")
    print(f"   用户数据: {len(users_data)} 条")
    print(f"   商品数据: {len(products_data)} 条")

    # 打印一些示例数据
    print("\n📋 数据示例:")
    if users_data:
        sample_user = users_data[0]
        print(f"   用户: {sample_user['name']} ({sample_user['email']})")
    if products_data:
        sample_product = products_data[0]
        print(f"   商品: {sample_product['name']} - {sample_product['category']}")


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束"""
    print("✅ 数据驱动测试完成")

    # 输出数据使用统计
    data_provider = getattr(environment, "data_provider", None)
    if data_provider:
        print("\n📊 数据使用统计:")
        for data_key in ["users", "products"]:
            stats = data_provider.get_data_stats(data_key)
            if stats:
                print(
                    f"   {data_key}: 总记录 {stats.get('total_records', 0)}, "
                    f"当前索引 {stats.get('current_index', 0)}"
                )


# 为DataProvider添加缺失的方法
class DataProvider:
    """数据提供者 - 简化实现"""

    def __init__(self):
        self.data_sets = {}
        self.current_indices = {}
        self.distribution_strategies = {}

    def _load_data_from_list(
        self, data_key: str, data: list, strategy: str = "sequential"
    ):
        """从列表加载数据"""
        self.data_sets[data_key] = data
        self.current_indices[data_key] = 0
        self.distribution_strategies[data_key] = strategy
        print(f"✅ 加载数据集 '{data_key}': {len(data)} 条记录, 策略: {strategy}")

    def get_next_data(self, data_key: str):
        """获取下一条数据"""
        if data_key not in self.data_sets:
            return None

        data_list = self.data_sets[data_key]
        if not data_list:
            return None

        strategy = self.distribution_strategies.get(data_key, "sequential")

        if strategy == "round_robin" or strategy == "sequential":
            index = self.current_indices[data_key]
            data = data_list[index % len(data_list)]
            self.current_indices[data_key] = index + 1
            return data
        elif strategy == "random":
            return random.choice(data_list)

        return data_list[0]

    def get_random_data(self, data_key: str, count: int = 1):
        """获取随机数据"""
        if data_key not in self.data_sets:
            return []

        data_list = self.data_sets[data_key]
        if not data_list:
            return []

        return random.sample(data_list, min(count, len(data_list)))

    def get_data_stats(self, data_key: str):
        """获取数据统计信息"""
        if data_key not in self.data_sets:
            return {}

        return {
            "total_records": len(self.data_sets[data_key]),
            "current_index": self.current_indices.get(data_key, 0),
            "distribution_strategy": self.distribution_strategies.get(
                data_key, "sequential"
            ),
            "last_accessed": "now",
        }


if __name__ == "__main__":
    print("💡 这是一个数据驱动测试示例")
    print("🔧 使用方法:")
    print("   locust -f locustfiles/examples/03_data_driven.py")
    print(
        "   locust -f locustfiles/examples/03_data_driven.py --headless -u 5 -r 2 -t 60s"
    )
    print("")
    print("📋 测试内容:")
    print("   - 使用生成的用户数据进行登录测试")
    print("   - 使用生成的商品数据进行搜索测试")
    print("   - 随机数据的购物车测试")
    print("   - 数据统计功能验证")
    print("")
    print("🎯 学习要点:")
    print("   - DataGenerator数据生成")
    print("   - DataProvider数据管理")
    print("   - 数据分发策略(round_robin/random)")
    print("   - 测试开始时的数据初始化")
    print("   - 数据驱动的测试逻辑")
