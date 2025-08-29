"""
基础插件类 - 符合文档API规范
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BasePlugin(ABC):
    """插件基类 - 符合文档API规范"""

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
            "config": self.config,
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
        return logging.getLogger(f"plugin.{self.__class__.__name__}")
