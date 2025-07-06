# 快速入门指南

本指南将在5分钟内带您体验Locust性能测试框架的核心功能。

## 🚀 5分钟快速体验

### 步骤1：验证安装

```bash
# 检查Python和Locust版本
python --version
python -c "import locust; print(f'Locust版本: {locust.__version__}')"

# 检查框架组件
python -c "
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.plugins.plugin_manager import PluginManager
print('框架组件加载成功！')
"
```

### 步骤2：创建第一个测试

创建文件 `my_first_test.py`：

```python
from locust import HttpUser, task, between
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.monitoring.performance_monitor import PerformanceMonitor, AlertRule

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # 用户等待时间1-3秒

    def on_start(self):
        """用户开始时执行"""
        self.client.verify = False  # 忽略SSL证书验证

    @task(3)
    def view_homepage(self):
        """访问首页 - 权重3"""
        self.client.get("/")

    @task(2)
    def view_about(self):
        """访问关于页面 - 权重2"""
        self.client.get("/about")

    @task(1)
    def view_contact(self):
        """访问联系页面 - 权重1"""
        self.client.get("/contact")

# 配置性能监控
def setup_monitoring():
    """设置性能监控"""
    alert_rules = [
        AlertRule("响应时间告警", "avg_response_time", 1000, ">", "warning"),
        AlertRule("错误率告警", "error_rate", 5.0, ">", "critical")
    ]

    monitor = PerformanceMonitor(alert_rules=alert_rules)
    monitor.start_monitoring()
    return monitor

if __name__ == "__main__":
    # 设置监控
    monitor = setup_monitoring()
    print("性能监控已启动，准备开始测试...")
```

### 步骤3：运行测试

```bash
# 启动Locust Web界面
locust -f my_first_test.py --host=http://httpbin.org

# 或者使用命令行模式
locust -f my_first_test.py --host=http://httpbin.org \
       --users 10 --spawn-rate 2 --run-time 60s --headless
```

### 步骤4：查看结果

打开浏览器访问 `http://localhost:8089`，您将看到：
- 实时性能指标
- 请求统计信息
- 响应时间分布
- 错误统计

测试完成后，您可以在以下位置找到详细报告：
- `reports/` - 生成的HTML和JSON报告
- `logs/` - 详细的测试日志
- Web界面的统计页面

## 📊 使用增强功能

### 性能分析示例

```python
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.analysis.report_generator import ReportGenerator

# 创建分析器
analyzer = PerformanceAnalyzer()

# 模拟测试数据
test_data = {
    'test_name': '快速入门测试',
    'start_time': '2024-01-01 10:00:00',
    'end_time': '2024-01-01 10:05:00',
    'duration': 300,
    'users': 10,
    'requests': [
        {'response_time': 200, 'success': True, 'name': 'GET /'},
        {'response_time': 350, 'success': True, 'name': 'GET /about'},
        {'response_time': 1200, 'success': False, 'name': 'GET /contact'},
        # ... 更多请求数据
    ]
}

# 执行分析
result = analyzer.comprehensive_analysis(test_data)
print(f"性能评分: {result['overall_grade']}")
print(f"响应时间P95: {result['response_time']['p95']}ms")

# 生成报告
report_generator = ReportGenerator()
report_generator.generate_html_report(result, 'reports/quickstart_report.html')
print("报告已生成: reports/quickstart_report.html")
```

### 数据管理示例

```python
from src.data_manager.data_generator import DataGenerator
from src.data_manager.data_provider import DataProvider

# 生成测试数据
generator = DataGenerator()
users = generator.generate_users(count=100)
products = generator.generate_products(count=50)

print(f"生成了 {len(users)} 个用户和 {len(products)} 个产品")

# 使用数据提供器
provider = DataProvider()
provider.add_data('users', users)
provider.add_data('products', products)

# 在测试中获取数据
user = provider.get_data('users')  # 轮询获取
product = provider.get_data('products', strategy='random')  # 随机获取

print(f"获取用户: {user['name']}")
print(f"获取产品: {product['name']}")
```

### 插件系统示例

```python
from src.plugins.plugin_manager import PluginManager

# 创建插件管理器
plugin_manager = PluginManager()

# 查看可用插件
plugins = plugin_manager.get_available_plugins()
print(f"可用插件: {plugins}")

# 启用CSV报告插件
if 'csv_report_plugin' in plugins:
    plugin_manager.enable_plugin('csv_report_plugin', {
        'output_directory': 'reports/csv',
        'include_summary': True
    })
    print("CSV报告插件已启用")

# 获取插件状态
status = plugin_manager.get_plugin_status()
for name, info in status.items():
    print(f"插件 {name}: {'启用' if info['enabled'] else '禁用'}")
```

## 🔧 高级负载模式

### 波浪负载测试

```python
from locust import HttpUser, task, LoadTestShape
from locustfiles.shape_classes.advanced_shapes import WaveLoadShape

class MyWaveTest(LoadTestShape):
    """波浪形负载测试"""

    def __init__(self):
        super().__init__()
        self.wave_shape = WaveLoadShape(
            min_users=5,      # 最小用户数
            max_users=50,     # 最大用户数
            wave_period=120,  # 波浪周期2分钟
            spawn_rate=5,     # 用户生成速率
            time_limit=600    # 总测试时间10分钟
        )

    def tick(self):
        return self.wave_shape.tick()

class WebsiteUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def load_page(self):
        self.client.get("/")
```

### 尖峰负载测试

```python
from locustfiles.shape_classes.advanced_shapes import SpikeLoadShape

class MySpikeTest(LoadTestShape):
    """尖峰负载测试"""

    def __init__(self):
        super().__init__()
        self.spike_shape = SpikeLoadShape(
            base_users=20,      # 基础用户数
            spike_users=100,    # 尖峰用户数
            spike_duration=30,  # 尖峰持续30秒
            spike_interval=180, # 每3分钟一次尖峰
            spawn_rate=10,      # 用户生成速率
            time_limit=900      # 总测试时间15分钟
        )

    def tick(self):
        return self.spike_shape.tick()
```

## 📈 实时监控配置

### 配置告警规则

```python
from src.monitoring.performance_monitor import PerformanceMonitor, AlertRule
from src.monitoring.notification_service import NotificationService

# 创建告警规则
alert_rules = [
    AlertRule(
        name="高响应时间",
        metric="avg_response_time",
        threshold=1000,
        operator=">",
        severity="warning"
    ),
    AlertRule(
        name="高错误率",
        metric="error_rate",
        threshold=5.0,
        operator=">",
        severity="critical"
    ),
    AlertRule(
        name="低吞吐量",
        metric="current_rps",
        threshold=10,
        operator="<",
        severity="warning"
    )
]

# 启动监控
monitor = PerformanceMonitor(alert_rules=alert_rules)
monitor.start_monitoring()

# 配置通知（可选）
notification_service = NotificationService()
# 配置飞书通知
notification_service.configure_channel('feishu', {
    'webhook_url': 'your-feishu-webhook-url'
})
```

## 🎯 完整测试示例

创建文件 `complete_example.py`：

```python
from locust import HttpUser, task, between, LoadTestShape
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.monitoring.performance_monitor import PerformanceMonitor, AlertRule
from src.data_manager.data_generator import DataGenerator
from src.data_manager.data_provider import DataProvider
from locustfiles.shape_classes.advanced_shapes import RampUpDownLoadShape

# 数据准备
generator = DataGenerator()
provider = DataProvider()

# 生成测试数据
users_data = generator.generate_users(count=100)
provider.add_data('users', users_data)

class APIUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # 获取测试用户数据
        self.user_data = provider.get_data('users')

    @task(3)
    def get_user_profile(self):
        """获取用户信息"""
        user_id = self.user_data['id']
        with self.client.get(f"/users/{user_id}",
                           catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"状态码: {response.status_code}")

    @task(2)
    def update_user_profile(self):
        """更新用户信息"""
        user_id = self.user_data['id']
        update_data = {
            'name': self.user_data['name'],
            'email': self.user_data['email']
        }
        self.client.put(f"/users/{user_id}", json=update_data)

    @task(1)
    def delete_user(self):
        """删除用户（模拟）"""
        user_id = self.user_data['id']
        self.client.delete(f"/users/{user_id}")

class MyLoadShape(LoadTestShape):
    """自定义负载模式"""

    def __init__(self):
        super().__init__()
        self.shape = RampUpDownLoadShape(
            target_users=50,     # 目标用户数
            ramp_up_time=120,    # 2分钟爬升
            hold_time=300,       # 5分钟保持
            ramp_down_time=60,   # 1分钟下降
            spawn_rate=5         # 用户生成速率
        )

    def tick(self):
        return self.shape.tick()

# 设置监控
def setup_monitoring():
    alert_rules = [
        AlertRule("响应时间告警", "avg_response_time", 800, ">", "warning"),
        AlertRule("错误率告警", "error_rate", 3.0, ">", "critical")
    ]

    monitor = PerformanceMonitor(alert_rules=alert_rules)
    monitor.start_monitoring()
    return monitor

if __name__ == "__main__":
    monitor = setup_monitoring()
    print("完整测试示例已准备就绪！")
    print("运行命令: locust -f complete_example.py --host=http://your-api-server")
```

## 🎉 下一步学习

恭喜！您已经完成了快速入门。接下来可以：

1. **深入学习**：
   - [基础概念](concepts.md) - 理解核心概念
   - [API文档](../api/analysis.md) - 查看详细API
   - [最佳实践](../examples/best-practices.md) - 学习经验技巧

2. **实践项目**：
   - [高级示例](../examples/advanced-examples.md) - 复杂场景实现
   - [插件开发](../development/plugin-development.md) - 开发自定义插件
   - [负载模式开发](../development/load-shape-development.md) - 创建负载模式

3. **配置优化**：
   - [框架配置](../configuration/framework-config.md) - 详细配置选项
   - [监控配置](../configuration/monitoring-config.md) - 监控系统配置
   - [生产环境](../configuration/production.md) - 生产环境部署

## 💡 小贴士

- **逐步学习**：从简单的HTTP测试开始，逐步添加高级功能
- **查看日志**：遇到问题时查看日志文件获取详细信息
- **参考示例**：examples目录包含丰富的示例代码
- **社区支持**：遇到问题可以在GitHub提交Issue或参与讨论

## 🔗 相关链接

- [安装指南](installation.md) - 详细安装说明
- [配置参考](../configuration/framework-config.md) - 配置选项说明
- [故障排除](../examples/troubleshooting.md) - 常见问题解决
- [GitHub仓库](https://github.com/your-repo) - 源码和问题反馈
