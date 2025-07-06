"""
插件加载器

负责动态加载和管理插件
"""

import importlib
import importlib.util
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from src.plugins.plugin_interface import PluginInfo, PluginInterface
from src.utils.log_moudle import logger


class PluginLoader:
    """插件加载器"""

    def __init__(self, plugin_dirs: List[str] = None):
        self.plugin_dirs = plugin_dirs or ["plugins", "src/plugins/builtin"]
        self.loaded_plugins = {}  # plugin_name -> plugin_class
        self.plugin_instances = {}  # plugin_name -> plugin_instance
        self.plugin_metadata = {}  # plugin_name -> metadata

        # 确保插件目录存在
        for plugin_dir in self.plugin_dirs:
            Path(plugin_dir).mkdir(parents=True, exist_ok=True)

    def discover_plugins(self) -> List[str]:
        """发现可用的插件"""
        discovered_plugins = []

        for plugin_dir in self.plugin_dirs:
            plugin_path = Path(plugin_dir)
            if not plugin_path.exists():
                continue

            # 扫描Python文件
            for py_file in plugin_path.glob("**/*.py"):
                if py_file.name.startswith("__"):
                    continue

                try:
                    plugin_name = self._get_plugin_name_from_file(py_file)
                    if plugin_name:
                        discovered_plugins.append(plugin_name)
                        logger.debug(f"发现插件: {plugin_name} ({py_file})")
                except Exception as e:
                    logger.warning(f"扫描插件文件失败 {py_file}: {e}")

        logger.info(f"发现 {len(discovered_plugins)} 个插件")
        return discovered_plugins

    def load_plugin(
        self, plugin_name: str, plugin_path: str = None
    ) -> Optional[Type[PluginInterface]]:
        """加载单个插件"""
        if plugin_name in self.loaded_plugins:
            logger.warning(f"插件已加载: {plugin_name}")
            return self.loaded_plugins[plugin_name]

        try:
            # 查找插件文件
            if plugin_path is None:
                plugin_path = self._find_plugin_file(plugin_name)
                if plugin_path is None:
                    logger.error(f"未找到插件文件: {plugin_name}")
                    return None

            # 加载模块
            module = self._load_module_from_file(plugin_name, plugin_path)
            if module is None:
                return None

            # 查找插件类
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                logger.error(f"未找到插件类: {plugin_name}")
                return None

            # 验证插件类
            if not self._validate_plugin_class(plugin_class):
                logger.error(f"插件类验证失败: {plugin_name}")
                return None

            # 加载插件元数据
            metadata = self._load_plugin_metadata(plugin_path, plugin_class)

            # 注册插件
            self.loaded_plugins[plugin_name] = plugin_class
            self.plugin_metadata[plugin_name] = metadata

            logger.info(f"成功加载插件: {plugin_name}")
            return plugin_class

        except Exception as e:
            logger.error(f"加载插件失败 {plugin_name}: {e}")
            return None

    def load_all_plugins(self) -> Dict[str, Type[PluginInterface]]:
        """加载所有发现的插件"""
        discovered_plugins = self.discover_plugins()
        loaded_count = 0

        for plugin_name in discovered_plugins:
            if self.load_plugin(plugin_name):
                loaded_count += 1

        logger.info(f"成功加载 {loaded_count}/{len(discovered_plugins)} 个插件")
        return self.loaded_plugins.copy()

    def unload_plugin(self, plugin_name: str):
        """卸载插件"""
        if plugin_name in self.plugin_instances:
            try:
                instance = self.plugin_instances[plugin_name]
                instance.cleanup()
                del self.plugin_instances[plugin_name]
            except Exception as e:
                logger.error(f"清理插件实例失败 {plugin_name}: {e}")

        if plugin_name in self.loaded_plugins:
            del self.loaded_plugins[plugin_name]

        if plugin_name in self.plugin_metadata:
            del self.plugin_metadata[plugin_name]

        logger.info(f"卸载插件: {plugin_name}")

    def create_plugin_instance(
        self, plugin_name: str, config: Dict[str, Any] = None
    ) -> Optional[PluginInterface]:
        """创建插件实例"""
        if plugin_name not in self.loaded_plugins:
            logger.error(f"插件未加载: {plugin_name}")
            return None

        if plugin_name in self.plugin_instances:
            logger.warning(f"插件实例已存在: {plugin_name}")
            return self.plugin_instances[plugin_name]

        try:
            plugin_class = self.loaded_plugins[plugin_name]
            instance = plugin_class()

            # 初始化插件
            if not instance.initialize(config or {}):
                logger.error(f"插件初始化失败: {plugin_name}")
                return None

            self.plugin_instances[plugin_name] = instance
            logger.info(f"创建插件实例: {plugin_name}")
            return instance

        except Exception as e:
            logger.error(f"创建插件实例失败 {plugin_name}: {e}")
            return None

    def get_plugin_instance(self, plugin_name: str) -> Optional[PluginInterface]:
        """获取插件实例"""
        return self.plugin_instances.get(plugin_name)

    def get_loaded_plugins(self) -> Dict[str, Type[PluginInterface]]:
        """获取已加载的插件"""
        return self.loaded_plugins.copy()

    def get_plugin_metadata(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取插件元数据"""
        return self.plugin_metadata.get(plugin_name)

    def get_plugins_by_category(self, category: str) -> List[str]:
        """根据类别获取插件"""
        plugins = []
        for plugin_name, metadata in self.plugin_metadata.items():
            if metadata.get("category") == category:
                plugins.append(plugin_name)
        return plugins

    def reload_plugin(self, plugin_name: str) -> bool:
        """重新加载插件"""
        if plugin_name not in self.loaded_plugins:
            logger.error(f"插件未加载: {plugin_name}")
            return False

        try:
            # 保存配置
            config = {}
            if plugin_name in self.plugin_instances:
                config = self.plugin_instances[plugin_name].config

            # 卸载插件
            self.unload_plugin(plugin_name)

            # 重新加载
            if self.load_plugin(plugin_name):
                # 重新创建实例
                if config:
                    self.create_plugin_instance(plugin_name, config)
                logger.info(f"重新加载插件成功: {plugin_name}")
                return True
            else:
                logger.error(f"重新加载插件失败: {plugin_name}")
                return False

        except Exception as e:
            logger.error(f"重新加载插件异常 {plugin_name}: {e}")
            return False

    def _find_plugin_file(self, plugin_name: str) -> Optional[str]:
        """查找插件文件"""
        for plugin_dir in self.plugin_dirs:
            plugin_path = Path(plugin_dir)

            # 尝试直接匹配文件名
            plugin_file = plugin_path / f"{plugin_name}.py"
            if plugin_file.exists():
                return str(plugin_file)

            # 尝试在子目录中查找
            for py_file in plugin_path.glob(f"**/{plugin_name}.py"):
                return str(py_file)

            # 尝试查找包含插件名的文件
            for py_file in plugin_path.glob("**/*.py"):
                if plugin_name.lower() in py_file.stem.lower():
                    return str(py_file)

        return None

    def _load_module_from_file(self, plugin_name: str, plugin_path: str):
        """从文件加载模块"""
        try:
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if spec is None:
                logger.error(f"无法创建模块规范: {plugin_path}")
                return None

            module = importlib.util.module_from_spec(spec)
            if module is None:
                logger.error(f"无法创建模块: {plugin_path}")
                return None

            # 添加到sys.modules以支持相对导入
            sys.modules[plugin_name] = module
            spec.loader.exec_module(module)

            return module

        except Exception as e:
            logger.error(f"加载模块失败 {plugin_path}: {e}")
            return None

    def _find_plugin_class(self, module) -> Optional[Type[PluginInterface]]:
        """在模块中查找插件类"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if (
                issubclass(obj, PluginInterface)
                and obj != PluginInterface
                and obj.__module__ == module.__name__
            ):
                return obj
        return None

    def _validate_plugin_class(self, plugin_class: Type[PluginInterface]) -> bool:
        """验证插件类"""
        try:
            # 检查必需的方法
            required_methods = ["plugin_info", "initialize", "cleanup"]
            for method_name in required_methods:
                if not hasattr(plugin_class, method_name):
                    logger.error(f"插件类缺少必需方法: {method_name}")
                    return False

            # 尝试创建临时实例来验证plugin_info
            temp_instance = plugin_class()
            plugin_info = temp_instance.plugin_info

            if not isinstance(plugin_info, PluginInfo):
                logger.error("plugin_info必须返回PluginInfo实例")
                return False

            return True

        except Exception as e:
            logger.error(f"验证插件类失败: {e}")
            return False

    def _load_plugin_metadata(
        self, plugin_path: str, plugin_class: Type[PluginInterface]
    ) -> Dict[str, Any]:
        """加载插件元数据"""
        metadata = {}

        try:
            # 从插件类获取信息
            temp_instance = plugin_class()
            plugin_info = temp_instance.plugin_info

            metadata.update(
                {
                    "name": plugin_info.name,
                    "version": plugin_info.version,
                    "description": plugin_info.description,
                    "author": plugin_info.author,
                    "category": plugin_info.category,
                    "dependencies": plugin_info.dependencies,
                    "config_schema": plugin_info.config_schema,
                    "file_path": plugin_path,
                    "class_name": plugin_class.__name__,
                }
            )

            # 尝试加载外部元数据文件
            metadata_file = Path(plugin_path).with_suffix(".json")
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    external_metadata = json.load(f)
                    metadata.update(external_metadata)

        except Exception as e:
            logger.warning(f"加载插件元数据失败 {plugin_path}: {e}")

        return metadata

    def _get_plugin_name_from_file(self, file_path: Path) -> Optional[str]:
        """从文件路径获取插件名"""
        try:
            # 简单的启发式方法：使用文件名作为插件名
            plugin_name = file_path.stem

            # 验证文件是否包含插件类
            module_name = f"temp_{plugin_name}"
            spec = importlib.util.spec_from_file_location(module_name, str(file_path))
            if spec is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 查找插件类
            plugin_class = self._find_plugin_class(module)
            if plugin_class:
                return plugin_name

            return None

        except Exception:
            return None
