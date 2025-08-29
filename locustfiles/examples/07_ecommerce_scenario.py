#!/usr/bin/env python3
"""
电商综合场景示例

演示完整的电商业务流程性能测试
目标：整合所有框架功能，模拟真实电商场景
"""

import json
import random
import time
from datetime import datetime

from locust import HttpUser, LoadTestShape, events, task
from locust.env import Environment

from src.analysis.performance_analyzer import PerformanceAnalyzer

# 框架模块导入
from src.data_manager.data_generator import DataGenerator
from src.monitoring.performance_monitor import AlertRule, PerformanceMonitor
from src.utils.locust_report import manual_report, measure
from src.utils.rendezvous import Rendezvous


class EcommerceLoadShape(LoadTestShape):
    """电商负载模式 - 模拟真实电商流量"""

    def tick(self):
        run_time = self.get_run_time()

        # 预热期 (0-60s): 少量用户
        if run_time < 60:
            return 3, 1

        # 正常浏览期 (60-180s): 中等用户数
        elif run_time < 180:
            return 15, 2

        # 促销高峰期 (180-240s): 大量用户涌入
        elif run_time < 240:
            return 35, 5

        # 下单高峰期 (240-300s): 最高负载
        elif run_time < 300:
            return 50, 8

        # 恢复期 (300-360s): 负载下降
        elif run_time < 360:
            return 20, 5

        # 收尾期 (360-420s): 少量用户
        elif run_time < 420:
            return 8, 2

        return None  # 测试结束


class EcommerceBuyer(HttpUser):
    """电商买家用户 - 完整购物流程"""

    wait_time_seconds = random.uniform(1, 3)
    host = "http://localhost:5005"
    weight = 7  # 占70%用户

    def on_start(self):
        """用户会话开始"""
        # 从数据提供者获取用户数据
        self.user_data = getattr(
            self.environment, "user_generator", DataGenerator()
        ).generate_user_profile()
        self.session_data = {
            "cart_items": [],
            "token": None,
            "orders": [],
            "session_start": time.time(),
        }

        print(f"🛍️  买家 {self.user_data['name']} 开始购物")

    def on_stop(self):
        """用户会话结束"""
        session_duration = time.time() - self.session_data["session_start"]
        print(
            f"🏁 买家 {self.user_data['name']} 结束购物 (耗时: {session_duration:.1f}s, "
            f"购物车: {len(self.session_data['cart_items'])}件, "
            f"下单: {len(self.session_data['orders'])}笔)"
        )

    @task(8)
    def browse_products(self):
        """浏览商品 - 最高频操作"""
        page = random.randint(1, 10)
        limit = random.choice([10, 20, 50])
        category = random.choice(["", "electronics", "clothing", "books"])

        params = f"page={page}&limit={limit}"
        if category:
            params += f"&category={category}"

        with manual_report("商品浏览"):
            with self.client.get(
                f"/api/products?{params}", name="浏览商品列表", catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        product_count = len(data.get("products", []))
                        response.success()

                        # 模拟用户阅读商品信息的时间
                        reading_time = product_count * 0.1  # 每个商品0.1秒
                        time.sleep(min(reading_time, 2))  # 最多2秒

                    except Exception as e:
                        response.failure(f"解析商品数据失败: {e}")
                else:
                    response.failure(f"获取商品列表失败: {response.status_code}")

    @task(5)
    def search_products(self):
        """搜索商品"""
        search_keywords = [
            "手机",
            "笔记本",
            "衣服",
            "图书",
            "家具",
            "运动",
            "美食",
            "化妆品",
        ]
        keyword = random.choice(search_keywords)
        sort = random.choice(["price", "rating", "name"])

        with manual_report("商品搜索"):
            with self.client.get(
                f"/api/search?q={keyword}&sort={sort}",
                name="搜索商品",
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        total = data.get("total", 0)
                        response.success()
                        print(f"🔍 搜索 '{keyword}' 找到 {total} 个商品")
                    except Exception as e:
                        response.failure(f"解析搜索结果失败: {e}")
                else:
                    response.failure(f"搜索失败: {response.status_code}")

    @task(6)
    def view_product_detail(self):
        """查看商品详情"""
        product_id = random.randint(1, 100)

        with manual_report("商品详情"):
            with self.client.get(
                f"/api/products/{product_id}", name="商品详情", catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        product = response.json()
                        response.success()

                        # 有一定概率加入购物车
                        if random.random() < 0.3:  # 30%概率
                            self._add_to_cart(
                                product_id, product.get("name", f"商品{product_id}")
                            )

                        # 模拟查看详情的时间
                        time.sleep(random.uniform(0.5, 2))

                    except Exception as e:
                        response.failure(f"解析商品详情失败: {e}")
                elif response.status_code == 404:
                    response.success()  # 商品不存在是正常情况
                else:
                    response.failure(f"获取商品详情失败: {response.status_code}")

    @task(2)
    def login_and_get_profile(self):
        """登录并获取用户信息"""
        if self.session_data["token"]:
            # 已登录，获取用户信息
            headers = {"Authorization": f'Bearer {self.session_data["token"]}'}
            with self.client.get(
                "/auth/profile", headers=headers, name="获取用户信息"
            ) as response:
                pass
            return

        # 执行登录
        login_data = {"username": self.user_data["username"], "password": "test123"}

        with manual_report("用户登录"):
            with self.client.post(
                "/auth/login", json=login_data, name="用户登录", catch_response=True
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.session_data["token"] = data.get("token")
                        response.success()
                        print(f"✅ 用户 {self.user_data['name']} 登录成功")
                    except Exception as e:
                        response.failure(f"登录响应解析失败: {e}")
                else:
                    response.failure(f"登录失败: {response.status_code}")

    @task(1)
    def checkout_process(self):
        """结账流程 - 需要登录和购物车商品"""
        if not self.session_data["token"]:
            return  # 未登录

        if len(self.session_data["cart_items"]) < 1:
            return  # 购物车为空

        # 模拟结账过程
        with manual_report("订单结账"):
            order_data = {
                "products": self.session_data["cart_items"],
                "total_amount": sum(
                    item["price"] * item["quantity"]
                    for item in self.session_data["cart_items"]
                ),
            }

            headers = {"Authorization": f'Bearer {self.session_data["token"]}'}

            with self.client.post(
                "/api/orders",
                json=order_data,
                headers=headers,
                name="创建订单",
                catch_response=True,
            ) as response:
                if response.status_code == 201:
                    try:
                        order = response.json()
                        self.session_data["orders"].append(order)
                        self.session_data["cart_items"] = []  # 清空购物车
                        response.success()
                        print(
                            f"💰 订单创建成功: {order.get('id', 'unknown')}, "
                            f"金额: ¥{order_data['total_amount']:.2f}"
                        )
                    except Exception as e:
                        response.failure(f"订单响应解析失败: {e}")
                else:
                    response.failure(f"创建订单失败: {response.status_code}")

    def _add_to_cart(self, product_id: int, product_name: str):
        """添加商品到购物车"""
        cart_item = {
            "product_id": str(product_id),
            "quantity": random.randint(1, 3),
            "price": random.uniform(10, 500),
            "name": product_name,
        }

        with self.client.post(
            "/api/cart/add", json=cart_item, name="添加购物车"
        ) as response:
            if response.status_code == 200:
                self.session_data["cart_items"].append(cart_item)
                print(f"🛒 添加到购物车: {product_name} x{cart_item['quantity']}")


class EcommerceBrowser(HttpUser):
    """电商浏览者 - 只浏览不购买"""

    wait_time_seconds = random.uniform(0.5, 2)
    host = "http://localhost:5005"
    weight = 3  # 占30%用户

    @task(10)
    def casual_browsing(self):
        """随机浏览"""
        # 随机选择浏览行为
        actions = [
            lambda: self.client.get(
                "/api/products?page=1&limit=20", name="浏览首页商品"
            ),
            lambda: self.client.get(
                f"/api/products/{random.randint(1, 50)}", name="随机查看商品"
            ),
            lambda: self.client.get(f"/api/search?q=test", name="随机搜索"),
            lambda: self.client.get("/health", name="健康检查"),
        ]

        action = random.choice(actions)
        action()

        # 模拟浏览时间
        time.sleep(random.uniform(0.2, 1))


# ==================== 事件监听器 ====================


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始 - 初始化完整的测试环境"""
    print("🚀 电商综合场景测试开始")
    print("📋 初始化测试环境...")

    # 1. 初始化数据生成器
    environment.user_generator = DataGenerator(locale="zh_CN", seed=12345)
    print("✅ 数据生成器初始化完成")

    # 2. 初始化性能分析器
    environment.performance_analyzer = PerformanceAnalyzer()
    environment.performance_analyzer.set_thresholds(
        response_time_p95=1200,  # 电商场景允许稍高的响应时间
        error_rate=0.02,  # 2%错误率
        throughput_min=20,  # 最小20 TPS
    )
    environment.performance_data = []
    print("✅ 性能分析器初始化完成")

    # 3. 初始化监控系统
    environment.performance_monitor = PerformanceMonitor(check_interval=10)

    # 添加电商特定的监控规则
    ecommerce_alert_rules = [
        AlertRule(
            name="购物车响应时间过长",
            metric_name="cart_response_time",
            condition="gt",
            threshold=1500,
            duration=20,
            callback=lambda alert: print(
                f"🛒⚠️  购物车性能告警: {alert['current_value']:.0f}ms"
            ),
        ),
        AlertRule(
            name="订单创建失败率过高",
            metric_name="order_error_rate",
            condition="gt",
            threshold=0.05,  # 5%
            duration=30,
            callback=lambda alert: print(
                f"💰🚨 订单创建告警: {alert['current_value']*100:.1f}%"
            ),
        ),
    ]

    for rule in ecommerce_alert_rules:
        environment.performance_monitor.add_alert_rule(rule)

    environment.performance_monitor.start_monitoring()
    print("✅ 监控告警系统启动完成")

    # 4. 初始化集合点(用于模拟抢购场景)
    expected_users = getattr(environment.parsed_options, "num_users", 10)
    if expected_users >= 20:  # 用户数足够时启用集合点
        environment.flash_sale_rendezvous = Rendezvous(min(expected_users // 2, 25))
        print("✅ 抢购集合点初始化完成")

    # 5. 记录测试开始时间
    environment.test_start_time = datetime.now()
    environment.business_metrics = {
        "total_orders": 0,
        "total_revenue": 0.0,
        "cart_additions": 0,
        "user_sessions": 0,
    }

    print(f"🎯 电商测试场景配置:")
    print(f"   目标用户数: {expected_users}")
    print(f"   响应时间阈值: P95 < 1200ms")
    print(f"   错误率阈值: < 2%")
    print(f"   吞吐量阈值: > 20 TPS")
    print(
        f"   集合点: {'启用' if hasattr(environment, 'flash_sale_rendezvous') else '禁用'}"
    )


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束 - 综合分析和报告生成"""
    print("✅ 电商综合场景测试完成")

    # 停止监控系统
    if hasattr(environment, "performance_monitor"):
        environment.performance_monitor.stop_monitoring()

    # 执行业务指标分析
    print("\n📊 业务指标统计:")
    if hasattr(environment, "business_metrics"):
        metrics = environment.business_metrics
        print(f"   总订单数: {metrics['total_orders']}")
        print(f"   总营收: ¥{metrics['total_revenue']:.2f}")
        print(f"   购物车添加: {metrics['cart_additions']}")
        print(f"   用户会话: {metrics['user_sessions']}")

    # 执行性能分析
    if hasattr(environment, "performance_data") and environment.performance_data:
        print("\n🔍 执行性能分析...")

        test_data = {
            "test_name": "电商综合场景测试",
            "start_time": environment.test_start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": int(
                (datetime.now() - environment.test_start_time).total_seconds()
            ),
            "users": getattr(environment.parsed_options, "num_users", 0),
            "requests": environment.performance_data,
        }

        try:
            analysis_result = environment.performance_analyzer.comprehensive_analysis(
                test_data
            )

            print(f"📋 性能分析结果:")
            print(f"   综合评级: {analysis_result['overall_grade']}")

            # 输出关键指标
            if analysis_result.get("response_time"):
                rt = analysis_result["response_time"]
                print(
                    f"   响应时间: P95={rt.get('p95', 0):.1f}ms, 平均={rt.get('mean', 0):.1f}ms"
                )

            if analysis_result.get("throughput"):
                tp = analysis_result["throughput"]
                print(f"   吞吐量: {tp.get('avg_tps', 0):.1f} TPS")

            if analysis_result.get("error_analysis"):
                er = analysis_result["error_analysis"]
                print(f"   错误率: {er.get('error_percentage', 0):.2f}%")

            # 生成综合报告
            from src.analysis.report_generator import ReportGenerator

            report_generator = ReportGenerator()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # HTML报告
            html_path = report_generator.generate_html_report(
                analysis_result,
                output_filename=f"ecommerce_comprehensive_{timestamp}.html",
            )

            # JSON报告
            json_path = report_generator.generate_json_report(
                analysis_result,
                output_filename=f"ecommerce_comprehensive_{timestamp}.json",
            )

            print(f"\n📄 综合报告已生成:")
            print(f"   HTML报告: {html_path}")
            print(f"   JSON报告: {json_path}")

            # 业务建议
            print(f"\n💡 电商业务建议:")
            if analysis_result["overall_grade"] in ["A", "B"]:
                print("   ✅ 系统性能良好，可支撑当前业务负载")
                print("   🚀 可考虑增加促销活动或扩大用户规模")
            elif analysis_result["overall_grade"] == "C":
                print("   ⚠️  系统性能一般，建议优化关键接口")
                print("   📈 重点关注商品搜索和订单创建性能")
            else:
                print("   🚨 系统性能存在问题，需立即优化")
                print("   🛠️  建议进行系统架构调整或资源扩容")

        except Exception as e:
            print(f"❌ 性能分析失败: {e}")

    print(f"\n🏁 电商综合测试完成!")


# 业务指标收集
@events.request.add_listener
def on_request_event(
    request_type, name, response_time, response_length, exception, **kwargs
):
    """请求事件监听 - 收集业务指标和监控"""
    if exception:
        # 处理失败请求的监控和告警
        if "订单" in name or "购物车" in name:
            print(f"❌ 关键业务失败: {name} - {exception}")
    else:
        # 处理成功请求的业务指标收集
        # 这里可以根据请求名称收集特定的业务指标
        pass


if __name__ == "__main__":
    print("💡 这是一个电商综合场景示例")
    print("🔧 使用方法:")
    print("   locust -f locustfiles/examples/07_ecommerce_scenario.py")
    print(
        "   locust -f locustfiles/examples/07_ecommerce_scenario.py --headless -u 30 -r 5 -t 300s"
    )
    print("")
    print("📋 场景特点:")
    print("   - 完整的用户购物流程")
    print("   - 真实的电商负载模式")
    print("   - 综合的性能监控分析")
    print("   - 业务指标统计")
    print("   - 多角色用户模拟")
    print("")
    print("🎭 用户角色:")
    print("   - EcommerceBuyer (70%): 完整购物流程用户")
    print("   - EcommerceBrowser (30%): 纯浏览用户")
    print("")
    print("🛍️  业务流程:")
    print("   1. 商品浏览和搜索")
    print("   2. 商品详情查看")
    print("   3. 用户登录认证")
    print("   4. 添加购物车")
    print("   5. 订单创建结账")
    print("")
    print("📊 集成功能:")
    print("   - 性能分析和评分")
    print("   - 实时监控告警")
    print("   - 数据生成管理")
    print("   - 自定义事务报告")
    print("   - 多格式报告生成")
