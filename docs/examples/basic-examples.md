# 基础使用示例

本文档提供框架的基础使用示例，帮助用户快速上手和理解核心功能。

## 🚀 快速开始示例

### 1. 最简单的测试

```python
# locustfiles/simple_test.py
from locust import HttpUser, task, between

class SimpleUser(HttpUser):
    """最简单的用户测试"""
    wait_time = between(1, 2)  # 请求间隔1-2秒

    @task
    def test_homepage(self):
        """测试首页"""
        self.client.get("/")

    @task(2)  # 权重为2，执行频率更高
    def test_about(self):
        """测试关于页面"""
        self.client.get("/about")
```

```bash
# 运行测试
locust -f locustfiles/simple_test.py --host=http://localhost:8080
```

### 2. 带登录的测试

```python
# locustfiles/login_test.py
from locust import HttpUser, task, between

class LoginUser(HttpUser):
    """带登录功能的用户测试"""
    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时执行登录"""
        # 获取登录页面
        response = self.client.get("/login")

        # 提取CSRF token (如果需要)
        # csrf_token = extract_csrf_token(response.text)

        # 执行登录
        login_response = self.client.post("/login", data={
            "username": "testuser",
            "password": "testpass"
        })

        if login_response.status_code == 200:
            print("登录成功")
        else:
            print(f"登录失败: {login_response.status_code}")

    @task(3)
    def view_dashboard(self):
        """查看仪表板"""
        self.client.get("/dashboard")

    @task(2)
    def view_profile(self):
        """查看个人资料"""
        self.client.get("/profile")

    @task(1)
    def update_profile(self):
        """更新个人资料"""
        self.client.post("/profile", data={
            "name": "Test User",
            "email": "test@example.com"
        })
```

## 📊 性能分析示例

### 1. 基础性能分析

```python
# locustfiles/analysis_test.py
from locust import HttpUser, task, between, events
from src.analysis.performance_analyzer import PerformanceAnalyzer
import time

class AnalysisUser(HttpUser):
    """带性能分析的用户测试"""
    wait_time = between(1, 2)

    @task
    def api_request(self):
        """API请求测试"""
        start_time = time.time()

        with self.client.get("/api/data", catch_response=True) as response:
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                # 检查响应内容
                data = response.json()
                if len(data) > 0:
                    response.success()
                else:
                    response.failure("Empty response")
            else:
                response.failure(f"Status code: {response.status_code}")

# 全局变量存储测试数据
test_data = {
    'test_name': 'API性能测试',
    'start_time': None,
    'end_time': None,
    'requests': []
}

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始事件"""
    test_data['start_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    test_data['requests'] = []
    print("开始性能分析...")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """请求事件监听"""
    test_data['requests'].append({
        'response_time': response_time,
        'success': exception is None,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'name': name,
        'method': request_type
    })

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束事件"""
    test_data['end_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    test_data['duration'] = (time.time() - time.mktime(time.strptime(test_data['start_time'], '%Y-%m-%d %H:%M:%S')))
    test_data['users'] = environment.parsed_options.num_users or 1

    # 执行性能分析
    analyzer = PerformanceAnalyzer()
    result = analyzer.comprehensive_analysis(test_data)

    print(f"\n=== 性能分析结果 ===")
    print(f"总体评级: {result['overall_grade']}")
    print(f"平均响应时间: {result['response_time']['avg']:.2f}ms")
    print(f"P95响应时间: {result['response_time']['p95']:.2f}ms")
    print(f"错误率: {result['error_analysis']['error_rate']:.2f}%")

    # 生成报告
    from src.analysis.report_generator import ReportGenerator
    report_generator = ReportGenerator()
    report_generator.generate_html_report(result, 'reports/performance_report.html')
    print("性能报告已生成: reports/performance_report.html")
```

### 2. 自定义负载形状

```python
# locustfiles/custom_shape_test.py
from locust import HttpUser, task, between
from locustfiles.shape_classes.advanced_shapes import WaveLoadShape

class ShapeUser(HttpUser):
    """自定义负载形状测试"""
    wait_time = between(1, 2)

    @task
    def test_endpoint(self):
        """测试端点"""
        self.client.get("/api/test")

class MyWaveShape(WaveLoadShape):
    """波浪形负载"""

    # 配置波浪参数
    min_users = 10      # 最小用户数
    max_users = 100     # 最大用户数
    wave_period = 300   # 波浪周期(秒)
    spawn_rate = 2      # 生成速率

    def tick(self):
        """自定义负载逻辑"""
        run_time = self.get_run_time()

        if run_time < 1800:  # 运行30分钟
            return super().tick()
        else:
            return None  # 停止测试
```

## 🔍 监控告警示例

### 1. 实时监控

```python
# locustfiles/monitoring_test.py
from locust import HttpUser, task, between, events
from src.monitoring.performance_monitor import PerformanceMonitor
from src.monitoring.alert_manager import AlertManager

class MonitoredUser(HttpUser):
    """带监控的用户测试"""
    wait_time = between(1, 3)

    @task
    def monitored_request(self):
        """被监控的请求"""
        with self.client.get("/api/monitored", catch_response=True) as response:
            # 记录自定义指标
            if hasattr(self.environment, 'monitor'):
                self.environment.monitor.record_metric(
                    "custom_response_time",
                    response.elapsed.total_seconds() * 1000
                )

            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status: {response.status_code}")

# 初始化监控组件
monitor = PerformanceMonitor()
alert_manager = AlertManager()

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """初始化监控"""
    environment.monitor = monitor
    environment.alert_manager = alert_manager

    # 配置告警规则
    alert_manager.add_alert_rule({
        "name": "high_response_time",
        "metric": "avg_response_time",
        "condition": ">",
        "threshold": 1000,
        "duration": 60,
        "severity": "warning",
        "message": "响应时间过高"
    })

    # 启动监控
    monitor.start_monitoring()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """停止监控"""
    if hasattr(environment, 'monitor'):
        environment.monitor.stop_monitoring()
```

### 2. 告警通知

```python
# locustfiles/notification_test.py
from locust import HttpUser, task, between, events
from src.monitoring.notification_service import NotificationService

class NotificationUser(HttpUser):
    """带通知的用户测试"""
    wait_time = between(1, 2)

    @task
    def critical_request(self):
        """关键请求测试"""
        response = self.client.get("/api/critical")

        # 检查关键业务指标
        if response.status_code >= 500:
            # 触发紧急通知
            if hasattr(self.environment, 'notification_service'):
                self.environment.notification_service.send_notification(
                    f"关键服务异常: HTTP {response.status_code}",
                    ["feishu", "email"],
                    priority="urgent"
                )

# 初始化通知服务
notification_service = NotificationService()

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """初始化通知服务"""
    environment.notification_service = notification_service

    # 配置通知渠道
    notification_service.register_channel("feishu", {
        "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    })

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始通知"""
    environment.notification_service.send_notification(
        "性能测试开始",
        ["feishu"],
        priority="normal"
    )

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束通知"""
    stats = environment.stats.total
    message = f"""
性能测试完成
- 总请求数: {stats.num_requests}
- 失败请求数: {stats.num_failures}
- 平均响应时间: {stats.avg_response_time:.2f}ms
- 错误率: {stats.fail_ratio:.2%}
    """

    environment.notification_service.send_notification(
        message,
        ["feishu", "email"],
        priority="normal"
    )
```

## 📁 数据驱动测试示例

### 1. CSV数据源

```python
# locustfiles/csv_data_test.py
from locust import HttpUser, task, between
from src.data_manager.data_provider import DataProvider
import csv

class CsvDataUser(HttpUser):
    """CSV数据驱动测试"""
    wait_time = between(1, 2)

    def on_start(self):
        """初始化数据提供者"""
        self.data_provider = DataProvider()

        # 加载CSV数据
        self.users_data = self.data_provider.load_data_from_file(
            "test_data/users.csv",
            distribution_strategy="round_robin"
        )

    @task
    def login_with_csv_data(self):
        """使用CSV数据登录"""
        user_data = self.data_provider.get_next_data("users")

        if user_data:
            response = self.client.post("/login", data={
                "username": user_data["username"],
                "password": user_data["password"]
            })

            if response.status_code == 200:
                # 登录成功后的操作
                self.client.get("/dashboard")
```

```csv
# test_data/users.csv
username,password,email
user1,pass1,user1@example.com
user2,pass2,user2@example.com
user3,pass3,user3@example.com
```

### 2. 动态数据生成

```python
# locustfiles/dynamic_data_test.py
from locust import HttpUser, task, between
from src.data_manager.data_generator import DataGenerator

class DynamicDataUser(HttpUser):
    """动态数据生成测试"""
    wait_time = between(1, 2)

    def on_start(self):
        """初始化数据生成器"""
        self.data_generator = DataGenerator()

    @task
    def create_user_with_dynamic_data(self):
        """使用动态数据创建用户"""
        user_data = {
            "username": self.data_generator.generate_username(),
            "email": self.data_generator.generate_email(),
            "phone": self.data_generator.generate_phone_number(),
            "address": self.data_generator.generate_address(),
            "age": self.data_generator.generate_integer(18, 65)
        }

        response = self.client.post("/api/users", json=user_data)

        if response.status_code == 201:
            user_id = response.json().get("id")
            # 存储生成的用户ID供后续使用
            self.data_generator.store_generated_data("user_ids", user_id)

    @task
    def update_user_profile(self):
        """更新用户资料"""
        user_ids = self.data_generator.get_stored_data("user_ids")
        if user_ids:
            user_id = self.data_generator.get_random_data("user_ids", user_ids)

            update_data = {
                "bio": self.data_generator.generate_text(max_length=200),
                "avatar": self.data_generator.generate_image_url()
            }

            self.client.put(f"/api/users/{user_id}", json=update_data)
```

## 🔌 插件使用示例

### 1. 使用内置插件

```python
# locustfiles/plugin_test.py
from locust import HttpUser, task, between, events
from src.plugins.plugin_manager import PluginManager

class PluginUser(HttpUser):
    """使用插件的测试"""
    wait_time = between(1, 2)

    @task
    def test_with_plugins(self):
        """使用插件增强的测试"""
        self.client.get("/api/data")

# 初始化插件管理器
plugin_manager = PluginManager()

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """初始化插件"""
    # 启用性能分析插件
    plugin_manager.enable_plugin("performance_analyzer", {
        "output_formats": ["html", "json"],
        "include_charts": True
    })

    # 启用系统监控插件
    plugin_manager.enable_plugin("system_monitor", {
        "interval": 5,
        "metrics": ["cpu", "memory", "disk"]
    })

    # 启用通知插件
    plugin_manager.enable_plugin("notification_service", {
        "channels": ["feishu"],
        "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    })

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时触发插件"""
    # 触发报告生成
    plugin_manager.trigger_event("generate_report", {
        "test_data": environment.stats,
        "output_path": "reports/"
    })
```

### 2. 自定义插件示例

```python
# plugins/custom_logger_plugin.py
from src.plugins.plugin_interface import PluginInterface, PluginInfo
import logging

class CustomLoggerPlugin(PluginInterface):
    """自定义日志插件"""

    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="Custom Logger",
            version="1.0.0",
            description="自定义日志记录插件",
            author="Your Name",
            category="logging"
        )

    def initialize(self, config=None) -> bool:
        """初始化插件"""
        self.logger = logging.getLogger("custom_logger")
        handler = logging.FileHandler("custom_test.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        return True

    def cleanup(self):
        """清理资源"""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

    def log_request(self, request_data):
        """记录请求信息"""
        self.logger.info(f"Request: {request_data}")

# 在测试中使用自定义插件
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """请求事件监听"""
    if hasattr(context, 'custom_logger_plugin'):
        context.custom_logger_plugin.log_request({
            "method": request_type,
            "url": name,
            "response_time": response_time,
            "success": exception is None
        })
```

## 🎯 最佳实践示例

### 1. 完整的电商测试场景

```python
# locustfiles/ecommerce_test.py
from locust import HttpUser, task, between, SequentialTaskSet
from src.data_manager.data_generator import DataGenerator
import random

class BrowsingBehavior(SequentialTaskSet):
    """浏览行为任务集"""

    def on_start(self):
        """开始浏览"""
        self.data_generator = DataGenerator()

    @task
    def visit_homepage(self):
        """访问首页"""
        self.client.get("/")

    @task
    def browse_categories(self):
        """浏览分类"""
        categories = ["electronics", "clothing", "books", "home"]
        category = random.choice(categories)
        self.client.get(f"/category/{category}")

    @task
    def search_products(self):
        """搜索商品"""
        keywords = ["phone", "laptop", "shirt", "book"]
        keyword = random.choice(keywords)
        self.client.get(f"/search?q={keyword}")

    @task
    def view_product(self):
        """查看商品详情"""
        product_id = random.randint(1, 1000)
        self.client.get(f"/product/{product_id}")

class ShoppingBehavior(SequentialTaskSet):
    """购物行为任务集"""

    @task
    def add_to_cart(self):
        """添加到购物车"""
        product_id = random.randint(1, 1000)
        self.client.post("/cart/add", json={
            "product_id": product_id,
            "quantity": random.randint(1, 3)
        })

    @task
    def view_cart(self):
        """查看购物车"""
        self.client.get("/cart")

    @task
    def checkout(self):
        """结账"""
        self.client.post("/checkout", json={
            "payment_method": "credit_card",
            "shipping_address": "Test Address"
        })

class EcommerceUser(HttpUser):
    """电商用户"""
    wait_time = between(2, 5)

    # 任务权重分配
    tasks = {
        BrowsingBehavior: 7,  # 70%用户只浏览
        ShoppingBehavior: 3   # 30%用户会购买
    }

    def on_start(self):
        """用户开始时可能登录"""
        if random.random() < 0.3:  # 30%概率登录
            self.login()

    def login(self):
        """用户登录"""
        self.client.post("/login", data={
            "username": f"user{random.randint(1, 1000)}",
            "password": "password123"
        })
```

### 2. API压测最佳实践

```python
# locustfiles/api_stress_test.py
from locust import HttpUser, task, between, events
from locust.exception import RescheduleTask
import time
import json

class APIStressUser(HttpUser):
    """API压力测试用户"""
    wait_time = between(0.1, 0.5)  # 高频请求

    def on_start(self):
        """获取认证token"""
        response = self.client.post("/auth/token", json={
            "client_id": "test_client",
            "client_secret": "test_secret"
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        else:
            raise RescheduleTask("Failed to get auth token")

    @task(5)
    def get_data(self):
        """获取数据 - 高频操作"""
        with self.client.get("/api/v1/data",
                           params={"limit": 10},
                           catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if len(data) > 0:
                    response.success()
                else:
                    response.failure("Empty response")
            elif response.status_code == 429:
                # 处理限流
                response.failure("Rate limited")
                time.sleep(1)
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(2)
    def create_data(self):
        """创建数据 - 中频操作"""
        payload = {
            "name": f"test_item_{int(time.time())}",
            "value": random.randint(1, 100),
            "timestamp": int(time.time())
        }

        with self.client.post("/api/v1/data",
                            json=payload,
                            catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 422:
                response.failure("Validation error")
            else:
                response.failure(f"HTTP {response.status_code}")

    @task(1)
    def update_data(self):
        """更新数据 - 低频操作"""
        item_id = random.randint(1, 1000)
        payload = {
            "value": random.randint(1, 100),
            "updated_at": int(time.time())
        }

        self.client.put(f"/api/v1/data/{item_id}", json=payload)

# 性能监控
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """监控请求性能"""
    if response_time > 1000:  # 响应时间超过1秒
        print(f"Slow request: {name} took {response_time}ms")

    if exception:
        print(f"Request failed: {name} - {exception}")
```

这些示例涵盖了框架的主要功能和使用场景，可以帮助用户快速理解和应用框架的各种特性。
