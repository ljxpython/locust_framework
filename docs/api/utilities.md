# 工具类API

本文档详细介绍Locust性能测试框架的工具类和辅助函数API。

## 📋 API概览

工具类API提供了丰富的辅助功能，包括：

- **文件操作工具**: 文件读写、路径处理
- **报告生成工具**: 报告格式化和生成
- **日志管理工具**: 日志配置和管理
- **集合点工具**: 用户同步和集合点
- **通用工具函数**: 常用的辅助函数

## 📁 文件操作工具

### FileOperationUtil

文件操作工具类，提供文件和目录的常用操作。

```python
import os
import json
import csv
import yaml
from typing import List, Dict, Any, Optional
from pathlib import Path

class FileOperationUtil:
    """文件操作工具类"""

    @staticmethod
    def read_file(file_path: str, encoding: str = 'utf-8') -> str:
        """
        读取文件内容

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            str: 文件内容

        Raises:
            FileNotFoundError: 文件不存在
            IOError: 读取失败
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise IOError(f"Failed to read file {file_path}: {e}")

    @staticmethod
    def write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文件内容

        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码

        Returns:
            bool: 写入是否成功
        """
        try:
            # 确保目录存在
            FileOperationUtil.ensure_dir(os.path.dirname(file_path))

            with open(file_path, 'w', encoding=encoding) as file:
                file.write(content)
            return True
        except Exception as e:
            print(f"Failed to write file {file_path}: {e}")
            return False

    @staticmethod
    def read_json(file_path: str) -> Dict[str, Any]:
        """
        读取JSON文件

        Args:
            file_path: JSON文件路径

        Returns:
            Dict[str, Any]: JSON数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            raise ValueError(f"Failed to read JSON file {file_path}: {e}")

    @staticmethod
    def write_json(file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
        """
        写入JSON文件

        Args:
            file_path: JSON文件路径
            data: 要写入的数据
            indent: 缩进空格数

        Returns:
            bool: 写入是否成功
        """
        try:
            FileOperationUtil.ensure_dir(os.path.dirname(file_path))

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=indent, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to write JSON file {file_path}: {e}")
            return False

    @staticmethod
    def read_csv(file_path: str, delimiter: str = ',') -> List[Dict[str, str]]:
        """
        读取CSV文件

        Args:
            file_path: CSV文件路径
            delimiter: 分隔符

        Returns:
            List[Dict[str, str]]: CSV数据列表
        """
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                data = list(reader)
            return data
        except Exception as e:
            raise ValueError(f"Failed to read CSV file {file_path}: {e}")

    @staticmethod
    def write_csv(file_path: str, data: List[Dict[str, Any]],
                  fieldnames: Optional[List[str]] = None) -> bool:
        """
        写入CSV文件

        Args:
            file_path: CSV文件路径
            data: 要写入的数据
            fieldnames: 字段名列表

        Returns:
            bool: 写入是否成功
        """
        try:
            if not data:
                return False

            FileOperationUtil.ensure_dir(os.path.dirname(file_path))

            if fieldnames is None:
                fieldnames = list(data[0].keys())

            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Failed to write CSV file {file_path}: {e}")
            return False

    @staticmethod
    def read_yaml(file_path: str) -> Dict[str, Any]:
        """
        读取YAML文件

        Args:
            file_path: YAML文件路径

        Returns:
            Dict[str, Any]: YAML数据
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Failed to read YAML file {file_path}: {e}")

    @staticmethod
    def write_yaml(file_path: str, data: Dict[str, Any]) -> bool:
        """
        写入YAML文件

        Args:
            file_path: YAML文件路径
            data: 要写入的数据

        Returns:
            bool: 写入是否成功
        """
        try:
            FileOperationUtil.ensure_dir(os.path.dirname(file_path))

            with open(file_path, 'w', encoding='utf-8') as file:
                yaml.dump(data, file, default_flow_style=False,
                         allow_unicode=True, indent=2)
            return True
        except Exception as e:
            print(f"Failed to write YAML file {file_path}: {e}")
            return False

    @staticmethod
    def ensure_dir(dir_path: str) -> bool:
        """
        确保目录存在

        Args:
            dir_path: 目录路径

        Returns:
            bool: 操作是否成功
        """
        try:
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create directory {dir_path}: {e}")
            return False

    @staticmethod
    def list_files(dir_path: str, pattern: str = "*", recursive: bool = False) -> List[str]:
        """
        列出目录中的文件

        Args:
            dir_path: 目录路径
            pattern: 文件模式
            recursive: 是否递归搜索

        Returns:
            List[str]: 文件路径列表
        """
        try:
            path = Path(dir_path)
            if recursive:
                return [str(p) for p in path.rglob(pattern) if p.is_file()]
            else:
                return [str(p) for p in path.glob(pattern) if p.is_file()]
        except Exception as e:
            print(f"Failed to list files in {dir_path}: {e}")
            return []

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """
        获取文件大小

        Args:
            file_path: 文件路径

        Returns:
            int: 文件大小(字节)
        """
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        检查文件是否存在

        Args:
            file_path: 文件路径

        Returns:
            bool: 文件是否存在
        """
        return os.path.isfile(file_path)

    @staticmethod
    def dir_exists(dir_path: str) -> bool:
        """
        检查目录是否存在

        Args:
            dir_path: 目录路径

        Returns:
            bool: 目录是否存在
        """
        return os.path.isdir(dir_path)
```

## 📊 报告生成工具

### LocustReportUtil

Locust报告生成和处理工具。

```python
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class LocustReportUtil:
    """Locust报告工具类"""

    @staticmethod
    def generate_html_report(stats_data: Dict[str, Any],
                           output_path: str = "report.html") -> bool:
        """
        生成HTML报告

        Args:
            stats_data: 统计数据
            output_path: 输出路径

        Returns:
            bool: 生成是否成功
        """
        try:
            html_content = LocustReportUtil._create_html_template(stats_data)
            return FileOperationUtil.write_file(output_path, html_content)
        except Exception as e:
            print(f"Failed to generate HTML report: {e}")
            return False

    @staticmethod
    def generate_csv_report(stats_data: Dict[str, Any],
                          output_path: str = "report.csv") -> bool:
        """
        生成CSV报告

        Args:
            stats_data: 统计数据
            output_path: 输出路径

        Returns:
            bool: 生成是否成功
        """
        try:
            csv_data = LocustReportUtil._convert_to_csv_format(stats_data)
            return FileOperationUtil.write_csv(output_path, csv_data)
        except Exception as e:
            print(f"Failed to generate CSV report: {e}")
            return False

    @staticmethod
    def generate_json_report(stats_data: Dict[str, Any],
                           output_path: str = "report.json") -> bool:
        """
        生成JSON报告

        Args:
            stats_data: 统计数据
            output_path: 输出路径

        Returns:
            bool: 生成是否成功
        """
        try:
            json_data = LocustReportUtil._format_json_report(stats_data)
            return FileOperationUtil.write_json(output_path, json_data)
        except Exception as e:
            print(f"Failed to generate JSON report: {e}")
            return False

    @staticmethod
    def parse_locust_stats(stats_file: str) -> Dict[str, Any]:
        """
        解析Locust统计文件

        Args:
            stats_file: 统计文件路径

        Returns:
            Dict[str, Any]: 解析后的统计数据
        """
        try:
            if stats_file.endswith('.csv'):
                raw_data = FileOperationUtil.read_csv(stats_file)
                return LocustReportUtil._process_csv_stats(raw_data)
            elif stats_file.endswith('.json'):
                return FileOperationUtil.read_json(stats_file)
            else:
                raise ValueError(f"Unsupported file format: {stats_file}")
        except Exception as e:
            print(f"Failed to parse stats file {stats_file}: {e}")
            return {}

    @staticmethod
    def calculate_percentiles(response_times: List[float],
                            percentiles: List[int] = [50, 90, 95, 99]) -> Dict[str, float]:
        """
        计算响应时间百分位数

        Args:
            response_times: 响应时间列表
            percentiles: 百分位数列表

        Returns:
            Dict[str, float]: 百分位数结果
        """
        if not response_times:
            return {f"p{p}": 0.0 for p in percentiles}

        sorted_times = sorted(response_times)
        result = {}

        for p in percentiles:
            index = int((p / 100.0) * len(sorted_times))
            if index >= len(sorted_times):
                index = len(sorted_times) - 1
            result[f"p{p}"] = sorted_times[index]

        return result

    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        格式化持续时间

        Args:
            seconds: 秒数

        Returns:
            str: 格式化的时间字符串
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    @staticmethod
    def format_size(bytes_size: int) -> str:
        """
        格式化文件大小

        Args:
            bytes_size: 字节大小

        Returns:
            str: 格式化的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f}{unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f}TB"

    @staticmethod
    def _create_html_template(stats_data: Dict[str, Any]) -> str:
        """创建HTML报告模板"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Locust Performance Test Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .stats-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .stats-table th {{ background-color: #f2f2f2; }}
                .summary {{ display: flex; justify-content: space-between; margin: 20px 0; }}
                .summary-item {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Performance Test Report</h1>
                <p>Generated at: {timestamp}</p>
            </div>

            <div class="summary">
                <div class="summary-item">
                    <h3>Total Requests</h3>
                    <p>{stats_data.get('total_requests', 0)}</p>
                </div>
                <div class="summary-item">
                    <h3>Failed Requests</h3>
                    <p>{stats_data.get('failed_requests', 0)}</p>
                </div>
                <div class="summary-item">
                    <h3>Average Response Time</h3>
                    <p>{stats_data.get('avg_response_time', 0):.2f}ms</p>
                </div>
                <div class="summary-item">
                    <h3>RPS</h3>
                    <p>{stats_data.get('rps', 0):.2f}</p>
                </div>
            </div>

            <!-- 更多报告内容 -->
        </body>
        </html>
        """
        return html

    @staticmethod
    def _convert_to_csv_format(stats_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """转换为CSV格式"""
        # 实现统计数据到CSV格式的转换
        return []

    @staticmethod
    def _format_json_report(stats_data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化JSON报告"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": stats_data,
            "version": "1.0"
        }

    @staticmethod
    def _process_csv_stats(raw_data: List[Dict[str, str]]) -> Dict[str, Any]:
        """处理CSV统计数据"""
        # 实现CSV数据的处理逻辑
        return {}
```

## 📝 日志管理工具

### LogUtil

日志配置和管理工具。

```python
import logging
import logging.handlers
from typing import Optional

class LogUtil:
    """日志工具类"""

    @staticmethod
    def setup_logger(name: str, log_file: Optional[str] = None,
                    level: int = logging.INFO,
                    format_string: Optional[str] = None) -> logging.Logger:
        """
        设置日志记录器

        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
            level: 日志级别
            format_string: 日志格式字符串

        Returns:
            logging.Logger: 配置好的日志记录器
        """
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 默认格式
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        formatter = logging.Formatter(format_string)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件处理器
        if log_file:
            FileOperationUtil.ensure_dir(os.path.dirname(log_file))
            file_handler = logging.handlers.RotatingFileHandler(
                log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            logging.Logger: 日志记录器
        """
        return logging.getLogger(name)

    @staticmethod
    def set_log_level(logger_name: str, level: int) -> None:
        """
        设置日志级别

        Args:
            logger_name: 日志记录器名称
            level: 日志级别
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)

        for handler in logger.handlers:
            handler.setLevel(level)
```

## 🔄 集合点工具

### RendezvousUtil

用户同步和集合点工具。

```python
import threading
import time
from typing import Optional

class RendezvousUtil:
    """集合点工具类"""

    def __init__(self, name: str, expected_users: int, timeout: int = 60):
        """
        初始化集合点

        Args:
            name: 集合点名称
            expected_users: 期望的用户数
            timeout: 超时时间(秒)
        """
        self.name = name
        self.expected_users = expected_users
        self.timeout = timeout
        self.arrived_users = 0
        self.lock = threading.Lock()
        self.condition = threading.Condition(self.lock)
        self.start_time = None

    def wait(self, user_id: Optional[str] = None) -> bool:
        """
        等待集合点

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否成功通过集合点
        """
        with self.condition:
            if self.start_time is None:
                self.start_time = time.time()

            self.arrived_users += 1
            current_users = self.arrived_users

            print(f"User {user_id or 'unknown'} arrived at rendezvous '{self.name}' "
                  f"({current_users}/{self.expected_users})")

            if current_users >= self.expected_users:
                # 所有用户都到达，释放所有等待的用户
                self.condition.notify_all()
                return True
            else:
                # 等待其他用户到达
                elapsed = time.time() - self.start_time
                remaining_timeout = self.timeout - elapsed

                if remaining_timeout <= 0:
                    print(f"Rendezvous '{self.name}' timeout")
                    return False

                return self.condition.wait(timeout=remaining_timeout)

    def reset(self) -> None:
        """重置集合点"""
        with self.condition:
            self.arrived_users = 0
            self.start_time = None

    def get_status(self) -> Dict[str, Any]:
        """
        获取集合点状态

        Returns:
            Dict[str, Any]: 状态信息
        """
        with self.lock:
            elapsed = time.time() - self.start_time if self.start_time else 0
            return {
                "name": self.name,
                "expected_users": self.expected_users,
                "arrived_users": self.arrived_users,
                "elapsed_time": elapsed,
                "timeout": self.timeout,
                "is_complete": self.arrived_users >= self.expected_users
            }

# 全局集合点管理器
class RendezvousManager:
    """集合点管理器"""

    def __init__(self):
        self._rendezvous = {}
        self._lock = threading.Lock()

    def create_rendezvous(self, name: str, expected_users: int,
                         timeout: int = 60) -> RendezvousUtil:
        """
        创建集合点

        Args:
            name: 集合点名称
            expected_users: 期望用户数
            timeout: 超时时间

        Returns:
            RendezvousUtil: 集合点对象
        """
        with self._lock:
            if name in self._rendezvous:
                return self._rendezvous[name]

            rendezvous = RendezvousUtil(name, expected_users, timeout)
            self._rendezvous[name] = rendezvous
            return rendezvous

    def get_rendezvous(self, name: str) -> Optional[RendezvousUtil]:
        """
        获取集合点

        Args:
            name: 集合点名称

        Returns:
            Optional[RendezvousUtil]: 集合点对象
        """
        with self._lock:
            return self._rendezvous.get(name)

    def remove_rendezvous(self, name: str) -> bool:
        """
        移除集合点

        Args:
            name: 集合点名称

        Returns:
            bool: 移除是否成功
        """
        with self._lock:
            if name in self._rendezvous:
                del self._rendezvous[name]
                return True
            return False

# 全局实例
rendezvous_manager = RendezvousManager()
```

## 🛠️ 通用工具函数

### CommonUtil

通用工具函数集合。

```python
import random
import string
import hashlib
import uuid
from typing import Any, List, Dict

class CommonUtil:
    """通用工具类"""

    @staticmethod
    def generate_random_string(length: int = 10,
                             chars: str = string.ascii_letters + string.digits) -> str:
        """
        生成随机字符串

        Args:
            length: 字符串长度
            chars: 字符集

        Returns:
            str: 随机字符串
        """
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def generate_uuid() -> str:
        """
        生成UUID

        Returns:
            str: UUID字符串
        """
        return str(uuid.uuid4())

    @staticmethod
    def calculate_md5(text: str) -> str:
        """
        计算MD5哈希值

        Args:
            text: 输入文本

        Returns:
            str: MD5哈希值
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    @staticmethod
    def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        安全获取字典值

        Args:
            data: 字典
            key: 键名
            default: 默认值

        Returns:
            Any: 字典值或默认值
        """
        return data.get(key, default)

    @staticmethod
    def retry_on_exception(func, max_retries: int = 3, delay: float = 1.0):
        """
        异常重试装饰器

        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            delay: 重试延迟

        Returns:
            Any: 函数返回值
        """
        for attempt in range(max_retries + 1):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries:
                    raise e
                time.sleep(delay)

    @staticmethod
    def format_number(number: float, precision: int = 2) -> str:
        """
        格式化数字

        Args:
            number: 数字
            precision: 精度

        Returns:
            str: 格式化的数字字符串
        """
        return f"{number:.{precision}f}"

    @staticmethod
    def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并多个字典

        Args:
            *dicts: 字典列表

        Returns:
            Dict[str, Any]: 合并后的字典
        """
        result = {}
        for d in dicts:
            if d:
                result.update(d)
        return result
```

## 📚 使用示例

### 综合使用示例

```python
from src.utils.file_operation import FileOperationUtil
from src.utils.locust_report import LocustReportUtil
from src.utils.log_moudle import LogUtil
from src.utils.rendezvous import rendezvous_manager
from src.utils.util import CommonUtil

# 设置日志
logger = LogUtil.setup_logger("test_logger", "logs/test.log")

# 读取配置文件
config = FileOperationUtil.read_yaml("config/test_config.yaml")

# 创建集合点
rendezvous = rendezvous_manager.create_rendezvous("login_sync", 10, 30)

# 生成测试数据
test_id = CommonUtil.generate_uuid()
random_data = CommonUtil.generate_random_string(20)

# 生成报告
stats_data = {"total_requests": 1000, "failed_requests": 5}
LocustReportUtil.generate_html_report(stats_data, "reports/test_report.html")

logger.info(f"Test {test_id} completed with data: {random_data}")
```

## 📚 相关文档

- [文件操作示例](../examples/basic-examples.md) - 文件操作使用示例
- [报告生成指南](../examples/advanced-usage.md) - 报告生成详细说明
- [日志配置](../configuration/framework-config.md) - 日志系统配置
- [开发指南](../development/setup.md) - 开发环境搭建
