# 测试指南

本文档详细介绍框架的测试策略、测试工具使用、测试最佳实践等内容。

## 🎯 测试策略

### 测试金字塔

```
    /\
   /  \     E2E Tests (端到端测试)
  /____\    Integration Tests (集成测试)
 /______\   Unit Tests (单元测试)
/__________\
```

- **单元测试 (70%)**: 测试单个函数、方法、类
- **集成测试 (20%)**: 测试模块间交互
- **端到端测试 (10%)**: 测试完整用户场景

### 测试分类

```python
# 测试标记分类
pytest.mark.unit        # 单元测试
pytest.mark.integration # 集成测试
pytest.mark.e2e         # 端到端测试
pytest.mark.slow        # 慢速测试
pytest.mark.smoke       # 冒烟测试
pytest.mark.regression  # 回归测试
```

## 🧪 单元测试

### 测试结构

```python
# tests/unit/test_performance_analyzer.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.exceptions import AnalysisError

class TestPerformanceAnalyzer:
    """性能分析器单元测试"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.analyzer = PerformanceAnalyzer()
        self.sample_data = {
            'test_name': 'API性能测试',
            'start_time': '2023-12-01 10:00:00',
            'end_time': '2023-12-01 10:10:00',
            'duration': 600,
            'users': 50,
            'requests': [
                {'response_time': 100, 'success': True, 'timestamp': '2023-12-01 10:01:00'},
                {'response_time': 200, 'success': True, 'timestamp': '2023-12-01 10:02:00'},
                {'response_time': 150, 'success': False, 'timestamp': '2023-12-01 10:03:00'}
            ]
        }

    def teardown_method(self):
        """每个测试方法后执行"""
        # 清理资源
        pass

    @pytest.mark.unit
    def test_analyze_performance_success(self):
        """测试性能分析成功场景"""
        # Given
        expected_grade = 'B'

        # When
        result = self.analyzer.comprehensive_analysis(self.sample_data)

        # Then
        assert result is not None
        assert result['overall_grade'] == expected_grade
        assert 'response_time' in result
        assert 'throughput' in result
        assert 'error_analysis' in result
        assert 'recommendations' in result

    @pytest.mark.unit
    def test_analyze_empty_requests(self):
        """测试空请求列表"""
        # Given
        empty_data = self.sample_data.copy()
        empty_data['requests'] = []

        # When & Then
        with pytest.raises(AnalysisError, match="请求数据不能为空"):
            self.analyzer.comprehensive_analysis(empty_data)

    @pytest.mark.unit
    @pytest.mark.parametrize("response_times,expected_grade", [
        ([50, 80, 60, 70, 90], 'A'),      # 优秀
        ([100, 200, 150, 180, 120], 'B'), # 良好
        ([300, 400, 350, 380, 320], 'C'), # 一般
        ([800, 900, 850, 880, 820], 'D'), # 较差
    ])
    def test_grading_algorithm(self, response_times, expected_grade):
        """参数化测试评级算法"""
        # Given
        test_data = self.sample_data.copy()
        test_data['requests'] = [
            {'response_time': rt, 'success': True, 'timestamp': '2023-12-01 10:01:00'}
            for rt in response_times
        ]

        # When
        result = self.analyzer.comprehensive_analysis(test_data)

        # Then
        assert result['overall_grade'] == expected_grade

    @pytest.mark.unit
    @patch('src.analysis.performance_analyzer.calculate_percentile')
    def test_response_time_calculation_with_mock(self, mock_percentile):
        """使用Mock测试响应时间计算"""
        # Given
        mock_percentile.side_effect = [50.0, 95.0, 99.0]  # P50, P95, P99

        # When
        result = self.analyzer.comprehensive_analysis(self.sample_data)

        # Then
        assert mock_percentile.call_count == 3
        assert result['response_time']['p50'] == 50.0
        assert result['response_time']['p95'] == 95.0
        assert result['response_time']['p99'] == 99.0

    @pytest.mark.unit
    def test_error_rate_calculation(self):
        """测试错误率计算"""
        # Given
        test_data = self.sample_data.copy()
        test_data['requests'] = [
            {'response_time': 100, 'success': True, 'timestamp': '2023-12-01 10:01:00'},
            {'response_time': 200, 'success': False, 'timestamp': '2023-12-01 10:02:00'},
            {'response_time': 150, 'success': False, 'timestamp': '2023-12-01 10:03:00'},
            {'response_time': 180, 'success': True, 'timestamp': '2023-12-01 10:04:00'}
        ]

        # When
        result = self.analyzer.comprehensive_analysis(test_data)

        # Then
        expected_error_rate = 50.0  # 2/4 = 50%
        assert result['error_analysis']['error_rate'] == expected_error_rate

    @pytest.mark.unit
    def test_throughput_calculation(self):
        """测试吞吐量计算"""
        # Given
        test_data = self.sample_data.copy()
        test_data['duration'] = 60  # 60秒
        test_data['requests'] = [
            {'response_time': 100, 'success': True, 'timestamp': '2023-12-01 10:01:00'}
            for _ in range(120)  # 120个请求
        ]

        # When
        result = self.analyzer.comprehensive_analysis(test_data)

        # Then
        expected_tps = 2.0  # 120请求 / 60秒 = 2 TPS
        assert result['throughput']['requests_per_second'] == expected_tps
```

### 测试工具和技巧

```python
# 使用fixtures
@pytest.fixture
def sample_analyzer():
    """分析器fixture"""
    return PerformanceAnalyzer()

@pytest.fixture
def sample_test_data():
    """测试数据fixture"""
    return {
        'requests': [
            {'response_time': 100, 'success': True},
            {'response_time': 200, 'success': True}
        ],
        'duration': 60,
        'users': 10
    }

# 使用临时文件
@pytest.fixture
def temp_config_file(tmp_path):
    """临时配置文件"""
    config_file = tmp_path / "test_config.toml"
    config_file.write_text("""
    [analysis]
    threshold = 1000
    """)
    return str(config_file)

# 使用Mock对象
def test_with_mock_dependencies():
    """使用Mock测试依赖"""
    # Given
    mock_data_provider = Mock()
    mock_data_provider.get_test_data.return_value = {'requests': []}

    analyzer = PerformanceAnalyzer(data_provider=mock_data_provider)

    # When
    result = analyzer.load_and_analyze('test_id')

    # Then
    mock_data_provider.get_test_data.assert_called_once_with('test_id')

# 异常测试
def test_exception_handling():
    """测试异常处理"""
    analyzer = PerformanceAnalyzer()

    with pytest.raises(ValueError, match="无效的测试数据"):
        analyzer.comprehensive_analysis(None)

# 属性测试
@pytest.mark.property
@given(st.lists(st.integers(min_value=1, max_value=5000), min_size=1))
def test_response_time_analysis_property(response_times):
    """属性测试：响应时间分析"""
    # Given
    test_data = {
        'requests': [{'response_time': rt, 'success': True} for rt in response_times],
        'duration': 60,
        'users': 10
    }

    analyzer = PerformanceAnalyzer()

    # When
    result = analyzer.comprehensive_analysis(test_data)

    # Then
    assert result['response_time']['min'] == min(response_times)
    assert result['response_time']['max'] == max(response_times)
    assert result['response_time']['avg'] == sum(response_times) / len(response_times)
```

## 🔗 集成测试

### 模块间集成测试

```python
# tests/integration/test_analysis_integration.py
import pytest
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.data_manager.data_provider import DataProvider
from src.monitoring.performance_monitor import PerformanceMonitor

class TestAnalysisIntegration:
    """分析模块集成测试"""

    @pytest.fixture
    def integrated_system(self):
        """集成系统fixture"""
        data_provider = DataProvider()
        monitor = PerformanceMonitor()
        analyzer = PerformanceAnalyzer(
            data_provider=data_provider,
            monitor=monitor
        )
        return {
            'data_provider': data_provider,
            'monitor': monitor,
            'analyzer': analyzer
        }

    @pytest.mark.integration
    def test_end_to_end_analysis_flow(self, integrated_system):
        """端到端分析流程测试"""
        # Given
        system = integrated_system
        test_data_file = "tests/fixtures/sample_test_data.json"

        # When
        # 1. 加载测试数据
        system['data_provider'].load_data_from_file(test_data_file)

        # 2. 启动监控
        system['monitor'].start_monitoring()

        # 3. 执行分析
        test_data = system['data_provider'].get_test_data('sample_test')
        result = system['analyzer'].comprehensive_analysis(test_data)

        # 4. 停止监控
        system['monitor'].stop_monitoring()

        # Then
        assert result is not None
        assert 'overall_grade' in result
        assert result['overall_grade'] in ['A', 'B', 'C', 'D']

    @pytest.mark.integration
    def test_data_flow_between_modules(self, integrated_system):
        """测试模块间数据流"""
        # Given
        system = integrated_system

        # When
        # 模拟数据在模块间流转
        raw_data = {'requests': [{'response_time': 100, 'success': True}]}
        system['data_provider'].store_test_data('test_001', raw_data)

        retrieved_data = system['data_provider'].get_test_data('test_001')
        analysis_result = system['analyzer'].comprehensive_analysis(retrieved_data)

        # Then
        assert retrieved_data == raw_data
        assert analysis_result is not None
```

### 数据库集成测试

```python
# tests/integration/test_database_integration.py
import pytest
import sqlite3
from src.data_manager.data_provider import DataProvider

class TestDatabaseIntegration:
    """数据库集成测试"""

    @pytest.fixture
    def test_database(self, tmp_path):
        """测试数据库fixture"""
        db_path = tmp_path / "test.db"
        conn = sqlite3.connect(str(db_path))

        # 创建测试表
        conn.execute("""
            CREATE TABLE test_results (
                id INTEGER PRIMARY KEY,
                test_name TEXT,
                response_time REAL,
                success BOOLEAN,
                timestamp TEXT
            )
        """)

        # 插入测试数据
        test_data = [
            ('API测试', 100.5, True, '2023-12-01 10:00:00'),
            ('API测试', 200.3, True, '2023-12-01 10:01:00'),
            ('API测试', 150.8, False, '2023-12-01 10:02:00')
        ]

        conn.executemany(
            "INSERT INTO test_results (test_name, response_time, success, timestamp) VALUES (?, ?, ?, ?)",
            test_data
        )
        conn.commit()
        conn.close()

        return str(db_path)

    @pytest.mark.integration
    def test_load_data_from_database(self, test_database):
        """测试从数据库加载数据"""
        # Given
        provider = DataProvider()
        connection_string = f"sqlite:///{test_database}"
        query = "SELECT * FROM test_results WHERE test_name = 'API测试'"

        # When
        success = provider.load_data_from_database(
            connection_string, query, "db_test_data"
        )

        # Then
        assert success is True

        # 验证数据加载
        data = provider.get_next_data("db_test_data")
        assert data is not None
        assert 'response_time' in data
        assert 'success' in data
```

## 🌐 端到端测试

### 完整场景测试

```python
# tests/e2e/test_complete_workflow.py
import pytest
import subprocess
import time
import requests
from pathlib import Path

class TestCompleteWorkflow:
    """完整工作流程端到端测试"""

    @pytest.fixture(scope="class")
    def locust_server(self):
        """启动Locust服务器"""
        # 启动Locust Web UI
        process = subprocess.Popen([
            'locust',
            '-f', 'tests/e2e/fixtures/test_locustfile.py',
            '--web-host', '127.0.0.1',
            '--web-port', '8089',
            '--headless'
        ])

        # 等待服务器启动
        time.sleep(5)

        yield process

        # 清理
        process.terminate()
        process.wait()

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_complete_performance_test_workflow(self, locust_server):
        """测试完整的性能测试工作流程"""
        base_url = "http://127.0.0.1:8089"

        # 1. 启动测试
        start_response = requests.post(f"{base_url}/swarm", data={
            'user_count': 10,
            'spawn_rate': 2,
            'host': 'http://httpbin.org'
        })
        assert start_response.status_code == 200

        # 2. 等待测试运行
        time.sleep(30)

        # 3. 检查统计信息
        stats_response = requests.get(f"{base_url}/stats/requests")
        assert stats_response.status_code == 200

        stats_data = stats_response.json()
        assert 'stats' in stats_data
        assert len(stats_data['stats']) > 0

        # 4. 停止测试
        stop_response = requests.get(f"{base_url}/stop")
        assert stop_response.status_code == 200

        # 5. 验证报告生成
        reports_dir = Path("reports")
        assert reports_dir.exists()

        # 检查是否生成了性能报告
        html_reports = list(reports_dir.glob("*.html"))
        assert len(html_reports) > 0
```

### API测试

```python
# tests/e2e/test_api_endpoints.py
import pytest
import requests

class TestAPIEndpoints:
    """API端点端到端测试"""

    @pytest.fixture
    def api_base_url(self):
        """API基础URL"""
        return "http://localhost:8089"

    @pytest.mark.e2e
    def test_web_ui_endpoints(self, api_base_url):
        """测试Web UI端点"""
        endpoints = [
            "/",
            "/stats/requests",
            "/stats/distribution",
            "/exceptions"
        ]

        for endpoint in endpoints:
            response = requests.get(f"{api_base_url}{endpoint}")
            assert response.status_code == 200

    @pytest.mark.e2e
    def test_api_workflow(self, api_base_url):
        """测试API工作流程"""
        # 1. 获取初始状态
        status_response = requests.get(f"{api_base_url}/stats/requests")
        assert status_response.status_code == 200

        # 2. 启动测试
        start_data = {
            'user_count': 5,
            'spawn_rate': 1,
            'host': 'http://httpbin.org'
        }
        start_response = requests.post(f"{api_base_url}/swarm", data=start_data)
        assert start_response.status_code == 200

        # 3. 检查运行状态
        time.sleep(10)
        running_stats = requests.get(f"{api_base_url}/stats/requests")
        assert running_stats.status_code == 200

        # 4. 停止测试
        stop_response = requests.get(f"{api_base_url}/stop")
        assert stop_response.status_code == 200
```

## 🚀 性能测试

### 基准测试

```python
# tests/performance/test_benchmarks.py
import pytest
import time
from src.analysis.performance_analyzer import PerformanceAnalyzer

class TestPerformanceBenchmarks:
    """性能基准测试"""

    @pytest.mark.benchmark
    def test_analysis_performance(self, benchmark):
        """测试分析性能"""
        # Given
        analyzer = PerformanceAnalyzer()
        large_dataset = {
            'requests': [
                {'response_time': i % 1000, 'success': True}
                for i in range(10000)
            ],
            'duration': 600,
            'users': 100
        }

        # When & Then
        result = benchmark(analyzer.comprehensive_analysis, large_dataset)
        assert result is not None

    @pytest.mark.benchmark
    def test_data_processing_performance(self, benchmark):
        """测试数据处理性能"""
        from src.data_manager.data_generator import DataGenerator

        generator = DataGenerator()

        def generate_large_dataset():
            return [generator.generate_user_profile() for _ in range(1000)]

        result = benchmark(generate_large_dataset)
        assert len(result) == 1000
```

### 内存测试

```python
# tests/performance/test_memory_usage.py
import pytest
import psutil
import os
from src.analysis.performance_analyzer import PerformanceAnalyzer

class TestMemoryUsage:
    """内存使用测试"""

    def get_memory_usage(self):
        """获取当前内存使用量"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB

    @pytest.mark.memory
    def test_memory_leak_in_analysis(self):
        """测试分析过程中的内存泄漏"""
        analyzer = PerformanceAnalyzer()

        initial_memory = self.get_memory_usage()

        # 执行多次分析
        for i in range(100):
            test_data = {
                'requests': [
                    {'response_time': j, 'success': True}
                    for j in range(100)
                ],
                'duration': 60,
                'users': 10
            }
            analyzer.comprehensive_analysis(test_data)

        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory

        # 内存增长不应超过50MB
        assert memory_increase < 50, f"内存泄漏检测：增长了 {memory_increase:.2f}MB"
```

## 🔧 测试工具配置

### pytest配置

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --strict-config
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    smoke: Smoke tests
    regression: Regression tests
    benchmark: Performance benchmark tests
    memory: Memory usage tests
    property: Property-based tests

filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

### 测试数据管理

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_test_data(test_data_dir):
    """示例测试数据"""
    data_file = test_data_dir / "sample_test_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

@pytest.fixture
def temp_reports_dir(tmp_path):
    """临时报告目录"""
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir()
    return reports_dir

# 数据库测试fixture
@pytest.fixture(scope="session")
def test_database():
    """测试数据库"""
    # 设置测试数据库
    # 返回数据库连接信息
    pass
```

## 📊 测试报告

### 覆盖率报告

```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 查看HTML报告
open htmlcov/index.html
```

### 测试结果分析

```python
# tests/utils/test_reporter.py
class TestReporter:
    """测试结果报告器"""

    def generate_test_summary(self, test_results):
        """生成测试摘要"""
        summary = {
            'total_tests': len(test_results),
            'passed': len([t for t in test_results if t.passed]),
            'failed': len([t for t in test_results if t.failed]),
            'skipped': len([t for t in test_results if t.skipped]),
            'coverage': self.calculate_coverage(),
            'duration': sum(t.duration for t in test_results)
        }
        return summary

    def generate_html_report(self, summary, output_path):
        """生成HTML测试报告"""
        # 生成详细的HTML报告
        pass
```

## ⚠️ 测试最佳实践

1. **测试命名**: 使用描述性的测试名称
2. **测试隔离**: 每个测试应该独立运行
3. **数据清理**: 测试后清理临时数据
4. **Mock使用**: 合理使用Mock隔离依赖
5. **断言明确**: 使用明确的断言消息
6. **性能考虑**: 避免测试运行时间过长
7. **持续集成**: 集成到CI/CD流程中

## 🔗 相关文档

- [开发环境搭建](setup.md) - 测试环境配置
- [编码规范](coding-standards.md) - 测试代码规范
- [贡献指南](contributing.md) - 测试贡献流程
- [性能优化](performance-tuning.md) - 性能测试指南
