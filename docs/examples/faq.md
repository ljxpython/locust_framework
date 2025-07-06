# 常见问题解答 (FAQ)

本文档收集了Locust性能测试框架使用过程中的常见问题和解决方案，帮助用户快速解决遇到的问题。

## 🚀 安装和配置

### Q1: 如何安装Locust框架？

**A:** 推荐使用pip安装：

```bash
# 基础安装
pip install locust

# 安装完整版本（包含所有依赖）
pip install locust[all]

# 从源码安装
git clone https://github.com/your-org/locust-framework.git
cd locust-framework
pip install -e .
```

### Q2: 支持哪些Python版本？

**A:** 支持Python 3.7及以上版本：
- Python 3.7+
- Python 3.8+ (推荐)
- Python 3.9+
- Python 3.10+
- Python 3.11+

### Q3: 如何配置分布式测试？

**A:** 分布式测试需要启动Master和Worker节点：

```bash
# 启动Master节点
locust -f locustfile.py --master --master-bind-host=0.0.0.0

# 启动Worker节点
locust -f locustfile.py --worker --master-host=master-ip
```

### Q4: Docker部署有什么要求？

**A:** Docker部署要求：
- Docker 20.10+
- Docker Compose 1.29+
- 至少2GB内存
- 网络端口：8089(Web UI), 5557(Master通信)

## 📊 性能测试

### Q5: 如何设置合理的用户数和增长率？

**A:** 建议遵循以下原则：

```python
# 渐进式增长
class GradualLoadShape(LoadTestShape):
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 2},
        {"duration": 120, "users": 50, "spawn_rate": 5},
        {"duration": 180, "users": 100, "spawn_rate": 10},
        {"duration": 300, "users": 200, "spawn_rate": 5}
    ]
```

**建议值：**
- 初始用户数：10-50
- 增长率：1-10 users/second
- 最大用户数：根据目标系统容量确定

### Q6: 响应时间多少算正常？

**A:** 响应时间标准：
- **优秀**: < 200ms
- **良好**: 200ms - 500ms
- **可接受**: 500ms - 1000ms
- **需要优化**: 1000ms - 2000ms
- **不可接受**: > 2000ms

### Q7: 错误率多少是可接受的？

**A:** 错误率标准：
- **生产环境**: < 0.1%
- **测试环境**: < 1%
- **压力测试**: < 5%
- **极限测试**: < 10%

### Q8: 如何模拟真实用户行为？

**A:** 使用以下技术：

```python
class RealisticUser(HttpUser):
    wait_time = between(1, 5)  # 用户思考时间

    def on_start(self):
        self.login()

    @task(3)  # 权重：浏览页面更频繁
    def browse_pages(self):
        self.client.get("/products")
        self.wait()  # 模拟阅读时间

    @task(1)  # 权重：购买行为较少
    def purchase(self):
        self.client.post("/cart/add", json={"product_id": 123})
        self.client.post("/checkout")
```

## 🔧 技术问题

### Q9: 如何处理认证和会话？

**A:** 多种认证方式：

```python
# 1. 基础认证
class AuthenticatedUser(HttpUser):
    def on_start(self):
        response = self.client.post("/login", {
            "username": "testuser",
            "password": "testpass"
        })
        # 会话自动保持在self.client中

# 2. Token认证
class TokenUser(HttpUser):
    def on_start(self):
        response = self.client.post("/auth/token", {
            "username": "testuser",
            "password": "testpass"
        })
        token = response.json()["token"]
        self.client.headers.update({"Authorization": f"Bearer {token}"})

# 3. Cookie认证
class CookieUser(HttpUser):
    def on_start(self):
        self.client.post("/login", {
            "username": "testuser",
            "password": "testpass"
        })
        # Cookies自动处理
```

### Q10: 如何处理动态数据？

**A:** 使用数据生成器：

```python
from faker import Faker
import random

fake = Faker('zh_CN')

class DynamicDataUser(HttpUser):
    def on_start(self):
        self.user_data = {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number()
        }

    @task
    def create_order(self):
        order_data = {
            "product_id": random.randint(1, 1000),
            "quantity": random.randint(1, 5),
            "customer": self.user_data
        }
        self.client.post("/orders", json=order_data)
```

### Q11: 如何测试WebSocket连接？

**A:** 使用WebSocket支持：

```python
from locust import User, task
import websocket
import json

class WebSocketUser(User):
    def on_start(self):
        self.ws = websocket.create_connection("ws://localhost:8080/ws")

    @task
    def send_message(self):
        message = {
            "type": "chat",
            "content": "Hello from Locust!",
            "timestamp": time.time()
        }
        self.ws.send(json.dumps(message))
        response = self.ws.recv()
        print(f"Received: {response}")

    def on_stop(self):
        self.ws.close()
```

### Q12: 如何测试文件上传？

**A:** 文件上传测试：

```python
class FileUploadUser(HttpUser):
    @task
    def upload_file(self):
        # 模拟文件内容
        files = {
            'file': ('test.txt', 'This is test content', 'text/plain')
        }

        response = self.client.post("/upload", files=files)

        # 或者上传真实文件
        with open('test_file.pdf', 'rb') as f:
            files = {'file': ('document.pdf', f, 'application/pdf')}
            response = self.client.post("/upload", files=files)
```

## 📈 监控和分析

### Q13: 如何查看实时测试结果？

**A:** 多种查看方式：
1. **Web UI**: http://localhost:8089
2. **命令行**: 使用 `--headless` 模式
3. **API**: http://localhost:8089/stats/requests
4. **自定义监控**: 集成Prometheus/Grafana

### Q14: 如何导出测试报告？

**A:** 多种导出格式：

```bash
# HTML报告
locust -f locustfile.py --headless -u 100 -r 10 -t 300s --html report.html

# CSV数据
locust -f locustfile.py --headless -u 100 -r 10 -t 300s --csv results

# JSON数据
curl http://localhost:8089/stats/requests | jq . > results.json
```

### Q15: 如何设置自定义指标？

**A:** 添加自定义指标：

```python
from locust import events
import time

# 自定义指标收集
custom_metrics = {}

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    if name == "/api/critical-endpoint":
        if name not in custom_metrics:
            custom_metrics[name] = []
        custom_metrics[name].append(response_time)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    for endpoint, times in custom_metrics.items():
        avg_time = sum(times) / len(times)
        print(f"Custom metric - {endpoint}: {avg_time:.2f}ms average")
```

## 🐛 故障排除

### Q16: 为什么Worker连接不上Master？

**A:** 常见原因和解决方案：

1. **网络问题**:
```bash
# 检查网络连通性
ping master-host
telnet master-host 5557
```

2. **防火墙设置**:
```bash
# 开放端口
sudo ufw allow 5557
sudo ufw allow 8089
```

3. **Docker网络**:
```yaml
# docker-compose.yml
networks:
  locust-network:
    driver: bridge
```

### Q17: 内存使用过高怎么办？

**A:** 内存优化策略：

```python
# 1. 限制数据保存
class MemoryEfficientUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0

    @task
    def make_request(self):
        response = self.client.get("/api/data")
        # 不保存响应数据
        self.request_count += 1

        # 定期清理
        if self.request_count % 100 == 0:
            import gc
            gc.collect()

# 2. 使用流式处理
@task
def download_large_file(self):
    with self.client.get("/large-file", stream=True) as response:
        for chunk in response.iter_content(chunk_size=8192):
            # 处理数据块，不保存到内存
            pass
```

### Q18: 测试结果不稳定怎么办？

**A:** 提高测试稳定性：

1. **预热阶段**:
```python
class StableLoadShape(LoadTestShape):
    def tick(self):
        run_time = self.get_run_time()

        if run_time < 60:  # 预热1分钟
            return (10, 2)
        elif run_time < 300:  # 正式测试
            return (100, 10)
        else:
            return None
```

2. **多次运行取平均值**:
```bash
# 运行多次测试
for i in {1..5}; do
    locust -f locustfile.py --headless -u 100 -r 10 -t 300s --csv run_$i
done
```

### Q19: 如何调试Locust脚本？

**A:** 调试技巧：

```python
import logging

# 1. 启用详细日志
logging.basicConfig(level=logging.DEBUG)

class DebugUser(HttpUser):
    @task
    def debug_request(self):
        # 添加调试信息
        print(f"Making request at {time.time()}")

        response = self.client.get("/api/test")

        # 检查响应
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content: {response.text[:100]}...")

        # 断言检查
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

# 2. 使用断点调试
import pdb

@task
def debug_with_breakpoint(self):
    pdb.set_trace()  # 设置断点
    response = self.client.get("/api/test")
```

## 🔄 最佳实践

### Q20: 性能测试的最佳实践是什么？

**A:** 关键最佳实践：

1. **测试环境**:
   - 使用与生产环境相似的配置
   - 独立的测试环境
   - 稳定的网络条件

2. **测试设计**:
   - 模拟真实用户行为
   - 渐进式负载增长
   - 包含异常场景

3. **数据管理**:
   - 使用真实但脱敏的数据
   - 数据隔离和清理
   - 避免数据污染

4. **结果分析**:
   - 关注多个指标
   - 建立基线对比
   - 趋势分析

### Q21: 如何进行容量规划？

**A:** 容量规划步骤：

1. **确定性能目标**:
   - 预期用户数
   - 响应时间要求
   - 可接受错误率

2. **基准测试**:
   - 单用户性能
   - 逐步增加负载
   - 找到性能拐点

3. **压力测试**:
   - 超出预期负载
   - 系统极限测试
   - 恢复能力测试

4. **容量计算**:
```python
# 容量计算示例
def calculate_capacity(baseline_rps, target_users, safety_margin=0.8):
    """
    计算系统容量

    Args:
        baseline_rps: 基准RPS
        target_users: 目标用户数
        safety_margin: 安全边际
    """
    required_rps = target_users * average_requests_per_user_per_second
    capacity_factor = required_rps / baseline_rps
    recommended_capacity = capacity_factor / safety_margin

    return {
        "required_rps": required_rps,
        "capacity_factor": capacity_factor,
        "recommended_servers": math.ceil(recommended_capacity)
    }
```

## 📚 相关资源

### 有用的链接
- [官方文档](https://docs.locust.io/)
- [GitHub仓库](https://github.com/locustio/locust)
- [社区论坛](https://github.com/locustio/locust/discussions)
- [示例代码](https://github.com/locustio/locust/tree/master/examples)

### 推荐阅读
- [性能测试最佳实践](best-practices.md)
- [故障排除指南](troubleshooting.md)
- [架构设计文档](../architecture/README.md)
- [API参考文档](../api/README.md)

### 社区支持
- **GitHub Issues**: 报告Bug和功能请求
- **Stack Overflow**: 标签 `locust` 或 `performance-testing`
- **Reddit**: r/QualityAssurance, r/Python
- **Discord/Slack**: 加入性能测试社区

---

**提示**: 如果您的问题没有在此FAQ中找到答案，请查看[故障排除指南](troubleshooting.md)或在GitHub上提交Issue。
