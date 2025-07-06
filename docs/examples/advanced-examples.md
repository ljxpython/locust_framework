# 高级示例

本文档提供Locust性能测试框架的高级使用示例，涵盖复杂场景、高级功能和实际项目应用案例。

## 🎯 目标读者

- 有一定Locust使用经验的开发者
- 需要实现复杂测试场景的测试工程师
- 希望深入了解框架高级功能的用户

## 📋 前置条件

- 已完成[基础示例](basic-examples.md)的学习
- 熟悉Python编程和面向对象概念
- 了解HTTP协议和Web服务架构
- 具备性能测试基础知识

## 🚀 高级负载模式

### 1. 自适应负载模式

```python
# locustfiles/adaptive_load_shape.py
from locust import LoadTestShape
import time
import requests

class AdaptiveLoadShape(LoadTestShape):
    """
    自适应负载模式 - 根据系统响应时间动态调整负载
    """

    def __init__(self):
        super().__init__()
        self.start_time = time.time()
        self.current_users = 10
        self.max_users = 1000
        self.min_users = 5
        self.target_response_time = 500  # 目标响应时间(ms)
        self.adjustment_interval = 30  # 调整间隔(秒)
        self.last_adjustment = 0

    def tick(self):
        run_time = time.time() - self.start_time

        # 每30秒调整一次负载
        if run_time - self.last_adjustment >= self.adjustment_interval:
            self.adjust_load()
            self.last_adjustment = run_time

        if run_time < 3600:  # 运行1小时
            return (self.current_users, 5)
        else:
            return None

    def adjust_load(self):
        """根据当前性能指标调整负载"""
        try:
            # 获取当前统计信息
            stats = self.runner.stats.total

            if stats.num_requests > 0:
                avg_response_time = stats.avg_response_time
                error_rate = stats.num_failures / stats.num_requests

                # 根据响应时间调整
                if avg_response_time > self.target_response_time * 1.2:
                    # 响应时间过高，减少用户数
                    self.current_users = max(
                        self.min_users,
                        int(self.current_users * 0.9)
                    )
                    print(f"High response time ({avg_response_time:.2f}ms), reducing users to {self.current_users}")

                elif avg_response_time < self.target_response_time * 0.8 and error_rate < 0.01:
                    # 响应时间良好且错误率低，增加用户数
                    self.current_users = min(
                        self.max_users,
                        int(self.current_users * 1.1)
                    )
                    print(f"Good performance, increasing users to {self.current_users}")

        except Exception as e:
            print(f"Error adjusting load: {e}")

class AdaptiveUser(HttpUser):
    """自适应用户行为"""

    wait_time = between(1, 3)

    def on_start(self):
        """用户启动时的初始化"""
        self.login()

    def login(self):
        """用户登录"""
        response = self.client.post("/auth/login", json={
            "username": f"user_{random.randint(1, 10000)}",
            "password": "password123"
        })

        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

    @task(3)
    def browse_products(self):
        """浏览产品"""
        # 获取产品列表
        response = self.client.get("/api/products", params={
            "page": random.randint(1, 10),
            "limit": 20
        })

        if response.status_code == 200:
            products = response.json().get("products", [])

            # 随机查看产品详情
            if products:
                product = random.choice(products)
                self.client.get(f"/api/products/{product['id']}")

    @task(2)
    def search_products(self):
        """搜索产品"""
        keywords = ["laptop", "phone", "tablet", "camera", "headphones"]
        keyword = random.choice(keywords)

        self.client.get("/api/search", params={
            "q": keyword,
            "sort": random.choice(["price", "rating", "popularity"])
        })

    @task(1)
    def add_to_cart(self):
        """添加到购物车"""
        # 先获取一个产品
        response = self.client.get("/api/products", params={"limit": 1})

        if response.status_code == 200:
            products = response.json().get("products", [])
            if products:
                product = products[0]
                self.client.post("/api/cart/add", json={
                    "product_id": product["id"],
                    "quantity": random.randint(1, 3)
                })
```

### 2. 多阶段压力测试

```python
# locustfiles/multi_stage_stress.py
from locust import LoadTestShape, HttpUser, task, between
import time

class MultiStageStressShape(LoadTestShape):
    """
    多阶段压力测试模式
    模拟真实业务场景的负载变化
    """

    stages = [
        # 阶段1: 预热阶段
        {"duration": 300, "users": 50, "spawn_rate": 2, "name": "warmup"},

        # 阶段2: 正常负载
        {"duration": 600, "users": 200, "spawn_rate": 5, "name": "normal_load"},

        # 阶段3: 高峰负载
        {"duration": 900, "users": 500, "spawn_rate": 10, "name": "peak_load"},

        # 阶段4: 极限压力
        {"duration": 1200, "users": 1000, "spawn_rate": 20, "name": "stress_test"},

        # 阶段5: 恢复测试
        {"duration": 1500, "users": 100, "spawn_rate": -30, "name": "recovery"},

        # 阶段6: 稳定性测试
        {"duration": 2100, "users": 300, "spawn_rate": 5, "name": "stability"},
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                # 记录当前阶段信息
                if not hasattr(self, 'current_stage') or self.current_stage != stage["name"]:
                    self.current_stage = stage["name"]
                    print(f"Entering stage: {stage['name']} - Users: {stage['users']}, Duration: {stage['duration']}s")

                return (stage["users"], stage["spawn_rate"])

        return None

class StressTestUser(HttpUser):
    """压力测试用户"""

    wait_time = between(0.5, 2)

    def on_start(self):
        """用户初始化"""
        self.user_id = random.randint(1, 100000)
        self.session_data = {}
        self.login()

    def login(self):
        """用户登录"""
        with self.client.post("/auth/login", json={
            "username": f"stress_user_{self.user_id}",
            "password": "stress_test_password"
        }, catch_response=True) as response:
            if response.status_code == 200:
                self.session_data = response.json()
                self.client.headers.update({
                    "Authorization": f"Bearer {self.session_data.get('token')}"
                })
            else:
                response.failure(f"Login failed: {response.status_code}")

    @task(5)
    def high_frequency_api_calls(self):
        """高频API调用"""
        endpoints = [
            "/api/user/profile",
            "/api/notifications",
            "/api/dashboard/stats",
            "/api/recent/activities"
        ]

        for endpoint in random.sample(endpoints, random.randint(1, 3)):
            with self.client.get(endpoint, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"API call failed: {endpoint}")

    @task(3)
    def data_intensive_operations(self):
        """数据密集型操作"""
        # 大数据量查询
        self.client.get("/api/reports/large-dataset", params={
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "include_details": True
        })

        # 批量数据处理
        batch_data = [
            {"id": i, "value": f"data_{i}", "timestamp": time.time()}
            for i in range(100)
        ]

        self.client.post("/api/batch/process", json={
            "data": batch_data,
            "operation": "bulk_insert"
        })

    @task(2)
    def concurrent_operations(self):
        """并发操作测试"""
        import threading

        def concurrent_request(endpoint, data=None):
            if data:
                self.client.post(endpoint, json=data)
            else:
                self.client.get(endpoint)

        # 创建多个并发请求
        threads = []
        operations = [
            ("/api/concurrent/read", None),
            ("/api/concurrent/write", {"data": f"concurrent_data_{time.time()}"}),
            ("/api/concurrent/update", {"id": self.user_id, "status": "active"}),
        ]

        for endpoint, data in operations:
            thread = threading.Thread(target=concurrent_request, args=(endpoint, data))
            threads.append(thread)
            thread.start()

        # 等待所有请求完成
        for thread in threads:
            thread.join()

    @task(1)
    def memory_intensive_operations(self):
        """内存密集型操作"""
        # 请求大文件
        self.client.get("/api/files/large-download", stream=True)

        # 上传大文件
        large_data = "x" * (1024 * 1024)  # 1MB数据
        self.client.post("/api/files/upload", files={
            "file": ("large_file.txt", large_data, "text/plain")
        })
```

## 🔧 高级插件开发

### 1. 自定义性能分析插件

```python
# src/plugins/advanced_analysis.py
from src.core.plugin_base import AnalysisPlugin
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns

class AdvancedAnalysisPlugin(AnalysisPlugin):
    """高级性能分析插件"""

    def __init__(self):
        super().__init__()
        self.name = "advanced_analysis"
        self.version = "1.0.0"
        self.description = "Advanced statistical analysis and machine learning insights"

    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行高级分析"""
        results = {
            "statistical_analysis": self._statistical_analysis(data),
            "trend_analysis": self._trend_analysis(data),
            "anomaly_detection": self._anomaly_detection(data),
            "performance_prediction": self._performance_prediction(data),
            "bottleneck_analysis": self._bottleneck_analysis(data)
        }

        return results

    def _statistical_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """统计分析"""
        response_times = data.get("response_times", [])

        if not response_times:
            return {"error": "No response time data available"}

        # 转换为numpy数组
        rt_array = np.array(response_times)

        # 基础统计
        basic_stats = {
            "count": len(rt_array),
            "mean": np.mean(rt_array),
            "median": np.median(rt_array),
            "std": np.std(rt_array),
            "variance": np.var(rt_array),
            "min": np.min(rt_array),
            "max": np.max(rt_array),
            "range": np.max(rt_array) - np.min(rt_array)
        }

        # 百分位数
        percentiles = {
            f"p{p}": np.percentile(rt_array, p)
            for p in [50, 75, 90, 95, 99, 99.9]
        }

        # 分布检验
        distribution_tests = {
            "normality_test": stats.normaltest(rt_array),
            "skewness": stats.skew(rt_array),
            "kurtosis": stats.kurtosis(rt_array)
        }

        # 置信区间
        confidence_interval = stats.t.interval(
            0.95, len(rt_array)-1,
            loc=np.mean(rt_array),
            scale=stats.sem(rt_array)
        )

        return {
            "basic_stats": basic_stats,
            "percentiles": percentiles,
            "distribution_tests": distribution_tests,
            "confidence_interval_95": confidence_interval
        }

    def _trend_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """趋势分析"""
        timestamps = data.get("timestamps", [])
        response_times = data.get("response_times", [])

        if len(timestamps) != len(response_times) or len(timestamps) < 10:
            return {"error": "Insufficient data for trend analysis"}

        # 创建时间序列
        df = pd.DataFrame({
            "timestamp": pd.to_datetime(timestamps),
            "response_time": response_times
        })
        df.set_index("timestamp", inplace=True)

        # 移动平均
        df["ma_5"] = df["response_time"].rolling(window=5).mean()
        df["ma_20"] = df["response_time"].rolling(window=20).mean()

        # 趋势检测
        x = np.arange(len(df))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, df["response_time"])

        # 季节性分析（如果数据足够）
        seasonal_analysis = {}
        if len(df) >= 100:
            # 简单的周期性检测
            autocorr = [df["response_time"].autocorr(lag=i) for i in range(1, 25)]
            max_autocorr_lag = np.argmax(autocorr) + 1
            seasonal_analysis = {
                "potential_period": max_autocorr_lag,
                "autocorrelation": max(autocorr)
            }

        return {
            "trend": {
                "slope": slope,
                "r_squared": r_value**2,
                "p_value": p_value,
                "trend_direction": "increasing" if slope > 0 else "decreasing"
            },
            "moving_averages": {
                "ma_5_current": df["ma_5"].iloc[-1] if not df["ma_5"].isna().iloc[-1] else None,
                "ma_20_current": df["ma_20"].iloc[-1] if not df["ma_20"].isna().iloc[-1] else None
            },
            "seasonal_analysis": seasonal_analysis
        }

    def _anomaly_detection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """异常检测"""
        response_times = np.array(data.get("response_times", []))

        if len(response_times) < 20:
            return {"error": "Insufficient data for anomaly detection"}

        # Z-score方法
        z_scores = np.abs(stats.zscore(response_times))
        z_anomalies = np.where(z_scores > 3)[0]

        # IQR方法
        q1, q3 = np.percentile(response_times, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        iqr_anomalies = np.where(
            (response_times < lower_bound) | (response_times > upper_bound)
        )[0]

        # 移动窗口异常检测
        window_size = min(20, len(response_times) // 4)
        moving_anomalies = []

        for i in range(window_size, len(response_times)):
            window = response_times[i-window_size:i]
            current = response_times[i]

            if abs(current - np.mean(window)) > 2 * np.std(window):
                moving_anomalies.append(i)

        return {
            "z_score_anomalies": {
                "count": len(z_anomalies),
                "indices": z_anomalies.tolist(),
                "percentage": len(z_anomalies) / len(response_times) * 100
            },
            "iqr_anomalies": {
                "count": len(iqr_anomalies),
                "indices": iqr_anomalies.tolist(),
                "percentage": len(iqr_anomalies) / len(response_times) * 100
            },
            "moving_window_anomalies": {
                "count": len(moving_anomalies),
                "indices": moving_anomalies,
                "percentage": len(moving_anomalies) / len(response_times) * 100
            }
        }

    def _performance_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """性能预测"""
        user_counts = data.get("user_counts", [])
        response_times = data.get("response_times", [])

        if len(user_counts) != len(response_times) or len(user_counts) < 10:
            return {"error": "Insufficient data for performance prediction"}

        # 线性回归预测
        slope, intercept, r_value, p_value, std_err = stats.linregress(user_counts, response_times)

        # 预测不同用户数下的响应时间
        prediction_points = [100, 200, 500, 1000, 2000]
        predictions = {}

        for users in prediction_points:
            predicted_rt = slope * users + intercept
            predictions[f"users_{users}"] = {
                "predicted_response_time": predicted_rt,
                "confidence": r_value**2
            }

        # 容量预测（响应时间阈值）
        rt_thresholds = [500, 1000, 2000, 5000]  # ms
        capacity_predictions = {}

        for threshold in rt_thresholds:
            if slope > 0:
                predicted_users = (threshold - intercept) / slope
                capacity_predictions[f"rt_{threshold}ms"] = max(0, predicted_users)

        return {
            "regression_model": {
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_value**2,
                "p_value": p_value,
                "standard_error": std_err
            },
            "response_time_predictions": predictions,
            "capacity_predictions": capacity_predictions
        }

    def _bottleneck_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """瓶颈分析"""
        endpoint_stats = data.get("endpoint_stats", {})

        if not endpoint_stats:
            return {"error": "No endpoint statistics available"}

        # 分析各端点性能
        bottlenecks = []

        for endpoint, stats in endpoint_stats.items():
            avg_rt = stats.get("avg_response_time", 0)
            error_rate = stats.get("error_rate", 0)
            request_count = stats.get("request_count", 0)

            # 计算瓶颈分数
            bottleneck_score = (
                (avg_rt / 1000) * 0.4 +  # 响应时间权重40%
                error_rate * 0.4 +        # 错误率权重40%
                (request_count / 1000) * 0.2  # 请求量权重20%
            )

            bottlenecks.append({
                "endpoint": endpoint,
                "bottleneck_score": bottleneck_score,
                "avg_response_time": avg_rt,
                "error_rate": error_rate,
                "request_count": request_count
            })

        # 按瓶颈分数排序
        bottlenecks.sort(key=lambda x: x["bottleneck_score"], reverse=True)

        # 识别主要瓶颈
        top_bottlenecks = bottlenecks[:5]

        # 瓶颈分类
        performance_bottlenecks = [b for b in bottlenecks if b["avg_response_time"] > 1000]
        reliability_bottlenecks = [b for b in bottlenecks if b["error_rate"] > 0.05]

        return {
            "top_bottlenecks": top_bottlenecks,
            "performance_bottlenecks": performance_bottlenecks,
            "reliability_bottlenecks": reliability_bottlenecks,
            "total_endpoints_analyzed": len(endpoint_stats)
        }

    def generate_report(self, analysis_results: Dict[str, Any]) -> str:
        """生成高级分析报告"""
        report = []
        report.append("# 高级性能分析报告\n")

        # 统计分析部分
        if "statistical_analysis" in analysis_results:
            stats = analysis_results["statistical_analysis"]
            if "basic_stats" in stats:
                basic = stats["basic_stats"]
                report.append("## 统计分析")
                report.append(f"- 平均响应时间: {basic['mean']:.2f}ms")
                report.append(f"- 中位数响应时间: {basic['median']:.2f}ms")
                report.append(f"- 标准差: {basic['std']:.2f}ms")
                report.append(f"- 95%置信区间: {stats.get('confidence_interval_95', 'N/A')}")
                report.append("")

        # 趋势分析部分
        if "trend_analysis" in analysis_results:
            trend = analysis_results["trend_analysis"]
            if "trend" in trend:
                t = trend["trend"]
                report.append("## 趋势分析")
                report.append(f"- 趋势方向: {t['trend_direction']}")
                report.append(f"- R²值: {t['r_squared']:.4f}")
                report.append(f"- 统计显著性: {'显著' if t['p_value'] < 0.05 else '不显著'}")
                report.append("")

        # 异常检测部分
        if "anomaly_detection" in analysis_results:
            anomaly = analysis_results["anomaly_detection"]
            report.append("## 异常检测")
            if "z_score_anomalies" in anomaly:
                z_anom = anomaly["z_score_anomalies"]
                report.append(f"- Z-score异常: {z_anom['count']}个 ({z_anom['percentage']:.2f}%)")
            if "iqr_anomalies" in anomaly:
                iqr_anom = anomaly["iqr_anomalies"]
                report.append(f"- IQR异常: {iqr_anom['count']}个 ({iqr_anom['percentage']:.2f}%)")
            report.append("")

        # 瓶颈分析部分
        if "bottleneck_analysis" in analysis_results:
            bottleneck = analysis_results["bottleneck_analysis"]
            if "top_bottlenecks" in bottleneck:
                report.append("## 瓶颈分析")
                report.append("### 主要瓶颈端点:")
                for i, b in enumerate(bottleneck["top_bottlenecks"][:3], 1):
                    report.append(f"{i}. {b['endpoint']} (分数: {b['bottleneck_score']:.2f})")
                    report.append(f"   - 平均响应时间: {b['avg_response_time']:.2f}ms")
                    report.append(f"   - 错误率: {b['error_rate']:.2%}")
                report.append("")

        return "\n".join(report)
```
