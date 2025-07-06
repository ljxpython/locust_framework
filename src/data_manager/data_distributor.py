"""
测试数据分发器

在分布式测试环境中分发和同步测试数据
"""

import hashlib
import json
import pickle
import socket
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from src.utils.log_moudle import logger


class DataDistributor:
    """测试数据分发器"""

    def __init__(self, node_id: str = None, is_master: bool = True):
        self.node_id = node_id or self._generate_node_id()
        self.is_master = is_master
        self.data_cache = {}  # data_key -> data
        self.data_versions = {}  # data_key -> version
        self.subscribers = {}  # data_key -> [callback_functions]
        self.distribution_log = deque(maxlen=1000)  # 分发日志
        self.lock = threading.Lock()

        # 网络配置
        self.master_host = "localhost"
        self.master_port = 8089
        self.sync_interval = 30  # 同步间隔(秒)

        # 统计信息
        self.stats = {
            "data_distributed": 0,
            "data_received": 0,
            "sync_count": 0,
            "last_sync_time": None,
        }

        # 同步线程
        self.sync_thread = None
        self.running = False

    def start(self):
        """启动分发器"""
        if self.running:
            logger.warning("数据分发器已在运行")
            return

        self.running = True

        if not self.is_master:
            # 从节点启动同步线程
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()
            logger.info(f"数据分发器已启动 (从节点: {self.node_id})")
        else:
            logger.info(f"数据分发器已启动 (主节点: {self.node_id})")

    def stop(self):
        """停止分发器"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("数据分发器已停止")

    def distribute_data(self, data_key: str, data: Any, version: str = None) -> bool:
        """分发数据"""
        try:
            with self.lock:
                # 生成版本号
                if version is None:
                    version = self._generate_version()

                # 存储数据
                self.data_cache[data_key] = data
                self.data_versions[data_key] = version

                # 记录分发日志
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "distribute",
                    "data_key": data_key,
                    "version": version,
                    "node_id": self.node_id,
                    "data_size": len(str(data)),
                }
                self.distribution_log.append(log_entry)

                # 更新统计
                self.stats["data_distributed"] += 1

                # 通知订阅者
                self._notify_subscribers(data_key, data, version)

                logger.info(f"分发数据: {data_key} (版本: {version})")
                return True

        except Exception as e:
            logger.error(f"分发数据失败 {data_key}: {e}")
            return False

    def get_data(self, data_key: str) -> Optional[Any]:
        """获取数据"""
        with self.lock:
            return self.data_cache.get(data_key)

    def get_data_version(self, data_key: str) -> Optional[str]:
        """获取数据版本"""
        with self.lock:
            return self.data_versions.get(data_key)

    def subscribe_data(self, data_key: str, callback: Callable[[str, Any, str], None]):
        """订阅数据更新"""
        with self.lock:
            if data_key not in self.subscribers:
                self.subscribers[data_key] = []
            self.subscribers[data_key].append(callback)
            logger.info(f"订阅数据更新: {data_key}")

    def unsubscribe_data(self, data_key: str, callback: Callable):
        """取消订阅数据更新"""
        with self.lock:
            if data_key in self.subscribers and callback in self.subscribers[data_key]:
                self.subscribers[data_key].remove(callback)
                logger.info(f"取消订阅数据更新: {data_key}")

    def sync_with_master(self) -> bool:
        """与主节点同步数据"""
        if self.is_master:
            logger.warning("主节点无需同步")
            return True

        try:
            # 获取主节点数据清单
            master_manifest = self._get_master_manifest()
            if not master_manifest:
                return False

            # 比较版本并同步
            sync_count = 0
            for data_key, master_version in master_manifest.items():
                local_version = self.data_versions.get(data_key)

                if local_version != master_version:
                    # 需要同步
                    data = self._fetch_data_from_master(data_key)
                    if data is not None:
                        with self.lock:
                            self.data_cache[data_key] = data
                            self.data_versions[data_key] = master_version
                            self._notify_subscribers(data_key, data, master_version)
                        sync_count += 1
                        logger.debug(f"同步数据: {data_key} (版本: {master_version})")

            # 更新统计
            self.stats["sync_count"] += 1
            self.stats["last_sync_time"] = datetime.now().isoformat()

            if sync_count > 0:
                logger.info(f"同步完成: {sync_count} 个数据项")

            return True

        except Exception as e:
            logger.error(f"同步数据失败: {e}")
            return False

    def export_data(self, output_path: str, data_keys: List[str] = None) -> bool:
        """导出数据"""
        try:
            export_data = {}

            with self.lock:
                keys_to_export = data_keys or list(self.data_cache.keys())

                for data_key in keys_to_export:
                    if data_key in self.data_cache:
                        export_data[data_key] = {
                            "data": self.data_cache[data_key],
                            "version": self.data_versions[data_key],
                            "exported_at": datetime.now().isoformat(),
                            "node_id": self.node_id,
                        }

            # 保存到文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            if output_file.suffix.lower() == ".json":
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
            else:
                # 使用pickle保存
                with open(output_file, "wb") as f:
                    pickle.dump(export_data, f)

            logger.info(f"导出数据: {len(export_data)} 项 -> {output_file}")
            return True

        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            return False

    def import_data(self, input_path: str, overwrite: bool = False) -> bool:
        """导入数据"""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                logger.error(f"导入文件不存在: {input_path}")
                return False

            # 加载数据
            if input_file.suffix.lower() == ".json":
                with open(input_file, "r", encoding="utf-8") as f:
                    import_data = json.load(f)
            else:
                # 使用pickle加载
                with open(input_file, "rb") as f:
                    import_data = pickle.load(f)

            # 导入数据
            imported_count = 0
            with self.lock:
                for data_key, data_info in import_data.items():
                    if not overwrite and data_key in self.data_cache:
                        logger.warning(f"数据已存在，跳过: {data_key}")
                        continue

                    self.data_cache[data_key] = data_info["data"]
                    self.data_versions[data_key] = data_info["version"]
                    imported_count += 1

                    # 通知订阅者
                    self._notify_subscribers(
                        data_key, data_info["data"], data_info["version"]
                    )

            logger.info(f"导入数据: {imported_count} 项")
            return True

        except Exception as e:
            logger.error(f"导入数据失败: {e}")
            return False

    def get_distribution_stats(self) -> Dict[str, Any]:
        """获取分发统计信息"""
        with self.lock:
            stats = self.stats.copy()
            stats.update(
                {
                    "node_id": self.node_id,
                    "is_master": self.is_master,
                    "cached_data_count": len(self.data_cache),
                    "subscribers_count": sum(
                        len(subs) for subs in self.subscribers.values()
                    ),
                    "running": self.running,
                }
            )
            return stats

    def get_data_manifest(self) -> Dict[str, str]:
        """获取数据清单"""
        with self.lock:
            return self.data_versions.copy()

    def clear_data(self, data_key: str = None):
        """清理数据"""
        with self.lock:
            if data_key:
                if data_key in self.data_cache:
                    del self.data_cache[data_key]
                    del self.data_versions[data_key]
                    logger.info(f"清理数据: {data_key}")
            else:
                self.data_cache.clear()
                self.data_versions.clear()
                logger.info("清理所有数据")

    def _generate_node_id(self) -> str:
        """生成节点ID"""
        hostname = socket.gethostname()
        timestamp = str(int(time.time()))
        return hashlib.md5(f"{hostname}_{timestamp}".encode()).hexdigest()[:8]

    def _generate_version(self) -> str:
        """生成版本号"""
        return str(int(time.time() * 1000))  # 毫秒时间戳

    def _notify_subscribers(self, data_key: str, data: Any, version: str):
        """通知订阅者"""
        if data_key in self.subscribers:
            for callback in self.subscribers[data_key]:
                try:
                    callback(data_key, data, version)
                except Exception as e:
                    logger.error(f"通知订阅者失败: {e}")

    def _sync_loop(self):
        """同步循环"""
        while self.running:
            try:
                self.sync_with_master()
                time.sleep(self.sync_interval)
            except Exception as e:
                logger.error(f"同步循环异常: {e}")
                time.sleep(self.sync_interval)

    def _get_master_manifest(self) -> Optional[Dict[str, str]]:
        """获取主节点数据清单"""
        # 这里应该实现与主节点的网络通信
        # 为了简化，这里返回空字典
        try:
            # TODO: 实现HTTP/TCP通信获取主节点清单
            logger.debug("获取主节点数据清单")
            return {}
        except Exception as e:
            logger.error(f"获取主节点清单失败: {e}")
            return None

    def _fetch_data_from_master(self, data_key: str) -> Optional[Any]:
        """从主节点获取数据"""
        # 这里应该实现与主节点的网络通信
        # 为了简化，这里返回None
        try:
            # TODO: 实现HTTP/TCP通信获取数据
            logger.debug(f"从主节点获取数据: {data_key}")
            return None
        except Exception as e:
            logger.error(f"从主节点获取数据失败 {data_key}: {e}")
            return None

    def create_data_snapshot(self, snapshot_name: str) -> bool:
        """创建数据快照"""
        try:
            snapshot_data = {
                "snapshot_name": snapshot_name,
                "created_at": datetime.now().isoformat(),
                "node_id": self.node_id,
                "data_cache": self.data_cache.copy(),
                "data_versions": self.data_versions.copy(),
            }

            snapshot_file = Path(f"snapshots/{snapshot_name}.snapshot")
            snapshot_file.parent.mkdir(parents=True, exist_ok=True)

            with open(snapshot_file, "wb") as f:
                pickle.dump(snapshot_data, f)

            logger.info(f"创建数据快照: {snapshot_name}")
            return True

        except Exception as e:
            logger.error(f"创建数据快照失败: {e}")
            return False

    def restore_data_snapshot(self, snapshot_name: str) -> bool:
        """恢复数据快照"""
        try:
            snapshot_file = Path(f"snapshots/{snapshot_name}.snapshot")
            if not snapshot_file.exists():
                logger.error(f"快照文件不存在: {snapshot_name}")
                return False

            with open(snapshot_file, "rb") as f:
                snapshot_data = pickle.load(f)

            with self.lock:
                self.data_cache = snapshot_data["data_cache"]
                self.data_versions = snapshot_data["data_versions"]

            logger.info(f"恢复数据快照: {snapshot_name}")
            return True

        except Exception as e:
            logger.error(f"恢复数据快照失败: {e}")
            return False
