# 性能分析API参考

本文档详细介绍性能分析模块的API接口，包括性能分析器、趋势分析器和报告生成器。

## 📊 PerformanceAnalyzer

性能分析器是框架的核心分析组件，提供全面的性能指标分析和评分功能。

### 类定义

```python
from src.analysis.performance_analyzer import PerformanceAnalyzer

class PerformanceAnalyzer:
    """性能分析器

    提供全面的性能分析功能，包括响应时间分析、吞吐量分析、
    错误率分析和综合性能评分。
    """
```

### 构造函数

```python
def __init__(self, config: Optional[Dict[str, Any]] = None):
    """初始化性能分析器

    Args:
        config: 配置参数字典，可选
            - response_time_thresholds: 响应时间阈值配置
            - throughput_thresholds: 吞吐量阈值配置
            - error_rate_thresholds: 错误率阈值配置
            - weights: 各指标权重配置

    Example:
        >>> config = {
        ...     'response_time_thresholds': {
        ...         'excellent': 500,
        ...         'good': 1000,
        ...         'acceptable': 2000,
        ...         'poor': 5000
        ...     }
        ... }
        >>> analyzer = PerformanceAnalyzer(config)
    """
```

### 核心方法

#### comprehensive_analysis()

```python
def comprehensive_analysis(self, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """执行综合性能分析

    Args:
        test_data: 测试数据字典，包含以下字段：
            - test_name: 测试名称
            - start_time: 开始时间
            - end_time: 结束时间
            - duration: 测试持续时间(秒)
            - users: 用户数
            - requests: 请求列表，每个请求包含：
                - response_time: 响应时间(毫秒)
                - success: 是否成功(布尔值)
                - timestamp: 时间戳
                - name: 请求名称(可选)
                - method: HTTP方法(可选)

    Returns:
        Dict[str, Any]: 分析结果字典，包含：
            - test_info: 测试基本信息
            - response_time: 响应时间分析结果
            - throughput: 吞吐量分析结果
            - error_analysis: 错误分析结果
            - performance_grade: 性能评分结果
            - overall_grade: 总体评级
            - recommendations: 优化建议

    Example:
        >>> test_data = {
        ...     'test_name': '用户登录测试',
        ...     'start_time': '2024-01-01 10:00:00',
        ...     'end_time': '2024-01-01 10:30:00',
        ...     'duration': 1800,
        ...     'users': 100,
        ...     'requests': [
        ...         {'response_time': 500, 'success': True, 'timestamp': '2024-01-01 10:00:01'},
        ...         {'response_time': 800, 'success': True, 'timestamp': '2024-01-01 10:00:02'},
        ...         # ... 更多请求数据
        ...     ]
        ... }
        >>> result = analyzer.comprehensive_analysis(test_data)
        >>> print(f"总体评级: {result['overall_grade']}")
    """
```

#### analyze_response_time()

```python
def analyze_response_time(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析响应时间

    Args:
        requests: 请求列表

    Returns:
        Dict[str, Any]: 响应时间分析结果
            - avg: 平均响应时间
            - min: 最小响应时间
            - max: 最大响应时间
            - median: 中位数响应时间
            - p50, p90, p95, p99: 百分位数响应时间
            - std_dev: 标准差
            - distribution: 响应时间分布
            - grade: 响应时间评级

    Example:
        >>> requests = [
        ...     {'response_time': 500, 'success': True},
        ...     {'response_time': 800, 'success': True},
        ...     {'response_time': 1200, 'success': False}
        ... ]
        >>> result = analyzer.analyze_response_time(requests)
        >>> print(f"P95响应时间: {result['p95']}ms")
    """
```

#### analyze_throughput()

```python
def analyze_throughput(self, requests: List[Dict[str, Any]],
                      duration: float) -> Dict[str, Any]:
    """分析吞吐量

    Args:
        requests: 请求列表
        duration: 测试持续时间(秒)

    Returns:
        Dict[str, Any]: 吞吐量分析结果
            - total_requests: 总请求数
            - successful_requests: 成功请求数
            - failed_requests: 失败请求数
            - avg_tps: 平均TPS
            - peak_tps: 峰值TPS
            - min_tps: 最低TPS
            - tps_trend: TPS趋势数据
            - grade: 吞吐量评级

    Example:
        >>> result = analyzer.analyze_throughput(requests, 1800)
        >>> print(f"平均TPS: {result['avg_tps']}")
    """
```

#### analyze_errors()

```python
def analyze_errors(self, requests: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析错误情况

    Args:
        requests: 请求列表

    Returns:
        Dict[str, Any]: 错误分析结果
            - total_errors: 总错误数
            - error_rate: 错误率(百分比)
            - error_types: 错误类型分布
            - error_trend: 错误趋势
            - critical_errors: 严重错误列表
            - grade: 错误率评级

    Example:
        >>> result = analyzer.analyze_errors(requests)
        >>> print(f"错误率: {result['error_rate']:.2f}%")
    """
```

#### calculate_performance_grade()

```python
def calculate_performance_grade(self, response_time_result: Dict[str, Any],
                               throughput_result: Dict[str, Any],
                               error_result: Dict[str, Any]) -> Dict[str, Any]:
    """计算性能评分

    Args:
        response_time_result: 响应时间分析结果
        throughput_result: 吞吐量分析结果
        error_result: 错误分析结果

    Returns:
        Dict[str, Any]: 性能评分结果
            - response_time_score: 响应时间得分
            - throughput_score: 吞吐量得分
            - error_rate_score: 错误率得分
            - stability_score: 稳定性得分
            - overall_score: 总体得分
            - grade: 评级(A/B/C/D)
            - grade_description: 评级描述

    Example:
        >>> grade_result = analyzer.calculate_performance_grade(
        ...     response_time_result, throughput_result, error_result
        ... )
        >>> print(f"总体评级: {grade_result['grade']}")
    """
```

### 配置选项

```python
# 默认配置
DEFAULT_CONFIG = {
    'response_time_thresholds': {
        'excellent': 500,    # A级: < 500ms
        'good': 1000,        # B级: < 1000ms
        'acceptable': 2000,  # C级: < 2000ms
        'poor': 5000         # D级: >= 2000ms
    },
    'throughput_thresholds': {
        'excellent': 1000,   # A级: > 1000 TPS
        'good': 500,         # B级: > 500 TPS
        'acceptable': 100,   # C级: > 100 TPS
        'poor': 50           # D级: <= 100 TPS
    },
    'error_rate_thresholds': {
        'excellent': 0.1,    # A级: < 0.1%
        'good': 1.0,         # B级: < 1%
        'acceptable': 5.0,   # C级: < 5%
        'poor': 10.0         # D级: >= 5%
    },
    'weights': {
        'response_time': 0.4,  # 响应时间权重40%
        'throughput': 0.3,     # 吞吐量权重30%
        'error_rate': 0.2,     # 错误率权重20%
        'stability': 0.1       # 稳定性权重10%
    }
}
```

## 📈 TrendAnalyzer

趋势分析器提供历史数据分析和性能趋势预测功能。

### 类定义

```python
from src.analysis.trend_analyzer import TrendAnalyzer

class TrendAnalyzer:
    """趋势分析器

    提供历史性能数据的趋势分析和预测功能。
    """
```

### 核心方法

#### analyze_historical_trend()

```python
def analyze_historical_trend(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析历史趋势

    Args:
        historical_data: 历史测试数据列表，每个元素包含：
            - timestamp: 时间戳
            - avg_response_time: 平均响应时间
            - throughput: 吞吐量
            - error_rate: 错误率
            - users: 用户数

    Returns:
        Dict[str, Any]: 趋势分析结果
            - response_time_trend: 响应时间趋势
            - throughput_trend: 吞吐量趋势
            - error_rate_trend: 错误率趋势
            - performance_trend: 整体性能趋势
            - trend_summary: 趋势摘要

    Example:
        >>> historical_data = [
        ...     {
        ...         'timestamp': '2024-01-01',
        ...         'avg_response_time': 500,
        ...         'throughput': 100,
        ...         'error_rate': 1.0,
        ...         'users': 50
        ...     },
        ...     # ... 更多历史数据
        ... ]
        >>> trend_result = trend_analyzer.analyze_historical_trend(historical_data)
    """
```

#### predict_performance()

```python
def predict_performance(self, historical_data: List[Dict[str, Any]],
                       prediction_days: int = 7) -> Dict[str, Any]:
    """性能预测

    Args:
        historical_data: 历史数据
        prediction_days: 预测天数

    Returns:
        Dict[str, Any]: 预测结果
            - predicted_response_time: 预测响应时间
            - predicted_throughput: 预测吞吐量
            - predicted_error_rate: 预测错误率
            - confidence_interval: 置信区间
            - prediction_accuracy: 预测准确度

    Example:
        >>> prediction = trend_analyzer.predict_performance(historical_data, 7)
        >>> print(f"预测响应时间: {prediction['predicted_response_time']}")
    """
```

## 📋 ReportGenerator

报告生成器提供多格式的测试报告生成功能。

### 类定义

```python
from src.analysis.report_generator import ReportGenerator

class ReportGenerator:
    """报告生成器

    支持生成HTML、JSON、CSV、Markdown等多种格式的测试报告。
    """
```

### 核心方法

#### generate_html_report()

```python
def generate_html_report(self, analysis_result: Dict[str, Any],
                        output_path: str,
                        template_name: str = 'default') -> bool:
    """生成HTML报告

    Args:
        analysis_result: 分析结果数据
        output_path: 输出文件路径
        template_name: 模板名称，默认为'default'

    Returns:
        bool: 生成是否成功

    Example:
        >>> success = report_generator.generate_html_report(
        ...     analysis_result,
        ...     'reports/test_report.html'
        ... )
        >>> print(f"报告生成{'成功' if success else '失败'}")
    """
```

#### generate_json_report()

```python
def generate_json_report(self, analysis_result: Dict[str, Any],
                        output_path: str) -> bool:
    """生成JSON报告

    Args:
        analysis_result: 分析结果数据
        output_path: 输出文件路径

    Returns:
        bool: 生成是否成功

    Example:
        >>> success = report_generator.generate_json_report(
        ...     analysis_result,
        ...     'reports/test_report.json'
        ... )
    """
```

#### generate_csv_report()

```python
def generate_csv_report(self, analysis_result: Dict[str, Any],
                       output_path: str) -> bool:
    """生成CSV报告

    Args:
        analysis_result: 分析结果数据
        output_path: 输出文件路径

    Returns:
        bool: 生成是否成功

    Example:
        >>> success = report_generator.generate_csv_report(
        ...     analysis_result,
        ...     'reports/test_report.csv'
        ... )
    """
```

#### generate_markdown_report()

```python
def generate_markdown_report(self, analysis_result: Dict[str, Any],
                            output_path: str) -> bool:
    """生成Markdown报告

    Args:
        analysis_result: 分析结果数据
        output_path: 输出文件路径

    Returns:
        bool: 生成是否成功

    Example:
        >>> success = report_generator.generate_markdown_report(
        ...     analysis_result,
        ...     'reports/test_report.md'
        ... )
    """
```

## 🔧 工具函数

### 指标计算工具

```python
from src.analysis.metrics_calculator import MetricsCalculator

class MetricsCalculator:
    """指标计算工具类"""

    @staticmethod
    def calculate_percentiles(values: List[float],
                             percentiles: List[int] = [50, 90, 95, 99]) -> Dict[str, float]:
        """计算百分位数

        Args:
            values: 数值列表
            percentiles: 百分位数列表

        Returns:
            Dict[str, float]: 百分位数结果
        """

    @staticmethod
    def calculate_statistics(values: List[float]) -> Dict[str, float]:
        """计算基础统计指标

        Args:
            values: 数值列表

        Returns:
            Dict[str, float]: 统计结果
                - mean: 平均值
                - median: 中位数
                - std_dev: 标准差
                - variance: 方差
                - min: 最小值
                - max: 最大值
        """
```

## 📊 使用示例

### 完整分析流程

```python
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.analysis.trend_analyzer import TrendAnalyzer
from src.analysis.report_generator import ReportGenerator

# 1. 创建分析器
analyzer = PerformanceAnalyzer()
trend_analyzer = TrendAnalyzer()
report_generator = ReportGenerator()

# 2. 准备测试数据
test_data = {
    'test_name': 'API性能测试',
    'start_time': '2024-01-01 10:00:00',
    'end_time': '2024-01-01 10:30:00',
    'duration': 1800,
    'users': 100,
    'requests': [
        # ... 请求数据
    ]
}

# 3. 执行性能分析
analysis_result = analyzer.comprehensive_analysis(test_data)

# 4. 趋势分析（如果有历史数据）
if historical_data:
    trend_result = trend_analyzer.analyze_historical_trend(historical_data)
    analysis_result['trend_analysis'] = trend_result

# 5. 生成报告
report_generator.generate_html_report(analysis_result, 'reports/performance_report.html')
report_generator.generate_json_report(analysis_result, 'reports/performance_report.json')

print(f"性能分析完成，总体评级: {analysis_result['overall_grade']}")
```

### 自定义配置示例

```python
# 自定义分析配置
custom_config = {
    'response_time_thresholds': {
        'excellent': 300,    # 更严格的响应时间要求
        'good': 800,
        'acceptable': 1500,
        'poor': 3000
    },
    'weights': {
        'response_time': 0.5,  # 更重视响应时间
        'throughput': 0.2,
        'error_rate': 0.2,
        'stability': 0.1
    }
}

analyzer = PerformanceAnalyzer(custom_config)
```

## ⚠️ 注意事项

1. **数据格式**: 确保输入数据格式正确，特别是时间戳格式
2. **内存使用**: 大量数据分析时注意内存使用情况
3. **并发安全**: 分析器实例不是线程安全的，多线程使用时需要注意
4. **配置验证**: 自定义配置时确保参数合理性
5. **异常处理**: 建议在调用API时添加适当的异常处理

## 🔗 相关文档

- [监控告警API](monitoring.md) - 监控告警模块API
- [数据管理API](data-manager.md) - 数据管理模块API
- [插件接口API](plugins.md) - 插件开发接口
- [配置参考](../configuration/framework-config.md) - 详细配置说明
