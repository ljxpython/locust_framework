"""
性能分析器

提供详细的性能指标分析功能
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils.log_moudle import logger


class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self):
        self.metrics = {}
        self.thresholds = {
            "response_time_p95": 1000,  # 95%响应时间阈值(ms)
            "response_time_p99": 2000,  # 99%响应时间阈值(ms)
            "error_rate": 0.05,  # 错误率阈值(5%)
            "throughput_min": 10,  # 最小吞吐量阈值(TPS)
        }

    def load_csv_data(self, csv_file_path: str) -> pd.DataFrame:
        """加载CSV格式的测试数据"""
        try:
            df = pd.read_csv(csv_file_path)
            logger.info(f"成功加载测试数据: {csv_file_path}")
            return df
        except Exception as e:
            logger.error(f"加载CSV数据失败: {e}")
            raise

    def analyze_response_time(self, df: pd.DataFrame) -> Dict:
        """分析响应时间指标"""
        if "Response Time" not in df.columns:
            logger.warning("数据中缺少响应时间列")
            return {}

        response_times = df["Response Time"].dropna()

        analysis = {
            "mean": float(response_times.mean()),
            "median": float(response_times.median()),
            "p50": float(response_times.quantile(0.5)),
            "p90": float(response_times.quantile(0.9)),
            "p95": float(response_times.quantile(0.95)),
            "p99": float(response_times.quantile(0.99)),
            "min": float(response_times.min()),
            "max": float(response_times.max()),
            "std": float(response_times.std()),
        }

        # 性能评估
        analysis["performance_grade"] = self._grade_response_time(analysis)

        return analysis

    def analyze_throughput(self, df: pd.DataFrame) -> Dict:
        """分析吞吐量指标"""
        if "Timestamp" not in df.columns:
            logger.warning("数据中缺少时间戳列")
            return {}

        # 按时间窗口计算TPS
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df_sorted = df.sort_values("Timestamp")

        # 计算每秒请求数
        tps_data = df_sorted.groupby(df_sorted["Timestamp"].dt.floor("S")).size()

        analysis = {
            "max_tps": float(tps_data.max()),
            "min_tps": float(tps_data.min()),
            "avg_tps": float(tps_data.mean()),
            "median_tps": float(tps_data.median()),
            "total_requests": len(df),
            "duration_seconds": (
                df_sorted["Timestamp"].max() - df_sorted["Timestamp"].min()
            ).total_seconds(),
        }

        analysis["performance_grade"] = self._grade_throughput(analysis)

        return analysis

    def analyze_error_rate(self, df: pd.DataFrame) -> Dict:
        """分析错误率指标"""
        total_requests = len(df)
        if total_requests == 0:
            return {"error_rate": 0, "total_requests": 0, "failed_requests": 0}

        # 假设有Success列或者通过状态码判断
        if "Success" in df.columns:
            failed_requests = len(df[df["Success"] == False])
        elif "Status Code" in df.columns:
            failed_requests = len(df[df["Status Code"] >= 400])
        else:
            logger.warning("无法确定请求成功/失败状态")
            failed_requests = 0

        error_rate = failed_requests / total_requests

        analysis = {
            "error_rate": float(error_rate),
            "error_percentage": float(error_rate * 100),
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "success_requests": total_requests - failed_requests,
        }

        analysis["performance_grade"] = self._grade_error_rate(analysis)

        return analysis

    def analyze_resource_usage(self, df: pd.DataFrame) -> Dict:
        """分析资源使用情况"""
        # 这里可以扩展分析CPU、内存等资源使用情况
        # 目前基于请求数据进行基础分析

        analysis = {
            "concurrent_users": self._estimate_concurrent_users(df),
            "request_distribution": self._analyze_request_distribution(df),
        }

        return analysis

    def comprehensive_analysis(self, csv_file_path: str) -> Dict:
        """综合性能分析"""
        df = self.load_csv_data(csv_file_path)

        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "data_source": csv_file_path,
            "response_time": self.analyze_response_time(df),
            "throughput": self.analyze_throughput(df),
            "error_rate": self.analyze_error_rate(df),
            "resource_usage": self.analyze_resource_usage(df),
        }

        # 综合评分
        analysis_result["overall_grade"] = self._calculate_overall_grade(
            analysis_result
        )

        return analysis_result

    def _grade_response_time(self, analysis: Dict) -> str:
        """响应时间评分"""
        p95 = analysis.get("p95", float("inf"))
        if p95 <= self.thresholds["response_time_p95"] * 0.5:
            return "A"
        elif p95 <= self.thresholds["response_time_p95"]:
            return "B"
        elif p95 <= self.thresholds["response_time_p95"] * 2:
            return "C"
        else:
            return "D"

    def _grade_throughput(self, analysis: Dict) -> str:
        """吞吐量评分"""
        avg_tps = analysis.get("avg_tps", 0)
        if avg_tps >= self.thresholds["throughput_min"] * 5:
            return "A"
        elif avg_tps >= self.thresholds["throughput_min"] * 2:
            return "B"
        elif avg_tps >= self.thresholds["throughput_min"]:
            return "C"
        else:
            return "D"

    def _grade_error_rate(self, analysis: Dict) -> str:
        """错误率评分"""
        error_rate = analysis.get("error_rate", 1)
        if error_rate <= self.thresholds["error_rate"] * 0.2:
            return "A"
        elif error_rate <= self.thresholds["error_rate"]:
            return "B"
        elif error_rate <= self.thresholds["error_rate"] * 2:
            return "C"
        else:
            return "D"

    def _calculate_overall_grade(self, analysis: Dict) -> str:
        """计算综合评分"""
        grades = []
        grade_map = {"A": 4, "B": 3, "C": 2, "D": 1}

        for category in ["response_time", "throughput", "error_rate"]:
            if category in analysis and "performance_grade" in analysis[category]:
                grades.append(grade_map.get(analysis[category]["performance_grade"], 1))

        if not grades:
            return "D"

        avg_score = sum(grades) / len(grades)
        if avg_score >= 3.5:
            return "A"
        elif avg_score >= 2.5:
            return "B"
        elif avg_score >= 1.5:
            return "C"
        else:
            return "D"

    def _estimate_concurrent_users(self, df: pd.DataFrame) -> int:
        """估算并发用户数"""
        if "Timestamp" not in df.columns:
            return 0

        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        # 简单估算：取1秒时间窗口内的最大请求数
        concurrent_estimate = df.groupby(df["Timestamp"].dt.floor("S")).size().max()
        return int(concurrent_estimate)

    def _analyze_request_distribution(self, df: pd.DataFrame) -> Dict:
        """分析请求分布"""
        if "Name" not in df.columns:
            return {}

        distribution = df["Name"].value_counts().to_dict()
        return {str(k): int(v) for k, v in distribution.items()}

    def set_thresholds(self, **thresholds):
        """设置性能阈值"""
        self.thresholds.update(thresholds)
        logger.info(f"更新性能阈值: {thresholds}")

    def export_analysis(self, analysis: Dict, output_path: str):
        """导出分析结果"""
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            logger.info(f"分析结果已导出到: {output_path}")
        except Exception as e:
            logger.error(f"导出分析结果失败: {e}")
            raise
