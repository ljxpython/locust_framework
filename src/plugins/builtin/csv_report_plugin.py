"""
CSV报告插件

生成CSV格式的测试报告
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from src.plugins.plugin_interface import PluginInfo, ReportPlugin
from src.utils.log_moudle import logger


class CSVReportPlugin(ReportPlugin):
    """CSV报告插件"""

    def __init__(self):
        super().__init__()
        self._plugin_info = PluginInfo(
            name="CSV Report Plugin",
            version="1.0.0",
            description="生成CSV格式的测试报告",
            author="Locust Framework",
            category="report",
        )

    @property
    def plugin_info(self) -> PluginInfo:
        return self._plugin_info

    def initialize(self, config: Dict[str, Any] = None) -> bool:
        """初始化插件"""
        try:
            self.configure(config or {})
            logger.info("CSV报告插件初始化成功")
            return True
        except Exception as e:
            logger.error(f"CSV报告插件初始化失败: {e}")
            return False

    def cleanup(self):
        """清理插件资源"""
        logger.info("CSV报告插件清理完成")

    def generate_report(self, test_data: Dict[str, Any], output_path: str) -> bool:
        """生成CSV报告"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 生成汇总报告
            self._generate_summary_report(
                test_data, output_file.with_suffix(".summary.csv")
            )

            # 生成详细请求报告
            self._generate_requests_report(
                test_data, output_file.with_suffix(".requests.csv")
            )

            # 生成错误报告
            self._generate_errors_report(
                test_data, output_file.with_suffix(".errors.csv")
            )

            logger.info(f"CSV报告生成成功: {output_file}")
            return True

        except Exception as e:
            logger.error(f"生成CSV报告失败: {e}")
            return False

    def get_supported_formats(self) -> List[str]:
        """获取支持的报告格式"""
        return ["csv"]

    def _generate_summary_report(self, test_data: Dict[str, Any], output_file: Path):
        """生成汇总报告"""
        summary_data = []

        # 基本信息
        basic_info = {
            "metric": "test_info",
            "name": test_data.get("test_name", "Unknown"),
            "start_time": test_data.get("start_time", ""),
            "end_time": test_data.get("end_time", ""),
            "duration": test_data.get("duration", 0),
            "users": test_data.get("users", 0),
            "value": "",
            "unit": "",
        }
        summary_data.append(basic_info)

        # 响应时间统计
        if "response_time" in test_data:
            rt_data = test_data["response_time"]
            for metric, value in rt_data.items():
                summary_data.append(
                    {
                        "metric": "response_time",
                        "name": metric,
                        "value": value,
                        "unit": "ms",
                        "start_time": "",
                        "end_time": "",
                        "duration": "",
                        "users": "",
                    }
                )

        # 吞吐量统计
        if "throughput" in test_data:
            tp_data = test_data["throughput"]
            for metric, value in tp_data.items():
                summary_data.append(
                    {
                        "metric": "throughput",
                        "name": metric,
                        "value": value,
                        "unit": "req/s",
                        "start_time": "",
                        "end_time": "",
                        "duration": "",
                        "users": "",
                    }
                )

        # 错误率统计
        if "error_rate" in test_data:
            er_data = test_data["error_rate"]
            for metric, value in er_data.items():
                summary_data.append(
                    {
                        "metric": "error_rate",
                        "name": metric,
                        "value": value,
                        "unit": "%",
                        "start_time": "",
                        "end_time": "",
                        "duration": "",
                        "users": "",
                    }
                )

        # 写入CSV文件
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "metric",
                "name",
                "value",
                "unit",
                "start_time",
                "end_time",
                "duration",
                "users",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summary_data)

    def _generate_requests_report(self, test_data: Dict[str, Any], output_file: Path):
        """生成请求详细报告"""
        requests_data = test_data.get("requests", [])

        if not requests_data:
            logger.warning("没有请求数据可生成报告")
            return

        # 准备CSV数据
        csv_data = []
        for req in requests_data:
            csv_data.append(
                {
                    "timestamp": req.get("timestamp", ""),
                    "method": req.get("method", ""),
                    "name": req.get("name", ""),
                    "response_time": req.get("response_time", 0),
                    "response_length": req.get("response_length", 0),
                    "status_code": req.get("status_code", ""),
                    "success": req.get("success", False),
                    "error": req.get("error", ""),
                    "user_id": req.get("user_id", ""),
                    "concurrent_users": req.get("concurrent_users", 0),
                }
            )

        # 写入CSV文件
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                "timestamp",
                "method",
                "name",
                "response_time",
                "response_length",
                "status_code",
                "success",
                "error",
                "user_id",
                "concurrent_users",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

    def _generate_errors_report(self, test_data: Dict[str, Any], output_file: Path):
        """生成错误报告"""
        errors_data = test_data.get("errors", [])

        if not errors_data:
            # 创建空的错误报告文件
            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "timestamp",
                    "method",
                    "name",
                    "error",
                    "count",
                    "percentage",
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            return

        # 准备CSV数据
        csv_data = []
        for error in errors_data:
            csv_data.append(
                {
                    "timestamp": error.get("timestamp", ""),
                    "method": error.get("method", ""),
                    "name": error.get("name", ""),
                    "error": error.get("error", ""),
                    "count": error.get("count", 0),
                    "percentage": error.get("percentage", 0.0),
                }
            )

        # 写入CSV文件
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["timestamp", "method", "name", "error", "count", "percentage"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

    def customize_report_data(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """自定义报告数据"""
        # 添加生成时间
        test_data["report_generated_at"] = datetime.now().isoformat()

        # 添加插件信息
        test_data["report_plugin"] = {
            "name": self.plugin_info.name,
            "version": self.plugin_info.version,
        }

        return test_data
