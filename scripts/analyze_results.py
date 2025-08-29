#!/usr/bin/env python3
"""
测试结果分析脚本

用于分析Locust测试结果和生成报告
"""

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加项目根目录到路径
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from src.analysis.performance_analyzer import PerformanceAnalyzer


def find_result_files(directory):
    """查找测试结果文件"""
    directory = Path(directory)
    if not directory.exists():
        return {}

    files = {"stats": None, "failures": None, "exceptions": None, "html": None}

    # 查找CSV和HTML报告文件
    for file in directory.glob("*"):
        if file.suffix == ".csv":
            if "stats" in file.name:
                files["stats"] = file
            elif "failures" in file.name:
                files["failures"] = file
            elif "exceptions" in file.name:
                files["exceptions"] = file
        elif file.suffix == ".html" and "report" in file.name:
            files["html"] = file

    return files


def parse_stats_csv(stats_file):
    """解析统计CSV文件"""
    if not stats_file or not stats_file.exists():
        return None

    stats = []
    with open(stats_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 转换数值字段
            for key in [
                "Request Count",
                "Failure Count",
                "Average Response Time",
                "Min Response Time",
                "Max Response Time",
            ]:
                if key in row and row[key]:
                    try:
                        row[key] = float(row[key])
                    except ValueError:
                        pass
            stats.append(row)

    return stats


def parse_failures_csv(failures_file):
    """解析失败CSV文件"""
    if not failures_file or not failures_file.exists():
        return None

    failures = []
    with open(failures_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 转换数值字段
            if "Occurrences" in row and row["Occurrences"]:
                try:
                    row["Occurrences"] = int(row["Occurrences"])
                except ValueError:
                    pass
            failures.append(row)

    return failures


def calculate_basic_metrics(stats):
    """计算基本指标"""
    if not stats:
        return {}

    # 过滤掉Aggregated行
    request_stats = [
        s for s in stats if s.get("Type") == "GET" or s.get("Type") == "POST"
    ]

    if not request_stats:
        return {}

    total_requests = sum(s.get("Request Count", 0) for s in request_stats)
    total_failures = sum(s.get("Failure Count", 0) for s in request_stats)

    response_times = [
        s.get("Average Response Time", 0)
        for s in request_stats
        if s.get("Average Response Time", 0) > 0
    ]

    metrics = {
        "total_requests": total_requests,
        "total_failures": total_failures,
        "success_rate": (
            (total_requests - total_failures) / total_requests * 100
            if total_requests > 0
            else 0
        ),
        "failure_rate": (
            total_failures / total_requests * 100 if total_requests > 0 else 0
        ),
    }

    if response_times:
        metrics.update(
            {
                "avg_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(
                    s.get("Min Response Time", 0)
                    for s in request_stats
                    if s.get("Min Response Time", 0) > 0
                ),
                "max_response_time": max(
                    s.get("Max Response Time", 0) for s in request_stats
                ),
            }
        )

    return metrics


def analyze_performance_trend(stats):
    """分析性能趋势"""
    if not stats:
        return {}

    # 按请求名称分组分析
    request_groups = {}
    for stat in stats:
        name = stat.get("Name", "Unknown")
        if name not in request_groups:
            request_groups[name] = []
        request_groups[name].append(stat)

    trends = {}
    for name, group in request_groups.items():
        if len(group) < 2:
            continue

        response_times = [s.get("Average Response Time", 0) for s in group]
        failure_rates = [
            s.get("Failure Count", 0) / s.get("Request Count", 1) * 100
            for s in group
            if s.get("Request Count", 0) > 0
        ]

        if response_times:
            trends[name] = {
                "response_time_trend": (
                    "increasing"
                    if response_times[-1] > response_times[0]
                    else "decreasing"
                ),
                "avg_response_time": statistics.mean(response_times),
                "response_time_variance": (
                    statistics.variance(response_times)
                    if len(response_times) > 1
                    else 0
                ),
            }

        if failure_rates:
            trends[name]["avg_failure_rate"] = statistics.mean(failure_rates)

    return trends


def generate_summary_report(metrics, trends, failures, output_file):
    """生成汇总报告"""
    report = {
        "summary": {
            "timestamp": str(Path(output_file).stem),
            "metrics": metrics,
            "grade": calculate_performance_grade(metrics),
        },
        "trends": trends,
        "top_failures": failures[:10] if failures else [],
        "recommendations": generate_recommendations(metrics, trends, failures),
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def calculate_performance_grade(metrics):
    """计算性能等级"""
    if not metrics:
        return "F"

    score = 0

    # 成功率评分 (40%)
    success_rate = metrics.get("success_rate", 0)
    if success_rate >= 99:
        score += 40
    elif success_rate >= 95:
        score += 35
    elif success_rate >= 90:
        score += 30
    elif success_rate >= 80:
        score += 20
    else:
        score += 10

    # 响应时间评分 (40%)
    avg_response_time = metrics.get("avg_response_time", 0)
    if avg_response_time <= 100:
        score += 40
    elif avg_response_time <= 300:
        score += 35
    elif avg_response_time <= 500:
        score += 30
    elif avg_response_time <= 1000:
        score += 20
    else:
        score += 10

    # 稳定性评分 (20%)
    failure_rate = metrics.get("failure_rate", 0)
    if failure_rate <= 1:
        score += 20
    elif failure_rate <= 5:
        score += 15
    elif failure_rate <= 10:
        score += 10
    else:
        score += 5

    # 等级划分
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def generate_recommendations(metrics, trends, failures):
    """生成优化建议"""
    recommendations = []

    if not metrics:
        return recommendations

    # 成功率建议
    success_rate = metrics.get("success_rate", 0)
    if success_rate < 95:
        recommendations.append(
            {
                "type": "reliability",
                "priority": "high",
                "message": f"成功率仅为{success_rate:.1f}%，建议检查错误原因并优化系统稳定性",
            }
        )

    # 响应时间建议
    avg_response_time = metrics.get("avg_response_time", 0)
    if avg_response_time > 500:
        recommendations.append(
            {
                "type": "performance",
                "priority": "high",
                "message": f"平均响应时间{avg_response_time:.0f}ms过长，建议优化性能",
            }
        )
    elif avg_response_time > 200:
        recommendations.append(
            {
                "type": "performance",
                "priority": "medium",
                "message": f"平均响应时间{avg_response_time:.0f}ms可以进一步优化",
            }
        )

    # 失败分析建议
    if failures:
        top_failure = failures[0]
        recommendations.append(
            {
                "type": "debugging",
                "priority": "high",
                "message": f'最常见错误: {top_failure.get("Error", "未知错误")}，出现{top_failure.get("Occurrences", 0)}次',
            }
        )

    # 趋势分析建议
    for name, trend in trends.items():
        if trend.get("response_time_trend") == "increasing":
            recommendations.append(
                {
                    "type": "trend",
                    "priority": "medium",
                    "message": f"接口 {name} 响应时间呈上升趋势，建议监控性能变化",
                }
            )

    return recommendations


def print_console_report(report):
    """打印控制台报告"""
    print("📊 测试结果分析报告")
    print("=" * 60)

    metrics = report["summary"]["metrics"]
    if metrics:
        print(f"🎯 性能等级: {report['summary']['grade']}")
        print(f"📈 总请求数: {metrics.get('total_requests', 0):,}")
        print(f"✅ 成功率: {metrics.get('success_rate', 0):.2f}%")
        print(f"❌ 失败率: {metrics.get('failure_rate', 0):.2f}%")

        if "avg_response_time" in metrics:
            print(f"⚡ 平均响应时间: {metrics['avg_response_time']:.2f}ms")
            print(
                f"⚡ 响应时间范围: {metrics.get('min_response_time', 0):.0f}-{metrics.get('max_response_time', 0):.0f}ms"
            )

    # 失败分析
    failures = report["top_failures"]
    if failures:
        print(f"\n❌ 主要失败原因:")
        for i, failure in enumerate(failures[:3], 1):
            print(
                f"   {i}. {failure.get('Error', '未知')}: {failure.get('Occurrences', 0)}次"
            )

    # 优化建议
    recommendations = report["recommendations"]
    if recommendations:
        print(f"\n💡 优化建议:")
        for rec in recommendations[:5]:
            priority_icon = (
                "🔴"
                if rec["priority"] == "high"
                else "🟡" if rec["priority"] == "medium" else "🟢"
            )
            print(f"   {priority_icon} {rec['message']}")

    print("\n" + "=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="分析Locust测试结果")

    # 输入参数
    parser.add_argument("--results-dir", default="reports", help="测试结果目录")
    parser.add_argument("--stats-file", help="统计CSV文件路径")
    parser.add_argument("--failures-file", help="失败CSV文件路径")

    # 输出参数
    parser.add_argument("--output", help="分析报告输出文件")
    parser.add_argument(
        "--format", choices=["json", "console", "both"], default="both", help="输出格式"
    )

    # 分析选项
    parser.add_argument("--detailed", action="store_true", help="详细分析")
    parser.add_argument("--with-trends", action="store_true", help="包含趋势分析")

    args = parser.parse_args()

    print("📊 Locust结果分析器")
    print("=" * 50)

    # 查找结果文件
    if args.stats_file:
        stats_file = Path(args.stats_file)
        failures_file = Path(args.failures_file) if args.failures_file else None
    else:
        files = find_result_files(args.results_dir)
        stats_file = files["stats"]
        failures_file = files["failures"]

        if not stats_file:
            print(f"❌ 在 {args.results_dir} 中未找到统计文件")
            return 1

    print(f"📁 分析文件: {stats_file}")
    if failures_file:
        print(f"📁 失败文件: {failures_file}")

    try:
        # 解析数据
        stats = parse_stats_csv(stats_file)
        failures = parse_failures_csv(failures_file) if failures_file else []

        if not stats:
            print("❌ 无法解析统计数据")
            return 1

        # 计算指标
        metrics = calculate_basic_metrics(stats)
        trends = analyze_performance_trend(stats) if args.with_trends else {}

        # 生成报告
        if args.format in ["json", "both"]:
            output_file = args.output or f"analysis_report_{Path(stats_file).stem}.json"
            report = generate_summary_report(metrics, trends, failures, output_file)
            print(f"✅ 分析报告已保存: {output_file}")
        else:
            report = {
                "summary": {
                    "metrics": metrics,
                    "grade": calculate_performance_grade(metrics),
                },
                "trends": trends,
                "top_failures": failures[:10],
                "recommendations": generate_recommendations(metrics, trends, failures),
            }

        # 控制台输出
        if args.format in ["console", "both"]:
            print_console_report(report)

        return 0

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
