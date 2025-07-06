"""
插件系统

提供可扩展的插件架构，支持自定义功能扩展
"""

from .plugin_interface import LocustPlugin, MonitorPlugin, PluginInterface, ReportPlugin
from .plugin_loader import PluginLoader
from .plugin_manager import PluginManager

__all__ = [
    "PluginManager",
    "PluginInterface",
    "LocustPlugin",
    "ReportPlugin",
    "MonitorPlugin",
    "PluginLoader",
]
