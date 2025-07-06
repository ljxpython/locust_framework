# 故障排除指南

本文档提供了Locust性能测试框架常见问题的诊断和解决方案，帮助您快速定位和解决测试过程中遇到的问题。

## 🔍 问题诊断流程

### 快速诊断检查清单

```bash
# 1. 检查服务状态
docker-compose ps
systemctl status locust

# 2. 检查端口占用
netstat -tlnp | grep :8089
netstat -tlnp | grep :5557

# 3. 检查日志
tail -f logs/locust.log
docker-compose logs -f locust-master

# 4. 检查资源使用
top -p $(pgrep -f locust)
docker stats

# 5. 检查网络连接
curl -I http://localhost:8089/
ping target-host
```

## 🚨 常见问题及解决方案

### 1. 启动和连接问题

#### 问题：Locust无法启动

**症状**
```
Error: No module named 'locust'
ImportError: cannot import name 'HttpUser' from 'locust'
```

**解决方案**
```bash
# 检查Python环境
python --version
pip list | grep locust

# 重新安装依赖
pip install --upgrade locust
pip install -r requirements.txt

# 检查虚拟环境
source venv/bin/activate
which python
```

#### 问题：Worker无法连接到Master

**症状**
```
[ERROR] Failed to connect to the Locust master
ConnectionRefusedError: [Errno 111] Connection refused
```

**诊断步骤**
```python
# diagnostic_tools.py
import socket
import time

def check_master_connectivity(master_host, master_port=5557):
    """检查Master连接性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((master_host, master_port))
        sock.close()

        if result == 0:
            print(f"✅ Master {master_host}:{master_port} is reachable")
            return True
        else:
            print(f"❌ Master {master_host}:{master_port} is not reachable")
            return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def diagnose_network_issues():
    """网络问题诊断"""
    import subprocess

    # 检查DNS解析
    try:
        result = subprocess.run(['nslookup', 'locust-master'],
                              capture_output=True, text=True, timeout=10)
        print("DNS Resolution:")
        print(result.stdout)
    except Exception as e:
        print(f"DNS check failed: {e}")

    # 检查路由
    try:
        result = subprocess.run(['traceroute', 'locust-master'],
                              capture_output=True, text=True, timeout=30)
        print("Network Route:")
        print(result.stdout)
    except Exception as e:
        print(f"Route check failed: {e}")

# 使用诊断工具
if __name__ == "__main__":
    check_master_connectivity("locust-master")
    diagnose_network_issues()
```

**解决方案**
```bash
# 1. 检查防火墙设置
sudo ufw status
sudo iptables -L

# 2. 检查Docker网络
docker network ls
docker network inspect locust_default

# 3. 修复网络配置
docker-compose down
docker network prune
docker-compose up -d

# 4. 使用正确的主机名
# 在docker-compose.yml中确保服务名称正确
services:
  locust-master:
    environment:
      - LOCUST_MASTER_BIND_HOST=0.0.0.0
  locust-worker:
    environment:
      - LOCUST_MASTER_HOST=locust-master
```

### 2. 性能问题

#### 问题：响应时间异常高

**症状**
```
Average response time: 5000ms+
95th percentile: 10000ms+
```

**诊断工具**
```python
# performance_analyzer.py
import time
import statistics
from locust import events

class PerformanceAnalyzer:
    """性能分析器"""

    def __init__(self):
        self.response_times = []
        self.slow_requests = []
        self.error_patterns = {}

    def analyze_response_time(self, response_time, request_name):
        """分析响应时间"""
        self.response_times.append(response_time)

        # 记录慢请求
        if response_time > 3000:  # 3秒以上为慢请求
            self.slow_requests.append({
                'name': request_name,
                'response_time': response_time,
                'timestamp': time.time()
            })

    def get_performance_summary(self):
        """获取性能摘要"""
        if not self.response_times:
            return "No data available"

        return {
            'avg_response_time': statistics.mean(self.response_times),
            'median_response_time': statistics.median(self.response_times),
            'p95_response_time': self.percentile(self.response_times, 95),
            'p99_response_time': self.percentile(self.response_times, 99),
            'slow_requests_count': len(self.slow_requests),
            'slow_requests_percentage': len(self.slow_requests) / len(self.response_times) * 100
        }

    def percentile(self, data, p):
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def identify_bottlenecks(self):
        """识别性能瓶颈"""
        bottlenecks = []

        # 分析慢请求模式
        slow_endpoints = {}
        for req in self.slow_requests:
            endpoint = req['name']
            if endpoint not in slow_endpoints:
                slow_endpoints[endpoint] = []
            slow_endpoints[endpoint].append(req['response_time'])

        # 找出最慢的端点
        for endpoint, times in slow_endpoints.items():
            if len(times) > 5:  # 至少5个慢请求
                avg_time = statistics.mean(times)
                bottlenecks.append({
                    'endpoint': endpoint,
                    'avg_slow_time': avg_time,
                    'slow_count': len(times)
                })

        return sorted(bottlenecks, key=lambda x: x['avg_slow_time'], reverse=True)

# 集成到Locust测试中
analyzer = PerformanceAnalyzer()

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    if not exception:
        analyzer.analyze_response_time(response_time, name)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    summary = analyzer.get_performance_summary()
    bottlenecks = analyzer.identify_bottlenecks()

    print("\n=== Performance Analysis ===")
    print(f"Average Response Time: {summary['avg_response_time']:.2f}ms")
    print(f"95th Percentile: {summary['p95_response_time']:.2f}ms")
    print(f"Slow Requests: {summary['slow_requests_count']} ({summary['slow_requests_percentage']:.2f}%)")

    if bottlenecks:
        print("\n=== Performance Bottlenecks ===")
        for bottleneck in bottlenecks[:5]:  # 显示前5个
            print(f"- {bottleneck['endpoint']}: {bottleneck['avg_slow_time']:.2f}ms avg, {bottleneck['slow_count']} slow requests")
```

**解决方案**
```python
# 1. 优化连接池
from locust import HttpUser
import requests.adapters

class OptimizedUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 增加连接池大小
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=50,
            max_retries=3
        )
        self.client.mount("http://", adapter)
        self.client.mount("https://", adapter)

        # 设置合理的超时
        self.client.timeout = (10, 60)  # 连接超时10s，读取超时60s

# 2. 检查目标系统
# - 数据库连接池
# - 缓存配置
# - 服务器资源
# - 网络带宽

# 3. 分析系统瓶颈
def analyze_system_bottlenecks():
    """分析系统瓶颈"""
    import psutil

    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU Usage: {cpu_percent}%")

    # 内存使用率
    memory = psutil.virtual_memory()
    print(f"Memory Usage: {memory.percent}%")

    # 磁盘IO
    disk_io = psutil.disk_io_counters()
    print(f"Disk Read: {disk_io.read_bytes / 1024 / 1024:.2f}MB")
    print(f"Disk Write: {disk_io.write_bytes / 1024 / 1024:.2f}MB")

    # 网络IO
    net_io = psutil.net_io_counters()
    print(f"Network Sent: {net_io.bytes_sent / 1024 / 1024:.2f}MB")
    print(f"Network Recv: {net_io.bytes_recv / 1024 / 1024:.2f}MB")
```

#### 问题：错误率过高

**症状**
```
Error rate: 10%+
Connection errors, timeouts, 5xx responses
```

**错误分析工具**
```python
# error_analyzer.py
from collections import defaultdict
import re

class ErrorAnalyzer:
    """错误分析器"""

    def __init__(self):
        self.errors = defaultdict(list)
        self.error_patterns = {}

    def record_error(self, request_name, error_message, response_code=None):
        """记录错误"""
        error_info = {
            'timestamp': time.time(),
            'request_name': request_name,
            'error_message': str(error_message),
            'response_code': response_code
        }

        # 分类错误
        error_type = self.classify_error(error_message, response_code)
        self.errors[error_type].append(error_info)

    def classify_error(self, error_message, response_code):
        """分类错误类型"""
        error_msg = str(error_message).lower()

        if response_code:
            if 400 <= response_code < 500:
                return "client_error"
            elif 500 <= response_code < 600:
                return "server_error"

        if "timeout" in error_msg or "timed out" in error_msg:
            return "timeout_error"
        elif "connection" in error_msg:
            return "connection_error"
        elif "ssl" in error_msg or "certificate" in error_msg:
            return "ssl_error"
        elif "dns" in error_msg:
            return "dns_error"
        else:
            return "unknown_error"

    def get_error_summary(self):
        """获取错误摘要"""
        total_errors = sum(len(errors) for errors in self.errors.values())

        summary = {
            'total_errors': total_errors,
            'error_types': {}
        }

        for error_type, errors in self.errors.items():
            summary['error_types'][error_type] = {
                'count': len(errors),
                'percentage': len(errors) / total_errors * 100 if total_errors > 0 else 0,
                'recent_examples': [e['error_message'] for e in errors[-3:]]  # 最近3个例子
            }

        return summary

    def suggest_solutions(self):
        """建议解决方案"""
        suggestions = []

        for error_type, errors in self.errors.items():
            if len(errors) > 10:  # 错误数量较多时给出建议
                if error_type == "timeout_error":
                    suggestions.append("增加请求超时时间，检查网络延迟")
                elif error_type == "connection_error":
                    suggestions.append("检查连接池配置，增加最大连接数")
                elif error_type == "server_error":
                    suggestions.append("检查目标服务器状态，查看服务器日志")
                elif error_type == "client_error":
                    suggestions.append("检查请求参数和认证信息")
                elif error_type == "ssl_error":
                    suggestions.append("检查SSL证书配置和有效性")

        return suggestions

# 集成错误分析
error_analyzer = ErrorAnalyzer()

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    if exception:
        response_code = getattr(exception, 'response', {}).get('status_code')
        error_analyzer.record_error(name, exception, response_code)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    summary = error_analyzer.get_error_summary()
    suggestions = error_analyzer.suggest_solutions()

    print("\n=== Error Analysis ===")
    print(f"Total Errors: {summary['total_errors']}")

    for error_type, info in summary['error_types'].items():
        print(f"\n{error_type}: {info['count']} ({info['percentage']:.2f}%)")
        for example in info['recent_examples']:
            print(f"  - {example}")

    if suggestions:
        print("\n=== Suggested Solutions ===")
        for suggestion in suggestions:
            print(f"- {suggestion}")
```

### 3. 资源问题

#### 问题：内存使用过高

**症状**
```
Memory usage: 90%+
OOMKilled containers
Slow garbage collection
```

**内存监控工具**
```python
# memory_monitor.py
import psutil
import gc
import tracemalloc
from locust import events

class MemoryMonitor:
    """内存监控器"""

    def __init__(self):
        self.memory_snapshots = []
        self.gc_stats = []
        tracemalloc.start()

    def take_snapshot(self):
        """获取内存快照"""
        # 系统内存
        memory = psutil.virtual_memory()

        # 进程内存
        process = psutil.Process()
        process_memory = process.memory_info()

        # Python内存
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        snapshot_data = {
            'timestamp': time.time(),
            'system_memory_percent': memory.percent,
            'process_memory_mb': process_memory.rss / 1024 / 1024,
            'python_memory_mb': sum(stat.size for stat in top_stats) / 1024 / 1024,
            'top_memory_lines': [(stat.traceback.format()[-1], stat.size / 1024 / 1024)
                               for stat in top_stats[:5]]
        }

        self.memory_snapshots.append(snapshot_data)
        return snapshot_data

    def force_gc(self):
        """强制垃圾回收"""
        before = self.get_memory_usage()

        # 执行垃圾回收
        collected = gc.collect()

        after = self.get_memory_usage()

        gc_info = {
            'timestamp': time.time(),
            'objects_collected': collected,
            'memory_before_mb': before,
            'memory_after_mb': after,
            'memory_freed_mb': before - after
        }

        self.gc_stats.append(gc_info)
        return gc_info

    def get_memory_usage(self):
        """获取当前内存使用量"""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024

    def analyze_memory_leaks(self):
        """分析内存泄漏"""
        if len(self.memory_snapshots) < 2:
            return "Insufficient data for leak analysis"

        # 检查内存增长趋势
        memory_growth = []
        for i in range(1, len(self.memory_snapshots)):
            current = self.memory_snapshots[i]['process_memory_mb']
            previous = self.memory_snapshots[i-1]['process_memory_mb']
            growth = current - previous
            memory_growth.append(growth)

        avg_growth = sum(memory_growth) / len(memory_growth)

        if avg_growth > 10:  # 平均增长超过10MB
            return f"Potential memory leak detected. Average growth: {avg_growth:.2f}MB per snapshot"
        else:
            return "No significant memory leak detected"

# 使用内存监控
memory_monitor = MemoryMonitor()

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    memory_monitor.take_snapshot()

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    final_snapshot = memory_monitor.take_snapshot()
    leak_analysis = memory_monitor.analyze_memory_leaks()

    print("\n=== Memory Analysis ===")
    print(f"Final Memory Usage: {final_snapshot['process_memory_mb']:.2f}MB")
    print(f"System Memory Usage: {final_snapshot['system_memory_percent']:.2f}%")
    print(f"Leak Analysis: {leak_analysis}")

    # 强制垃圾回收
    gc_info = memory_monitor.force_gc()
    print(f"GC Freed: {gc_info['memory_freed_mb']:.2f}MB")
```

**解决方案**
```python
# 1. 优化内存使用
class MemoryOptimizedUser(HttpUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_count = 0

    @task
    def memory_efficient_request(self):
        # 使用流式处理大响应
        with self.client.get("/large-data", stream=True) as response:
            for chunk in response.iter_content(chunk_size=8192):
                # 处理数据块
                pass

        self.request_count += 1

        # 定期清理
        if self.request_count % 100 == 0:
            gc.collect()

# 2. 配置垃圾回收
import gc

# 调整垃圾回收阈值
gc.set_threshold(700, 10, 10)

# 3. 限制容器内存
# 在docker-compose.yml中
services:
  locust-worker:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## 🛠️ 调试工具

### 1. 实时监控脚本

```bash
#!/bin/bash
# monitor.sh

echo "Locust Real-time Monitor"
echo "======================="

while true; do
    clear
    echo "$(date)"
    echo "======================="

    # 服务状态
    echo "Service Status:"
    docker-compose ps
    echo ""

    # 资源使用
    echo "Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
    echo ""

    # 最新日志
    echo "Recent Logs:"
    docker-compose logs --tail=5 locust-master
    echo ""

    sleep 10
done
```

### 2. 性能基准测试

```python
# benchmark.py
import time
import statistics
from locust import HttpUser, task, between

class BenchmarkUser(HttpUser):
    """基准测试用户"""

    wait_time = between(1, 2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_times = []

    @task
    def benchmark_request(self):
        """基准测试请求"""
        start_time = time.time()

        try:
            response = self.client.get("/api/health")
            response_time = (time.time() - start_time) * 1000

            self.response_times.append(response_time)

            # 每100个请求输出统计
            if len(self.response_times) % 100 == 0:
                self.print_stats()

        except Exception as e:
            print(f"Request failed: {e}")

    def print_stats(self):
        """输出统计信息"""
        if self.response_times:
            avg = statistics.mean(self.response_times)
            median = statistics.median(self.response_times)
            p95 = self.percentile(self.response_times, 95)

            print(f"Stats (last {len(self.response_times)} requests):")
            print(f"  Avg: {avg:.2f}ms, Median: {median:.2f}ms, P95: {p95:.2f}ms")

    def percentile(self, data, p):
        """计算百分位数"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
```

## 📚 故障预防

### 1. 健康检查

```python
# health_check.py
import requests
import time
from typing import Dict, List

class HealthChecker:
    """健康检查器"""

    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints
        self.health_history = {}

    def check_endpoint(self, endpoint: str) -> Dict:
        """检查单个端点"""
        try:
            start_time = time.time()
            response = requests.get(endpoint, timeout=10)
            response_time = (time.time() - start_time) * 1000

            return {
                'endpoint': endpoint,
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status': 'error',
                'error': str(e),
                'timestamp': time.time()
            }

    def check_all_endpoints(self) -> List[Dict]:
        """检查所有端点"""
        results = []
        for endpoint in self.endpoints:
            result = self.check_endpoint(endpoint)
            results.append(result)

            # 记录历史
            if endpoint not in self.health_history:
                self.health_history[endpoint] = []
            self.health_history[endpoint].append(result)

            # 保持历史记录在合理范围内
            if len(self.health_history[endpoint]) > 100:
                self.health_history[endpoint].pop(0)

        return results

    def get_health_summary(self) -> Dict:
        """获取健康状况摘要"""
        summary = {}

        for endpoint, history in self.health_history.items():
            if history:
                healthy_count = sum(1 for h in history if h.get('status') == 'healthy')
                total_count = len(history)
                uptime_percentage = (healthy_count / total_count) * 100

                recent_response_times = [h.get('response_time', 0) for h in history[-10:]
                                       if h.get('response_time')]
                avg_response_time = sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0

                summary[endpoint] = {
                    'uptime_percentage': uptime_percentage,
                    'avg_response_time': avg_response_time,
                    'total_checks': total_count,
                    'last_status': history[-1].get('status')
                }

        return summary

# 使用健康检查
health_checker = HealthChecker([
    "http://localhost:8089/",
    "http://localhost:8089/stats/requests",
    "https://target-api.com/health"
])

def run_health_checks():
    """运行健康检查"""
    results = health_checker.check_all_endpoints()

    print("Health Check Results:")
    for result in results:
        status_icon = "✅" if result['status'] == 'healthy' else "❌"
        print(f"{status_icon} {result['endpoint']}: {result['status']}")

        if 'response_time' in result:
            print(f"   Response time: {result['response_time']:.2f}ms")
        if 'error' in result:
            print(f"   Error: {result['error']}")

    # 显示摘要
    summary = health_checker.get_health_summary()
    print("\nHealth Summary:")
    for endpoint, stats in summary.items():
        print(f"{endpoint}: {stats['uptime_percentage']:.2f}% uptime, {stats['avg_response_time']:.2f}ms avg")

if __name__ == "__main__":
    run_health_checks()
```

## 🎉 总结

有效的故障排除需要：

1. **系统化诊断**: 遵循标准的问题诊断流程
2. **工具支持**: 使用专业的监控和分析工具
3. **预防措施**: 建立健康检查和监控机制
4. **知识积累**: 记录和分享故障处理经验
5. **持续改进**: 根据问题反馈优化系统设计

## 📚 相关文档

- [最佳实践](best-practices.md) - 避免常见问题的最佳实践
- [监控配置](../configuration/monitoring-config.md) - 监控系统配置
- [生产环境配置](../configuration/production.md) - 生产环境部署
- [常见问题解答](faq.md) - 常见问题快速解答
