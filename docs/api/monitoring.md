# 监控告警API参考

本文档详细介绍监控告警模块的API接口，包括性能监控器、告警管理器和通知服务。

## 📊 PerformanceMonitor

性能监控器提供实时性能指标收集和监控功能。

### 类定义

```python
from src.monitoring.performance_monitor import PerformanceMonitor

class PerformanceMonitor:
    """性能监控器

    提供实时性能监控功能，包括指标收集、阈值检查、
    告警触发等核心监控能力。
    """
```

### 构造函数

```python
def __init__(self, config: Optional[Dict[str, Any]] = None):
    """初始化性能监控器

    Args:
        config: 监控配置参数
            - interval: 监控间隔(秒)，默认5
            - buffer_size: 缓冲区大小，默认1000
            - metrics_retention: 指标保留时间(秒)，默认3600
            - alert_cooldown: 告警冷却时间(秒)，默认300

    Example:
        >>> config = {
        ...     'interval': 10,
        ...     'buffer_size': 2000,
        ...     'alert_cooldown': 600
        ... }
        >>> monitor = PerformanceMonitor(config)
    """
```

### 核心方法

#### start_monitoring()

```python
def start_monitoring(self) -> bool:
    """开始监控

    启动监控线程，开始收集性能指标。

    Returns:
        bool: 启动是否成功

    Example:
        >>> monitor = PerformanceMonitor()
        >>> success = monitor.start_monitoring()
        >>> print(f"监控启动{'成功' if success else '失败'}")
    """
```

#### stop_monitoring()

```python
def stop_monitoring(self) -> bool:
    """停止监控

    停止监控线程，清理资源。

    Returns:
        bool: 停止是否成功

    Example:
        >>> monitor.stop_monitoring()
    """
```

#### collect_metrics()

```python
def collect_metrics(self) -> Dict[str, Any]:
    """收集当前性能指标

    Returns:
        Dict[str, Any]: 当前性能指标
            - timestamp: 时间戳
            - response_time: 响应时间统计
            - throughput: 吞吐量统计
            - error_rate: 错误率
            - active_users: 活跃用户数
            - system_metrics: 系统指标(可选)

    Example:
        >>> metrics = monitor.collect_metrics()
        >>> print(f"当前TPS: {metrics['throughput']['current']}")
    """
```

#### register_custom_metric()

```python
def register_custom_metric(self, name: str, metric_type: str,
                          description: str = "") -> bool:
    """注册自定义指标

    Args:
        name: 指标名称
        metric_type: 指标类型 (counter/gauge/histogram)
        description: 指标描述

    Returns:
        bool: 注册是否成功

    Example:
        >>> success = monitor.register_custom_metric(
        ...     "business_transactions",
        ...     "counter",
        ...     "业务交易计数"
        ... )
    """
```

#### record_metric()

```python
def record_metric(self, name: str, value: Union[int, float],
                 labels: Optional[Dict[str, str]] = None) -> bool:
    """记录指标值

    Args:
        name: 指标名称
        value: 指标值
        labels: 标签字典(可选)

    Returns:
        bool: 记录是否成功

    Example:
        >>> monitor.record_metric("response_time", 500.0, {"endpoint": "/api/users"})
        >>> monitor.record_metric("error_count", 1, {"error_type": "timeout"})
    """
```

#### get_metrics_history()

```python
def get_metrics_history(self, metric_name: str,
                       time_range: Optional[Tuple[float, float]] = None) -> List[Dict[str, Any]]:
    """获取指标历史数据

    Args:
        metric_name: 指标名称
        time_range: 时间范围(开始时间戳, 结束时间戳)，可选

    Returns:
        List[Dict[str, Any]]: 历史数据列表

    Example:
        >>> import time
        >>> end_time = time.time()
        >>> start_time = end_time - 3600  # 最近1小时
        >>> history = monitor.get_metrics_history("response_time", (start_time, end_time))
    """
```

## 🚨 AlertManager

告警管理器负责告警规则管理、告警触发和生命周期管理。

### 类定义

```python
from src.monitoring.alert_manager import AlertManager

class AlertManager:
    """告警管理器

    管理告警规则、触发告警、处理告警生命周期。
    """
```

### 核心方法

#### add_alert_rule()

```python
def add_alert_rule(self, rule: Dict[str, Any]) -> bool:
    """添加告警规则

    Args:
        rule: 告警规则配置
            - name: 规则名称
            - metric: 监控指标
            - condition: 触发条件
            - threshold: 阈值
            - duration: 持续时间
            - severity: 严重级别
            - message: 告警消息
            - actions: 告警动作列表

    Returns:
        bool: 添加是否成功

    Example:
        >>> rule = {
        ...     "name": "high_response_time",
        ...     "metric": "avg_response_time",
        ...     "condition": ">",
        ...     "threshold": 2000,
        ...     "duration": 300,
        ...     "severity": "warning",
        ...     "message": "平均响应时间过高",
        ...     "actions": ["notify", "log"]
        ... }
        >>> alert_manager.add_alert_rule(rule)
    """
```

#### remove_alert_rule()

```python
def remove_alert_rule(self, rule_name: str) -> bool:
    """移除告警规则

    Args:
        rule_name: 规则名称

    Returns:
        bool: 移除是否成功

    Example:
        >>> alert_manager.remove_alert_rule("high_response_time")
    """
```

#### trigger_alert()

```python
def trigger_alert(self, alert_name: str, message: str,
                 severity: str = "warning",
                 metadata: Optional[Dict[str, Any]] = None) -> str:
    """手动触发告警

    Args:
        alert_name: 告警名称
        message: 告警消息
        severity: 严重级别 (info/warning/critical)
        metadata: 附加元数据

    Returns:
        str: 告警ID

    Example:
        >>> alert_id = alert_manager.trigger_alert(
        ...     "manual_alert",
        ...     "手动触发的测试告警",
        ...     "warning",
        ...     {"source": "manual", "test_id": "test_001"}
        ... )
    """
```

#### resolve_alert()

```python
def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
    """解决告警

    Args:
        alert_id: 告警ID
        resolution_note: 解决说明

    Returns:
        bool: 解决是否成功

    Example:
        >>> alert_manager.resolve_alert("alert_123", "问题已修复")
    """
```

#### get_active_alerts()

```python
def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取活跃告警列表

    Args:
        severity: 过滤严重级别，可选

    Returns:
        List[Dict[str, Any]]: 活跃告警列表

    Example:
        >>> active_alerts = alert_manager.get_active_alerts("critical")
        >>> print(f"严重告警数量: {len(active_alerts)}")
    """
```

#### get_alert_history()

```python
def get_alert_history(self, time_range: Optional[Tuple[float, float]] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
    """获取告警历史

    Args:
        time_range: 时间范围，可选
        limit: 返回数量限制

    Returns:
        List[Dict[str, Any]]: 告警历史列表

    Example:
        >>> history = alert_manager.get_alert_history(limit=50)
    """
```

## 📢 NotificationService

通知服务负责多渠道消息发送和通知管理。

### 类定义

```python
from src.monitoring.notification_service import NotificationService

class NotificationService:
    """通知服务

    支持多种通知渠道的消息发送服务。
    """
```

### 核心方法

#### send_notification()

```python
def send_notification(self, message: str, channels: List[str],
                     priority: str = "normal",
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, bool]:
    """发送通知

    Args:
        message: 通知消息
        channels: 通知渠道列表
        priority: 优先级 (low/normal/high/urgent)
        metadata: 附加元数据

    Returns:
        Dict[str, bool]: 各渠道发送结果

    Example:
        >>> result = notification_service.send_notification(
        ...     "测试完成，请查看报告",
        ...     ["feishu", "email"],
        ...     "normal",
        ...     {"test_id": "test_001", "report_url": "http://example.com/report"}
        ... )
        >>> print(f"飞书发送结果: {result['feishu']}")
    """
```

#### send_alert_notification()

```python
def send_alert_notification(self, alert: Dict[str, Any]) -> Dict[str, bool]:
    """发送告警通知

    Args:
        alert: 告警信息
            - id: 告警ID
            - name: 告警名称
            - message: 告警消息
            - severity: 严重级别
            - timestamp: 时间戳
            - metadata: 元数据

    Returns:
        Dict[str, bool]: 各渠道发送结果

    Example:
        >>> alert = {
        ...     "id": "alert_123",
        ...     "name": "high_error_rate",
        ...     "message": "错误率超过阈值",
        ...     "severity": "critical",
        ...     "timestamp": time.time()
        ... }
        >>> result = notification_service.send_alert_notification(alert)
    """
```

#### register_channel()

```python
def register_channel(self, channel_name: str, channel_config: Dict[str, Any]) -> bool:
    """注册通知渠道

    Args:
        channel_name: 渠道名称
        channel_config: 渠道配置

    Returns:
        bool: 注册是否成功

    Example:
        >>> config = {
        ...     "webhook_url": "https://hooks.slack.com/xxx",
        ...     "channel": "#alerts",
        ...     "username": "LocustBot"
        ... }
        >>> notification_service.register_channel("slack", config)
    """
```

#### get_channel_status()

```python
def get_channel_status(self) -> Dict[str, Dict[str, Any]]:
    """获取渠道状态

    Returns:
        Dict[str, Dict[str, Any]]: 各渠道状态信息

    Example:
        >>> status = notification_service.get_channel_status()
        >>> for channel, info in status.items():
        ...     print(f"{channel}: {'可用' if info['available'] else '不可用'}")
    """
```

## 📈 MetricsCollector

指标收集器负责从各种数据源收集性能指标。

### 类定义

```python
from src.monitoring.metrics_collector import MetricsCollector

class MetricsCollector:
    """指标收集器

    从多种数据源收集性能指标数据。
    """
```

### 核心方法

#### collect_locust_metrics()

```python
def collect_locust_metrics(self, environment) -> Dict[str, Any]:
    """收集Locust指标

    Args:
        environment: Locust环境对象

    Returns:
        Dict[str, Any]: Locust指标数据

    Example:
        >>> metrics = collector.collect_locust_metrics(environment)
        >>> print(f"总请求数: {metrics['total_requests']}")
    """
```

#### collect_system_metrics()

```python
def collect_system_metrics(self) -> Dict[str, Any]:
    """收集系统指标

    Returns:
        Dict[str, Any]: 系统指标数据
            - cpu_usage: CPU使用率
            - memory_usage: 内存使用率
            - disk_usage: 磁盘使用率
            - network_io: 网络IO统计

    Example:
        >>> system_metrics = collector.collect_system_metrics()
        >>> print(f"CPU使用率: {system_metrics['cpu_usage']}%")
    """
```

#### collect_custom_metrics()

```python
def collect_custom_metrics(self, metric_sources: List[str]) -> Dict[str, Any]:
    """收集自定义指标

    Args:
        metric_sources: 指标源列表

    Returns:
        Dict[str, Any]: 自定义指标数据

    Example:
        >>> custom_metrics = collector.collect_custom_metrics(["database", "cache"])
    """
```

## 🔧 使用示例

### 完整监控流程

```python
from src.monitoring.performance_monitor import PerformanceMonitor
from src.monitoring.alert_manager import AlertManager
from src.monitoring.notification_service import NotificationService

# 1. 初始化监控组件
monitor = PerformanceMonitor({
    'interval': 5,
    'buffer_size': 2000
})

alert_manager = AlertManager()
notification_service = NotificationService()

# 2. 配置告警规则
alert_rules = [
    {
        "name": "high_response_time",
        "metric": "avg_response_time",
        "condition": ">",
        "threshold": 2000,
        "duration": 300,
        "severity": "warning",
        "message": "平均响应时间超过2秒"
    },
    {
        "name": "high_error_rate",
        "metric": "error_rate",
        "condition": ">",
        "threshold": 5.0,
        "duration": 120,
        "severity": "critical",
        "message": "错误率超过5%"
    }
]

for rule in alert_rules:
    alert_manager.add_alert_rule(rule)

# 3. 配置通知渠道
notification_service.register_channel("feishu", {
    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
})

# 4. 启动监控
monitor.start_monitoring()

# 5. 注册自定义指标
monitor.register_custom_metric("business_success_rate", "gauge")

# 6. 在测试过程中记录指标
def on_request_success(request_type, name, response_time, response_length, **kwargs):
    monitor.record_metric("response_time", response_time, {"endpoint": name})
    monitor.record_metric("business_success_rate", 1.0)

def on_request_failure(request_type, name, response_time, response_length, exception, **kwargs):
    monitor.record_metric("response_time", response_time, {"endpoint": name})
    monitor.record_metric("business_success_rate", 0.0)

    # 触发告警
    if response_time > 5000:
        alert_manager.trigger_alert(
            "slow_request",
            f"请求 {name} 响应时间过长: {response_time}ms",
            "warning"
        )

# 7. 停止监控
monitor.stop_monitoring()
```

### 自定义监控插件

```python
from src.monitoring.performance_monitor import PerformanceMonitor

class DatabaseMonitor(PerformanceMonitor):
    """数据库监控插件"""

    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config

    def collect_custom_metrics(self):
        """收集数据库指标"""
        # 连接数据库
        # 查询性能指标
        # 返回指标数据
        return {
            "active_connections": 50,
            "query_latency": 100,
            "cache_hit_rate": 0.95
        }
```

## ⚠️ 注意事项

1. **性能影响**: 监控会消耗系统资源，合理设置监控间隔
2. **内存管理**: 定期清理历史数据，避免内存泄漏
3. **告警风暴**: 设置告警冷却时间，避免重复告警
4. **网络依赖**: 通知服务依赖网络，需要处理网络异常
5. **配置验证**: 启动前验证监控配置的正确性

## 🔗 相关文档

- [性能分析API](analysis.md) - 性能分析模块API
- [数据管理API](data-manager.md) - 数据管理模块API
- [插件接口API](plugins.md) - 插件开发接口
- [监控配置](../configuration/monitoring-config.md) - 监控配置说明
