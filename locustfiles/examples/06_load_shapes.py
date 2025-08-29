#!/usr/bin/env python3
"""
负载模式示例

演示框架支持的各种负载模式
目标：展示不同负载曲线对系统性能的影响
"""

import math
import time

from locust import HttpUser, LoadTestShape, between, events, task
from locust.env import Environment

# ==================== 负载模式定义 ====================
# 注意：同时只能有一个LoadTestShape类处于激活状态
# 要使用不同的负载模式，请注释掉其他形状，只保留一个取消注释


# 1. 阶梯负载模式 (默认激活)
class StepLoadShape(LoadTestShape):
    """阶梯负载模式"""

    stages = [
        {"duration": 30, "users": 5, "spawn_rate": 2},  # 阶段1: 30秒内到达5用户
        {"duration": 60, "users": 10, "spawn_rate": 2},  # 阶段2: 60秒内到达10用户
        {"duration": 90, "users": 20, "spawn_rate": 5},  # 阶段3: 90秒内到达20用户
        {"duration": 120, "users": 15, "spawn_rate": 3},  # 阶段4: 120秒内降到15用户
        {"duration": 150, "users": 5, "spawn_rate": 5},  # 阶段5: 150秒内降到5用户
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return stage["users"], stage["spawn_rate"]

        return None  # 测试结束


# 2. 波浪负载模式 (取消注释以使用)
## class WaveLoadShape(LoadTestShape):
##     """波浪负载模式"""
#
#    def __init__(self):
#        self.min_users = 5
#        self.max_users = 25
#        self.wave_period = 60  # 60秒一个周期
#        self.spawn_rate = 3
#        self.total_duration = 180  # 总共3分钟
#
#    def tick(self):
#        run_time = self.get_run_time()
#
#        if run_time >= self.total_duration:
#            return None
#
#        # 计算正弦波用户数
#        wave_position = (run_time % self.wave_period) / self.wave_period
#        sine_value = math.sin(2 * math.pi * wave_position)
#
#        # 将正弦值映射到用户数范围
#        user_range = self.max_users - self.min_users
#        current_users = self.min_users + int((sine_value + 1) / 2 * user_range)
#
#        return current_users, self.spawn_rate
# """
#
## 3. 尖峰负载模式 (取消注释以使用)
# """
# class SpikeLoadShape(LoadTestShape):
#    """尖峰负载模式"""
#
#    def __init__(self):
#        self.base_users = 8
#        self.spike_users = 30
#        self.spawn_rate = 10
#        self.spike_start = 60   # 60秒时开始尖峰
#        self.spike_duration = 30  # 尖峰持续30秒
#        self.total_duration = 180
#
#    def tick(self):
#        run_time = self.get_run_time()
#
#        if run_time >= self.total_duration:
#            return None
#
#        # 检查是否在尖峰期间
#        spike_end = self.spike_start + self.spike_duration
#        if self.spike_start <= run_time < spike_end:
#            return self.spike_users, self.spawn_rate
#        else:
#            return self.base_users, self.spawn_rate
# """
#
## 4. 自定义负载模式 (取消注释以使用)
# """
# class CustomLoadShape(LoadTestShape):
#    """自定义负载模式 - 演示复杂场景"""
#
#    def tick(self):
#        run_time = self.get_run_time()
#
#        # 阶段1: 预热 (0-30秒)
#        if run_time < 30:
#            return 3, 1
#
#        # 阶段2: 正常负载 (30-90秒)
#        elif run_time < 90:
#            return 10, 2
#
#        # 阶段3: 压力测试 (90-120秒)
#        elif run_time < 120:
#            return 25, 5
#
#        # 阶段4: 峰值负载 (120-140秒)
#        elif run_time < 140:
#            return 40, 10
#
#        # 阶段5: 恢复 (140-180秒)
#        elif run_time < 180:
#            return 8, 3
#
#        # 测试结束
#        return None
# """
#
# ==================== 用户行为定义 ====================


class LoadShapeUser(HttpUser):
    """负载模式测试用户"""

    wait_time = between(1, 2)
    host = "http://localhost:5004"

    def on_start(self):
        """用户启动时记录"""
        current_users = getattr(self.environment.runner, "user_count", 0)
        print(f"🏃 用户启动 (当前总用户数: {current_users})")

    def on_stop(self):
        """用户停止时记录"""
        current_users = getattr(self.environment.runner, "user_count", 0)
        print(f"🛑 用户停止 (当前总用户数: {current_users})")

    @task(3)
    def lightweight_request(self):
        """轻量级请求"""
        with self.client.get("/health", name="健康检查") as response:
            pass

    @task(2)
    def medium_request(self):
        """中等负载请求"""
        with self.client.get(
            "/api/products?page=1&limit=10", name="商品列表"
        ) as response:
            pass

    @task(1)
    def heavy_request(self):
        """重负载请求"""
        # 模拟较重的操作
        time.sleep(0.1)  # 100ms额外处理时间
        with self.client.get(
            "/api/search?q=test&sort=price", name="商品搜索"
        ) as response:
            pass


# ==================== 事件监听器 ====================


@events.test_start.add_listener
def on_test_start(environment: Environment, **kwargs):
    """测试开始"""
    print("🚀 负载模式测试开始")

    # 检测负载模式类型
    shape_class = (
        environment.parsed_options.shape_class
        if hasattr(environment.parsed_options, "shape_class")
        else None
    )

    if shape_class:
        shape_name = shape_class.__name__
        print(f"📊 负载模式: {shape_name}")

        # 根据负载模式输出说明
        if shape_name == "StepLoadShape":
            print("   阶梯式增加负载，测试系统在不同负载级别下的表现")
        elif shape_name == "WaveLoadShape":
            print("   波浪式负载变化，测试系统对动态负载的适应性")
        elif shape_name == "SpikeLoadShape":
            print("   突发尖峰负载，测试系统的峰值处理能力")
        elif shape_name == "CustomLoadShape":
            print("   自定义复杂负载场景，全面测试系统性能")
    else:
        print("📊 使用默认负载模式")

    # 初始化负载统计
    environment.load_stats = {
        "start_time": time.time(),
        "user_changes": [],
        "max_users": 0,
        "total_user_seconds": 0,
    }


# 使用request事件替代用户生命周期事件来跟踪负载变化
@events.request.add_listener
def on_load_tracking(
    request_type,
    name,
    response_time,
    response_length,
    response,
    context,
    exception,
    **kwargs,
):
    """通过请求事件跟踪负载模式效果"""
    if not hasattr(on_load_tracking, "last_report_time"):
        on_load_tracking.last_report_time = time.time()
        on_load_tracking.request_count = 0

    on_load_tracking.request_count += 1
    current_time = time.time()

    # 每10秒报告一次负载状态
    if current_time - on_load_tracking.last_report_time >= 10:
        print(f"📈 负载状态报告 - 已完成 {on_load_tracking.request_count} 个请求")
        on_load_tracking.last_report_time = current_time


@events.test_stop.add_listener
def on_test_stop(environment: Environment, **kwargs):
    """测试结束 - 分析负载模式效果"""
    print("✅ 负载模式测试完成")

    if hasattr(environment, "load_stats"):
        load_stats = environment.load_stats
        total_time = time.time() - load_stats["start_time"]

        print(f"\n📊 负载统计摘要:")
        print(f"   测试总时长: {total_time:.1f}秒")
        print(f"   最大并发用户: {load_stats['max_users']}")
        print(f"   用户变化次数: {len(load_stats['user_changes'])}")

        # 分析负载变化模式
        if load_stats["user_changes"]:
            print(f"\n📈 负载变化时间线:")
            for i, change in enumerate(
                load_stats["user_changes"][:10]
            ):  # 显示前10次变化
                action_emoji = "📈" if change["action"] == "add" else "📉"
                print(
                    f"   {action_emoji} {change['time']:6.1f}s -> {change['users']:2d} 用户"
                )

            if len(load_stats["user_changes"]) > 10:
                print(f"   ... 还有 {len(load_stats['user_changes']) - 10} 次变化")

        # 输出性能统计
        stats = environment.stats
        if stats.total.num_requests > 0:
            print(f"\n📊 性能表现:")
            print(f"   总请求数: {stats.total.num_requests}")
            print(f"   平均响应时间: {stats.total.avg_response_time:.1f}ms")
            print(
                f"   错误率: {(stats.total.num_failures/stats.total.num_requests*100):.1f}%"
            )
            print(f"   峰值RPS: {stats.total.max_response_time:.1f}")

            # 根据负载模式给出分析建议
            error_rate = stats.total.num_failures / stats.total.num_requests * 100
            avg_response_time = stats.total.avg_response_time

            print(f"\n💡 负载模式分析:")
            if error_rate > 5:
                print(f"   ⚠️  高错误率 ({error_rate:.1f}%) - 系统在高负载下出现问题")
            elif avg_response_time > 1000:
                print(
                    f"   ⚠️  高响应时间 ({avg_response_time:.1f}ms) - 系统性能在负载压力下下降"
                )
            else:
                print(f"   ✅ 系统在该负载模式下表现良好")

            if load_stats["max_users"] > 0:
                requests_per_user = stats.total.num_requests / load_stats["max_users"]
                print(f"   📊 平均每用户请求数: {requests_per_user:.1f}")


if __name__ == "__main__":
    print("💡 这是一个负载模式示例")
    print("🔧 使用方法:")
    print("   # 当前活跃的负载模式 (默认: StepLoadShape)")
    print("   locust -f locustfiles/examples/06_load_shapes.py --headless")
    print("")
    print("   # 要使用不同的负载模式:")
    print("   1. 编辑文件，注释掉当前激活的LoadTestShape类")
    print("   2. 取消注释想要使用的LoadTestShape类")
    print("   3. 重新运行测试")
    print("")
    print("   # Web UI模式查看实时负载变化")
    print("   locust -f locustfiles/examples/06_load_shapes.py")
    print("")
    print("📋 负载模式特点:")
    print("   - StepLoadShape: 阶梯式负载增长，适合容量规划")
    print("   - WaveLoadShape: 正弦波动负载，模拟真实流量波动")
    print("   - SpikeLoadShape: 突发流量测试，验证系统弹性")
    print("   - CustomLoadShape: 复杂多阶段测试，全面性能评估")
    print("")
    print("🎯 学习要点:")
    print("   - LoadTestShape基类使用")
    print("   - tick()方法实现负载控制")
    print("   - 用户生命周期事件监听")
    print("   - 负载统计和分析")
    print("   - 不同负载模式的适用场景")
