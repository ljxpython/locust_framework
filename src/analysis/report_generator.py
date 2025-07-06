"""
报告生成器

提供多种格式的测试报告生成功能
"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from src.utils.log_moudle import logger


class ReportGenerator:
    """报告生成器"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 报告模板
        self.html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>性能测试分析报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .section { margin-bottom: 30px; }
        .metric-card { background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .grade-A { border-left: 5px solid #4CAF50; }
        .grade-B { border-left: 5px solid #FF9800; }
        .grade-C { border-left: 5px solid #FF5722; }
        .grade-D { border-left: 5px solid #F44336; }
        .trend-up { color: #4CAF50; }
        .trend-down { color: #F44336; }
        .trend-stable { color: #2196F3; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .summary { background: #e3f2fd; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>性能测试分析报告</h1>
        <p><strong>生成时间:</strong> {timestamp}</p>
        <p><strong>数据源:</strong> {data_source}</p>
    </div>

    <div class="section">
        <h2>执行摘要</h2>
        <div class="summary">
            <p><strong>综合评分:</strong> {overall_grade}</p>
            <p><strong>测试建议:</strong> {recommendations}</p>
        </div>
    </div>

    <div class="section">
        <h2>响应时间分析</h2>
        <div class="metric-card grade-{response_time_grade}">
            <h3>响应时间指标 (评分: {response_time_grade})</h3>
            <table>
                <tr><th>指标</th><th>值</th></tr>
                <tr><td>平均响应时间</td><td>{mean_rt:.2f} ms</td></tr>
                <tr><td>95%响应时间</td><td>{p95_rt:.2f} ms</td></tr>
                <tr><td>99%响应时间</td><td>{p99_rt:.2f} ms</td></tr>
                <tr><td>最大响应时间</td><td>{max_rt:.2f} ms</td></tr>
            </table>
        </div>
    </div>

    <div class="section">
        <h2>吞吐量分析</h2>
        <div class="metric-card grade-{throughput_grade}">
            <h3>吞吐量指标 (评分: {throughput_grade})</h3>
            <table>
                <tr><th>指标</th><th>值</th></tr>
                <tr><td>平均TPS</td><td>{avg_tps:.2f}</td></tr>
                <tr><td>最大TPS</td><td>{max_tps:.2f}</td></tr>
                <tr><td>总请求数</td><td>{total_requests}</td></tr>
                <tr><td>测试时长</td><td>{duration:.2f} 秒</td></tr>
            </table>
        </div>
    </div>

    <div class="section">
        <h2>错误率分析</h2>
        <div class="metric-card grade-{error_rate_grade}">
            <h3>错误率指标 (评分: {error_rate_grade})</h3>
            <table>
                <tr><th>指标</th><th>值</th></tr>
                <tr><td>错误率</td><td>{error_percentage:.2f}%</td></tr>
                <tr><td>失败请求数</td><td>{failed_requests}</td></tr>
                <tr><td>成功请求数</td><td>{success_requests}</td></tr>
            </table>
        </div>
    </div>

    {trend_section}

    <div class="section">
        <h2>详细数据</h2>
        <pre>{raw_data}</pre>
    </div>
</body>
</html>
"""

    def generate_html_report(
        self,
        analysis_data: Dict,
        trend_data: Optional[Dict] = None,
        output_filename: str = None,
    ) -> str:
        """生成HTML格式报告"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"performance_report_{timestamp}.html"

        output_path = self.output_dir / output_filename

        # 准备模板数据
        template_data = self._prepare_template_data(analysis_data, trend_data)

        # 生成HTML内容
        html_content = self.html_template.format(**template_data)

        # 写入文件
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML报告已生成: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            raise

    def generate_json_report(
        self,
        analysis_data: Dict,
        trend_data: Optional[Dict] = None,
        output_filename: str = None,
    ) -> str:
        """生成JSON格式报告"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"performance_report_{timestamp}.json"

        output_path = self.output_dir / output_filename

        # 合并数据
        report_data = {
            "report_info": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "performance_analysis",
                "version": "1.0",
            },
            "analysis": analysis_data,
        }

        if trend_data:
            report_data["trend_analysis"] = trend_data

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            logger.info(f"JSON报告已生成: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"生成JSON报告失败: {e}")
            raise

    def generate_csv_summary(
        self, analysis_data: Dict, output_filename: str = None
    ) -> str:
        """生成CSV格式的摘要报告"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"performance_summary_{timestamp}.csv"

        output_path = self.output_dir / output_filename

        # 准备CSV数据
        csv_data = []

        # 基本信息
        csv_data.append(["报告生成时间", analysis_data.get("timestamp", "")])
        csv_data.append(["数据源", analysis_data.get("data_source", "")])
        csv_data.append(["综合评分", analysis_data.get("overall_grade", "")])
        csv_data.append(["", ""])  # 空行

        # 响应时间指标
        if "response_time" in analysis_data:
            rt_data = analysis_data["response_time"]
            csv_data.append(["响应时间指标", ""])
            csv_data.append(["平均响应时间(ms)", rt_data.get("mean", 0)])
            csv_data.append(["95%响应时间(ms)", rt_data.get("p95", 0)])
            csv_data.append(["99%响应时间(ms)", rt_data.get("p99", 0)])
            csv_data.append(["最大响应时间(ms)", rt_data.get("max", 0)])
            csv_data.append(["响应时间评分", rt_data.get("performance_grade", "")])
            csv_data.append(["", ""])

        # 吞吐量指标
        if "throughput" in analysis_data:
            tp_data = analysis_data["throughput"]
            csv_data.append(["吞吐量指标", ""])
            csv_data.append(["平均TPS", tp_data.get("avg_tps", 0)])
            csv_data.append(["最大TPS", tp_data.get("max_tps", 0)])
            csv_data.append(["总请求数", tp_data.get("total_requests", 0)])
            csv_data.append(["测试时长(秒)", tp_data.get("duration_seconds", 0)])
            csv_data.append(["吞吐量评分", tp_data.get("performance_grade", "")])
            csv_data.append(["", ""])

        # 错误率指标
        if "error_rate" in analysis_data:
            er_data = analysis_data["error_rate"]
            csv_data.append(["错误率指标", ""])
            csv_data.append(["错误率(%)", er_data.get("error_percentage", 0)])
            csv_data.append(["失败请求数", er_data.get("failed_requests", 0)])
            csv_data.append(["成功请求数", er_data.get("success_requests", 0)])
            csv_data.append(["错误率评分", er_data.get("performance_grade", "")])

        try:
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(csv_data)
            logger.info(f"CSV摘要报告已生成: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"生成CSV摘要报告失败: {e}")
            raise

    def generate_markdown_report(
        self,
        analysis_data: Dict,
        trend_data: Optional[Dict] = None,
        output_filename: str = None,
    ) -> str:
        """生成Markdown格式报告"""
        if output_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"performance_report_{timestamp}.md"

        output_path = self.output_dir / output_filename

        # 生成Markdown内容
        md_content = self._generate_markdown_content(analysis_data, trend_data)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(md_content)
            logger.info(f"Markdown报告已生成: {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"生成Markdown报告失败: {e}")
            raise

    def _prepare_template_data(
        self, analysis_data: Dict, trend_data: Optional[Dict] = None
    ) -> Dict:
        """准备模板数据"""
        # 默认值
        template_data = {
            "timestamp": analysis_data.get("timestamp", datetime.now().isoformat()),
            "data_source": analysis_data.get("data_source", "未知"),
            "overall_grade": analysis_data.get("overall_grade", "D"),
            "recommendations": self._generate_recommendations(analysis_data),
            # 响应时间数据
            "response_time_grade": "D",
            "mean_rt": 0,
            "p95_rt": 0,
            "p99_rt": 0,
            "max_rt": 0,
            # 吞吐量数据
            "throughput_grade": "D",
            "avg_tps": 0,
            "max_tps": 0,
            "total_requests": 0,
            "duration": 0,
            # 错误率数据
            "error_rate_grade": "D",
            "error_percentage": 0,
            "failed_requests": 0,
            "success_requests": 0,
            # 趋势分析
            "trend_section": "",
            # 原始数据
            "raw_data": json.dumps(analysis_data, ensure_ascii=False, indent=2),
        }

        # 填充实际数据
        if "response_time" in analysis_data:
            rt_data = analysis_data["response_time"]
            template_data.update(
                {
                    "response_time_grade": rt_data.get("performance_grade", "D"),
                    "mean_rt": rt_data.get("mean", 0),
                    "p95_rt": rt_data.get("p95", 0),
                    "p99_rt": rt_data.get("p99", 0),
                    "max_rt": rt_data.get("max", 0),
                }
            )

        if "throughput" in analysis_data:
            tp_data = analysis_data["throughput"]
            template_data.update(
                {
                    "throughput_grade": tp_data.get("performance_grade", "D"),
                    "avg_tps": tp_data.get("avg_tps", 0),
                    "max_tps": tp_data.get("max_tps", 0),
                    "total_requests": tp_data.get("total_requests", 0),
                    "duration": tp_data.get("duration_seconds", 0),
                }
            )

        if "error_rate" in analysis_data:
            er_data = analysis_data["error_rate"]
            template_data.update(
                {
                    "error_rate_grade": er_data.get("performance_grade", "D"),
                    "error_percentage": er_data.get("error_percentage", 0),
                    "failed_requests": er_data.get("failed_requests", 0),
                    "success_requests": er_data.get("success_requests", 0),
                }
            )

        # 添加趋势分析部分
        if trend_data:
            template_data["trend_section"] = self._generate_trend_section(trend_data)

        return template_data

    def _generate_recommendations(self, analysis_data: Dict) -> str:
        """生成优化建议"""
        recommendations = []

        # 基于综合评分给出建议
        overall_grade = analysis_data.get("overall_grade", "D")
        if overall_grade == "A":
            recommendations.append("系统性能优秀，继续保持当前配置和优化策略")
        elif overall_grade == "B":
            recommendations.append("系统性能良好，可考虑进一步优化以达到更高性能")
        elif overall_grade == "C":
            recommendations.append("系统性能一般，建议进行性能调优和瓶颈分析")
        else:
            recommendations.append("系统性能需要改善，建议立即进行性能优化")

        return "; ".join(recommendations)

    def _generate_trend_section(self, trend_data: Dict) -> str:
        """生成趋势分析HTML部分"""
        if not trend_data:
            return ""

        trend_html = """
    <div class="section">
        <h2>趋势分析</h2>
        <div class="metric-card">
            <h3>性能趋势概览</h3>
            <p><strong>分析周期:</strong> {analysis_period}</p>
            <p><strong>整体健康状况:</strong> {overall_health}</p>
        </div>
    </div>
        """.format(
            analysis_period=f"{trend_data.get('analysis_period', {}).get('start', '')} 至 {trend_data.get('analysis_period', {}).get('end', '')}",
            overall_health=trend_data.get("overall_health", "未知"),
        )

        return trend_html

    def _generate_markdown_content(
        self, analysis_data: Dict, trend_data: Optional[Dict] = None
    ) -> str:
        """生成Markdown内容"""
        md_content = f"""# 性能测试分析报告

**生成时间:** {analysis_data.get('timestamp', datetime.now().isoformat())}
**数据源:** {analysis_data.get('data_source', '未知')}
**综合评分:** {analysis_data.get('overall_grade', 'D')}

## 执行摘要

{self._generate_recommendations(analysis_data)}

## 响应时间分析

"""

        if "response_time" in analysis_data:
            rt_data = analysis_data["response_time"]
            md_content += f"""
| 指标 | 值 |
|------|-----|
| 平均响应时间 | {rt_data.get('mean', 0):.2f} ms |
| 95%响应时间 | {rt_data.get('p95', 0):.2f} ms |
| 99%响应时间 | {rt_data.get('p99', 0):.2f} ms |
| 最大响应时间 | {rt_data.get('max', 0):.2f} ms |
| 评分 | {rt_data.get('performance_grade', 'D')} |

"""

        if "throughput" in analysis_data:
            tp_data = analysis_data["throughput"]
            md_content += f"""## 吞吐量分析

| 指标 | 值 |
|------|-----|
| 平均TPS | {tp_data.get('avg_tps', 0):.2f} |
| 最大TPS | {tp_data.get('max_tps', 0):.2f} |
| 总请求数 | {tp_data.get('total_requests', 0)} |
| 测试时长 | {tp_data.get('duration_seconds', 0):.2f} 秒 |
| 评分 | {tp_data.get('performance_grade', 'D')} |

"""

        if "error_rate" in analysis_data:
            er_data = analysis_data["error_rate"]
            md_content += f"""## 错误率分析

| 指标 | 值 |
|------|-----|
| 错误率 | {er_data.get('error_percentage', 0):.2f}% |
| 失败请求数 | {er_data.get('failed_requests', 0)} |
| 成功请求数 | {er_data.get('success_requests', 0)} |
| 评分 | {er_data.get('performance_grade', 'D')} |

"""

        if trend_data:
            md_content += f"""## 趋势分析

**整体健康状况:** {trend_data.get('overall_health', '未知')}

"""

        return md_content
