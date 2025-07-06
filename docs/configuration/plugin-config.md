# 插件配置参考

本文档详细介绍插件系统的配置选项，包括插件管理、内置插件配置、自定义插件开发配置等。

## 🔌 插件系统概述

插件系统采用模块化设计，支持动态加载、配置管理、依赖检查等功能：

```python
# 插件架构层次
1. 插件管理器 (PluginManager)
2. 插件接口 (PluginInterface)
3. 插件实现 (具体插件类)
4. 插件配置 (配置文件)
```

## ⚙️ 插件管理器配置

### 基础配置 (conf/plugins/plugin_manager.toml)

```toml
[plugin_manager]
# 插件发现配置
discovery_enabled = true
discovery_paths = [
    "src/plugins/builtin",     # 内置插件路径
    "plugins/custom",          # 自定义插件路径
    "~/.locust/plugins",       # 用户插件路径
    "/usr/local/lib/locust/plugins"  # 系统插件路径
]

# 插件加载配置
auto_load_enabled = true
load_timeout = 30
parallel_loading = true
max_load_workers = 4

# 插件依赖管理
dependency_check = true
auto_install_dependencies = false
dependency_timeout = 60

# 插件安全配置
security_check = true
allowed_plugin_sources = ["builtin", "verified", "local"]
signature_verification = false

# 插件缓存配置
cache_enabled = true
cache_directory = ".plugin_cache"
cache_ttl = 3600  # 1小时

# 插件日志配置
logging_enabled = true
log_level = "INFO"
log_file = "logs/plugins.log"
```

### 插件注册表配置

```toml
# conf/plugins/plugin_registry.toml
[registry]
# 注册表配置
registry_file = "conf/plugins/installed_plugins.json"
auto_register = true
register_on_load = true

# 插件元数据
[registry.metadata]
track_usage = true
track_performance = true
track_errors = true

# 插件版本管理
[registry.versioning]
version_check = true
compatibility_check = true
auto_update_check = false
```

## 🔧 内置插件配置

### 性能分析插件

```toml
# conf/plugins/performance_analyzer.toml
[performance_analyzer]
enabled = true
priority = 10

# 分析配置
[performance_analyzer.analysis]
# 响应时间阈值配置 (毫秒)
response_time_thresholds = { excellent = 500, good = 1000, acceptable = 2000, poor = 5000 }

# 吞吐量阈值配置 (TPS)
throughput_thresholds = { excellent = 1000, good = 500, acceptable = 100, poor = 50 }

# 错误率阈值配置 (百分比)
error_rate_thresholds = { excellent = 0.1, good = 1.0, acceptable = 5.0, poor = 10.0 }

# 指标权重配置
metric_weights = { response_time = 0.4, throughput = 0.3, error_rate = 0.2, stability = 0.1 }

# 报告配置
[performance_analyzer.reporting]
output_formats = ["html", "json", "pdf"]
include_charts = true
chart_types = ["line", "bar", "pie"]
template_path = "templates/performance_report.html"
output_directory = "reports/performance"

# 趋势分析配置
[performance_analyzer.trend]
enabled = true
history_days = 30
prediction_days = 7
confidence_level = 0.95
trend_algorithms = ["linear", "polynomial", "seasonal"]
```

### 系统监控插件

```toml
# conf/plugins/system_monitor.toml
[system_monitor]
enabled = true
priority = 5

# 监控配置
[system_monitor.monitoring]
interval = 5  # 监控间隔(秒)
buffer_size = 1000
retention_period = 3600  # 数据保留时间(秒)

# 监控指标配置
[system_monitor.metrics]
cpu_enabled = true
memory_enabled = true
disk_enabled = true
network_enabled = true
process_enabled = true

# CPU监控配置
[system_monitor.metrics.cpu]
per_cpu = true
load_average = true
context_switches = true

# 内存监控配置
[system_monitor.metrics.memory]
virtual_memory = true
swap_memory = true
memory_maps = false

# 磁盘监控配置
[system_monitor.metrics.disk]
disk_usage = true
disk_io = true
mount_points = ["/", "/tmp", "/var"]

# 网络监控配置
[system_monitor.metrics.network]
network_io = true
connections = true
interface_stats = true
interfaces = ["eth0", "lo"]

# 告警配置
[system_monitor.alerts]
cpu_threshold = 80.0
memory_threshold = 85.0
disk_threshold = 90.0
network_threshold = 80.0
```

### 通知服务插件

```toml
# conf/plugins/notification_service.toml
[notification_service]
enabled = true
priority = 8

# 通知渠道配置
[notification_service.channels]
enabled_channels = ["feishu", "dingtalk", "email", "wechat_work"]
default_channels = ["feishu", "email"]
fallback_channels = ["email"]

# 飞书配置
[notification_service.channels.feishu]
enabled = true
webhook_url = "${FEISHU_WEBHOOK_URL}"
secret = "${FEISHU_SECRET}"
at_all = false
at_users = []
message_type = "interactive"  # text, post, interactive
retry_count = 3
retry_interval = 5

# 钉钉配置
[notification_service.channels.dingtalk]
enabled = false
webhook_url = "${DINGTALK_WEBHOOK_URL}"
secret = "${DINGTALK_SECRET}"
at_mobiles = []
at_all = false
retry_count = 3

# 邮件配置
[notification_service.channels.email]
enabled = true
smtp_server = "${EMAIL_SMTP_SERVER}"
smtp_port = 587
username = "${EMAIL_USERNAME}"
password = "${EMAIL_PASSWORD}"
from_addr = "${EMAIL_FROM_ADDR}"
to_addrs = ["${EMAIL_TO_ADDRS}"]
cc_addrs = []
bcc_addrs = []
use_tls = true
use_ssl = false
timeout = 30

# 企业微信配置
[notification_service.channels.wechat_work]
enabled = false
webhook_url = "${WECHAT_WEBHOOK_URL}"
mentioned_list = []
mentioned_mobile_list = []

# 消息模板配置
[notification_service.templates]
test_start = """
🚀 性能测试开始
测试名称: {test_name}
开始时间: {start_time}
目标用户数: {target_users}
测试环境: {environment}
"""

test_complete = """
✅ 性能测试完成
测试名称: {test_name}
结束时间: {end_time}
测试时长: {duration}
总请求数: {total_requests}
成功率: {success_rate}%
平均响应时间: {avg_response_time}ms
报告链接: {report_url}
"""

alert_critical = """
🚨 严重告警
告警名称: {alert_name}
告警级别: {severity}
触发时间: {trigger_time}
告警内容: {message}
当前值: {current_value}
阈值: {threshold}
"""
```

### 数据管理插件

```toml
# conf/plugins/data_manager.toml
[data_manager]
enabled = true
priority = 7

# 数据生成器配置
[data_manager.generator]
locale = "zh_CN"
seed = 12345
cache_size = 10000
cache_ttl = 3600

# 数据提供者配置
[data_manager.provider]
default_strategy = "round_robin"  # round_robin, random, sequential
batch_size = 100
prefetch_enabled = true
prefetch_size = 1000

# 数据源配置
[[data_manager.provider.sources]]
name = "csv_users"
type = "file"
path = "test_data/users.csv"
format = "csv"
encoding = "utf-8"
delimiter = ","

[[data_manager.provider.sources]]
name = "db_products"
type = "database"
connection = "${DATABASE_URL}"
query = "SELECT * FROM products WHERE active = 1"
cache_enabled = true

[[data_manager.provider.sources]]
name = "api_orders"
type = "api"
url = "${API_BASE_URL}/orders"
headers = { "Authorization" = "Bearer ${API_TOKEN}" }
method = "GET"
timeout = 30

# 数据分发器配置
[data_manager.distributor]
enabled = true
sync_interval = 60
batch_size = 1000
compression = true
encryption = false

# 分布式配置
[data_manager.distributor.distributed]
master_node = true
worker_nodes = ["worker1", "worker2", "worker3"]
sync_strategy = "push"  # push, pull, hybrid
conflict_resolution = "master_wins"  # master_wins, timestamp, merge
```

## 🎨 负载形状插件配置

```toml
# conf/plugins/load_shapes.toml
[load_shapes]
enabled = true
priority = 6

# 默认负载形状配置
[load_shapes.defaults]
default_shape = "constant"
spawn_rate = 1
time_limit = 600

# 波浪形负载配置
[load_shapes.wave]
min_users = 10
max_users = 100
wave_period = 300
wave_type = "sine"  # sine, cosine, triangle, square

# 阶梯形负载配置
[load_shapes.step]
initial_users = 10
step_size = 20
step_duration = 60
max_users = 200

# 尖峰负载配置
[load_shapes.spike]
base_users = 50
spike_users = 500
spike_duration = 30
spike_interval = 300

# 自适应负载配置
[load_shapes.adaptive]
target_response_time = 1000
adjustment_factor = 0.1
min_users = 10
max_users = 1000
adjustment_interval = 30
```

## 🔍 自定义插件配置

### 插件开发配置

```toml
# conf/plugins/custom_plugin_template.toml
[custom_plugin]
# 基础信息
name = "Custom Plugin"
version = "1.0.0"
description = "自定义插件描述"
author = "Your Name"
email = "your.email@example.com"
license = "MIT"
category = "analysis"  # analysis, monitoring, data, notification, load_shape

# 插件配置
enabled = false
priority = 5
dependencies = ["requests", "pandas"]
python_version = ">=3.7"

# 插件特定配置
[custom_plugin.config]
# 在这里添加插件特定的配置项
api_endpoint = "https://api.example.com"
api_key = "${CUSTOM_API_KEY}"
timeout = 30
retry_count = 3

# 插件钩子配置
[custom_plugin.hooks]
# 定义插件响应的事件钩子
on_test_start = true
on_test_stop = true
on_request = false
on_failure = true
```

### 插件验证配置

```toml
# conf/plugins/plugin_validation.toml
[validation]
# 插件验证规则
[validation.rules]
required_methods = ["initialize", "cleanup"]
optional_methods = ["configure", "get_info"]
forbidden_imports = ["os.system", "subprocess.call"]
max_memory_usage = "100MB"
max_cpu_usage = 50.0

# 安全检查
[validation.security]
sandbox_enabled = true
network_access = "restricted"  # allowed, restricted, denied
file_access = "restricted"
system_access = "denied"

# 性能检查
[validation.performance]
max_init_time = 10.0
max_cleanup_time = 5.0
memory_leak_check = true
```

## 📊 插件监控配置

```toml
# conf/plugins/plugin_monitoring.toml
[monitoring]
# 插件性能监控
[monitoring.performance]
enabled = true
track_execution_time = true
track_memory_usage = true
track_error_rate = true
alert_on_slow_plugin = true
slow_plugin_threshold = 5.0  # 秒

# 插件使用统计
[monitoring.usage]
enabled = true
track_plugin_calls = true
track_plugin_success_rate = true
generate_usage_report = true
report_interval = 3600  # 1小时

# 插件健康检查
[monitoring.health]
enabled = true
health_check_interval = 300  # 5分钟
auto_disable_failed_plugins = true
max_consecutive_failures = 3
```

## 🔧 插件配置示例

### 完整插件配置示例

```python
# plugins/custom/example_plugin.py
from src.plugins.plugin_interface import PluginInterface, PluginInfo
from typing import Dict, Any, Optional

class ExamplePlugin(PluginInterface):
    """示例插件实现"""

    @property
    def plugin_info(self) -> PluginInfo:
        return PluginInfo(
            name="Example Plugin",
            version="1.0.0",
            description="这是一个示例插件",
            author="Your Name",
            category="analysis"
        )

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """初始化插件"""
        self.config = config or {}
        self.api_endpoint = self.config.get('api_endpoint', 'https://api.example.com')
        self.api_key = self.config.get('api_key')
        self.timeout = self.config.get('timeout', 30)

        # 验证必要配置
        if not self.api_key:
            self.logger.error("API密钥未配置")
            return False

        self.logger.info("示例插件初始化成功")
        return True

    def cleanup(self):
        """清理资源"""
        self.logger.info("示例插件清理完成")

    def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理数据"""
        # 插件具体逻辑
        result = {
            'processed': True,
            'timestamp': time.time(),
            'data_size': len(str(data))
        }
        return result
```

### 插件配置文件

```toml
# conf/plugins/example_plugin.toml
[example_plugin]
enabled = true
priority = 5

[example_plugin.config]
api_endpoint = "https://api.example.com/v1"
api_key = "${EXAMPLE_API_KEY}"
timeout = 30
retry_count = 3
batch_size = 100

[example_plugin.features]
data_processing = true
real_time_analysis = false
batch_processing = true

[example_plugin.limits]
max_requests_per_minute = 1000
max_data_size = "10MB"
max_processing_time = 60
```

## 🚀 插件部署配置

### 生产环境配置

```toml
# conf/environments/production/plugins.toml
[production.plugins]
# 生产环境只启用稳定插件
enabled_plugins = [
    "performance_analyzer",
    "system_monitor",
    "notification_service"
]

# 禁用开发插件
disabled_plugins = [
    "debug_plugin",
    "test_plugin"
]

# 严格的安全配置
[production.plugins.security]
security_check = true
signature_verification = true
sandbox_enabled = true
allowed_plugin_sources = ["builtin", "verified"]

# 性能优化配置
[production.plugins.performance]
parallel_loading = true
max_load_workers = 8
cache_enabled = true
preload_plugins = true
```

### 开发环境配置

```toml
# conf/environments/development/plugins.toml
[development.plugins]
# 开发环境启用所有插件
auto_load_enabled = true
discovery_enabled = true

# 宽松的安全配置
[development.plugins.security]
security_check = false
signature_verification = false
sandbox_enabled = false
allowed_plugin_sources = ["builtin", "local", "development"]

# 调试配置
[development.plugins.debug]
verbose_logging = true
performance_profiling = true
memory_tracking = true
```

## ⚠️ 配置注意事项

1. **安全性**: 生产环境必须启用安全检查
2. **性能**: 合理配置插件优先级和并发数
3. **依赖**: 确保插件依赖正确安装
4. **版本**: 注意插件版本兼容性
5. **监控**: 启用插件性能监控
6. **备份**: 定期备份插件配置

## 🔗 相关文档

- [插件开发指南](../development/plugin-development.md) - 插件开发详细指南
- [框架配置](framework-config.md) - 框架核心配置
- [环境配置](environment-config.md) - 环境特定配置
- [API参考](../api/plugins.md) - 插件API接口文档
