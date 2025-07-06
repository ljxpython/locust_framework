"""
测试数据提供器

管理和提供测试数据，支持多种数据源和分发策略
"""

import csv
import json
import random
import sqlite3
import threading
from abc import ABC, abstractmethod
from collections import deque
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from src.utils.log_moudle import logger


class DataSource(ABC):
    """数据源抽象基类"""

    @abstractmethod
    def load_data(self) -> List[Dict]:
        """加载数据"""
        pass

    @abstractmethod
    def get_data_count(self) -> int:
        """获取数据总数"""
        pass


class FileDataSource(DataSource):
    """文件数据源"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._data = None
        self._load_data()

    def _load_data(self):
        """加载文件数据"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.file_path}")

        try:
            if self.file_path.suffix.lower() == ".json":
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            elif self.file_path.suffix.lower() == ".csv":
                self._data = []
                with open(self.file_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # 尝试解析JSON字段
                        processed_row = {}
                        for key, value in row.items():
                            try:
                                processed_row[key] = json.loads(value)
                            except (json.JSONDecodeError, TypeError):
                                processed_row[key] = value
                        self._data.append(processed_row)
            else:
                raise ValueError(f"不支持的文件格式: {self.file_path.suffix}")

            logger.info(f"从文件加载了 {len(self._data)} 条数据: {self.file_path}")

        except Exception as e:
            logger.error(f"加载数据文件失败: {e}")
            raise

    def load_data(self) -> List[Dict]:
        """获取数据"""
        return self._data.copy() if self._data else []

    def get_data_count(self) -> int:
        """获取数据总数"""
        return len(self._data) if self._data else 0


class DatabaseDataSource(DataSource):
    """数据库数据源"""

    def __init__(self, db_path: str, table_name: str, query: str = None):
        self.db_path = db_path
        self.table_name = table_name
        self.query = query or f"SELECT * FROM {table_name}"
        self._data = None
        self._load_data()

    def _load_data(self):
        """从数据库加载数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
            cursor = conn.cursor()

            cursor.execute(self.query)
            rows = cursor.fetchall()

            self._data = [dict(row) for row in rows]

            conn.close()
            logger.info(f"从数据库加载了 {len(self._data)} 条数据")

        except Exception as e:
            logger.error(f"从数据库加载数据失败: {e}")
            raise

    def load_data(self) -> List[Dict]:
        """获取数据"""
        return self._data.copy() if self._data else []

    def get_data_count(self) -> int:
        """获取数据总数"""
        return len(self._data) if self._data else 0


class MemoryDataSource(DataSource):
    """内存数据源"""

    def __init__(self, data: List[Dict]):
        self._data = data.copy() if data else []

    def load_data(self) -> List[Dict]:
        """获取数据"""
        return self._data.copy()

    def get_data_count(self) -> int:
        """获取数据总数"""
        return len(self._data)

    def add_data(self, data: Union[Dict, List[Dict]]):
        """添加数据"""
        if isinstance(data, dict):
            self._data.append(data)
        elif isinstance(data, list):
            self._data.extend(data)
        else:
            raise ValueError("数据必须是字典或字典列表")

    def clear_data(self):
        """清空数据"""
        self._data.clear()


class DataProvider:
    """测试数据提供器"""

    def __init__(self, name: str):
        self.name = name
        self.data_sources = {}  # source_name -> DataSource
        self.current_data = {}  # source_name -> current_data
        self.data_iterators = {}  # source_name -> iterator
        self.distribution_strategy = "round_robin"  # 分发策略
        self.lock = threading.Lock()

        # 统计信息
        self.access_count = {}  # source_name -> count
        self.last_access_time = {}  # source_name -> timestamp

    def add_data_source(self, source_name: str, data_source: DataSource):
        """添加数据源"""
        with self.lock:
            self.data_sources[source_name] = data_source
            self.current_data[source_name] = data_source.load_data()
            self.access_count[source_name] = 0

            # 初始化迭代器
            self._init_iterator(source_name)

            logger.info(
                f"添加数据源: {source_name}, 数据量: {data_source.get_data_count()}"
            )

    def remove_data_source(self, source_name: str):
        """移除数据源"""
        with self.lock:
            if source_name in self.data_sources:
                del self.data_sources[source_name]
                del self.current_data[source_name]
                del self.data_iterators[source_name]
                del self.access_count[source_name]
                if source_name in self.last_access_time:
                    del self.last_access_time[source_name]

                logger.info(f"移除数据源: {source_name}")

    def get_data(self, source_name: str, count: int = 1) -> List[Dict]:
        """获取指定数量的数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        with self.lock:
            data = []
            iterator = self.data_iterators[source_name]

            for _ in range(count):
                try:
                    item = next(iterator)
                    data.append(item)
                except StopIteration:
                    # 重新初始化迭代器
                    self._init_iterator(source_name)
                    iterator = self.data_iterators[source_name]
                    try:
                        item = next(iterator)
                        data.append(item)
                    except StopIteration:
                        # 数据源为空
                        break

            # 更新统计信息
            self.access_count[source_name] += len(data)
            self.last_access_time[source_name] = threading.current_thread().ident

            return data

    def get_random_data(self, source_name: str, count: int = 1) -> List[Dict]:
        """随机获取数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        with self.lock:
            source_data = self.current_data[source_name]
            if not source_data:
                return []

            # 随机选择数据
            if count >= len(source_data):
                selected_data = source_data.copy()
            else:
                selected_data = random.sample(source_data, count)

            # 更新统计信息
            self.access_count[source_name] += len(selected_data)

            return selected_data

    def get_all_data(self, source_name: str) -> List[Dict]:
        """获取所有数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        return self.current_data[source_name].copy()

    def reload_data_source(self, source_name: str):
        """重新加载数据源"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        with self.lock:
            data_source = self.data_sources[source_name]
            self.current_data[source_name] = data_source.load_data()
            self._init_iterator(source_name)

            logger.info(f"重新加载数据源: {source_name}")

    def set_distribution_strategy(self, strategy: str):
        """设置分发策略"""
        valid_strategies = ["round_robin", "random", "sequential"]
        if strategy not in valid_strategies:
            raise ValueError(
                f"无效的分发策略: {strategy}, 支持的策略: {valid_strategies}"
            )

        self.distribution_strategy = strategy

        # 重新初始化所有迭代器
        with self.lock:
            for source_name in self.data_sources:
                self._init_iterator(source_name)

        logger.info(f"设置分发策略: {strategy}")

    def _init_iterator(self, source_name: str):
        """初始化数据迭代器"""
        data = self.current_data[source_name]

        if self.distribution_strategy == "round_robin":
            # 循环迭代器
            def round_robin_iterator():
                while True:
                    for item in data:
                        yield item

            self.data_iterators[source_name] = round_robin_iterator()

        elif self.distribution_strategy == "random":
            # 随机迭代器
            def random_iterator():
                while True:
                    if data:
                        yield random.choice(data)

            self.data_iterators[source_name] = random_iterator()

        elif self.distribution_strategy == "sequential":
            # 顺序迭代器（一次性）
            self.data_iterators[source_name] = iter(data)

    def get_data_statistics(self) -> Dict[str, Dict]:
        """获取数据统计信息"""
        stats = {}

        for source_name in self.data_sources:
            stats[source_name] = {
                "total_count": len(self.current_data[source_name]),
                "access_count": self.access_count.get(source_name, 0),
                "last_access_thread": self.last_access_time.get(source_name),
                "data_source_type": type(self.data_sources[source_name]).__name__,
            }

        return stats

    def filter_data(self, source_name: str, filter_func: callable) -> List[Dict]:
        """过滤数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        source_data = self.current_data[source_name]
        filtered_data = [item for item in source_data if filter_func(item)]

        logger.info(
            f"过滤数据源 {source_name}: {len(source_data)} -> {len(filtered_data)}"
        )
        return filtered_data

    def search_data(self, source_name: str, search_criteria: Dict) -> List[Dict]:
        """搜索数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        source_data = self.current_data[source_name]
        results = []

        for item in source_data:
            match = True
            for key, value in search_criteria.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                results.append(item)

        logger.info(f"搜索数据源 {source_name}: 找到 {len(results)} 条匹配记录")
        return results

    def create_data_pool(self, pool_name: str, source_configs: List[Dict]):
        """创建数据池"""
        pool_data = []

        for config in source_configs:
            source_name = config["source_name"]
            count = config.get("count", 10)
            strategy = config.get("strategy", "random")

            if source_name not in self.data_sources:
                logger.warning(f"数据源不存在: {source_name}")
                continue

            if strategy == "random":
                data = self.get_random_data(source_name, count)
            else:
                data = self.get_data(source_name, count)

            pool_data.extend(data)

        # 创建内存数据源
        pool_source = MemoryDataSource(pool_data)
        self.add_data_source(pool_name, pool_source)

        logger.info(f"创建数据池 {pool_name}: {len(pool_data)} 条数据")
        return pool_data

    def export_data(self, source_name: str, output_path: str, format: str = "json"):
        """导出数据"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        data = self.current_data[source_name]
        output_file = Path(output_path)

        try:
            if format.lower() == "json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif format.lower() == "csv":
                if not data:
                    logger.warning("没有数据可导出")
                    return

                with open(output_file, "w", newline="", encoding="utf-8") as f:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()

                    for row in data:
                        # 处理嵌套对象
                        processed_row = {}
                        for key, value in row.items():
                            if isinstance(value, (dict, list)):
                                processed_row[key] = json.dumps(
                                    value, ensure_ascii=False
                                )
                            else:
                                processed_row[key] = value
                        writer.writerow(processed_row)
            else:
                raise ValueError(f"不支持的导出格式: {format}")

            logger.info(f"数据已导出到: {output_file}")

        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            raise

    def get_data_sample(self, source_name: str, sample_size: int = 5) -> List[Dict]:
        """获取数据样本"""
        if source_name not in self.data_sources:
            raise ValueError(f"数据源不存在: {source_name}")

        source_data = self.current_data[source_name]
        if not source_data:
            return []

        sample_size = min(sample_size, len(source_data))
        return random.sample(source_data, sample_size)
