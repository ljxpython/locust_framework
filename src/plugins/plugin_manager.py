"""
插件管理器

统一管理所有插件的生命周期和交互
"""

import json
import threading
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

from src.plugins.plugin_interface import PluginInfo, PluginInterface
from src.plugins.plugin_loader import PluginLoader
from src.utils.log_moudle import logger


class PluginManager:
    """插件管理器"""

    def __init__(self, config_file: str = "plugin_config.json"):
        self.config_file = config_file
        self.plugin_loader = PluginLoader()
        self.enabled_plugins = set()  # 启用的插件名称
        self.plugin_configs = {}  # plugin_name -> config
        self.event_handlers = defaultdict(list)  # event_name -> [handler_functions]
        self.lock = threading.Lock()

        # 加载配置
        self._load_config()

        # 自动发现和加载插件
        self.discover_and_load_plugins()

    def discover_and_load_plugins(self):
        """发现并加载所有插件"""
        logger.info("开始发现和加载插件...")

        # 发现插件
        discovered_plugins = self.plugin_loader.discover_plugins()
        logger.info(f"发现 {len(discovered_plugins)} 个插件")

        # 加载所有插件
        loaded_plugins = self.plugin_loader.load_all_plugins()
        logger.info(f"成功加载 {len(loaded_plugins)} 个插件")

        # 根据配置启用插件
        for plugin_name in loaded_plugins:
            if self._should_enable_plugin(plugin_name):
                self.enable_plugin(plugin_name)

    def enable_plugin(self, plugin_name: str, config: Dict[str, Any] = None) -> bool:
        """启用插件"""
        with self.lock:
            if plugin_name in self.enabled_plugins:
                logger.warning(f"插件已启用: {plugin_name}")
                return True

            # 获取插件配置
            plugin_config = config or self.plugin_configs.get(plugin_name, {})

            # 创建插件实例
            instance = self.plugin_loader.create_plugin_instance(
                plugin_name, plugin_config
            )
            if instance is None:
                logger.error(f"创建插件实例失败: {plugin_name}")
                return False

            # 启用插件
            instance.enable()
            self.enabled_plugins.add(plugin_name)

            # 注册事件处理器
            self._register_plugin_events(plugin_name, instance)

            logger.info(f"启用插件: {plugin_name}")
            return True

    def disable_plugin(self, plugin_name: str) -> bool:
        """禁用插件"""
        with self.lock:
            if plugin_name not in self.enabled_plugins:
                logger.warning(f"插件未启用: {plugin_name}")
                return True

            # 获取插件实例
            instance = self.plugin_loader.get_plugin_instance(plugin_name)
            if instance:
                try:
                    instance.disable()
                    instance.cleanup()
                except Exception as e:
                    logger.error(f"禁用插件失败 {plugin_name}: {e}")
                    return False

            # 注销事件处理器
            self._unregister_plugin_events(plugin_name)

            self.enabled_plugins.discard(plugin_name)
            logger.info(f"禁用插件: {plugin_name}")
            return True

    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        logger.info(f"重新加载插件: {plugin_name}")

        # 保存当前状态
        was_enabled = plugin_name in self.enabled_plugins
        config = self.plugin_configs.get(plugin_name, {})

        # 禁用插件
        if was_enabled:
            self.disable_plugin(plugin_name)

        # 重新加载
        if self.plugin_loader.reload_plugin(plugin_name):
            # 如果之前启用，重新启用
            if was_enabled:
                return self.enable_plugin(plugin_name, config)
            return True

        return False

    def configure_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """配置插件"""
        with self.lock:
            # 保存配置
            self.plugin_configs[plugin_name] = config

            # 如果插件已启用，应用配置
            instance = self.plugin_loader.get_plugin_instance(plugin_name)
            if instance:
                try:
                    instance.configure(config)
                    logger.info(f"配置插件: {plugin_name}")
                    return True
                except Exception as e:
                    logger.error(f"配置插件失败 {plugin_name}: {e}")
                    return False

            return True

    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        instance = self.plugin_loader.get_plugin_instance(plugin_name)
        if instance:
            return instance.plugin_info

        # 如果实例不存在，尝试从元数据获取
        metadata = self.plugin_loader.get_plugin_metadata(plugin_name)
        if metadata:
            return PluginInfo(
                name=metadata.get("name", plugin_name),
                version=metadata.get("version", "1.0.0"),
                description=metadata.get("description", ""),
                author=metadata.get("author", ""),
                category=metadata.get("category", "general"),
                dependencies=metadata.get("dependencies", []),
                config_schema=metadata.get("config_schema", {}),
            )

        return None

    def get_enabled_plugins(self) -> List[str]:
        """获取已启用的插件列表"""
        return list(self.enabled_plugins)

    def get_available_plugins(self) -> List[str]:
        """获取可用的插件列表"""
        return list(self.plugin_loader.get_loaded_plugins().keys())

    def get_plugins_by_category(self, category: str) -> List[str]:
        """根据类别获取插件"""
        return self.plugin_loader.get_plugins_by_category(category)

    def is_plugin_enabled(self, plugin_name: str) -> bool:
        """检查插件是否启用"""
        return plugin_name in self.enabled_plugins

    def get_plugin_instance(self, plugin_name: str) -> Optional[PluginInterface]:
        """获取插件实例"""
        if plugin_name not in self.enabled_plugins:
            return None
        return self.plugin_loader.get_plugin_instance(plugin_name)

    def trigger_event(self, event_name: str, *args, **kwargs):
        """触发事件"""
        handlers = self.event_handlers.get(event_name, [])

        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(f"事件处理器执行失败 {event_name}: {e}")

    def register_event_handler(self, event_name: str, handler: Callable):
        """注册事件处理器"""
        self.event_handlers[event_name].append(handler)
        logger.debug(f"注册事件处理器: {event_name}")

    def unregister_event_handler(self, event_name: str, handler: Callable):
        """注销事件处理器"""
        if handler in self.event_handlers[event_name]:
            self.event_handlers[event_name].remove(handler)
            logger.debug(f"注销事件处理器: {event_name}")

    def get_plugin_status(self) -> Dict[str, Dict[str, Any]]:
        """获取所有插件状态"""
        status = {}

        for plugin_name in self.get_available_plugins():
            info = self.get_plugin_info(plugin_name)
            instance = self.plugin_loader.get_plugin_instance(plugin_name)

            status[plugin_name] = {
                "enabled": plugin_name in self.enabled_plugins,
                "version": info.version if info else "unknown",
                "category": info.category if info else "unknown",
                "description": info.description if info else "",
                "has_instance": instance is not None,
                "config": self.plugin_configs.get(plugin_name, {}),
            }

        return status

    def validate_plugin_dependencies(self, plugin_name: str) -> bool:
        """验证插件依赖"""
        info = self.get_plugin_info(plugin_name)
        if not info or not info.dependencies:
            return True

        available_plugins = self.get_available_plugins()

        for dependency in info.dependencies:
            if dependency not in available_plugins:
                logger.error(f"插件 {plugin_name} 缺少依赖: {dependency}")
                return False

        return True

    def save_config(self):
        """保存配置"""
        config_data = {
            "enabled_plugins": list(self.enabled_plugins),
            "plugin_configs": self.plugin_configs,
        }

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            logger.info(f"保存插件配置: {self.config_file}")
        except Exception as e:
            logger.error(f"保存插件配置失败: {e}")

    def _load_config(self):
        """加载配置"""
        config_path = Path(self.config_file)
        if not config_path.exists():
            logger.info("插件配置文件不存在，使用默认配置")
            return

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            self.enabled_plugins = set(config_data.get("enabled_plugins", []))
            self.plugin_configs = config_data.get("plugin_configs", {})

            logger.info(f"加载插件配置: {len(self.enabled_plugins)} 个启用插件")

        except Exception as e:
            logger.error(f"加载插件配置失败: {e}")

    def _should_enable_plugin(self, plugin_name: str) -> bool:
        """判断是否应该启用插件"""
        # 检查配置中是否启用
        if plugin_name not in self.enabled_plugins:
            return False

        # 验证依赖
        if not self.validate_plugin_dependencies(plugin_name):
            logger.warning(f"插件依赖验证失败，跳过启用: {plugin_name}")
            return False

        return True

    def _register_plugin_events(self, plugin_name: str, instance: PluginInterface):
        """注册插件事件处理器"""
        # 根据插件类型注册相应的事件处理器
        from src.plugins.plugin_interface import (
            DataPlugin,
            LocustPlugin,
            MonitorPlugin,
            NotificationPlugin,
            ReportPlugin,
        )

        if isinstance(instance, LocustPlugin):
            self.register_event_handler("test_start", instance.on_test_start)
            self.register_event_handler("test_stop", instance.on_test_stop)

            if hasattr(instance, "on_user_start"):
                self.register_event_handler("user_start", instance.on_user_start)
            if hasattr(instance, "on_user_stop"):
                self.register_event_handler("user_stop", instance.on_user_stop)
            if hasattr(instance, "on_request_success"):
                self.register_event_handler(
                    "request_success", instance.on_request_success
                )
            if hasattr(instance, "on_request_failure"):
                self.register_event_handler(
                    "request_failure", instance.on_request_failure
                )

        if isinstance(instance, MonitorPlugin):
            self.register_event_handler("start_monitoring", instance.start_monitoring)
            self.register_event_handler("stop_monitoring", instance.stop_monitoring)

    def _unregister_plugin_events(self, plugin_name: str):
        """注销插件事件处理器"""
        instance = self.plugin_loader.get_plugin_instance(plugin_name)
        if not instance:
            return

        # 从所有事件中移除该插件的处理器
        for event_name, handlers in self.event_handlers.items():
            handlers_to_remove = []
            for handler in handlers:
                # 检查处理器是否属于该插件实例
                if hasattr(handler, "__self__") and handler.__self__ == instance:
                    handlers_to_remove.append(handler)

            for handler in handlers_to_remove:
                handlers.remove(handler)

    def shutdown(self):
        """关闭插件管理器"""
        logger.info("关闭插件管理器...")

        # 禁用所有插件
        for plugin_name in list(self.enabled_plugins):
            self.disable_plugin(plugin_name)

        # 保存配置
        self.save_config()

        logger.info("插件管理器已关闭")
