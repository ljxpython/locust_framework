# 框架配置参考

本文档详细介绍Locust性能测试框架的配置选项，包括核心配置、插件配置、环境配置等。

## 📋 配置概述

框架使用Dynaconf进行配置管理，支持多种配置源和环境隔离：

```python
# 配置优先级（从高到低）
1. 环境变量
2. 命令行参数
3. 用户配置文件
4. 环境特定配置
5. 默认配置
```

## 🔧 核心配置

### 主配置文件 (conf/settings.toml)

```toml
# 基础配置
[default]
# 框架基础设置
framework_name = "Locust Performance Testing Framework"
version = "2.0.0"
debug = false
log_level = "INFO"

# 测试配置
[default.test]
# 默认测试设置
default_host = "http://localhost:8080"
default_users = 10
default_spawn_rate = 1
default_run_time = "10m"
stop_timeout = 30

# Web UI配置
[default.web]
enabled = true
host = "0.0.0.0"
port = 8089
auth_enabled = false
username = "admin"
password = "admin"

# 分布式配置
[default.distributed]
master_host = "127.0.0.1"
master_port = 5557
worker_timeout = 60
expect_workers = 1
heartbeat_interval = 3

# 日志配置
[default.logging]
level = "INFO"
format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
rotation = "100 MB"
retention = "30 days"
compression = "gz"

# 输出配置
[default.output]
reports_dir = "reports"
data_dir = "data"
logs_dir = "logs"
auto_cleanup = true
cleanup_days = 7

# 性能配置
[default.performance]
max_workers = 100
connection_pool_size = 50
request_timeout = 30
max_retries = 3
backoff_factor = 1.0
```

### 环境特定配置

#### 开发环境 (conf/environments/development.toml)

```toml
[default]
debug = true
log_level = "DEBUG"

[default.test]
default_host = "http://localhost:3000"
default_users = 5
default_run_time = "5m"

[default.web]
port = 8089

[default.logging]
level = "DEBUG"

[default.performance]
max_workers = 10
connection_pool_size = 10
```

#### 测试环境 (conf/environments/testing.toml)

```toml
[default]
debug = false
log_level = "INFO"

[default.test]
default_host = "http://test-api.example.com"
default_users = 50
default_run_time = "30m"

[default.distributed]
expect_workers = 3

[default.performance]
max_workers = 200
connection_pool_size = 100
```

#### 生产环境 (conf/environments/production.toml)

```toml
[default]
debug = false
log_level = "WARNING"

[default.test]
default_host = "http://api.example.com"
default_users = 1000
default_run_time = "2h"

[default.web]
auth_enabled = true
username = "${WEB_USERNAME}"
password = "${WEB_PASSWORD}"

[default.distributed]
expect_workers = 10

[default.performance]
max_workers = 1000
connection_pool_size = 500
request_timeout = 60

[default.security]
ssl_verify = true
api_key = "${API_KEY}"
```

## 🔌 插件配置

### 插件管理配置

```toml
# conf/plugins/plugin_config.toml
[plugins]
# 插件发现路径
discovery_paths = [
    "src/plugins/builtin",
    "plugins/custom",
    "~/.locust/plugins"
]

# 自动加载插件
auto_load = true
load_timeout = 30

# 插件依赖检查
check_dependencies = true
install_missing = false

# 插件配置
[plugins.performance_analyzer]
enabled = true
config = { output_formats = ["html", "json"], include_charts = true }

[plugins.system_monitor]
enabled = true
config = {
    interval = 5,
    metrics = ["cpu", "memory", "disk", "network"],
    alert_thresholds = { cpu = 80, memory = 85 }
}

[plugins.notification_service]
enabled = true
config = {
    channels = ["feishu", "email"],
    feishu_webhook = "${FEISHU_WEBHOOK}",
    email_smtp = "smtp.example.com"
}
```

### 分析插件配置

```toml
[analysis]
# 性能分析配置
[analysis.performance_analyzer]
enabled = true

# 响应时间阈值 (毫秒)
[analysis.performance_analyzer.response_time_thresholds]
excellent = 500
good = 1000
acceptable = 2000
poor = 5000

# 吞吐量阈值 (TPS)
[analysis.performance_analyzer.throughput_thresholds]
excellent = 1000
good = 500
acceptable = 100
poor = 50

# 错误率阈值 (百分比)
[analysis.performance_analyzer.error_rate_thresholds]
excellent = 0.1
good = 1.0
acceptable = 5.0
poor = 10.0

# 指标权重
[analysis.performance_analyzer.weights]
response_time = 0.4
throughput = 0.3
error_rate = 0.2
stability = 0.1

# 趋势分析配置
[analysis.trend_analyzer]
enabled = true
history_days = 30
prediction_days = 7
confidence_level = 0.95
```

### 监控插件配置

```toml
[monitoring]
# 性能监控配置
[monitoring.performance_monitor]
enabled = true
interval = 5
buffer_size = 1000

# 告警管理配置
[monitoring.alert_manager]
enabled = true
check_interval = 10
max_alerts_per_minute = 10

# 告警规则
[[monitoring.alert_rules]]
name = "high_response_time"
metric = "avg_response_time"
condition = "> 2000"
duration = "5m"
severity = "warning"
message = "平均响应时间超过2秒"

[[monitoring.alert_rules]]
name = "high_error_rate"
metric = "error_rate"
condition = "> 5"
duration = "2m"
severity = "critical"
message = "错误率超过5%"

[[monitoring.alert_rules]]
name = "low_throughput"
metric = "requests_per_second"
condition = "< 10"
duration = "3m"
severity = "warning"
message = "吞吐量低于10 RPS"
```

### 通知插件配置

```toml
[notifications]
# 飞书通知配置
[notifications.feishu]
enabled = true
webhook_url = "${FEISHU_WEBHOOK_URL}"
secret = "${FEISHU_SECRET}"
at_all = false
at_users = []

# 钉钉通知配置
[notifications.dingtalk]
enabled = false
webhook_url = "${DINGTALK_WEBHOOK_URL}"
secret = "${DINGTALK_SECRET}"

# 邮件通知配置
[notifications.email]
enabled = true
smtp_server = "smtp.example.com"
smtp_port = 587
username = "${EMAIL_USERNAME}"
password = "${EMAIL_PASSWORD}"
from_addr = "noreply@example.com"
to_addrs = ["admin@example.com"]
use_tls = true

# 企业微信通知配置
[notifications.wechat_work]
enabled = false
webhook_url = "${WECHAT_WEBHOOK_URL}"
```

## 📊 数据管理配置

```toml
[data_manager]
# 数据生成配置
[data_manager.generator]
enabled = true
locale = "zh_CN"
seed = 12345
cache_size = 10000

# 数据提供配置
[data_manager.provider]
enabled = true
default_strategy = "round_robin"
data_sources = [
    { type = "file", path = "test_data/users.csv" },
    { type = "database", connection = "mysql://user:pass@localhost/testdb" },
    { type = "api", url = "http://api.example.com/test-data" }
]

# 数据分发配置
[data_manager.distributor]
enabled = true
sync_interval = 60
batch_size = 1000
compression = true
```

## 🔒 安全配置

```toml
[security]
# 认证配置
[security.authentication]
enabled = true
method = "token"  # token, basic, oauth
token_header = "Authorization"
token_prefix = "Bearer"

# SSL/TLS配置
[security.ssl]
verify = true
cert_file = ""
key_file = ""
ca_file = ""

# API安全配置
[security.api]
rate_limit = 1000
rate_limit_window = 3600
api_key_header = "X-API-Key"
allowed_origins = ["*"]
```

## 🚀 性能优化配置

```toml
[performance]
# 连接池配置
[performance.connection_pool]
max_connections = 100
max_connections_per_host = 20
keepalive_timeout = 30
connection_timeout = 10

# 请求配置
[performance.requests]
timeout = 30
max_retries = 3
backoff_factor = 1.0
retry_on_status = [500, 502, 503, 504]

# 内存配置
[performance.memory]
max_memory_usage = "2GB"
gc_threshold = 0.8
cache_size = 10000

# 并发配置
[performance.concurrency]
max_workers = 1000
worker_queue_size = 10000
task_timeout = 300
```

## 📝 日志配置

### 详细日志配置 (conf/logging.conf)

```ini
[loggers]
keys=root,locust,framework

[handlers]
keys=consoleHandler,fileHandler,rotatingFileHandler

[formatters]
keys=simpleFormatter,detailedFormatter

[logger_root]
level=INFO
handlers=consoleHandler,rotatingFileHandler

[logger_locust]
level=INFO
handlers=fileHandler
qualname=locust
propagate=0

[logger_framework]
level=DEBUG
handlers=rotatingFileHandler
qualname=framework
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=detailedFormatter
args=('logs/locust.log',)

[handler_rotatingFileHandler]
class=handlers.RotatingFileHandler
level=DEBUG
formatter=detailedFormatter
args=('logs/framework.log', 'a', 10485760, 5)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s

[formatter_detailedFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s
```

## 🔧 配置使用示例

### 1. 基础配置加载

```python
from dynaconf import Dynaconf

# 加载配置
settings = Dynaconf(
    envvar_prefix="LOCUST",
    settings_files=['conf/settings.toml', 'conf/.secrets.toml'],
    environments=True,
    load_dotenv=True,
    env_switcher="LOCUST_ENV"
)

# 使用配置
print(f"当前环境: {settings.current_env}")
print(f"默认主机: {settings.test.default_host}")
print(f"Web端口: {settings.web.port}")
```

### 2. 环境切换

```bash
# 设置环境变量
export LOCUST_ENV=production

# 或在代码中切换
settings.setenv('production')
```

### 3. 动态配置更新

```python
# 运行时更新配置
settings.set('test.default_users', 100)
settings.set('web.port', 9089)

# 保存配置
settings.save()
```

### 4. 配置验证

```python
from pydantic import BaseModel, validator

class TestConfig(BaseModel):
    default_host: str
    default_users: int
    default_spawn_rate: float

    @validator('default_users')
    def validate_users(cls, v):
        if v <= 0:
            raise ValueError('用户数必须大于0')
        return v

    @validator('default_spawn_rate')
    def validate_spawn_rate(cls, v):
        if v <= 0:
            raise ValueError('生成速率必须大于0')
        return v

# 验证配置
try:
    test_config = TestConfig(**settings.test)
    print("配置验证通过")
except Exception as e:
    print(f"配置验证失败: {e}")
```

## 🔐 敏感信息管理

### 1. 环境变量

```bash
# .env 文件
LOCUST_ENV=production
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
EMAIL_PASSWORD=your_email_password
API_KEY=your_api_key
```

### 2. 密钥文件

```toml
# conf/.secrets.toml (不提交到版本控制)
[default]
api_key = "your_secret_api_key"
database_password = "your_db_password"

[production]
ssl_cert = "/path/to/cert.pem"
ssl_key = "/path/to/key.pem"
```

## ⚠️ 配置注意事项

1. **安全性**: 敏感信息使用环境变量或密钥文件
2. **验证**: 启动时验证关键配置项
3. **备份**: 定期备份配置文件
4. **版本控制**: 不要提交包含敏感信息的配置文件
5. **文档**: 及时更新配置文档

## 🔗 相关文档

- [插件配置](plugin-config.md) - 插件专用配置
- [环境配置](environment-config.md) - 环境特定配置
- [安全配置](security-config.md) - 安全相关配置
- [性能调优](../development/performance-tuning.md) - 性能优化指南
