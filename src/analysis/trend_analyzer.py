"""
趋势分析器

提供性能趋势分析和预测功能
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.utils.log_moudle import logger


class TrendAnalyzer:
    """趋势分析器"""

    def __init__(self):
        self.historical_data = []
        self.trend_window = 10  # 趋势分析窗口大小

    def add_historical_data(self, analysis_result: Dict):
        """添加历史分析数据"""
        if "timestamp" not in analysis_result:
            analysis_result["timestamp"] = datetime.now().isoformat()

        self.historical_data.append(analysis_result)
        logger.info(f"添加历史数据，当前数据点数量: {len(self.historical_data)}")

    def load_historical_data(self, file_path: str):
        """从文件加载历史数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.historical_data = data
                else:
                    self.historical_data = [data]
            logger.info(f"从 {file_path} 加载了 {len(self.historical_data)} 条历史数据")
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")
            raise

    def save_historical_data(self, file_path: str):
        """保存历史数据到文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.historical_data, f, ensure_ascii=False, indent=2)
            logger.info(f"历史数据已保存到: {file_path}")
        except Exception as e:
            logger.error(f"保存历史数据失败: {e}")
            raise

    def analyze_response_time_trend(self) -> Dict:
        """分析响应时间趋势"""
        if len(self.historical_data) < 2:
            return {"trend": "insufficient_data", "message": "数据不足，无法分析趋势"}

        # 提取响应时间数据
        timestamps = []
        p95_values = []
        mean_values = []

        for data in self.historical_data:
            if "response_time" in data and data["response_time"]:
                timestamps.append(data["timestamp"])
                p95_values.append(data["response_time"].get("p95", 0))
                mean_values.append(data["response_time"].get("mean", 0))

        if len(p95_values) < 2:
            return {"trend": "insufficient_data", "message": "响应时间数据不足"}

        # 计算趋势
        p95_trend = self._calculate_trend(p95_values)
        mean_trend = self._calculate_trend(mean_values)

        # 计算变化率
        p95_change_rate = self._calculate_change_rate(p95_values)
        mean_change_rate = self._calculate_change_rate(mean_values)

        return {
            "p95_trend": p95_trend,
            "mean_trend": mean_trend,
            "p95_change_rate": p95_change_rate,
            "mean_change_rate": mean_change_rate,
            "data_points": len(p95_values),
            "latest_p95": p95_values[-1] if p95_values else 0,
            "latest_mean": mean_values[-1] if mean_values else 0,
            "recommendation": self._get_response_time_recommendation(
                p95_trend, p95_change_rate
            ),
        }

    def analyze_throughput_trend(self) -> Dict:
        """分析吞吐量趋势"""
        if len(self.historical_data) < 2:
            return {"trend": "insufficient_data", "message": "数据不足，无法分析趋势"}

        # 提取吞吐量数据
        timestamps = []
        avg_tps_values = []
        max_tps_values = []

        for data in self.historical_data:
            if "throughput" in data and data["throughput"]:
                timestamps.append(data["timestamp"])
                avg_tps_values.append(data["throughput"].get("avg_tps", 0))
                max_tps_values.append(data["throughput"].get("max_tps", 0))

        if len(avg_tps_values) < 2:
            return {"trend": "insufficient_data", "message": "吞吐量数据不足"}

        # 计算趋势
        avg_tps_trend = self._calculate_trend(avg_tps_values)
        max_tps_trend = self._calculate_trend(max_tps_values)

        # 计算变化率
        avg_tps_change_rate = self._calculate_change_rate(avg_tps_values)
        max_tps_change_rate = self._calculate_change_rate(max_tps_values)

        return {
            "avg_tps_trend": avg_tps_trend,
            "max_tps_trend": max_tps_trend,
            "avg_tps_change_rate": avg_tps_change_rate,
            "max_tps_change_rate": max_tps_change_rate,
            "data_points": len(avg_tps_values),
            "latest_avg_tps": avg_tps_values[-1] if avg_tps_values else 0,
            "latest_max_tps": max_tps_values[-1] if max_tps_values else 0,
            "recommendation": self._get_throughput_recommendation(
                avg_tps_trend, avg_tps_change_rate
            ),
        }

    def analyze_error_rate_trend(self) -> Dict:
        """分析错误率趋势"""
        if len(self.historical_data) < 2:
            return {"trend": "insufficient_data", "message": "数据不足，无法分析趋势"}

        # 提取错误率数据
        timestamps = []
        error_rates = []

        for data in self.historical_data:
            if "error_rate" in data and data["error_rate"]:
                timestamps.append(data["timestamp"])
                error_rates.append(data["error_rate"].get("error_rate", 0))

        if len(error_rates) < 2:
            return {"trend": "insufficient_data", "message": "错误率数据不足"}

        # 计算趋势
        error_rate_trend = self._calculate_trend(error_rates)

        # 计算变化率
        error_rate_change_rate = self._calculate_change_rate(error_rates)

        return {
            "error_rate_trend": error_rate_trend,
            "error_rate_change_rate": error_rate_change_rate,
            "data_points": len(error_rates),
            "latest_error_rate": error_rates[-1] if error_rates else 0,
            "recommendation": self._get_error_rate_recommendation(
                error_rate_trend, error_rate_change_rate
            ),
        }

    def comprehensive_trend_analysis(self) -> Dict:
        """综合趋势分析"""
        return {
            "timestamp": datetime.now().isoformat(),
            "analysis_period": {
                "start": (
                    self.historical_data[0]["timestamp"]
                    if self.historical_data
                    else None
                ),
                "end": (
                    self.historical_data[-1]["timestamp"]
                    if self.historical_data
                    else None
                ),
                "data_points": len(self.historical_data),
            },
            "response_time_trend": self.analyze_response_time_trend(),
            "throughput_trend": self.analyze_throughput_trend(),
            "error_rate_trend": self.analyze_error_rate_trend(),
            "overall_health": self._assess_overall_health(),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """计算趋势方向"""
        if len(values) < 2:
            return "unknown"

        # 使用线性回归计算趋势
        x = np.arange(len(values))
        y = np.array(values)

        # 计算斜率
        slope = np.polyfit(x, y, 1)[0]

        # 判断趋势
        if abs(slope) < 0.01:  # 阈值可调整
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def _calculate_change_rate(self, values: List[float]) -> float:
        """计算变化率"""
        if len(values) < 2:
            return 0.0

        first_value = values[0]
        last_value = values[-1]

        if first_value == 0:
            return 0.0

        return ((last_value - first_value) / first_value) * 100

    def _get_response_time_recommendation(self, trend: str, change_rate: float) -> str:
        """获取响应时间优化建议"""
        if trend == "increasing" and change_rate > 20:
            return "响应时间显著增长，建议检查系统性能瓶颈，考虑优化代码或扩容"
        elif trend == "increasing" and change_rate > 10:
            return "响应时间有上升趋势，建议关注系统负载和资源使用情况"
        elif trend == "stable":
            return "响应时间保持稳定，系统性能良好"
        elif trend == "decreasing":
            return "响应时间有改善趋势，继续保持当前优化策略"
        else:
            return "数据不足，建议继续监控"

    def _get_throughput_recommendation(self, trend: str, change_rate: float) -> str:
        """获取吞吐量优化建议"""
        if trend == "decreasing" and change_rate < -20:
            return "吞吐量显著下降，建议检查系统瓶颈，可能需要性能调优或扩容"
        elif trend == "decreasing" and change_rate < -10:
            return "吞吐量有下降趋势，建议关注系统资源使用情况"
        elif trend == "stable":
            return "吞吐量保持稳定，系统处理能力良好"
        elif trend == "increasing":
            return "吞吐量有提升趋势，系统性能优化效果良好"
        else:
            return "数据不足，建议继续监控"

    def _get_error_rate_recommendation(self, trend: str, change_rate: float) -> str:
        """获取错误率优化建议"""
        if trend == "increasing" and change_rate > 50:
            return "错误率显著上升，建议立即检查系统稳定性和错误日志"
        elif trend == "increasing" and change_rate > 20:
            return "错误率有上升趋势，建议关注系统异常情况"
        elif trend == "stable" and change_rate < 5:
            return "错误率保持稳定且较低，系统稳定性良好"
        elif trend == "decreasing":
            return "错误率有下降趋势，系统稳定性在改善"
        else:
            return "数据不足，建议继续监控"

    def _assess_overall_health(self) -> str:
        """评估系统整体健康状况"""
        if len(self.historical_data) < 2:
            return "数据不足"

        response_trend = self.analyze_response_time_trend()
        throughput_trend = self.analyze_throughput_trend()
        error_trend = self.analyze_error_rate_trend()

        # 简单的健康评估逻辑
        health_score = 0

        # 响应时间评估
        if response_trend.get("p95_trend") == "decreasing":
            health_score += 2
        elif response_trend.get("p95_trend") == "stable":
            health_score += 1

        # 吞吐量评估
        if throughput_trend.get("avg_tps_trend") == "increasing":
            health_score += 2
        elif throughput_trend.get("avg_tps_trend") == "stable":
            health_score += 1

        # 错误率评估
        if error_trend.get("error_rate_trend") == "decreasing":
            health_score += 2
        elif error_trend.get("error_rate_trend") == "stable":
            health_score += 1

        if health_score >= 5:
            return "优秀"
        elif health_score >= 3:
            return "良好"
        elif health_score >= 1:
            return "一般"
        else:
            return "需要关注"

    def predict_future_performance(self, days_ahead: int = 7) -> Dict:
        """预测未来性能趋势（简单线性预测）"""
        if len(self.historical_data) < 3:
            return {
                "prediction": "insufficient_data",
                "message": "数据不足，无法进行预测",
            }

        # 提取最近的数据进行预测
        recent_data = self.historical_data[-min(10, len(self.historical_data)) :]

        # 简单的线性预测逻辑
        prediction = {
            "prediction_date": (
                datetime.now() + timedelta(days=days_ahead)
            ).isoformat(),
            "confidence": "low" if len(recent_data) < 5 else "medium",
            "warning": [],
        }

        # 这里可以实现更复杂的预测算法
        # 目前只提供基础的趋势延续预测

        return prediction
