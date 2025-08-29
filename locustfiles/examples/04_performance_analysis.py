#!/usr/bin/env python3
"""
性能分析示例

演示如何集成框架的性能分析功能
目标：展示性能分析器、趋势分析和报告生成
"""

import json
import random
import time
from datetime import datetime

from locust import HttpUser, between, events, task
from locust.env import Environment

from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.analysis.report_generator import ReportGenerator
from src.analysis.trend_analyzer import TrendAnalyzer


class PerformanceAnalysisUser(HttpUser):
    """性能分析用户类"""

    wait_time = between(1, 2)
    host = "http://localhost:5002"

    @task(4)
    def api_performance_test(self):
        """API性能测试"""
        # 测试商品列表API的性能
        start_time = time.time()

        with self.client.get(
            "/api/products?page=1&limit=20",
            name="商品列表性能测试",
            catch_response=True,
        ) as response:
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                # 记录性能数据到环境共享存储
                self.environment.performance_data.append(
                    {
                        "response_time": response_time,
                        "success": True,
                        "timestamp": datetime.now().isoformat(),
                        "name": "商品列表API",
                        "method": "GET",
                    }
                )
                response.success()
            else:
                self.environment.performance_data.append(
                    {
                        "response_time": response_time,
                        "success": False,
                        "timestamp": datetime.now().isoformat(),
                        "name": "商品列表API",
                        "method": "GET",
                    }
                )
                response.failure(f"状态码异常: {response.status_code}")

    @task(3)
    def search_performance_test(self):
        """搜索性能测试"""
        import random

        search_terms = ["手机", "电脑", "图书", "衣服", "家具"]
        query = random.choice(search_terms)

        start_time = time.time()

        with self.client.get(
            f"/api/search?q={query}&sort=price",
            name="搜索性能测试",
            catch_response=True,
        ) as response:
            response_time = (time.time() - start_time) * 1000

            success = response.status_code == 200
            self.environment.performance_data.append(
                {
                    "response_time": response_time,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "name": "商品搜索API",
                    "method": "GET",
                }
            )

            if success:
                response.success()
            else:
                response.failure(f"搜索失败: {response.status_code}")

    @task(2)
    def auth_performance_test(self):
        """认证性能测试"""
        login_data = {
            "username": f"test_user_{random.randint(1, 100)}",
            "password": "test123",
        }

        start_time = time.time()

        with self.client.post(
            "/auth/login", json=login_data, name="登录性能测试", catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000

            success = response.status_code == 200
            self.environment.performance_data.append(
                {
                    "response_time": response_time,
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "name": "用户登录API",
                    "method": "POST",
                }
            )

            if success:
                response.success()
            else:
                response.failure(f"登录失败: {response.status_code}")

    @task(1)
    def slow_operation_test(self):
        """慢操作测试 - 用于演示性能问题检测"""
        # 模拟一个可能较慢的操作
        start_time = time.time()

        # 获取商品详情（可能触发慢查询）
        product_id = random.randint(80, 100)  # 使用较大的ID，可能触发未找到情况

        with self.client.get(
            f"/api/products/{product_id}", name="慢操作测试", catch_response=True
        ) as response:
            response_time = (time.time() - start_time) * 1000

            # 强制增加一些处理时间来模拟慢操作
            time.sleep(0.05)  # 50ms额外延迟

            success = response.status_code in [200, 404]  # 404也算正常
            self.environment.performance_data.append(
                {
                    "response_time": response_time + 50,  # 包含额外延迟
                    "success": success,
                    "timestamp": datetime.now().isoformat(),
                    "name": "商品详情API(慢)",
                    "method": "GET",
                }
            )

            if success:
                response.success()
            else:
                response.failure(f"意外错误: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始 - 初始化性能分析"""
    print("🚀 性能分析测试开始")

    # 初始化性能数据收集
    environment.performance_data = []

    # 初始化分析器
    environment.performance_analyzer = PerformanceAnalyzer()
    environment.trend_analyzer = TrendAnalyzer()
    environment.report_generator = ReportGenerator()

    # 设置性能阈值
    environment.performance_analyzer.set_thresholds(
        response_time_p95=800,  # 95%响应时间阈值调整为800ms
        response_time_p99=1500,  # 99%响应时间阈值调整为1500ms
        error_rate=0.03,  # 错误率阈值3%
        throughput_min=15,  # 最小吞吐量15 TPS
    )

    # 记录开始时间
    environment.test_start_time = datetime.now()

    print("📊 性能分析器已初始化")
    print(
        f"   响应时间阈值: P95={environment.performance_analyzer.thresholds['response_time_p95']}ms"
    )
    print(
        f"   错误率阈值: {environment.performance_analyzer.thresholds['error_rate']*100}%"
    )
    print(
        f"   吞吐量阈值: {environment.performance_analyzer.thresholds['throughput_min']} TPS"
    )


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束 - 执行性能分析"""
    print("✅ 性能测试完成，开始分析...")

    if not hasattr(environment, "performance_data") or not environment.performance_data:
        print("⚠️  没有收集到性能数据")
        return

    try:
        # 准备测试数据
        test_data = {
            "test_name": "性能分析测试",
            "start_time": environment.test_start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": int(
                (datetime.now() - environment.test_start_time).total_seconds()
            ),
            "users": getattr(environment.parsed_options, "num_users", 1),
            "requests": environment.performance_data,
        }

        print(f"📊 开始分析 {len(environment.performance_data)} 条请求数据...")

        # 执行综合性能分析
        analysis_result = environment.performance_analyzer.comprehensive_analysis(
            test_data
        )

        # 输出分析结果摘要
        print("\n🔍 性能分析结果:")
        print(f"   综合评级: {analysis_result['overall_grade']}")

        if analysis_result.get("response_time"):
            rt = analysis_result["response_time"]
            print(
                f"   响应时间: 平均{rt.get('mean', 0):.1f}ms, P95={rt.get('p95', 0):.1f}ms, 评级={rt.get('performance_grade', 'N/A')}"
            )

        if analysis_result.get("throughput"):
            tp = analysis_result["throughput"]
            print(
                f"   吞吐量: 平均{tp.get('avg_tps', 0):.1f} TPS, 评级={tp.get('performance_grade', 'N/A')}"
            )

        if analysis_result.get("error_analysis"):
            er = analysis_result["error_analysis"]
            print(
                f"   错误率: {er.get('error_percentage', 0):.2f}%, 评级={er.get('performance_grade', 'N/A')}"
            )

        # 输出优化建议
        if analysis_result.get("recommendations"):
            print("\n💡 优化建议:")
            for i, recommendation in enumerate(analysis_result["recommendations"], 1):
                print(f"   {i}. {recommendation}")

        # 生成报告
        print("\n📋 正在生成性能报告...")

        # 生成JSON报告
        json_report_path = environment.report_generator.generate_json_report(
            analysis_result,
            output_filename=f"performance_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        )
        print(f"   JSON报告: {json_report_path}")

        # 生成HTML报告 (暂时跳过，模板有问题)
        print("   HTML报告生成跳过 (模板修复中...)")

        # 生成CSV摘要
        csv_report_path = environment.report_generator.generate_csv_summary(
            analysis_result,
            output_filename=f"performance_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        )
        print(f"   CSV摘要: {csv_report_path}")

        # 添加到趋势分析（为未来的趋势分析做准备）
        environment.trend_analyzer.add_historical_data(analysis_result)

        print(f"\n🎯 性能分析完成! 总体评级: {analysis_result['overall_grade']}")

        # 如果性能不佳，给出警告
        if analysis_result["overall_grade"] in ["C", "D"]:
            print("⚠️  检测到性能问题，请检查分析报告中的优化建议")

    except Exception as e:
        print(f"❌ 性能分析过程中出现错误: {e}")
        import traceback

        traceback.print_exc()


# 定期执行中间分析
# 注意：使用request事件代替用户生命周期事件进行中间分析
@events.request.add_listener
def on_request(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    start_time,
    url,
    **kwargs,
):
    """请求完成时的事件 - 用于中间分析"""
    global request_count
    if not hasattr(on_request, "counter"):
        on_request.counter = 0

    on_request.counter += 1

    # 每100个请求执行一次中间分析
    if on_request.counter % 100 == 0:
        print(f"📊 已完成 {on_request.counter} 个请求，执行中间分析...")
        if exception:
            print(f"❌ 检测到错误: {exception}")


# 用于跟踪请求计数
request_count = 0


if __name__ == "__main__":
    print("💡 这是一个性能分析集成示例")
    print("🔧 使用方法:")
    print("   locust -f locustfiles/examples/04_performance_analysis.py")
    print(
        "   locust -f locustfiles/examples/04_performance_analysis.py --headless -u 10 -r 2 -t 120s"
    )
    print("")
    print("📋 测试内容:")
    print("   - API性能测试和数据收集")
    print("   - 实时性能数据分析")
    print("   - 综合性能评分")
    print("   - 多格式报告生成")
    print("   - 性能优化建议")
    print("")
    print("🎯 学习要点:")
    print("   - PerformanceAnalyzer集成")
    print("   - 实时性能数据收集")
    print("   - comprehensive_analysis API")
    print("   - 自动报告生成")
    print("   - 性能阈值配置")
    print("")
    print("📊 生成的报告:")
    print("   - reports/performance_analysis_*.json")
    print("   - reports/performance_analysis_*.html")
    print("   - reports/performance_summary_*.csv")
