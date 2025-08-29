#!/usr/bin/env python3
"""
监控告警示例

演示如何使用框架的监控告警功能
目标：展示实时监控、告警规则和通知系统
"""

import random
import time

from locust import HttpUser, between, events, task
from locust.env import Environment

from src.monitoring.alert_manager import AlertManager
from src.monitoring.performance_monitor import AlertRule, PerformanceMonitor


class MonitoringUser(HttpUser):
    """监控告警用户类"""

    wait_time = between(1, 2)
    host = "http://localhost:5003"

    @task(4)
    def normal_request(self):
        """正常请求 - 模拟正常业务流量"""
        with self.client.get(
            "/api/products?page=1&limit=10", name="正常请求", catch_response=True
        ) as response:

            # 记录监控指标
            if hasattr(self.environment, "performance_monitor"):
                response_time = response.elapsed.total_seconds() * 1000
                self.environment.performance_monitor.add_metric(
                    "response_time",
                    response_time,
                    tags={"endpoint": "/api/products", "method": "GET"},
                )

                # 记录成功/失败
                success_rate = 1.0 if response.status_code == 200 else 0.0
                self.environment.performance_monitor.add_metric(
                    "success_rate", success_rate, tags={"endpoint": "/api/products"}
                )

            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"请求失败: {response.status_code}")

    @task(2)
    def slow_request(self):
        """慢请求 - 可能触发响应时间告警"""
        # 随机产生慢请求
        if random.random() < 0.3:  # 30%概率产生慢请求
            time.sleep(random.uniform(1.0, 2.0))  # 额外延迟1-2秒

        start_time = time.time()

        with self.client.get(
            f"/api/products/{random.randint(1, 100)}",
            name="慢请求测试",
            catch_response=True,
        ) as response:

            response_time = (time.time() - start_time) * 1000

            # 记录监控指标
            if hasattr(self.environment, "performance_monitor"):
                self.environment.performance_monitor.add_metric(
                    "response_time",
                    response_time,
                    tags={"endpoint": "/api/products/{id}", "method": "GET"},
                )

                # 如果响应时间超过1秒，记录为慢请求
                if response_time > 1000:
                    self.environment.performance_monitor.add_metric(
                        "slow_request_count", 1, tags={"endpoint": "/api/products/{id}"}
                    )

            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"请求异常: {response.status_code}")

    @task(1)
    def error_request(self):
        """错误请求 - 可能触发错误率告警"""
        # 随机产生错误请求
        if random.random() < 0.2:  # 20%概率访问不存在的端点
            endpoint = "/api/nonexistent"
            expected_error = True
        else:
            endpoint = "/api/products"
            expected_error = False

        with self.client.get(
            endpoint, name="错误测试", catch_response=True
        ) as response:

            # 记录错误率指标
            if hasattr(self.environment, "performance_monitor"):
                error_rate = 1.0 if response.status_code >= 400 else 0.0
                self.environment.performance_monitor.add_metric(
                    "error_rate",
                    error_rate,
                    tags={
                        "endpoint": endpoint,
                        "status_code": str(response.status_code),
                    },
                )

                # 记录总请求数
                self.environment.performance_monitor.add_metric(
                    "total_requests", 1, tags={"endpoint": endpoint}
                )

            if expected_error and response.status_code >= 400:
                response.success()  # 预期的错误
            elif not expected_error and response.status_code == 200:
                response.success()  # 正常响应
            else:
                response.failure(f"意外的响应: {response.status_code}")

    @task(1)
    def high_load_request(self):
        """高负载请求 - 测试系统负载监控"""
        # 模拟CPU密集型操作
        if random.random() < 0.1:  # 10%概率产生高负载
            # 模拟高CPU使用率
            start = time.time()
            while time.time() - start < 0.1:  # 100ms的CPU密集计算
                _ = sum(range(1000))

        with self.client.get("/api/search?q=test", name="高负载测试") as response:

            # 记录负载相关指标
            if hasattr(self.environment, "performance_monitor"):
                # 模拟CPU使用率指标
                cpu_usage = random.uniform(20, 90)  # 随机CPU使用率
                self.environment.performance_monitor.add_metric(
                    "cpu_usage", cpu_usage, tags={"host": "test-server"}
                )

                # 模拟内存使用率
                memory_usage = random.uniform(30, 85)
                self.environment.performance_monitor.add_metric(
                    "memory_usage", memory_usage, tags={"host": "test-server"}
                )


def alert_callback(alert_info):
    """告警回调函数"""
    severity_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}

    severity = alert_info.get("tags", {}).get("severity", "warning")
    emoji = severity_emoji.get(severity, "⚠️")

    print(f"{emoji} 告警触发: {alert_info['rule_name']}")
    print(f"   指标: {alert_info['metric_name']}")
    print(f"   当前值: {alert_info['current_value']:.2f}")
    print(f"   阈值: {alert_info['threshold']}")
    print(f"   时间: {alert_info['timestamp']}")


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始 - 初始化监控系统"""
    print("🚀 监控告警测试开始")

    # 初始化性能监控器
    environment.performance_monitor = PerformanceMonitor(check_interval=5)

    # 添加告警回调
    environment.performance_monitor.add_alert_callback(alert_callback)

    # 创建告警规则
    alert_rules = [
        # 响应时间告警
        AlertRule(
            name="响应时间过高",
            metric_name="response_time",
            condition="gt",
            threshold=1000,  # 1秒
            duration=10,  # 持续10秒
            callback=lambda alert: print(
                f"🐌 检测到慢响应: {alert['current_value']:.0f}ms"
            ),
        ),
        # 错误率告警
        AlertRule(
            name="错误率过高",
            metric_name="error_rate",
            condition="gt",
            threshold=0.15,  # 15%
            duration=15,  # 持续15秒
            callback=lambda alert: print(
                f"💥 检测到高错误率: {alert['current_value']*100:.1f}%"
            ),
        ),
        # CPU使用率告警
        AlertRule(
            name="CPU使用率过高",
            metric_name="cpu_usage",
            condition="gt",
            threshold=80,  # 80%
            duration=20,  # 持续20秒
            callback=lambda alert: print(
                f"🔥 CPU使用率过高: {alert['current_value']:.1f}%"
            ),
        ),
        # 内存使用率告警
        AlertRule(
            name="内存使用率过高",
            metric_name="memory_usage",
            condition="gt",
            threshold=80,  # 80%
            duration=20,  # 持续20秒
            callback=lambda alert: print(
                f"💾 内存使用率过高: {alert['current_value']:.1f}%"
            ),
        ),
        # 慢请求数量告警
        AlertRule(
            name="慢请求数量过多",
            metric_name="slow_request_count",
            condition="gt",
            threshold=3,  # 超过3个慢请求
            duration=30,  # 持续30秒
            callback=lambda alert: print(
                f"🚫 慢请求过多: {alert['current_value']:.0f}个"
            ),
        ),
    ]

    # 添加告警规则
    for rule in alert_rules:
        environment.performance_monitor.add_alert_rule(rule)

    # 启动监控
    environment.performance_monitor.start_monitoring()

    print("📊 性能监控系统已启动")
    print(f"   监控间隔: {environment.performance_monitor.check_interval}秒")
    print(f"   告警规则数: {len(alert_rules)}")

    # 显示监控阈值
    print("\n🎯 监控阈值:")
    print(f"   响应时间: > 1000ms")
    print(f"   错误率: > 15%")
    print(f"   CPU使用率: > 80%")
    print(f"   内存使用率: > 80%")
    print(f"   慢请求数: > 3个")


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束 - 输出监控统计"""
    print("✅ 监控告警测试完成")

    if hasattr(environment, "performance_monitor"):
        # 停止监控
        environment.performance_monitor.stop_monitoring()

        # 获取监控统计
        print("\n📊 监控统计摘要:")

        metrics_summary = environment.performance_monitor.get_all_metrics_summary()

        for metric_name, stats in metrics_summary.items():
            if stats:  # 确保有数据
                print(f"   {metric_name}:")
                print(f"     数量: {stats.get('count', 0)}")
                print(f"     平均值: {stats.get('avg', 0):.2f}")
                print(f"     最大值: {stats.get('max', 0):.2f}")
                print(f"     最小值: {stats.get('min', 0):.2f}")

        # 导出监控数据
        try:
            exported_data = environment.performance_monitor.export_metrics(
                duration_hours=1
            )
            if exported_data:
                # 保存到文件
                import json
                from datetime import datetime

                filename = (
                    f"monitoring_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(f"reports/{filename}", "w", encoding="utf-8") as f:
                    json.dump(exported_data, f, indent=2, ensure_ascii=False)

                print(f"\n💾 监控数据已导出: reports/{filename}")
                print(f"   记录数量: {len(exported_data)}")

        except Exception as e:
            print(f"⚠️  导出监控数据失败: {e}")


# 中间状态报告
@events.request.add_listener
def on_request_monitoring(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    **kwargs,
):
    """请求完成时更新监控状态"""
    # 静态计数器
    if not hasattr(on_request_monitoring, "counter"):
        on_request_monitoring.counter = 0
    on_request_monitoring.counter += 1

    # 每50个请求输出一次监控状态
    if on_request_monitoring.counter % 50 == 0:
        print(f"📊 监控状态更新 - 已完成 {on_request_monitoring.counter} 个请求")
        if exception:
            print(f"🚨 检测到错误: {exception} - 可能触发告警")
        else:
            print(f"✅ 响应时间: {response_time:.2f}ms")


if __name__ == "__main__":
    print("💡 这是一个监控告警集成示例")
    print("🔧 使用方法:")
    print("   locust -f locustfiles/examples/05_monitoring_alerts.py")
    print(
        "   locust -f locustfiles/examples/05_monitoring_alerts.py --headless -u 20 -r 5 -t 180s"
    )
    print("")
    print("📋 测试内容:")
    print("   - 实时性能指标监控")
    print("   - 多种告警规则触发")
    print("   - 告警回调函数执行")
    print("   - 监控数据导出")
    print("")
    print("🎯 学习要点:")
    print("   - PerformanceMonitor集成")
    print("   - AlertRule配置和使用")
    print("   - 实时指标收集")
    print("   - 告警回调处理")
    print("   - 监控数据导出")
    print("")
    print("📊 监控指标:")
    print("   - response_time (响应时间)")
    print("   - error_rate (错误率)")
    print("   - cpu_usage (CPU使用率)")
    print("   - memory_usage (内存使用率)")
    print("   - slow_request_count (慢请求数)")
