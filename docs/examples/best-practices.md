# 性能测试最佳实践

本文档总结了使用Locust性能测试框架的最佳实践，帮助您编写高质量的性能测试并获得准确的测试结果。

## 🎯 测试设计原则

### 1. 真实性原则

**模拟真实用户行为**
```python
from locust import HttpUser, task, between
import random

class RealisticUser(HttpUser):
    """真实用户行为模拟"""

    # 真实的等待时间分布
    wait_time = between(2, 8)  # 用户思考时间2-8秒

    def on_start(self):
        """用户会话开始 - 模拟登录流程"""
        self.login()
        self.load_user_preferences()

    def login(self):
        """真实的登录流程"""
        # 先访问登录页面
        self.client.get("/login")

        # 模拟用户输入延迟
        time.sleep(random.uniform(1, 3))

        # 执行登录
        response = self.client.post("/api/login", json={
            "username": f"user_{random.randint(1, 1000)}",
            "password": "password123"
        })

        if response.status_code == 200:
            self.token = response.json().get("token")

    @task(5)  # 浏览行为占主要比重
    def browse_products(self):
        """浏览产品 - 最常见的用户行为"""
        # 模拟用户浏览多个页面
        for _ in range(random.randint(1, 5)):
            product_id = random.randint(1, 100)
            self.client.get(f"/products/{product_id}")

            # 模拟阅读时间
            time.sleep(random.uniform(3, 10))

    @task(2)  # 搜索行为
    def search_products(self):
        """搜索产品"""
        keywords = ["laptop", "phone", "tablet", "headphones", "camera"]
        keyword = random.choice(keywords)

        self.client.get(f"/search", params={"q": keyword})

        # 模拟查看搜索结果
        time.sleep(random.uniform(2, 5))

    @task(1)  # 购买行为相对较少
    def purchase_flow(self):
        """完整的购买流程"""
        if not hasattr(self, 'token'):
            return

        # 1. 添加到购物车
        product_id = random.randint(1, 50)
        self.client.post("/api/cart/add",
                        json={"product_id": product_id, "quantity": 1},
                        headers={"Authorization": f"Bearer {self.token}"})

        # 2. 查看购物车
        time.sleep(random.uniform(1, 3))
        self.client.get("/cart",
                       headers={"Authorization": f"Bearer {self.token}"})

        # 3. 结算（只有部分用户会完成购买）
        if random.random() < 0.3:  # 30%的转化率
            self.client.post("/api/checkout",
                           json={"payment_method": "credit_card"},
                           headers={"Authorization": f"Bearer {self.token}"})
```

### 2. 渐进式加压原则

**避免突然的负载冲击**
```python
from locust import LoadTestShape

class GradualLoadShape(LoadTestShape):
    """渐进式负载模式"""

    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},    # 预热阶段
        {"duration": 120, "users": 50, "spawn_rate": 5},   # 缓慢增长
        {"duration": 300, "users": 200, "spawn_rate": 10}, # 目标负载
        {"duration": 180, "users": 200, "spawn_rate": 10}, # 稳定运行
        {"duration": 60, "users": 50, "spawn_rate": 5},    # 缓慢下降
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])

        return None
```

### 3. 数据隔离原则

**使用独立的测试数据**
```python
import csv
import random
from typing import List, Dict

class TestDataManager:
    """测试数据管理器"""

    def __init__(self, data_file: str):
        self.data_file = data_file
        self.test_data = self.load_test_data()
        self.used_data = set()

    def load_test_data(self) -> List[Dict]:
        """加载测试数据"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as file:
                return list(csv.DictReader(file))
        except FileNotFoundError:
            # 生成默认测试数据
            return self.generate_test_data(1000)

    def generate_test_data(self, count: int) -> List[Dict]:
        """生成测试数据"""
        data = []
        for i in range(count):
            data.append({
                "user_id": f"test_user_{i:04d}",
                "email": f"test{i:04d}@example.com",
                "phone": f"1{random.randint(3000000000, 9999999999)}",
                "region": random.choice(["北京", "上海", "广州", "深圳"])
            })
        return data

    def get_unique_data(self) -> Dict:
        """获取唯一的测试数据"""
        available_data = [d for d in self.test_data
                         if d["user_id"] not in self.used_data]

        if not available_data:
            # 重置已使用数据
            self.used_data.clear()
            available_data = self.test_data

        selected = random.choice(available_data)
        self.used_data.add(selected["user_id"])
        return selected

# 在测试中使用
class DataDrivenUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data_manager = TestDataManager("test_data.csv")
        self.user_data = self.data_manager.get_unique_data()
```

## 🔧 性能优化实践

### 1. 连接池优化

```python
from locust import HttpUser
import requests.adapters

class OptimizedHttpUser(HttpUser):
    """优化的HTTP用户"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 配置连接池
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,    # 连接池大小
            pool_maxsize=20,       # 最大连接数
            max_retries=3,         # 重试次数
            pool_block=False       # 非阻塞模式
        )

        self.client.mount("http://", adapter)
        self.client.mount("https://", adapter)

        # 设置超时
        self.client.timeout = (5, 30)  # (连接超时, 读取超时)
```

### 2. 内存管理

```python
import gc
from locust import events

class MemoryOptimizedUser(HttpUser):
    """内存优化的用户类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0

    @task
    def optimized_request(self):
        """优化的请求方法"""
        response = self.client.get("/api/data")

        # 及时释放响应内容
        if hasattr(response, 'close'):
            response.close()

        self.request_count += 1

        # 定期触发垃圾回收
        if self.request_count % 100 == 0:
            gc.collect()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时清理资源"""
    gc.collect()
    print("Memory cleanup completed")
```

### 3. 错误处理和重试

```python
import time
from locust.exception import RescheduleTask

class RobustUser(HttpUser):
    """健壮的用户类"""

    def safe_request(self, method: str, url: str, **kwargs):
        """安全的请求方法"""
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                response = getattr(self.client, method)(url, **kwargs)

                # 检查响应状态
                if response.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))  # 指数退避
                        continue
                    else:
                        response.failure(f"Server error: {response.status_code}")

                return response

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                else:
                    # 记录错误并重新调度任务
                    print(f"Request failed after {max_retries} attempts: {e}")
                    raise RescheduleTask()

    @task
    def robust_api_call(self):
        """健壮的API调用"""
        response = self.safe_request("get", "/api/users")

        if response and response.status_code == 200:
            # 处理成功响应
            data = response.json()
            print(f"Retrieved {len(data)} users")
```

## 📊 监控和分析实践

### 1. 自定义指标收集

```python
from locust import events
import time

class CustomMetrics:
    """自定义指标收集器"""

    def __init__(self):
        self.business_metrics = {}
        self.start_time = time.time()

    def record_business_metric(self, metric_name: str, value: float):
        """记录业务指标"""
        if metric_name not in self.business_metrics:
            self.business_metrics[metric_name] = []

        self.business_metrics[metric_name].append({
            'timestamp': time.time(),
            'value': value
        })

    def get_summary(self):
        """获取指标摘要"""
        summary = {}
        for metric_name, values in self.business_metrics.items():
            if values:
                metric_values = [v['value'] for v in values]
                summary[metric_name] = {
                    'count': len(metric_values),
                    'avg': sum(metric_values) / len(metric_values),
                    'min': min(metric_values),
                    'max': max(metric_values)
                }
        return summary

# 全局指标收集器
custom_metrics = CustomMetrics()

class MetricsAwareUser(HttpUser):
    """支持自定义指标的用户"""

    @task
    def business_operation(self):
        """业务操作"""
        start_time = time.time()

        # 执行业务操作
        response = self.client.post("/api/business-operation", json={
            "operation_type": "critical_business_flow",
            "user_id": "test_user"
        })

        # 记录业务指标
        operation_time = (time.time() - start_time) * 1000
        custom_metrics.record_business_metric("business_operation_time", operation_time)

        if response.status_code == 200:
            custom_metrics.record_business_metric("successful_operations", 1)
        else:
            custom_metrics.record_business_metric("failed_operations", 1)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时输出自定义指标"""
    summary = custom_metrics.get_summary()
    print("\n=== Custom Business Metrics ===")
    for metric_name, stats in summary.items():
        print(f"{metric_name}: {stats}")
```

### 2. 实时监控告警

```python
from locust import events
import requests

class AlertManager:
    """告警管理器"""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.alert_thresholds = {
            'error_rate': 5.0,      # 错误率阈值 5%
            'avg_response_time': 2000,  # 平均响应时间阈值 2秒
            'rps': 100              # 最小RPS阈值
        }
        self.last_alert_time = {}
        self.alert_cooldown = 300   # 告警冷却时间 5分钟

    def check_and_alert(self, stats):
        """检查指标并发送告警"""
        current_time = time.time()

        # 检查错误率
        if stats.total.num_requests > 0:
            error_rate = (stats.total.num_failures / stats.total.num_requests) * 100
            if error_rate > self.alert_thresholds['error_rate']:
                self.send_alert("high_error_rate",
                              f"Error rate: {error_rate:.2f}%", current_time)

        # 检查响应时间
        if stats.total.avg_response_time > self.alert_thresholds['avg_response_time']:
            self.send_alert("high_response_time",
                          f"Avg response time: {stats.total.avg_response_time:.2f}ms",
                          current_time)

        # 检查RPS
        if stats.total.current_rps < self.alert_thresholds['rps']:
            self.send_alert("low_rps",
                          f"Current RPS: {stats.total.current_rps:.2f}",
                          current_time)

    def send_alert(self, alert_type: str, message: str, current_time: float):
        """发送告警"""
        # 检查冷却时间
        if alert_type in self.last_alert_time:
            if current_time - self.last_alert_time[alert_type] < self.alert_cooldown:
                return

        self.last_alert_time[alert_type] = current_time

        alert_message = f"🚨 Performance Alert: {alert_type}\n{message}"
        print(alert_message)

        # 发送到外部系统
        if self.webhook_url:
            try:
                requests.post(self.webhook_url, json={
                    "text": alert_message,
                    "alert_type": alert_type,
                    "timestamp": current_time
                }, timeout=5)
            except Exception as e:
                print(f"Failed to send alert: {e}")

# 全局告警管理器
alert_manager = AlertManager("https://hooks.slack.com/your-webhook-url")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时初始化监控"""
    print("Performance monitoring started")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时发送总结"""
    stats = environment.stats
    alert_manager.check_and_alert(stats)
    print("Performance monitoring completed")
```

## 🎯 测试策略实践

### 1. 分层测试策略

```python
# 基准测试
class BaselineTest(HttpUser):
    """基准性能测试"""
    wait_time = between(1, 2)

    @task
    def baseline_request(self):
        self.client.get("/api/health")

# 负载测试
class LoadTest(HttpUser):
    """负载测试"""
    wait_time = between(2, 5)

    @task(3)
    def normal_operation(self):
        self.client.get("/api/users")

    @task(1)
    def heavy_operation(self):
        self.client.post("/api/reports/generate")

# 压力测试
class StressTest(HttpUser):
    """压力测试"""
    wait_time = between(0.5, 1)

    @task
    def stress_operation(self):
        # 高频率请求
        for _ in range(5):
            self.client.get("/api/data")
```

### 2. 环境配置管理

```python
import os
from typing import Dict, Any

class EnvironmentConfig:
    """环境配置管理"""

    ENVIRONMENTS = {
        "dev": {
            "host": "https://dev-api.example.com",
            "max_users": 50,
            "duration": "5m"
        },
        "staging": {
            "host": "https://staging-api.example.com",
            "max_users": 200,
            "duration": "15m"
        },
        "prod": {
            "host": "https://api.example.com",
            "max_users": 1000,
            "duration": "30m"
        }
    }

    @classmethod
    def get_config(cls, env: str = None) -> Dict[str, Any]:
        """获取环境配置"""
        env = env or os.getenv("TEST_ENV", "dev")
        return cls.ENVIRONMENTS.get(env, cls.ENVIRONMENTS["dev"])

    @classmethod
    def setup_for_environment(cls, env: str = None):
        """为特定环境设置配置"""
        config = cls.get_config(env)

        # 设置环境变量
        os.environ["LOCUST_HOST"] = config["host"]
        os.environ["LOCUST_USERS"] = str(config["max_users"])
        os.environ["LOCUST_RUN_TIME"] = config["duration"]

        return config

# 使用环境配置
config = EnvironmentConfig.setup_for_environment()
print(f"Testing against: {config['host']}")
```

## 📚 报告和文档实践

### 1. 自动化报告生成

```python
import json
from datetime import datetime
from jinja2 import Template

class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.report_template = """
        # Performance Test Report

        **Test Date**: {{ test_date }}
        **Environment**: {{ environment }}
        **Duration**: {{ duration }}

        ## Summary
        - **Total Requests**: {{ total_requests }}
        - **Failed Requests**: {{ failed_requests }}
        - **Error Rate**: {{ error_rate }}%
        - **Average Response Time**: {{ avg_response_time }}ms
        - **95th Percentile**: {{ p95_response_time }}ms
        - **Max Response Time**: {{ max_response_time }}ms
        - **RPS**: {{ rps }}

        ## Performance Grade: {{ grade }}

        ## Recommendations
        {% for rec in recommendations %}
        - {{ rec }}
        {% endfor %}
        """

    def generate_report(self, stats_data: Dict[str, Any],
                       output_file: str = "performance_report.md"):
        """生成性能测试报告"""
        # 计算性能等级
        grade = self.calculate_grade(stats_data)

        # 生成建议
        recommendations = self.generate_recommendations(stats_data)

        # 准备模板数据
        template_data = {
            "test_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "environment": os.getenv("TEST_ENV", "unknown"),
            "grade": grade,
            "recommendations": recommendations,
            **stats_data
        }

        # 渲染报告
        template = Template(self.report_template)
        report_content = template.render(**template_data)

        # 保存报告
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"Report generated: {output_file}")
        return output_file

    def calculate_grade(self, stats: Dict[str, Any]) -> str:
        """计算性能等级"""
        error_rate = stats.get('error_rate', 0)
        avg_response_time = stats.get('avg_response_time', 0)

        if error_rate > 5 or avg_response_time > 3000:
            return "D - Poor"
        elif error_rate > 2 or avg_response_time > 2000:
            return "C - Fair"
        elif error_rate > 1 or avg_response_time > 1000:
            return "B - Good"
        else:
            return "A - Excellent"

    def generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []

        error_rate = stats.get('error_rate', 0)
        avg_response_time = stats.get('avg_response_time', 0)
        rps = stats.get('rps', 0)

        if error_rate > 2:
            recommendations.append("错误率较高，建议检查服务器日志和错误处理逻辑")

        if avg_response_time > 2000:
            recommendations.append("响应时间较长，建议优化数据库查询和缓存策略")

        if rps < 50:
            recommendations.append("吞吐量较低，建议检查服务器配置和网络连接")

        if not recommendations:
            recommendations.append("性能表现良好，建议继续监控关键指标")

        return recommendations
```

## 🔍 故障排查实践

### 1. 常见问题诊断

```python
class PerformanceDiagnostic:
    """性能诊断工具"""

    @staticmethod
    def diagnose_high_response_time(stats):
        """诊断高响应时间问题"""
        issues = []

        if stats.total.avg_response_time > 2000:
            issues.append("平均响应时间过高")

            if stats.total.max_response_time > 10000:
                issues.append("存在极慢的请求，可能是超时或死锁")

            # 检查不同端点的响应时间
            slow_endpoints = []
            for name, stat in stats.entries.items():
                if stat.avg_response_time > 3000:
                    slow_endpoints.append(f"{name}: {stat.avg_response_time:.2f}ms")

            if slow_endpoints:
                issues.append(f"慢端点: {', '.join(slow_endpoints)}")

        return issues

    @staticmethod
    def diagnose_high_error_rate(stats):
        """诊断高错误率问题"""
        issues = []

        if stats.total.num_requests > 0:
            error_rate = (stats.total.num_failures / stats.total.num_requests) * 100

            if error_rate > 5:
                issues.append(f"错误率过高: {error_rate:.2f}%")

                # 分析错误类型
                error_types = {}
                for name, stat in stats.entries.items():
                    if stat.num_failures > 0:
                        failure_rate = (stat.num_failures / stat.num_requests) * 100
                        error_types[name] = failure_rate

                if error_types:
                    sorted_errors = sorted(error_types.items(),
                                         key=lambda x: x[1], reverse=True)
                    top_errors = sorted_errors[:3]
                    issues.append(f"主要错误端点: {top_errors}")

        return issues

@events.test_stop.add_listener
def diagnose_performance_issues(environment, **kwargs):
    """测试结束后进行性能诊断"""
    stats = environment.stats
    diagnostic = PerformanceDiagnostic()

    print("\n=== Performance Diagnostic ===")

    # 诊断响应时间问题
    response_time_issues = diagnostic.diagnose_high_response_time(stats)
    if response_time_issues:
        print("Response Time Issues:")
        for issue in response_time_issues:
            print(f"  - {issue}")

    # 诊断错误率问题
    error_rate_issues = diagnostic.diagnose_high_error_rate(stats)
    if error_rate_issues:
        print("Error Rate Issues:")
        for issue in error_rate_issues:
            print(f"  - {issue}")

    if not response_time_issues and not error_rate_issues:
        print("No significant performance issues detected.")
```

## 🎉 总结

遵循这些最佳实践可以帮助您：

1. **提高测试质量**: 编写更真实、更可靠的性能测试
2. **优化测试性能**: 减少资源消耗，提高测试效率
3. **增强监控能力**: 实时发现和诊断性能问题
4. **改善测试策略**: 采用分层、渐进的测试方法
5. **自动化报告**: 生成专业的测试报告和建议

## 📚 相关文档

- [第一个测试](../getting-started/first-test.md) - 入门指南
- [高级用法](advanced-usage.md) - 高级功能使用
- [故障排除](troubleshooting.md) - 问题诊断和解决
- [配置参考](../configuration/framework-config.md) - 详细配置说明
