"""
通知服务

统一管理各种通知渠道，提供统一的通知接口
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from conf.config import settings
from src.utils.log_moudle import logger
from src.utils.robot import (
    DingTalkNotification,
    EmailNotification,
    FeishuNotification,
    NotificationChannel,
    WeChatWorkNotification,
)


class NotificationService:
    """通知服务"""

    def __init__(self):
        self.channels = {}  # channel_name -> NotificationChannel
        self.default_channels = []  # 默认通知渠道
        self.message_templates = {}  # 消息模板

        # 初始化默认模板
        self._init_default_templates()

        # 从配置加载通知渠道
        self._load_channels_from_config()

    def add_channel(
        self, name: str, channel: NotificationChannel, is_default: bool = False
    ):
        """添加通知渠道"""
        self.channels[name] = channel
        if is_default and name not in self.default_channels:
            self.default_channels.append(name)
        logger.info(f"添加通知渠道: {name}")

    def remove_channel(self, name: str):
        """移除通知渠道"""
        if name in self.channels:
            del self.channels[name]
            if name in self.default_channels:
                self.default_channels.remove(name)
            logger.info(f"移除通知渠道: {name}")

    def send_notification(
        self, message: str, channels: List[str] = None, template: str = None, **kwargs
    ) -> Dict[str, bool]:
        """发送通知"""
        # 使用指定渠道或默认渠道
        target_channels = channels or self.default_channels

        # 应用消息模板
        if template and template in self.message_templates:
            message = self._apply_template(template, message, **kwargs)

        results = {}

        for channel_name in target_channels:
            if channel_name not in self.channels:
                logger.warning(f"通知渠道不存在: {channel_name}")
                results[channel_name] = False
                continue

            try:
                channel = self.channels[channel_name]
                success = channel.send_message(message, **kwargs)
                results[channel_name] = success

                if success:
                    logger.info(f"通知发送成功: {channel_name}")
                else:
                    logger.error(f"通知发送失败: {channel_name}")

            except Exception as e:
                logger.error(f"发送通知异常 {channel_name}: {e}")
                results[channel_name] = False

        return results

    def send_alert_notification(
        self, alert_info: Dict, action: str = "created"
    ) -> Dict[str, bool]:
        """发送告警通知"""
        if action == "created":
            template = "alert_created"
            title = "🚨 性能告警"
        elif action == "resolved":
            template = "alert_resolved"
            title = "✅ 告警解决"
        else:
            template = "alert_general"
            title = "📊 告警通知"

        # 构建消息内容
        message_data = {
            "title": title,
            "alert_info": alert_info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 根据告警严重程度选择通知渠道
        severity = alert_info.get("severity", "medium")
        channels = self._get_channels_by_severity(severity)

        return self.send_notification(
            message="",  # 消息内容由模板生成
            channels=channels,
            template=template,
            **message_data,
        )

    def send_performance_report(
        self, report_data: Dict, channels: List[str] = None
    ) -> Dict[str, bool]:
        """发送性能报告通知"""
        message_data = {
            "title": "📈 性能测试报告",
            "report_data": report_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return self.send_notification(
            message="", channels=channels, template="performance_report", **message_data
        )

    def send_test_completion(
        self, test_info: Dict, channels: List[str] = None
    ) -> Dict[str, bool]:
        """发送测试完成通知"""
        message_data = {
            "title": "🎯 性能测试完成",
            "test_info": test_info,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return self.send_notification(
            message="", channels=channels, template="test_completion", **message_data
        )

    def add_message_template(self, name: str, template: str):
        """添加消息模板"""
        self.message_templates[name] = template
        logger.info(f"添加消息模板: {name}")

    def _init_default_templates(self):
        """初始化默认消息模板"""
        self.message_templates = {
            "alert_created": """🚨 **性能告警触发**

**告警规则:** {alert_info[rule_name]}
**指标名称:** {alert_info[metric_name]}
**当前值:** {alert_info[current_value]}
**阈值:** {alert_info[threshold]}
**触发时间:** {timestamp}

请及时关注系统性能状况！""",
            "alert_resolved": """✅ **告警已解决**

**告警规则:** {alert_info[rule_name]}
**指标名称:** {alert_info[metric_name]}
**解决时间:** {timestamp}

系统性能已恢复正常。""",
            "performance_report": """📈 **性能测试报告**

**测试时间:** {timestamp}
**综合评分:** {report_data[overall_grade]}

**响应时间:**
- 平均: {report_data[response_time][mean]:.2f}ms
- P95: {report_data[response_time][p95]:.2f}ms

**吞吐量:**
- 平均TPS: {report_data[throughput][avg_tps]:.2f}
- 最大TPS: {report_data[throughput][max_tps]:.2f}

**错误率:** {report_data[error_rate][error_percentage]:.2f}%

详细报告请查看测试平台。""",
            "test_completion": """🎯 **性能测试完成**

**测试名称:** {test_info[name]}
**测试时长:** {test_info[duration]}
**并发用户:** {test_info[users]}
**完成时间:** {timestamp}

测试已成功完成，请查看详细报告。""",
            "system_status": """📊 **系统状态通知**

**状态:** {status}
**时间:** {timestamp}
**详情:** {details}""",
            "alert_general": """⚠️ **系统告警**

**告警内容:** {alert_info[message]}
**时间:** {timestamp}""",
        }

    def _apply_template(self, template_name: str, message: str, **kwargs) -> str:
        """应用消息模板"""
        try:
            template = self.message_templates[template_name]

            # 如果message为空，则完全使用模板
            if not message.strip():
                return template.format(**kwargs)
            else:
                # 否则将message作为额外内容添加
                formatted_template = template.format(**kwargs)
                return f"{formatted_template}\n\n{message}"

        except KeyError as e:
            logger.error(f"消息模板不存在: {template_name}")
            return message
        except Exception as e:
            logger.error(f"应用消息模板异常: {e}")
            return message

    def _get_channels_by_severity(self, severity: str) -> List[str]:
        """根据告警严重程度获取通知渠道"""
        # 可以根据严重程度配置不同的通知渠道
        if severity == "critical":
            # 严重告警使用所有渠道
            return list(self.channels.keys())
        elif severity == "high":
            # 高级告警使用主要渠道
            return [
                name
                for name in self.channels.keys()
                if name in ["feishu", "dingtalk", "email"]
            ]
        elif severity == "medium":
            # 中级告警使用即时通讯渠道
            return [
                name for name in self.channels.keys() if name in ["feishu", "dingtalk"]
            ]
        else:
            # 低级告警使用默认渠道
            return self.default_channels

    def _load_channels_from_config(self):
        """从配置文件加载通知渠道"""
        try:
            # 飞书配置
            if hasattr(settings, "notification") and hasattr(
                settings.notification, "feishu"
            ):
                feishu_config = settings.notification.feishu
                if feishu_config.get("enabled", False) and feishu_config.get(
                    "webhook_url"
                ):
                    feishu_channel = FeishuNotification(feishu_config["webhook_url"])
                    self.add_channel(
                        "feishu", feishu_channel, feishu_config.get("default", False)
                    )

            # 钉钉配置
            if hasattr(settings, "notification") and hasattr(
                settings.notification, "dingtalk"
            ):
                dingtalk_config = settings.notification.dingtalk
                if dingtalk_config.get("enabled", False) and dingtalk_config.get(
                    "webhook_url"
                ):
                    dingtalk_channel = DingTalkNotification(
                        dingtalk_config["webhook_url"], dingtalk_config.get("secret")
                    )
                    self.add_channel(
                        "dingtalk",
                        dingtalk_channel,
                        dingtalk_config.get("default", False),
                    )

            # 邮件配置
            if hasattr(settings, "notification") and hasattr(
                settings.notification, "email"
            ):
                email_config = settings.notification.email
                if email_config.get("enabled", False):
                    email_channel = EmailNotification(
                        email_config["smtp_server"],
                        email_config["smtp_port"],
                        email_config["username"],
                        email_config["password"],
                        email_config.get("use_tls", True),
                    )
                    self.add_channel(
                        "email", email_channel, email_config.get("default", False)
                    )

            # 企业微信配置
            if hasattr(settings, "notification") and hasattr(
                settings.notification, "wechat_work"
            ):
                wechat_config = settings.notification.wechat_work
                if wechat_config.get("enabled", False) and wechat_config.get(
                    "webhook_url"
                ):
                    wechat_channel = WeChatWorkNotification(
                        wechat_config["webhook_url"]
                    )
                    self.add_channel(
                        "wechat_work",
                        wechat_channel,
                        wechat_config.get("default", False),
                    )

            logger.info(f"从配置加载了 {len(self.channels)} 个通知渠道")

        except Exception as e:
            logger.error(f"加载通知渠道配置异常: {e}")

    def test_channels(self, channels: List[str] = None) -> Dict[str, bool]:
        """测试通知渠道"""
        test_message = (
            f"🧪 通知渠道测试 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        target_channels = channels or list(self.channels.keys())
        results = {}

        for channel_name in target_channels:
            if channel_name not in self.channels:
                results[channel_name] = False
                continue

            try:
                channel = self.channels[channel_name]
                success = channel.send_message(test_message)
                results[channel_name] = success
            except Exception as e:
                logger.error(f"测试通知渠道 {channel_name} 异常: {e}")
                results[channel_name] = False

        return results

    def get_channel_status(self) -> Dict[str, Dict]:
        """获取通知渠道状态"""
        status = {}

        for name, channel in self.channels.items():
            status[name] = {
                "type": type(channel).__name__,
                "is_default": name in self.default_channels,
                "available": True,  # 这里可以添加更复杂的可用性检查
            }

        return status
