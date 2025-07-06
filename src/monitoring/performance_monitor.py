"""
性能监控器

实时监控系统性能指标并触发告警
"""

import queue
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from src.utils.log_moudle import logger


@dataclass
class MetricData:
    """指标数据"""

    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class AlertRule:
    """告警规则"""

    name: str
    metric_name: str
    condition: str  # 'gt', 'lt', 'eq', 'gte', 'lte'
    threshold: float
    duration: int = 60  # 持续时间(秒)
    enabled: bool = True
    callback: Optional[Callable] = None


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.metrics_queue = queue.Queue()
        self.alert_rules = []
        self.metric_history = {}
        self.is_running = False
        self.monitor_thread = None
        self.alert_callbacks = []

        # 性能阈值配置
        self.default_thresholds = {
            "response_time_p95": 1000,  # ms
            "response_time_p99": 2000,  # ms
            "error_rate": 0.05,  # 5%
            "throughput": 10,  # TPS
            "cpu_usage": 80,  # %
            "memory_usage": 80,  # %
        }

    def add_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """添加指标数据"""
        metric = MetricData(
            name=name, value=value, timestamp=datetime.now(), tags=tags or {}
        )
        self.metrics_queue.put(metric)

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules.append(rule)
        logger.info(f"添加告警规则: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        self.alert_rules = [rule for rule in self.alert_rules if rule.name != rule_name]
        logger.info(f"移除告警规则: {rule_name}")

    def add_alert_callback(self, callback: Callable):
        """添加告警回调函数"""
        self.alert_callbacks.append(callback)

    def start_monitoring(self):
        """开始监控"""
        if self.is_running:
            logger.warning("监控已在运行中")
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("性能监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("性能监控已停止")

    def _monitor_loop(self):
        """监控主循环"""
        while self.is_running:
            try:
                # 处理指标数据
                self._process_metrics()

                # 检查告警规则
                self._check_alert_rules()

                # 清理过期数据
                self._cleanup_old_data()

                time.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(self.check_interval)

    def _process_metrics(self):
        """处理指标数据"""
        while not self.metrics_queue.empty():
            try:
                metric = self.metrics_queue.get_nowait()

                # 存储到历史数据
                if metric.name not in self.metric_history:
                    self.metric_history[metric.name] = []

                self.metric_history[metric.name].append(metric)

                # 限制历史数据大小
                if len(self.metric_history[metric.name]) > 1000:
                    self.metric_history[metric.name] = self.metric_history[metric.name][
                        -500:
                    ]

            except queue.Empty:
                break
            except Exception as e:
                logger.error(f"处理指标数据异常: {e}")

    def _check_alert_rules(self):
        """检查告警规则"""
        current_time = datetime.now()

        for rule in self.alert_rules:
            if not rule.enabled:
                continue

            try:
                # 获取指标历史数据
                if rule.metric_name not in self.metric_history:
                    continue

                metrics = self.metric_history[rule.metric_name]
                if not metrics:
                    continue

                # 检查是否满足告警条件
                if self._evaluate_alert_condition(rule, metrics, current_time):
                    self._trigger_alert(rule, metrics[-1])

            except Exception as e:
                logger.error(f"检查告警规则 {rule.name} 异常: {e}")

    def _evaluate_alert_condition(
        self, rule: AlertRule, metrics: List[MetricData], current_time: datetime
    ) -> bool:
        """评估告警条件"""
        # 获取指定时间范围内的数据
        duration_start = current_time - timedelta(seconds=rule.duration)
        recent_metrics = [m for m in metrics if m.timestamp >= duration_start]

        if not recent_metrics:
            return False

        # 计算平均值
        avg_value = sum(m.value for m in recent_metrics) / len(recent_metrics)

        # 评估条件
        if rule.condition == "gt":
            return avg_value > rule.threshold
        elif rule.condition == "lt":
            return avg_value < rule.threshold
        elif rule.condition == "gte":
            return avg_value >= rule.threshold
        elif rule.condition == "lte":
            return avg_value <= rule.threshold
        elif rule.condition == "eq":
            return abs(avg_value - rule.threshold) < 0.001

        return False

    def _trigger_alert(self, rule: AlertRule, metric: MetricData):
        """触发告警"""
        alert_info = {
            "rule_name": rule.name,
            "metric_name": rule.metric_name,
            "current_value": metric.value,
            "threshold": rule.threshold,
            "condition": rule.condition,
            "timestamp": metric.timestamp.isoformat(),
            "tags": metric.tags,
        }

        logger.warning(
            f"触发告警: {rule.name}, 当前值: {metric.value}, 阈值: {rule.threshold}"
        )

        # 执行规则回调
        if rule.callback:
            try:
                rule.callback(alert_info)
            except Exception as e:
                logger.error(f"执行告警规则回调异常: {e}")

        # 执行全局回调
        for callback in self.alert_callbacks:
            try:
                callback(alert_info)
            except Exception as e:
                logger.error(f"执行告警回调异常: {e}")

    def _cleanup_old_data(self):
        """清理过期数据"""
        cutoff_time = datetime.now() - timedelta(hours=1)

        for metric_name in self.metric_history:
            self.metric_history[metric_name] = [
                m for m in self.metric_history[metric_name] if m.timestamp > cutoff_time
            ]

    def get_metric_stats(self, metric_name: str, duration_minutes: int = 10) -> Dict:
        """获取指标统计信息"""
        if metric_name not in self.metric_history:
            return {}

        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_metrics = [
            m for m in self.metric_history[metric_name] if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return {}

        values = [m.value for m in recent_metrics]

        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1],
            "timestamp_range": {
                "start": recent_metrics[0].timestamp.isoformat(),
                "end": recent_metrics[-1].timestamp.isoformat(),
            },
        }

    def get_all_metrics_summary(self) -> Dict:
        """获取所有指标摘要"""
        summary = {}
        for metric_name in self.metric_history:
            summary[metric_name] = self.get_metric_stats(metric_name)
        return summary

    def setup_default_rules(self):
        """设置默认告警规则"""
        default_rules = [
            AlertRule(
                name="响应时间P95过高",
                metric_name="response_time_p95",
                condition="gt",
                threshold=self.default_thresholds["response_time_p95"],
                duration=30,
            ),
            AlertRule(
                name="错误率过高",
                metric_name="error_rate",
                condition="gt",
                threshold=self.default_thresholds["error_rate"],
                duration=60,
            ),
            AlertRule(
                name="吞吐量过低",
                metric_name="throughput",
                condition="lt",
                threshold=self.default_thresholds["throughput"],
                duration=120,
            ),
        ]

        for rule in default_rules:
            self.add_alert_rule(rule)

        logger.info("已设置默认告警规则")

    def update_thresholds(self, **thresholds):
        """更新性能阈值"""
        self.default_thresholds.update(thresholds)
        logger.info(f"更新性能阈值: {thresholds}")

    def export_metrics(
        self, metric_name: str = None, duration_hours: int = 1
    ) -> List[Dict]:
        """导出指标数据"""
        cutoff_time = datetime.now() - timedelta(hours=duration_hours)
        exported_data = []

        metrics_to_export = [metric_name] if metric_name else self.metric_history.keys()

        for name in metrics_to_export:
            if name not in self.metric_history:
                continue

            for metric in self.metric_history[name]:
                if metric.timestamp > cutoff_time:
                    exported_data.append(
                        {
                            "metric_name": metric.name,
                            "value": metric.value,
                            "timestamp": metric.timestamp.isoformat(),
                            "tags": metric.tags,
                        }
                    )

        return exported_data
