# 插件接口API

本文档详细介绍Locust性能测试框架的插件开发接口API。

## 📋 API概览

插件系统提供了丰富的API接口，支持多种类型的插件开发：

- **基础插件API**: 所有插件的基础接口
- **Locust插件API**: 扩展Locust核心功能
- **报告插件API**: 自定义报告生成
- **监控插件API**: 扩展监控能力
- **数据插件API**: 数据源和处理扩展
- **通知插件API**: 通知渠道扩展

## 🔌 基础插件API

### BasePlugin

所有插件的基础类，提供插件的基本生命周期管理。

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BasePlugin(ABC):
    """插件基类"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化插件

        Args:
            config: 插件配置字典
        """
        self.config = config or {}
        self.enabled = True
        self.logger = self._setup_logger()
        self.name = self.__class__.__name__
        self.version = "1.0.0"

    @abstractmethod
    def initialize(self) -> bool:
        """
        插件初始化

        Returns:
            bool: 初始化是否成功
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """插件清理资源"""
        pass

    def enable(self) -> None:
        """启用插件"""
        self.enabled = True

    def disable(self) -> None:
        """禁用插件"""
        self.enabled = False

    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return self.enabled

    def get_info(self) -> Dict[str, Any]:
        """
        获取插件信息

        Returns:
            Dict[str, Any]: 插件信息字典
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "config": self.config
        }

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置

        Args:
            config: 配置字典

        Returns:
            bool: 配置是否有效
        """
        return True

    def _setup_logger(self):
        """设置日志记录器"""
        import logging
        return logging.getLogger(f"plugin.{self.__class__.__name__}")
```

## 🦗 Locust插件API

### LocustPlugin

扩展Locust核心功能的插件接口。

```python
from locust import events
from locust.env import Environment

class LocustPlugin(BasePlugin):
    """Locust功能扩展插件"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.environment: Optional[Environment] = None

    def set_environment(self, environment: Environment) -> None:
        """
        设置Locust环境

        Args:
            environment: Locust环境对象
        """
        self.environment = environment

    def on_test_start(self, environment: Environment, **kwargs) -> None:
        """
        测试开始时调用

        Args:
            environment: Locust环境对象
            **kwargs: 额外参数
        """
        pass

    def on_test_stop(self, environment: Environment, **kwargs) -> None:
        """
        测试结束时调用

        Args:
            environment: Locust环境对象
            **kwargs: 额外参数
        """
        pass

    def on_user_add(self, user_instance, **kwargs) -> None:
        """
        用户添加时调用

        Args:
            user_instance: 用户实例
            **kwargs: 额外参数
        """
        pass

    def on_user_remove(self, user_instance, **kwargs) -> None:
        """
        用户移除时调用

        Args:
            user_instance: 用户实例
            **kwargs: 额外参数
        """
        pass

    def on_request_success(self, request_type: str, name: str,
                          response_time: float, response_length: int, **kwargs) -> None:
        """
        请求成功时调用

        Args:
            request_type: 请求类型
            name: 请求名称
            response_time: 响应时间
            response_length: 响应长度
            **kwargs: 额外参数
        """
        pass

    def on_request_failure(self, request_type: str, name: str,
                          response_time: float, response_length: int,
                          exception: Exception, **kwargs) -> None:
        """
        请求失败时调用

        Args:
            request_type: 请求类型
            name: 请求名称
            response_time: 响应时间
            response_length: 响应长度
            exception: 异常对象
            **kwargs: 额外参数
        """
        pass

    def register_events(self) -> None:
        """注册事件监听器"""
        if self.environment:
            events.test_start.add_listener(self.on_test_start)
            events.test_stop.add_listener(self.on_test_stop)
            events.user_add.add_listener(self.on_user_add)
            events.user_remove.add_listener(self.on_user_remove)
            events.request_success.add_listener(self.on_request_success)
            events.request_failure.add_listener(self.on_request_failure)
```

## 📊 报告插件API

### ReportPlugin

自定义报告生成插件接口。

```python
from typing import List, Dict, Any
from pathlib import Path

class ReportPlugin(BasePlugin):
    """报告生成插件"""

    def generate_report(self, stats: Dict[str, Any],
                       output_path: Path, **kwargs) -> bool:
        """
        生成报告

        Args:
            stats: 统计数据
            output_path: 输出路径
            **kwargs: 额外参数

        Returns:
            bool: 生成是否成功
        """
        pass

    def format_data(self, data: Any, format_type: str) -> str:
        """
        格式化数据

        Args:
            data: 原始数据
            format_type: 格式类型 (html, json, csv, markdown)

        Returns:
            str: 格式化后的数据
        """
        pass

    def export_report(self, report_content: str,
                     output_path: Path, format_type: str) -> bool:
        """
        导出报告

        Args:
            report_content: 报告内容
            output_path: 输出路径
            format_type: 格式类型

        Returns:
            bool: 导出是否成功
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """
        获取支持的格式列表

        Returns:
            List[str]: 支持的格式列表
        """
        return ["html", "json", "csv", "markdown"]

    def validate_template(self, template_path: Path) -> bool:
        """
        验证模板文件

        Args:
            template_path: 模板文件路径

        Returns:
            bool: 模板是否有效
        """
        pass
```

## 📈 监控插件API

### MonitorPlugin

扩展监控能力的插件接口。

```python
from typing import Dict, List, Any, Optional
from datetime import datetime

class MonitorPlugin(BasePlugin):
    """监控插件"""

    def collect_metrics(self) -> Dict[str, Any]:
        """
        收集监控指标

        Returns:
            Dict[str, Any]: 监控指标数据
        """
        pass

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        检查阈值

        Args:
            metrics: 监控指标

        Returns:
            List[Dict[str, Any]]: 告警列表
        """
        pass

    def trigger_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        触发告警

        Args:
            alert_data: 告警数据

        Returns:
            bool: 告警是否成功触发
        """
        pass

    def get_metric_definition(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指标定义

        Args:
            metric_name: 指标名称

        Returns:
            Optional[Dict[str, Any]]: 指标定义
        """
        pass

    def register_metric(self, metric_name: str,
                       metric_config: Dict[str, Any]) -> bool:
        """
        注册新指标

        Args:
            metric_name: 指标名称
            metric_config: 指标配置

        Returns:
            bool: 注册是否成功
        """
        pass

    def start_monitoring(self) -> bool:
        """
        开始监控

        Returns:
            bool: 启动是否成功
        """
        pass

    def stop_monitoring(self) -> bool:
        """
        停止监控

        Returns:
            bool: 停止是否成功
        """
        pass
```

## 💾 数据插件API

### DataPlugin

数据源和数据处理扩展插件接口。

```python
from typing import Iterator, List, Dict, Any, Optional

class DataPlugin(BasePlugin):
    """数据插件"""

    def load_data(self, source_config: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """
        加载数据

        Args:
            source_config: 数据源配置

        Yields:
            Dict[str, Any]: 数据记录
        """
        pass

    def process_data(self, raw_data: Any) -> Any:
        """
        处理数据

        Args:
            raw_data: 原始数据

        Returns:
            Any: 处理后的数据
        """
        pass

    def distribute_data(self, data: List[Any],
                       strategy: str, node_count: int) -> List[List[Any]]:
        """
        分发数据

        Args:
            data: 数据列表
            strategy: 分发策略 (round_robin, random, sequential)
            node_count: 节点数量

        Returns:
            List[List[Any]]: 分发后的数据
        """
        pass

    def validate_data(self, data: Any, schema: Dict[str, Any]) -> bool:
        """
        验证数据

        Args:
            data: 数据
            schema: 数据模式

        Returns:
            bool: 数据是否有效
        """
        pass

    def get_data_schema(self) -> Dict[str, Any]:
        """
        获取数据模式

        Returns:
            Dict[str, Any]: 数据模式定义
        """
        pass

    def cache_data(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        缓存数据

        Args:
            key: 缓存键
            data: 数据
            ttl: 生存时间(秒)

        Returns:
            bool: 缓存是否成功
        """
        pass

    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        获取缓存数据

        Args:
            key: 缓存键

        Returns:
            Optional[Any]: 缓存的数据
        """
        pass
```

## 📢 通知插件API

### NotificationPlugin

通知渠道扩展插件接口。

```python
from typing import List, Dict, Any, Optional

class NotificationPlugin(BasePlugin):
    """通知插件"""

    def send_notification(self, message: str,
                         recipients: List[str], **kwargs) -> bool:
        """
        发送通知

        Args:
            message: 消息内容
            recipients: 接收者列表
            **kwargs: 额外参数

        Returns:
            bool: 发送是否成功
        """
        pass

    def format_message(self, data: Dict[str, Any],
                      template: str) -> str:
        """
        格式化消息

        Args:
            data: 数据字典
            template: 消息模板

        Returns:
            str: 格式化后的消息
        """
        pass

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        验证配置

        Args:
            config: 配置字典

        Returns:
            bool: 配置是否有效
        """
        pass

    def test_connection(self) -> bool:
        """
        测试连接

        Returns:
            bool: 连接是否正常
        """
        pass

    def get_supported_formats(self) -> List[str]:
        """
        获取支持的消息格式

        Returns:
            List[str]: 支持的格式列表
        """
        return ["text", "markdown", "html"]

    def send_rich_message(self, title: str, content: str,
                         message_type: str, recipients: List[str]) -> bool:
        """
        发送富文本消息

        Args:
            title: 消息标题
            content: 消息内容
            message_type: 消息类型 (info, warning, error)
            recipients: 接收者列表

        Returns:
            bool: 发送是否成功
        """
        pass
```

## 🔧 插件管理API

### PluginManager

插件管理器API，用于插件的注册、加载和管理。

```python
class PluginManager:
    """插件管理器"""

    def register_plugin(self, plugin_class: type,
                       plugin_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        注册插件

        Args:
            plugin_class: 插件类
            plugin_config: 插件配置

        Returns:
            bool: 注册是否成功
        """
        pass

    def load_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        加载插件

        Args:
            plugin_name: 插件名称

        Returns:
            Optional[BasePlugin]: 插件实例
        """
        pass

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件

        Args:
            plugin_name: 插件名称

        Returns:
            bool: 卸载是否成功
        """
        pass

    def get_plugin(self, plugin_name: str) -> Optional[BasePlugin]:
        """
        获取插件实例

        Args:
            plugin_name: 插件名称

        Returns:
            Optional[BasePlugin]: 插件实例
        """
        pass

    def list_plugins(self, plugin_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        列出插件

        Args:
            plugin_type: 插件类型过滤

        Returns:
            List[Dict[str, Any]]: 插件信息列表
        """
        pass

    def enable_plugin(self, plugin_name: str) -> bool:
        """
        启用插件

        Args:
            plugin_name: 插件名称

        Returns:
            bool: 启用是否成功
        """
        pass

    def disable_plugin(self, plugin_name: str) -> bool:
        """
        禁用插件

        Args:
            plugin_name: 插件名称

        Returns:
            bool: 禁用是否成功
        """
        pass
```

## 📚 使用示例

### 创建自定义Locust插件

```python
class CustomLocustPlugin(LocustPlugin):
    def initialize(self) -> bool:
        self.logger.info("Custom Locust plugin initialized")
        return True

    def cleanup(self) -> None:
        self.logger.info("Custom Locust plugin cleaned up")

    def on_test_start(self, environment, **kwargs):
        self.logger.info("Test started with custom plugin")

    def on_request_success(self, request_type, name, response_time, response_length, **kwargs):
        if response_time > 1000:  # 响应时间超过1秒
            self.logger.warning(f"Slow request detected: {name} took {response_time}ms")

# 注册插件
plugin_manager.register_plugin(CustomLocustPlugin, {
    "log_level": "INFO",
    "slow_request_threshold": 1000
})
```

## 📚 相关文档

- [插件开发指南](../development/plugin-development.md) - 详细的插件开发教程
- [插件系统架构](../architecture/plugin-system.md) - 插件系统设计
- [插件配置](../configuration/plugin-config.md) - 插件配置说明
- [示例代码](../examples/advanced-usage.md) - 插件使用示例
