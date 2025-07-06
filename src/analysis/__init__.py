"""
性能分析模块

提供测试结果的深度分析功能，包括：
- 性能指标统计分析
- 趋势分析
- 异常检测
- 性能对比分析
"""

from .performance_analyzer import PerformanceAnalyzer
from .report_generator import ReportGenerator
from .trend_analyzer import TrendAnalyzer

__all__ = ["PerformanceAnalyzer", "TrendAnalyzer", "ReportGenerator"]
