# 编码规范

本文档定义了Locust性能测试框架的编码规范，确保代码质量、可读性和可维护性。

## 🎯 总体原则

### 设计原则

1. **SOLID原则**
   - **单一职责原则(SRP)**: 每个类只负责一个功能
   - **开闭原则(OCP)**: 对扩展开放，对修改关闭
   - **里氏替换原则(LSP)**: 子类可以替换父类
   - **接口隔离原则(ISP)**: 接口应该小而专一
   - **依赖倒置原则(DIP)**: 依赖抽象而非具体实现

2. **代码质量原则**
   - **DRY (Don't Repeat Yourself)**: 避免重复代码
   - **KISS (Keep It Simple, Stupid)**: 保持简单
   - **YAGNI (You Aren't Gonna Need It)**: 不要过度设计

## 📝 Python编码规范

### 代码风格

遵循 **PEP 8** 标准，使用 **Black** 进行代码格式化。

#### 命名规范

```python
# 模块名：小写字母，下划线分隔
# ✅ 正确
performance_analyzer.py
data_manager.py

# ❌ 错误
PerformanceAnalyzer.py
dataManager.py

# 类名：大驼峰命名法
# ✅ 正确
class PerformanceAnalyzer:
    pass

class DataProvider:
    pass

# ❌ 错误
class performance_analyzer:
    pass

class dataProvider:
    pass

# 函数名和变量名：小写字母，下划线分隔
# ✅ 正确
def analyze_performance():
    pass

user_count = 100
response_time = 500.0

# ❌ 错误
def analyzePerformance():
    pass

userCount = 100
responseTime = 500.0

# 常量：大写字母，下划线分隔
# ✅ 正确
MAX_USERS = 1000
DEFAULT_TIMEOUT = 30
API_VERSION = "v1"

# 私有属性/方法：单下划线前缀
class MyClass:
    def __init__(self):
        self._private_var = "private"

    def _private_method(self):
        pass

# 特殊方法：双下划线前后
class MyClass:
    def __init__(self):
        pass

    def __str__(self):
        return "MyClass instance"
```

#### 导入规范

```python
# 导入顺序：标准库 -> 第三方库 -> 本地模块
# 每组之间空一行

# 标准库
import os
import sys
import time
from typing import Dict, List, Optional, Any

# 第三方库
import requests
from locust import HttpUser, task
from dynaconf import Dynaconf

# 本地模块
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.monitoring.alert_manager import AlertManager
from .utils import helper_function

# ✅ 正确的导入方式
from typing import Dict, List, Optional

# ❌ 避免使用通配符导入
from module import *

# ✅ 使用别名简化长模块名
import src.very_long_module_name as vlmn

# ✅ 相对导入用于同包内模块
from .sibling_module import function
from ..parent_module import ParentClass
```

#### 字符串格式化

```python
# ✅ 推荐使用 f-string (Python 3.6+)
name = "张三"
age = 25
message = f"用户 {name} 年龄 {age} 岁"

# ✅ 复杂格式化使用 format()
template = "响应时间: {time:.2f}ms, 状态: {status}"
result = template.format(time=response_time, status="success")

# ❌ 避免使用 % 格式化
message = "用户 %s 年龄 %d 岁" % (name, age)

# ✅ 多行字符串
sql_query = """
SELECT user_id, username, email
FROM users
WHERE created_at > %s
ORDER BY created_at DESC
"""

# ✅ 长字符串拼接
long_message = (
    "这是一个很长的消息，"
    "需要分成多行来提高可读性，"
    "每行不超过88个字符。"
)
```

### 文档字符串规范

使用 **Google风格** 的文档字符串。

```python
def analyze_performance(test_data: Dict[str, Any],
                       config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """分析测试性能数据

    对测试数据进行综合性能分析，包括响应时间、吞吐量、错误率等指标，
    并生成性能评级和改进建议。

    Args:
        test_data: 测试数据字典，包含以下字段：
            - requests: 请求列表
            - duration: 测试持续时间
            - users: 用户数量
        config: 分析配置参数，可选
            - thresholds: 性能阈值设置
            - weights: 指标权重配置

    Returns:
        Dict[str, Any]: 分析结果字典，包含：
            - overall_grade: 总体评级 (A/B/C/D)
            - response_time: 响应时间分析
            - throughput: 吞吐量分析
            - error_analysis: 错误分析
            - recommendations: 改进建议

    Raises:
        ValueError: 当test_data格式不正确时
        AnalysisError: 当分析过程出现错误时

    Example:
        >>> test_data = {
        ...     'requests': [{'response_time': 100, 'success': True}],
        ...     'duration': 60,
        ...     'users': 10
        ... }
        >>> result = analyze_performance(test_data)
        >>> print(result['overall_grade'])
        'A'

    Note:
        此函数会消耗较多CPU资源，建议在测试结束后调用。

    Todo:
        - 添加更多性能指标
        - 支持自定义评级算法
    """
    pass

class PerformanceAnalyzer:
    """性能分析器

    提供全面的性能测试数据分析功能，包括统计分析、
    趋势分析、异常检测等。

    Attributes:
        config: 分析器配置
        thresholds: 性能阈值设置

    Example:
        >>> analyzer = PerformanceAnalyzer()
        >>> result = analyzer.analyze(test_data)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化性能分析器

        Args:
            config: 分析器配置，包含阈值和权重设置
        """
        pass
```

### 类型注解规范

```python
from typing import Dict, List, Optional, Union, Tuple, Any, Callable

# ✅ 基础类型注解
def process_data(data: str) -> int:
    return len(data)

# ✅ 复合类型注解
def analyze_requests(requests: List[Dict[str, Any]]) -> Dict[str, float]:
    pass

# ✅ 可选参数
def create_user(name: str, age: Optional[int] = None) -> Dict[str, Any]:
    pass

# ✅ 联合类型
def parse_value(value: Union[str, int, float]) -> str:
    return str(value)

# ✅ 回调函数类型
def register_callback(callback: Callable[[str], None]) -> None:
    pass

# ✅ 类属性注解
class DataManager:
    config: Dict[str, Any]
    providers: List[str]

    def __init__(self):
        self.config = {}
        self.providers = []

# ✅ 泛型类型
from typing import TypeVar, Generic

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value
```

### 异常处理规范

```python
# ✅ 自定义异常类
class FrameworkError(Exception):
    """框架基础异常类"""
    pass

class AnalysisError(FrameworkError):
    """分析相关异常"""
    pass

class ConfigurationError(FrameworkError):
    """配置相关异常"""
    pass

# ✅ 异常处理最佳实践
def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"配置文件不存在: {config_path}")
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"配置文件格式错误: {e}")
    except Exception as e:
        # 记录未预期的异常
        logger.exception(f"加载配置文件时发生未知错误: {e}")
        raise

# ✅ 使用上下文管理器
class DatabaseConnection:
    def __enter__(self):
        self.connection = create_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()

# 使用方式
with DatabaseConnection() as conn:
    # 使用连接
    pass

# ✅ 异常链
def process_data(data: str) -> Dict[str, Any]:
    try:
        return parse_json(data)
    except ValueError as e:
        raise AnalysisError("数据解析失败") from e
```

### 日志规范

```python
import logging

# ✅ 日志配置
logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析性能数据"""
        self.logger.info("开始性能分析")
        self.logger.debug(f"输入数据: {data}")

        try:
            result = self._do_analysis(data)
            self.logger.info(f"分析完成，评级: {result.get('grade')}")
            return result
        except Exception as e:
            self.logger.error(f"分析失败: {e}", exc_info=True)
            raise

# ✅ 日志级别使用
logger.debug("详细的调试信息")      # 开发调试
logger.info("一般信息")            # 正常流程
logger.warning("警告信息")         # 潜在问题
logger.error("错误信息")           # 错误但程序可继续
logger.critical("严重错误")        # 严重错误，程序可能停止

# ✅ 结构化日志
logger.info("用户登录", extra={
    'user_id': user_id,
    'ip_address': request.remote_addr,
    'user_agent': request.headers.get('User-Agent')
})
```

## 🏗️ 架构规范

### 目录结构

```
src/
├── analysis/           # 性能分析模块
│   ├── __init__.py
│   ├── performance_analyzer.py
│   ├── trend_analyzer.py
│   └── report_generator.py
├── monitoring/         # 监控告警模块
│   ├── __init__.py
│   ├── performance_monitor.py
│   ├── alert_manager.py
│   └── notification_service.py
├── data_manager/       # 数据管理模块
│   ├── __init__.py
│   ├── data_generator.py
│   ├── data_provider.py
│   └── data_distributor.py
├── plugins/           # 插件系统
│   ├── __init__.py
│   ├── plugin_interface.py
│   ├── plugin_manager.py
│   └── builtin/       # 内置插件
└── utils/             # 工具模块
    ├── __init__.py
    ├── helpers.py
    └── decorators.py
```

### 模块设计规范

```python
# ✅ 接口定义
from abc import ABC, abstractmethod
from typing import Protocol

class AnalyzerInterface(ABC):
    """分析器接口"""

    @abstractmethod
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析数据"""
        pass

# ✅ 使用Protocol定义结构化类型
class Configurable(Protocol):
    """可配置对象协议"""

    def configure(self, config: Dict[str, Any]) -> None:
        """配置对象"""
        ...

# ✅ 工厂模式
class AnalyzerFactory:
    """分析器工厂"""

    _analyzers = {
        'performance': PerformanceAnalyzer,
        'trend': TrendAnalyzer,
    }

    @classmethod
    def create_analyzer(cls, analyzer_type: str, **kwargs) -> AnalyzerInterface:
        """创建分析器实例"""
        if analyzer_type not in cls._analyzers:
            raise ValueError(f"未知的分析器类型: {analyzer_type}")

        analyzer_class = cls._analyzers[analyzer_type]
        return analyzer_class(**kwargs)

# ✅ 单例模式
class ConfigManager:
    """配置管理器单例"""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self, config_path: str) -> None:
        """加载配置"""
        if self._config is None:
            self._config = self._load_from_file(config_path)

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self._config or {}
```

### 依赖注入

```python
# ✅ 依赖注入示例
class PerformanceAnalyzer:
    def __init__(self,
                 data_provider: DataProviderInterface,
                 config_manager: ConfigManagerInterface,
                 logger: logging.Logger):
        self.data_provider = data_provider
        self.config_manager = config_manager
        self.logger = logger

    def analyze(self, test_id: str) -> Dict[str, Any]:
        """分析性能数据"""
        # 使用注入的依赖
        data = self.data_provider.get_test_data(test_id)
        config = self.config_manager.get_analysis_config()

        self.logger.info(f"开始分析测试 {test_id}")
        # 执行分析逻辑
        return result

# ✅ 依赖容器
class DIContainer:
    """依赖注入容器"""

    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register(self, interface: type, implementation: type, singleton: bool = False):
        """注册服务"""
        self._services[interface] = (implementation, singleton)

    def get(self, interface: type):
        """获取服务实例"""
        if interface in self._singletons:
            return self._singletons[interface]

        implementation, is_singleton = self._services[interface]
        instance = implementation()

        if is_singleton:
            self._singletons[interface] = instance

        return instance
```

## 🧪 测试规范

### 单元测试

```python
import pytest
from unittest.mock import Mock, patch
from src.analysis.performance_analyzer import PerformanceAnalyzer

class TestPerformanceAnalyzer:
    """性能分析器测试类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.analyzer = PerformanceAnalyzer()
        self.sample_data = {
            'requests': [
                {'response_time': 100, 'success': True},
                {'response_time': 200, 'success': True},
                {'response_time': 150, 'success': False}
            ],
            'duration': 60,
            'users': 10
        }

    def test_analyze_performance_success(self):
        """测试性能分析成功场景"""
        # Given
        expected_grade = 'B'

        # When
        result = self.analyzer.analyze(self.sample_data)

        # Then
        assert result['overall_grade'] == expected_grade
        assert 'response_time' in result
        assert 'throughput' in result
        assert 'error_analysis' in result

    def test_analyze_performance_empty_data(self):
        """测试空数据场景"""
        # Given
        empty_data = {'requests': [], 'duration': 0, 'users': 0}

        # When & Then
        with pytest.raises(ValueError, match="测试数据不能为空"):
            self.analyzer.analyze(empty_data)

    @patch('src.analysis.performance_analyzer.calculate_percentile')
    def test_analyze_with_mock(self, mock_percentile):
        """测试使用Mock"""
        # Given
        mock_percentile.return_value = 150.0

        # When
        result = self.analyzer.analyze(self.sample_data)

        # Then
        mock_percentile.assert_called()
        assert result['response_time']['p95'] == 150.0

    @pytest.mark.parametrize("response_times,expected_grade", [
        ([100, 200, 150], 'B'),
        ([50, 80, 60], 'A'),
        ([500, 600, 700], 'D'),
    ])
    def test_grading_algorithm(self, response_times, expected_grade):
        """参数化测试评级算法"""
        # Given
        test_data = {
            'requests': [{'response_time': rt, 'success': True} for rt in response_times],
            'duration': 60,
            'users': 10
        }

        # When
        result = self.analyzer.analyze(test_data)

        # Then
        assert result['overall_grade'] == expected_grade
```

### 集成测试

```python
import pytest
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.data_manager.data_provider import DataProvider

class TestAnalysisIntegration:
    """分析模块集成测试"""

    @pytest.fixture
    def analyzer(self):
        """分析器fixture"""
        return PerformanceAnalyzer()

    @pytest.fixture
    def data_provider(self):
        """数据提供者fixture"""
        provider = DataProvider()
        provider.load_test_data("tests/fixtures/sample_data.json")
        return provider

    def test_end_to_end_analysis(self, analyzer, data_provider):
        """端到端分析测试"""
        # Given
        test_data = data_provider.get_test_data("sample_test")

        # When
        result = analyzer.comprehensive_analysis(test_data)

        # Then
        assert result is not None
        assert 'overall_grade' in result
        assert result['overall_grade'] in ['A', 'B', 'C', 'D']
```

## 📊 性能规范

### 性能要求

```python
import time
import functools

def performance_monitor(max_time: float = 1.0):
    """性能监控装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            if execution_time > max_time:
                logger.warning(
                    f"函数 {func.__name__} 执行时间过长: {execution_time:.2f}s"
                )

            return result
        return wrapper
    return decorator

# ✅ 使用性能监控
@performance_monitor(max_time=0.5)
def analyze_large_dataset(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析大数据集"""
    # 实现分析逻辑
    pass

# ✅ 内存优化
def process_large_file(file_path: str) -> None:
    """处理大文件"""
    with open(file_path, 'r') as f:
        for line in f:  # 逐行处理，避免一次性加载
            process_line(line)

# ✅ 缓存优化
from functools import lru_cache

class DataAnalyzer:
    @lru_cache(maxsize=128)
    def calculate_statistics(self, data_hash: str) -> Dict[str, float]:
        """计算统计信息（带缓存）"""
        # 耗时的统计计算
        pass
```

## 🔒 安全规范

```python
# ✅ 输入验证
def validate_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """验证用户输入"""
    from cerberus import Validator

    schema = {
        'username': {'type': 'string', 'minlength': 3, 'maxlength': 50},
        'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+$'},
        'age': {'type': 'integer', 'min': 0, 'max': 150}
    }

    validator = Validator(schema)
    if not validator.validate(data):
        raise ValueError(f"输入验证失败: {validator.errors}")

    return validator.normalized(data)

# ✅ 敏感信息处理
import hashlib
import secrets

def hash_password(password: str) -> str:
    """安全的密码哈希"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
    return f"{salt}:{password_hash.hex()}"

# ✅ 日志脱敏
def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """日志数据脱敏"""
    sensitive_fields = ['password', 'token', 'secret', 'key']
    sanitized = data.copy()

    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "***"

    return sanitized
```

## 🔧 工具配置

### pre-commit配置

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3.9

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### 代码质量检查

```bash
# 运行所有检查
make lint

# 单独运行各工具
black --check src tests
isort --check-only src tests
flake8 src tests
pylint src
mypy src
```

遵循这些编码规范将确保代码库的一致性、可读性和可维护性，为团队协作和项目长期发展奠定坚实基础。
