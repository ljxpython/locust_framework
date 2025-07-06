"""
告警管理器

管理告警规则、告警历史和告警策略
"""

import json
import threading
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.utils.log_moudle import logger


@dataclass
class Alert:
    """告警信息"""

    id: str
    rule_name: str
    metric_name: str
    current_value: float
    threshold: float
    condition: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    status: str  # 'active', 'resolved', 'suppressed'
    created_at: datetime
    resolved_at: Optional[datetime] = None
    message: str = ""
    tags: Dict[str, str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class AlertPolicy:
    """告警策略"""

    name: str
    conditions: List[str]  # 触发条件
    cooldown_minutes: int = 5  # 冷却时间
    max_alerts_per_hour: int = 10  # 每小时最大告警数
    escalation_rules: List[Dict] = None  # 升级规则
    notification_channels: List[str] = None  # 通知渠道

    def __post_init__(self):
        if self.escalation_rules is None:
            self.escalation_rules = []
        if self.notification_channels is None:
            self.notification_channels = []


class AlertManager:
    """告警管理器"""

    def __init__(self, storage_path: str = "alerts"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.active_alerts = {}  # alert_id -> Alert
        self.alert_history = []
        self.alert_policies = {}  # policy_name -> AlertPolicy
        self.alert_counters = {}  # 告警计数器
        self.notification_callbacks = []
        self.lock = threading.Lock()

        # 加载历史数据
        self._load_alert_history()
        self._load_alert_policies()

    def create_alert(
        self,
        rule_name: str,
        metric_name: str,
        current_value: float,
        threshold: float,
        condition: str,
        severity: str = "medium",
        message: str = "",
        tags: Dict[str, str] = None,
    ) -> Alert:
        """创建告警"""
        alert_id = (
            f"{rule_name}_{metric_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        alert = Alert(
            id=alert_id,
            rule_name=rule_name,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold,
            condition=condition,
            severity=severity,
            status="active",
            created_at=datetime.now(),
            message=message
            or self._generate_alert_message(
                rule_name, metric_name, current_value, threshold, condition
            ),
            tags=tags or {},
        )

        with self.lock:
            # 检查是否应该抑制告警
            if self._should_suppress_alert(alert):
                alert.status = "suppressed"
                logger.info(f"告警被抑制: {alert.id}")
                return alert

            # 添加到活跃告警
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)

            # 更新计数器
            self._update_alert_counter(alert)

            logger.warning(f"创建告警: {alert.id} - {alert.message}")

            # 触发通知
            self._trigger_notifications(alert)

        return alert

    def resolve_alert(self, alert_id: str, resolution_message: str = ""):
        """解决告警"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = "resolved"
                alert.resolved_at = datetime.now()
                if resolution_message:
                    alert.message += f" | 解决: {resolution_message}"

                del self.active_alerts[alert_id]
                logger.info(f"告警已解决: {alert_id}")

                # 触发解决通知
                self._trigger_resolution_notifications(alert)

    def suppress_alert(self, alert_id: str, reason: str = ""):
        """抑制告警"""
        with self.lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.status = "suppressed"
                if reason:
                    alert.message += f" | 抑制原因: {reason}"

                logger.info(f"告警已抑制: {alert_id}")

    def get_active_alerts(
        self, severity: str = None, metric_name: str = None
    ) -> List[Alert]:
        """获取活跃告警"""
        with self.lock:
            alerts = list(self.active_alerts.values())

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

            if metric_name:
                alerts = [a for a in alerts if a.metric_name == metric_name]

            return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    def get_alert_history(self, hours: int = 24, severity: str = None) -> List[Alert]:
        """获取告警历史"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.lock:
            alerts = [a for a in self.alert_history if a.created_at > cutoff_time]

            if severity:
                alerts = [a for a in alerts if a.severity == severity]

            return sorted(alerts, key=lambda x: x.created_at, reverse=True)

    def add_alert_policy(self, policy: AlertPolicy):
        """添加告警策略"""
        self.alert_policies[policy.name] = policy
        logger.info(f"添加告警策略: {policy.name}")
        self._save_alert_policies()

    def remove_alert_policy(self, policy_name: str):
        """移除告警策略"""
        if policy_name in self.alert_policies:
            del self.alert_policies[policy_name]
            logger.info(f"移除告警策略: {policy_name}")
            self._save_alert_policies()

    def add_notification_callback(self, callback: Callable):
        """添加通知回调"""
        self.notification_callbacks.append(callback)

    def get_alert_statistics(self, hours: int = 24) -> Dict:
        """获取告警统计"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.lock:
            recent_alerts = [
                a for a in self.alert_history if a.created_at > cutoff_time
            ]

            stats = {
                "total_alerts": len(recent_alerts),
                "active_alerts": len(self.active_alerts),
                "resolved_alerts": len(
                    [a for a in recent_alerts if a.status == "resolved"]
                ),
                "suppressed_alerts": len(
                    [a for a in recent_alerts if a.status == "suppressed"]
                ),
                "by_severity": {},
                "by_metric": {},
                "by_hour": {},
            }

            # 按严重程度统计
            for alert in recent_alerts:
                severity = alert.severity
                stats["by_severity"][severity] = (
                    stats["by_severity"].get(severity, 0) + 1
                )

            # 按指标统计
            for alert in recent_alerts:
                metric = alert.metric_name
                stats["by_metric"][metric] = stats["by_metric"].get(metric, 0) + 1

            # 按小时统计
            for alert in recent_alerts:
                hour_key = alert.created_at.strftime("%Y-%m-%d %H:00")
                stats["by_hour"][hour_key] = stats["by_hour"].get(hour_key, 0) + 1

            return stats

    def cleanup_old_alerts(self, days: int = 7):
        """清理旧告警"""
        cutoff_time = datetime.now() - timedelta(days=days)

        with self.lock:
            original_count = len(self.alert_history)
            self.alert_history = [
                a for a in self.alert_history if a.created_at > cutoff_time
            ]
            cleaned_count = original_count - len(self.alert_history)

            if cleaned_count > 0:
                logger.info(f"清理了 {cleaned_count} 条旧告警记录")
                self._save_alert_history()

    def _should_suppress_alert(self, alert: Alert) -> bool:
        """判断是否应该抑制告警"""
        # 检查冷却时间
        for existing_alert in self.active_alerts.values():
            if (
                existing_alert.rule_name == alert.rule_name
                and existing_alert.metric_name == alert.metric_name
            ):
                time_diff = (
                    alert.created_at - existing_alert.created_at
                ).total_seconds()
                if time_diff < 300:  # 5分钟冷却时间
                    return True

        # 检查频率限制
        hour_key = alert.created_at.strftime("%Y-%m-%d %H")
        counter_key = f"{alert.rule_name}_{hour_key}"
        current_count = self.alert_counters.get(counter_key, 0)

        if current_count >= 10:  # 每小时最多10个相同告警
            return True

        return False

    def _update_alert_counter(self, alert: Alert):
        """更新告警计数器"""
        hour_key = alert.created_at.strftime("%Y-%m-%d %H")
        counter_key = f"{alert.rule_name}_{hour_key}"
        self.alert_counters[counter_key] = self.alert_counters.get(counter_key, 0) + 1

    def _generate_alert_message(
        self,
        rule_name: str,
        metric_name: str,
        current_value: float,
        threshold: float,
        condition: str,
    ) -> str:
        """生成告警消息"""
        condition_text = {
            "gt": "超过",
            "lt": "低于",
            "gte": "大于等于",
            "lte": "小于等于",
            "eq": "等于",
        }.get(condition, condition)

        return f"告警规则 '{rule_name}' 触发: 指标 '{metric_name}' 当前值 {current_value} {condition_text} 阈值 {threshold}"

    def _trigger_notifications(self, alert: Alert):
        """触发通知"""
        for callback in self.notification_callbacks:
            try:
                callback(alert, "created")
            except Exception as e:
                logger.error(f"执行告警通知回调异常: {e}")

    def _trigger_resolution_notifications(self, alert: Alert):
        """触发解决通知"""
        for callback in self.notification_callbacks:
            try:
                callback(alert, "resolved")
            except Exception as e:
                logger.error(f"执行告警解决通知回调异常: {e}")

    def _load_alert_history(self):
        """加载告警历史"""
        history_file = self.storage_path / "alert_history.json"
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.alert_history = [
                        Alert(
                            id=item["id"],
                            rule_name=item["rule_name"],
                            metric_name=item["metric_name"],
                            current_value=item["current_value"],
                            threshold=item["threshold"],
                            condition=item["condition"],
                            severity=item["severity"],
                            status=item["status"],
                            created_at=datetime.fromisoformat(item["created_at"]),
                            resolved_at=(
                                datetime.fromisoformat(item["resolved_at"])
                                if item.get("resolved_at")
                                else None
                            ),
                            message=item.get("message", ""),
                            tags=item.get("tags", {}),
                        )
                        for item in data
                    ]
                logger.info(f"加载了 {len(self.alert_history)} 条告警历史")
            except Exception as e:
                logger.error(f"加载告警历史失败: {e}")

    def _save_alert_history(self):
        """保存告警历史"""
        history_file = self.storage_path / "alert_history.json"
        try:
            data = []
            for alert in self.alert_history:
                item = asdict(alert)
                item["created_at"] = alert.created_at.isoformat()
                if alert.resolved_at:
                    item["resolved_at"] = alert.resolved_at.isoformat()
                data.append(item)

            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存告警历史失败: {e}")

    def _load_alert_policies(self):
        """加载告警策略"""
        policies_file = self.storage_path / "alert_policies.json"
        if policies_file.exists():
            try:
                with open(policies_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for name, policy_data in data.items():
                        self.alert_policies[name] = AlertPolicy(**policy_data)
                logger.info(f"加载了 {len(self.alert_policies)} 个告警策略")
            except Exception as e:
                logger.error(f"加载告警策略失败: {e}")

    def _save_alert_policies(self):
        """保存告警策略"""
        policies_file = self.storage_path / "alert_policies.json"
        try:
            data = {
                name: asdict(policy) for name, policy in self.alert_policies.items()
            }
            with open(policies_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存告警策略失败: {e}")

    def export_alerts(self, format: str = "json", hours: int = 24) -> str:
        """导出告警数据"""
        alerts = self.get_alert_history(hours)

        if format == "json":
            data = []
            for alert in alerts:
                item = asdict(alert)
                item["created_at"] = alert.created_at.isoformat()
                if alert.resolved_at:
                    item["resolved_at"] = alert.resolved_at.isoformat()
                data.append(item)
            return json.dumps(data, ensure_ascii=False, indent=2)

        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(
                [
                    "ID",
                    "规则名称",
                    "指标名称",
                    "当前值",
                    "阈值",
                    "条件",
                    "严重程度",
                    "状态",
                    "创建时间",
                    "解决时间",
                    "消息",
                ]
            )

            # 写入数据
            for alert in alerts:
                writer.writerow(
                    [
                        alert.id,
                        alert.rule_name,
                        alert.metric_name,
                        alert.current_value,
                        alert.threshold,
                        alert.condition,
                        alert.severity,
                        alert.status,
                        alert.created_at.isoformat(),
                        alert.resolved_at.isoformat() if alert.resolved_at else "",
                        alert.message,
                    ]
                )

            return output.getvalue()

        else:
            raise ValueError(f"不支持的导出格式: {format}")
