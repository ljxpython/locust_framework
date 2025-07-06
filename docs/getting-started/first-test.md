# 第一个性能测试

本指南将带您创建第一个完整的性能测试，从编写测试脚本到分析测试结果。

## 🎯 学习目标

通过本指南，您将学会：
- 编写基础的Locust测试脚本
- 配置测试参数和数据
- 运行性能测试
- 分析测试结果
- 使用框架的高级功能

## 📝 创建测试脚本

### 1. 基础HTTP测试

创建您的第一个测试文件 `my_first_test.py`：

```python
from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    """网站用户行为模拟"""

    # 用户等待时间：1-3秒
    wait_time = between(1, 3)

    def on_start(self):
        """用户开始时执行的操作"""
        self.login()

    def login(self):
        """用户登录"""
        response = self.client.post("/login", json={
            "username": "testuser",
            "password": "testpass"
        })

        if response.status_code == 200:
            self.token = response.json().get("token")
        else:
            print(f"Login failed: {response.status_code}")

    @task(3)
    def view_homepage(self):
        """浏览首页 - 权重3"""
        self.client.get("/")

    @task(2)
    def view_products(self):
        """浏览产品页面 - 权重2"""
        product_id = random.randint(1, 100)
        self.client.get(f"/products/{product_id}")

    @task(1)
    def search_products(self):
        """搜索产品 - 权重1"""
        keywords = ["laptop", "phone", "tablet", "camera"]
        keyword = random.choice(keywords)
        self.client.get(f"/search?q={keyword}")

    @task(1)
    def add_to_cart(self):
        """添加到购物车"""
        if hasattr(self, 'token'):
            product_id = random.randint(1, 50)
            self.client.post("/cart/add",
                           json={"product_id": product_id, "quantity": 1},
                           headers={"Authorization": f"Bearer {self.token}"})

    def on_stop(self):
        """用户结束时执行的操作"""
        if hasattr(self, 'token'):
            self.client.post("/logout",
                           headers={"Authorization": f"Bearer {self.token}"})
```

### 2. 添加数据驱动测试

创建测试数据文件 `test_data.csv`：

```csv
username,password,email
user1,pass123,user1@example.com
user2,pass456,user2@example.com
user3,pass789,user3@example.com
user4,pass000,user4@example.com
```

修改测试脚本使用数据文件：

```python
import csv
from locust import HttpUser, task, between

class DataDrivenUser(HttpUser):
    """数据驱动的用户测试"""

    wait_time = between(1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_data = self.load_test_data()
        self.user_data = None

    def load_test_data(self):
        """加载测试数据"""
        data = []
        try:
            with open('test_data.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)
        except FileNotFoundError:
            print("Warning: test_data.csv not found, using default data")
            data = [{"username": "testuser", "password": "testpass",
                    "email": "test@example.com"}]
        return data

    def on_start(self):
        """选择测试数据并登录"""
        import random
        self.user_data = random.choice(self.test_data)
        self.login()

    def login(self):
        """使用测试数据登录"""
        response = self.client.post("/login", json={
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        })

        if response.status_code == 200:
            self.token = response.json().get("token")
            print(f"User {self.user_data['username']} logged in successfully")
        else:
            print(f"Login failed for {self.user_data['username']}: {response.status_code}")

    @task
    def get_user_profile(self):
        """获取用户资料"""
        if hasattr(self, 'token'):
            self.client.get("/profile",
                          headers={"Authorization": f"Bearer {self.token}"})
```

## ⚙️ 配置测试参数

### 1. 创建配置文件

创建 `test_config.yaml`：

```yaml
# 测试配置
test:
  host: "https://api.example.com"
  users: 50
  spawn_rate: 5
  run_time: "5m"

# 数据配置
data:
  source: "csv"
  file_path: "test_data.csv"
  distribution: "round_robin"

# 监控配置
monitoring:
  enabled: true
  cpu_threshold: 80
  memory_threshold: 85
  response_time_threshold: 2000

# 报告配置
reporting:
  formats: ["html", "csv"]
  output_dir: "reports"
  include_charts: true
```

### 2. 使用配置文件

修改测试脚本读取配置：

```python
import yaml
from locust import HttpUser, task, between

class ConfigurableUser(HttpUser):
    """可配置的用户测试"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = self.load_config()
        self.wait_time = between(1, 3)

    def load_config(self):
        """加载配置文件"""
        try:
            with open('test_config.yaml', 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            return {"test": {"host": "http://localhost:8000"}}

    @task
    def api_test(self):
        """API测试"""
        # 使用配置中的参数
        timeout = self.config.get("test", {}).get("timeout", 30)

        response = self.client.get("/api/health", timeout=timeout)

        # 检查响应时间阈值
        threshold = self.config.get("monitoring", {}).get("response_time_threshold", 2000)
        if response.elapsed.total_seconds() * 1000 > threshold:
            print(f"Warning: Response time {response.elapsed.total_seconds() * 1000}ms exceeds threshold {threshold}ms")
```

## 🚀 运行测试

### 1. 命令行运行

```bash
# 基础运行
locust -f my_first_test.py --host=https://api.example.com

# 指定用户数和生成速率
locust -f my_first_test.py --host=https://api.example.com -u 50 -r 5

# 无头模式运行
locust -f my_first_test.py --host=https://api.example.com -u 50 -r 5 -t 300s --headless

# 生成HTML报告
locust -f my_first_test.py --host=https://api.example.com -u 50 -r 5 -t 300s --headless --html=report.html
```

### 2. 使用框架运行

```python
# run_test.py
from src.model.locust_test import LocustTest

def main():
    # 创建测试实例
    test = LocustTest()

    # 配置测试参数
    test.configure({
        "locustfile": "my_first_test.py",
        "host": "https://api.example.com",
        "users": 50,
        "spawn_rate": 5,
        "run_time": "5m",
        "headless": True
    })

    # 运行测试
    result = test.run()

    # 输出结果
    print(f"Test completed: {result}")

if __name__ == "__main__":
    main()
```

## 📊 分析测试结果

### 1. 查看实时监控

测试运行时，您可以：
- 访问 http://localhost:8089 查看Web界面
- 监控实时性能指标
- 观察错误率和响应时间变化
- 调整用户数和生成速率

### 2. 分析HTML报告

测试完成后，查看生成的HTML报告：

```html
<!-- 报告包含以下信息 -->
- 总体统计信息
- 请求统计详情
- 响应时间分布
- 错误统计和分析
- 性能趋势图表
```

### 3. 使用分析工具

```python
# analyze_results.py
from src.analysis.performance_analyzer import PerformanceAnalyzer

def analyze_test_results():
    analyzer = PerformanceAnalyzer()

    # 加载测试结果
    results = analyzer.load_results("reports/stats.csv")

    # 生成分析报告
    analysis = analyzer.analyze(results)

    # 输出分析结果
    print(f"Performance Grade: {analysis['grade']}")
    print(f"Average Response Time: {analysis['avg_response_time']}ms")
    print(f"95th Percentile: {analysis['p95_response_time']}ms")
    print(f"Error Rate: {analysis['error_rate']}%")
    print(f"Throughput: {analysis['throughput']} RPS")

    # 生成建议
    recommendations = analyzer.get_recommendations(analysis)
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")

if __name__ == "__main__":
    analyze_test_results()
```

## 🔧 使用高级功能

### 1. 添加监控告警

```python
from src.monitoring.system_monitor import SystemMonitor

class MonitoredUser(HttpUser):
    """带监控的用户测试"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = SystemMonitor()
        self.monitor.start()

    @task
    def monitored_request(self):
        """带监控的请求"""
        start_time = time.time()

        response = self.client.get("/api/data")

        # 记录自定义指标
        response_time = (time.time() - start_time) * 1000
        self.monitor.record_metric("custom_response_time", response_time)

        # 检查告警条件
        if response_time > 2000:
            self.monitor.trigger_alert("slow_response", {
                "response_time": response_time,
                "url": "/api/data",
                "user": self.user_data.get("username", "unknown")
            })
```

### 2. 使用插件系统

```python
# custom_plugin.py
from src.plugins.base_plugin import BasePlugin

class TestMetricsPlugin(BasePlugin):
    """自定义测试指标插件"""

    def initialize(self):
        self.request_count = 0
        self.error_count = 0
        return True

    def on_request_success(self, request_type, name, response_time, response_length, **kwargs):
        self.request_count += 1

        # 记录慢请求
        if response_time > 1000:
            print(f"Slow request detected: {name} took {response_time}ms")

    def on_request_failure(self, request_type, name, response_time, response_length, exception, **kwargs):
        self.error_count += 1
        print(f"Request failed: {name} - {exception}")

    def cleanup(self):
        print(f"Test completed: {self.request_count} requests, {self.error_count} errors")

# 在测试中使用插件
from src.plugins.plugin_manager import PluginManager

plugin_manager = PluginManager()
plugin_manager.register_plugin(TestMetricsPlugin)
```

## 🎯 最佳实践

### 1. 测试设计原则

- **渐进式加压**: 从小负载开始，逐步增加
- **真实场景**: 模拟真实用户行为模式
- **数据隔离**: 使用独立的测试数据
- **环境一致**: 保持测试环境的一致性

### 2. 性能指标关注点

- **响应时间**: 关注P95、P99百分位数
- **吞吐量**: 监控TPS和RPS指标
- **错误率**: 保持在可接受范围内
- **资源使用**: 监控CPU、内存、网络

### 3. 问题排查技巧

- **查看日志**: 检查详细的错误日志
- **分析趋势**: 观察性能指标变化趋势
- **对比基线**: 与历史数据进行对比
- **逐步排查**: 从简单到复杂逐步排查

## 🎉 下一步

恭喜！您已经完成了第一个性能测试。接下来可以：

1. **学习高级功能**:
   - [负载模式](../api/load-shapes.md) - 使用不同的负载模式
   - [插件开发](../development/plugin-development.md) - 开发自定义插件
   - [分布式测试](../examples/advanced-usage.md) - 运行分布式测试

2. **优化测试脚本**:
   - [最佳实践](../examples/best-practices.md) - 学习最佳实践
   - [代码规范](../development/coding-standards.md) - 遵循代码规范
   - [测试策略](../examples/advanced-examples.md) - 高级测试策略

3. **生产环境部署**:
   - [生产配置](../configuration/production.md) - 生产环境配置
   - [监控部署](../configuration/monitoring-config.md) - 监控系统部署
   - [CI/CD集成](../examples/advanced-usage.md) - 持续集成

## 📚 相关文档

- [快速入门](quickstart.md) - 5分钟快速上手
- [基础概念](concepts.md) - 核心概念说明
- [API参考](../api/analysis.md) - 详细API文档
- [配置参考](../configuration/framework-config.md) - 配置选项说明
