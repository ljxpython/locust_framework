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

    def comprehensive_analysis(self, test_data: Dict) -> Dict:
        """综合性能分析 - 符合文档API规范"""
        # 支持两种输入方式：CSV文件路径或直接的测试数据字典
        if isinstance(test_data, str):
            # 兼容旧版本，输入为CSV文件路径
            df = self.load_csv_data(test_data)
            data_source = test_data
        else:
            # 新版本API，输入为测试数据字典
            df = self._convert_test_data_to_df(test_data)
            data_source = test_data.get("test_name", "未知测试")

        analysis_result = {
            "timestamp": datetime.now().isoformat(),
            "test_info": {
                "test_name": (
                    test_data.get("test_name", "未知测试")
                    if isinstance(test_data, dict)
                    else data_source
                ),
                "start_time": (
                    test_data.get("start_time", "")
                    if isinstance(test_data, dict)
                    else ""
                ),
                "end_time": (
                    test_data.get("end_time", "") if isinstance(test_data, dict) else ""
                ),
                "duration": (
                    test_data.get("duration", 0) if isinstance(test_data, dict) else 0
                ),
                "users": (
                    test_data.get("users", 0) if isinstance(test_data, dict) else 0
                ),
            },
            "response_time": self.analyze_response_time(df),
            "throughput": self.analyze_throughput(df),
            "error_analysis": self.analyze_error_rate(df),
            "performance_grade": {},
            "overall_grade": "",
            "recommendations": [],
        }

        # 计算性能评分
        analysis_result["performance_grade"] = self.calculate_performance_grade(
            analysis_result["response_time"],
            analysis_result["throughput"],
            analysis_result["error_analysis"],
        )

        # 综合评分
        analysis_result["overall_grade"] = analysis_result["performance_grade"].get(
            "grade", "D"
        )

        # 生成优化建议
        analysis_result["recommendations"] = self._generate_recommendations(
            analysis_result
        )

        return analysis_result

    def _convert_test_data_to_df(self, test_data: Dict) -> pd.DataFrame:
        """将测试数据字典转换为DataFrame"""
        requests = test_data.get("requests", [])

        # 转换请求数据为DataFrame格式
        df_data = []
        for req in requests:
            df_data.append(
                {
                    "Response Time": req.get("response_time", 0),
                    "Success": req.get("success", True),
                    "Timestamp": req.get("timestamp", datetime.now().isoformat()),
                    "Name": req.get("name", "request"),
                    "Method": req.get("method", "GET"),
                    "Status Code": 200 if req.get("success", True) else 500,
                }
            )

        return pd.DataFrame(df_data) if df_data else pd.DataFrame()

    def calculate_performance_grade(
        self, response_time_result: Dict, throughput_result: Dict, error_result: Dict
    ) -> Dict:
        """计算性能评分 - 符合文档API规范"""
        # 响应时间得分
        rt_grade = response_time_result.get("performance_grade", "D")
        rt_score = self._grade_to_score(rt_grade)

        # 吞吐量得分
        tp_grade = throughput_result.get("performance_grade", "D")
        tp_score = self._grade_to_score(tp_grade)

        # 错误率得分
        er_grade = error_result.get("performance_grade", "D")
        er_score = self._grade_to_score(er_grade)

        # 稳定性得分 (基于响应时间标准差)
        std_dev = response_time_result.get("std", 0)
        mean_rt = response_time_result.get("mean", 0)
        stability_score = (
            100 if mean_rt == 0 else max(0, 100 - (std_dev / mean_rt * 100))
        )

        # 加权计算总体得分
        weights = {
            "response_time": 0.4,
            "throughput": 0.3,
            "error_rate": 0.2,
            "stability": 0.1,
        }

        overall_score = (
            rt_score * weights["response_time"]
            + tp_score * weights["throughput"]
            + er_score * weights["error_rate"]
            + stability_score * weights["stability"]
        )

        # 转换为等级
        overall_grade = self._score_to_grade(overall_score)

        return {
            "response_time_score": rt_score,
            "throughput_score": tp_score,
            "error_rate_score": er_score,
            "stability_score": stability_score,
            "overall_score": round(overall_score, 2),
            "grade": overall_grade,
            "grade_description": self._get_grade_description(overall_grade),
        }

    def _grade_to_score(self, grade: str) -> float:
        """等级转换为分数"""
        grade_map = {"A": 90, "B": 75, "C": 60, "D": 40}
        return grade_map.get(grade, 40)

    def _score_to_grade(self, score: float) -> str:
        """分数转换为等级"""
        if score >= 85:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 55:
            return "C"
        else:
            return "D"

    def _get_grade_description(self, grade: str) -> str:
        """获取等级描述"""
        descriptions = {
            "A": "优秀 - 性能表现出色，系统运行稳定",
            "B": "良好 - 性能表现较好，有小幅优化空间",
            "C": "一般 - 性能基本满足要求，建议进行优化",
            "D": "较差 - 性能存在明显问题，需要立即优化",
        }
        return descriptions.get(grade, "未知")

    def _generate_recommendations(self, analysis_result: Dict) -> List[str]:
        """生成优化建议"""
        recommendations = []

        # 响应时间建议
        rt_grade = analysis_result["response_time"].get("performance_grade", "D")
        if rt_grade in ["C", "D"]:
            recommendations.append(
                "响应时间较高，建议检查应用性能瓶颈，考虑缓存优化或代码优化"
            )

        # 吞吐量建议
        tp_grade = analysis_result["throughput"].get("performance_grade", "D")
        if tp_grade in ["C", "D"]:
            recommendations.append(
                "吞吐量偏低，建议检查系统资源使用情况，考虑扩容或性能调优"
            )

        # 错误率建议
        er_grade = analysis_result["error_analysis"].get("performance_grade", "D")
        if er_grade in ["C", "D"]:
            recommendations.append("错误率较高，建议检查应用日志，修复系统稳定性问题")

        # 稳定性建议
        stability_score = analysis_result["performance_grade"].get("stability_score", 0)
        if stability_score < 70:
            recommendations.append("响应时间波动较大，建议检查系统负载均衡和资源配置")

        if not recommendations:
            recommendations.append("系统性能表现良好，建议持续监控和定期优化")

        return recommendations

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
