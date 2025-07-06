"""
插件接口定义

定义各种类型插件的标准接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class PluginInfo:
    """插件信息"""

    name: str
    version: str
    description: str
    author: str
    category: str
    dependencies: List[str] = None
    config_schema: Dict = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.config_schema is None:
            self.config_schema = {}


class PluginInterface(ABC):
    """插件基础接口"""

    def __init__(self):
        self._enabled = False
        self._config = {}

    @property
    @abstractmethod
    def plugin_info(self) -> PluginInfo:
        """获取插件信息"""
        pass

    @abstractmethod
    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """初始化插件"""
        pass

    @abstractmethod
    def cleanup(self):
        """清理插件资源"""
        pass

    def enable(self):
        """启用插件"""
        self._enabled = True

    def disable(self):
        """禁用插件"""
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        """检查插件是否启用"""
        return self._enabled

    def configure(self, config: Dict[str, Any]):
        """配置插件"""
        self._config.update(config)

    @property
    def config(self) -> Dict[str, Any]:
        """获取插件配置"""
        return self._config.copy()

    def validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置"""
        # 基础验证，子类可以重写
        return True


class LocustPlugin(PluginInterface):
    """Locust测试插件接口"""

    @abstractmethod
    def on_test_start(self, environment, **kwargs):
        """测试开始时调用"""
        pass

    @abstractmethod
    def on_test_stop(self, environment, **kwargs):
        """测试停止时调用"""
        pass

    def on_user_start(self, user_instance, **kwargs):
        """用户开始时调用（可选）"""
        pass

    def on_user_stop(self, user_instance, **kwargs):
        """用户停止时调用（可选）"""
        pass

    def on_request_success(
        self, request_type, name, response_time, response_length, **kwargs
    ):
        """请求成功时调用（可选）"""
        pass

    def on_request_failure(
        self, request_type, name, response_time, response_length, exception, **kwargs
    ):
        """请求失败时调用（可选）"""
        pass


class ReportPlugin(PluginInterface):
    """报告插件接口"""

    @abstractmethod
    def generate_report(self, test_data: Dict[str, Any], output_path: str) -> bool:
        """生成报告"""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """获取支持的报告格式"""
        pass

    def customize_report_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """自定义报告数据（可选）"""
        return test_data

    def get_report_template(self) -> Optional[str]:
        """获取报告模板（可选）"""
        return None


class MonitorPlugin(PluginInterface):
    """监控插件接口"""

    @abstractmethod
    def start_monitoring(self):
        """开始监控"""
        pass

    @abstractmethod
    def stop_monitoring(self):
        """停止监控"""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """获取监控指标"""
        pass

    def on_metric_threshold_exceeded(
        self, metric_name: str, current_value: float, threshold: float
    ):
        """指标超过阈值时调用（可选）"""
        pass

    def configure_thresholds(self, thresholds: Dict[str, float]):
        """配置监控阈值（可选）"""
        pass


class DataPlugin(PluginInterface):
    """数据插件接口"""

    @abstractmethod
    def generate_test_data(
        self, data_type: str, count: int, **kwargs
    ) -> List[Dict[str, Any]]:
        """生成测试数据"""
        pass

    @abstractmethod
    def get_supported_data_types(self) -> List[str]:
        """获取支持的数据类型"""
        pass

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """验证数据（可选）"""
        return True

    def transform_data(
        self, data: List[Dict[str, Any]], transformation: str
    ) -> List[Dict[str, Any]]:
        """转换数据（可选）"""
        return data


class NotificationPlugin(PluginInterface):
    """通知插件接口"""

    @abstractmethod
    def send_notification(self, message: str, **kwargs) -> bool:
        """发送通知"""
        pass

    @abstractmethod
    def get_notification_channels(self) -> List[str]:
        """获取支持的通知渠道"""
        pass

    def format_message(self, message: str, message_type: str = "text") -> str:
        """格式化消息（可选）"""
        return message

    def test_connection(self) -> bool:
        """测试连接（可选）"""
        return True


class LoadShapePlugin(PluginInterface):
    """负载模式插件接口"""

    @abstractmethod
    def get_load_shape_class(self):
        """获取负载模式类"""
        pass

    @abstractmethod
    def get_shape_parameters(self) -> Dict[str, Any]:
        """获取模式参数"""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """验证参数（可选）"""
        return True

    def get_shape_description(self) -> str:
        """获取模式描述（可选）"""
        return ""


class AnalysisPlugin(PluginInterface):
    """分析插件接口"""

    @abstractmethod
    def analyze_results(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析测试结果"""
        pass

    @abstractmethod
    def get_analysis_types(self) -> List[str]:
        """获取支持的分析类型"""
        pass

    def generate_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成洞察（可选）"""
        return []

    def compare_results(
        self, current_results: Dict[str, Any], historical_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """比较结果（可选）"""
        return {}


class StoragePlugin(PluginInterface):
    """存储插件接口"""

    @abstractmethod
    def save_test_results(self, results: Dict[str, Any], test_id: str) -> bool:
        """保存测试结果"""
        pass

    @abstractmethod
    def load_test_results(self, test_id: str) -> Optional[Dict[str, Any]]:
        """加载测试结果"""
        pass

    @abstractmethod
    def list_test_results(self, limit: int = 100) -> List[Dict[str, Any]]:
        """列出测试结果"""
        pass

    def delete_test_results(self, test_id: str) -> bool:
        """删除测试结果（可选）"""
        return False

    def search_test_results(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """搜索测试结果（可选）"""
        return []


class AuthenticationPlugin(PluginInterface):
    """认证插件接口"""

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """认证"""
        pass

    @abstractmethod
    def get_auth_token(self, credentials: Dict[str, Any]) -> Optional[str]:
        """获取认证令牌"""
        pass

    def refresh_token(self, token: str) -> Optional[str]:
        """刷新令牌（可选）"""
        return None

    def validate_token(self, token: str) -> bool:
        """验证令牌（可选）"""
        return True

    def logout(self, token: str) -> bool:
        """登出（可选）"""
        return True


class ProtocolPlugin(PluginInterface):
    """协议插件接口"""

    @abstractmethod
    def create_client(self, **kwargs):
        """创建协议客户端"""
        pass

    @abstractmethod
    def get_supported_protocols(self) -> List[str]:
        """获取支持的协议"""
        pass

    def validate_connection(self, client) -> bool:
        """验证连接（可选）"""
        return True

    def close_connection(self, client):
        """关闭连接（可选）"""
        pass
