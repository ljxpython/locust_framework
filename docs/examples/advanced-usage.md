# 高级使用示例

本文档提供框架的高级使用示例，包括复杂场景测试、性能优化、分布式部署等实际应用案例。

## 🎯 复杂负载场景

### 1. 多阶段负载测试

```python
# locustfiles/complex_load_test.py
from locust import HttpUser, task, between
from src.plugins.plugin_manager import PluginManager
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.monitoring.performance_monitor import PerformanceMonitor
from locustfiles.shape_classes.advanced_shapes import MultiStageLoadShape

class ComplexUser(HttpUser):
    """复杂用户行为模拟"""
    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时的初始化"""
        # 登录获取token
        response = self.client.post("/api/login", json={
            "username": "test_user",
            "password": "test_pass"
        })
        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def browse_products(self):
        """浏览商品 - 高频操作"""
        with self.client.get("/api/products",
                           params={"page": 1, "limit": 20},
                           catch_response=True) as response:
            if response.status_code == 200:
                products = response.json().get("data", [])
                if len(products) > 0:
                    response.success()
                else:
                    response.failure("No products returned")

    @task(2)
    def search_products(self):
        """搜索商品 - 中频操作"""
        keywords = ["手机", "电脑", "耳机", "键盘", "鼠标"]
        keyword = self.environment.parsed_options.data_manager.get_random_data("keywords", keywords)

        self.client.get("/api/search", params={"q": keyword})

    @task(1)
    def add_to_cart(self):
        """添加到购物车 - 低频操作"""
        # 先获取商品列表
        response = self.client.get("/api/products", params={"limit": 10})
        if response.status_code == 200:
            products = response.json().get("data", [])
            if products:
                product = products[0]
                self.client.post("/api/cart", json={
                    "product_id": product["id"],
                    "quantity": 1
                })

class MultiStageTest(MultiStageLoadShape):
    """多阶段负载形状"""

    stages = [
        # 预热阶段：5分钟内从0增长到50用户
        {"duration": 300, "users": 50, "spawn_rate": 1},
        # 稳定阶段：保持50用户10分钟
        {"duration": 600, "users": 50, "spawn_rate": 1},
        # 压力阶段：5分钟内增长到200用户
        {"duration": 300, "users": 200, "spawn_rate": 2},
        # 峰值阶段：保持200用户15分钟
        {"duration": 900, "users": 200, "spawn_rate": 2},
        # 降压阶段：5分钟内降到100用户
        {"duration": 300, "users": 100, "spawn_rate": 1},
        # 恢复阶段：保持100用户10分钟
        {"duration": 600, "users": 100, "spawn_rate": 1}
    ]
```

### 2. 数据驱动测试

```python
# locustfiles/data_driven_test.py
from locust import HttpUser, task
from src.data_manager.data_provider import DataProvider
from src.data_manager.data_generator import DataGenerator

class DataDrivenUser(HttpUser):
    """数据驱动的用户测试"""

    def on_start(self):
        """初始化数据提供者"""
        self.data_provider = DataProvider()
        self.data_generator = DataGenerator()

        # 加载测试数据
        self.users_data = self.data_provider.load_data_from_file(
            "test_data/users.csv",
            distribution_strategy="round_robin"
        )

        # 生成动态数据
        self.dynamic_data = self.data_generator.generate_user_data(
            count=1000,
            locale="zh_CN"
        )

    @task
    def user_registration(self):
        """用户注册测试"""
        # 获取测试用户数据
        user_data = self.data_provider.get_next_data("users")

        # 生成随机邮箱避免冲突
        email = self.data_generator.generate_email()

        registration_data = {
            "username": user_data.get("username"),
            "email": email,
            "password": "Test123!",
            "phone": self.data_generator.generate_phone_number(),
            "address": self.data_generator.generate_address()
        }

        response = self.client.post("/api/register", json=registration_data)

        # 验证响应
        if response.status_code == 201:
            user_id = response.json().get("user_id")
            # 存储用户ID供后续使用
            self.data_provider.store_generated_data("user_ids", user_id)

    @task
    def user_profile_update(self):
        """用户资料更新测试"""
        # 获取已注册的用户ID
        user_ids = self.data_provider.get_stored_data("user_ids")
        if not user_ids:
            return

        user_id = self.data_provider.get_random_data("user_ids", user_ids)

        update_data = {
            "nickname": self.data_generator.generate_name(),
            "bio": self.data_generator.generate_text(max_length=200),
            "avatar": self.data_generator.generate_image_url()
        }

        self.client.put(f"/api/users/{user_id}", json=update_data)
```

## 🔧 性能优化实践

### 1. 连接池优化

```python
# locustfiles/optimized_test.py
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from locust import HttpUser, task

class OptimizedHttpUser(HttpUser):
    """优化的HTTP用户类"""

    def on_start(self):
        """配置连接池和重试策略"""
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        # 配置HTTP适配器
        adapter = HTTPAdapter(
            pool_connections=100,  # 连接池大小
            pool_maxsize=100,      # 最大连接数
            max_retries=retry_strategy
        )

        # 应用到客户端
        self.client.mount("http://", adapter)
        self.client.mount("https://", adapter)

        # 设置超时
        self.client.timeout = (5, 30)  # 连接超时5秒，读取超时30秒

    @task
    def optimized_request(self):
        """优化的请求"""
        # 使用会话保持连接
        with self.client.get("/api/data",
                           stream=True,  # 流式处理大响应
                           catch_response=True) as response:
            if response.status_code == 200:
                # 分块处理响应数据
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        # 处理数据块
                        pass
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
```

### 2. 内存优化

```python
# locustfiles/memory_optimized_test.py
import gc
import weakref
from locust import HttpUser, task

class MemoryOptimizedUser(HttpUser):
    """内存优化的用户类"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._response_cache = weakref.WeakValueDictionary()
        self._request_count = 0

    @task
    def memory_efficient_request(self):
        """内存高效的请求"""
        self._request_count += 1

        # 定期清理内存
        if self._request_count % 100 == 0:
            gc.collect()

        # 使用生成器处理大数据
        response = self.client.get("/api/large-data")
        if response.status_code == 200:
            # 避免将大响应存储在内存中
            self._process_response_stream(response)

    def _process_response_stream(self, response):
        """流式处理响应数据"""
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # 逐行处理，避免内存积累
                    self._process_line(line)
        finally:
            # 确保响应被正确关闭
            response.close()

    def _process_line(self, line):
        """处理单行数据"""
        # 处理逻辑，避免存储大量数据
        pass
```

## 📊 实时监控集成

### 1. 自定义监控指标

```python
# locustfiles/monitored_test.py
from locust import HttpUser, task, events
from src.monitoring.performance_monitor import PerformanceMonitor
from src.monitoring.alert_manager import AlertManager
import time

class MonitoredUser(HttpUser):
    """带监控的用户测试"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()

        # 注册自定义指标
        self.monitor.register_custom_metric("business_success_rate", "gauge")
        self.monitor.register_custom_metric("payment_latency", "histogram")

    @task
    def monitored_payment(self):
        """带监控的支付流程"""
        start_time = time.time()

        try:
            # 创建订单
            order_response = self.client.post("/api/orders", json={
                "product_id": 123,
                "quantity": 1,
                "amount": 99.99
            })

            if order_response.status_code != 201:
                self.monitor.increment_counter("payment_failures")
                return

            order_id = order_response.json()["order_id"]

            # 执行支付
            payment_response = self.client.post(f"/api/orders/{order_id}/pay", json={
                "payment_method": "credit_card",
                "card_token": "test_token"
            })

            # 记录业务指标
            if payment_response.status_code == 200:
                self.monitor.set_gauge("business_success_rate", 1)
                self.monitor.increment_counter("successful_payments")
            else:
                self.monitor.set_gauge("business_success_rate", 0)
                self.monitor.increment_counter("failed_payments")

                # 触发告警
                if payment_response.status_code >= 500:
                    self.alert_manager.trigger_alert(
                        "payment_system_error",
                        f"Payment failed with status {payment_response.status_code}",
                        severity="critical"
                    )

        finally:
            # 记录支付延迟
            payment_latency = (time.time() - start_time) * 1000
            self.monitor.record_histogram("payment_latency", payment_latency)

# 事件监听器
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """请求事件监听器"""
    if exception:
        # 记录异常
        monitor = context.get("monitor")
        if monitor:
            monitor.increment_counter(f"exceptions.{type(exception).__name__}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始事件"""
    print("开始监控测试...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束事件"""
    print("停止监控，生成报告...")
```

### 2. 告警规则配置

```python
# 告警配置示例
ALERT_RULES = {
    "response_time_high": {
        "metric": "avg_response_time",
        "condition": "> 2000",
        "duration": "5m",
        "severity": "warning",
        "message": "平均响应时间超过2秒"
    },
    "error_rate_high": {
        "metric": "error_rate",
        "condition": "> 5",
        "duration": "2m",
        "severity": "critical",
        "message": "错误率超过5%"
    },
    "throughput_low": {
        "metric": "requests_per_second",
        "condition": "< 10",
        "duration": "3m",
        "severity": "warning",
        "message": "吞吐量低于10 RPS"
    }
}
```

## 🌐 分布式测试部署

### 1. Master-Worker配置

```python
# master_config.py
MASTER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8089,
    "expect_workers": 5,
    "worker_timeout": 60,
    "stats_history_enabled": True,
    "web_ui_enabled": True
}

# worker_config.py
WORKER_CONFIG = {
    "master_host": "192.168.1.100",
    "master_port": 8089,
    "worker_id": None,  # 自动生成
    "heartbeat_interval": 3
}
```

### 2. Docker部署

```dockerfile
# Dockerfile.master
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8089 5557

CMD ["locust", "-f", "locustfiles/distributed_test.py", "--master", "--host=http://api.example.com"]
```

```dockerfile
# Dockerfile.worker
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["locust", "-f", "locustfiles/distributed_test.py", "--worker", "--master-host=master"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  master:
    build:
      context: .
      dockerfile: Dockerfile.master
    ports:
      - "8089:8089"
      - "5557:5557"
    environment:
      - LOCUST_MODE=master
    volumes:
      - ./reports:/app/reports

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      - LOCUST_MODE=worker
      - LOCUST_MASTER_HOST=master
    depends_on:
      - master
    deploy:
      replicas: 3
    volumes:
      - ./test_data:/app/test_data
```

### 3. Kubernetes部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-master
spec:
  replicas: 1
  selector:
    matchLabels:
      app: locust-master
  template:
    metadata:
      labels:
        app: locust-master
    spec:
      containers:
      - name: locust-master
        image: locust-framework:latest
        ports:
        - containerPort: 8089
        - containerPort: 5557
        env:
        - name: LOCUST_MODE
          value: "master"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: locust-worker
spec:
  replicas: 5
  selector:
    matchLabels:
      app: locust-worker
  template:
    metadata:
      labels:
        app: locust-worker
    spec:
      containers:
      - name: locust-worker
        image: locust-framework:latest
        env:
        - name: LOCUST_MODE
          value: "worker"
        - name: LOCUST_MASTER_HOST
          value: "locust-master-service"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: locust-master-service
spec:
  selector:
    app: locust-master
  ports:
  - name: web
    port: 8089
    targetPort: 8089
  - name: communication
    port: 5557
    targetPort: 5557
  type: LoadBalancer
```
