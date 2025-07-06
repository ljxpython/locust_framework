# 负载模式开发指南

本指南详细介绍如何开发自定义负载模式，扩展框架的负载控制能力。

## 🎯 开发目标

通过本指南，您将学会：
- 理解负载模式的设计原理
- 开发自定义负载模式
- 实现复杂的负载控制逻辑
- 集成和测试负载模式
- 遵循最佳实践和规范

## 📚 基础概念

### 负载模式架构

负载模式基于Locust的LoadTestShape类，提供了灵活的负载控制机制：

```python
from locust import LoadTestShape
from typing import Tuple, Optional

class CustomLoadShape(LoadTestShape):
    """自定义负载模式基类"""

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        核心方法：返回当前时刻的负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率) 或 None表示测试结束
        """
        pass
```

### 核心组件

1. **时间管理**: 跟踪测试运行时间
2. **用户数控制**: 动态调整并发用户数
3. **生成速率控制**: 控制用户生成的速度
4. **状态管理**: 维护负载模式的内部状态
5. **配置验证**: 验证负载模式参数的有效性

## 🔧 开发基础负载模式

### 1. 线性增长负载模式

```python
from locust import LoadTestShape
from typing import Tuple, Optional
import time

class LinearLoadShape(LoadTestShape):
    """线性增长负载模式"""

    def __init__(self, max_users: int = 100, duration: int = 300,
                 spawn_rate: float = 10):
        """
        初始化线性负载模式

        Args:
            max_users: 最大用户数
            duration: 测试持续时间(秒)
            spawn_rate: 用户生成速率
        """
        super().__init__()
        self.max_users = max_users
        self.duration = duration
        self.spawn_rate = spawn_rate
        self.start_time = None

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        计算当前负载

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        # 初始化开始时间
        if self.start_time is None:
            self.start_time = time.time()

        # 计算运行时间
        elapsed_time = time.time() - self.start_time

        # 检查是否超时
        if elapsed_time >= self.duration:
            return None

        # 计算当前用户数（线性增长）
        progress = elapsed_time / self.duration
        current_users = int(self.max_users * progress)
        current_users = max(1, current_users)  # 至少1个用户

        return current_users, self.spawn_rate
```

### 2. 阶段式负载模式

```python
from typing import List, NamedTuple

class LoadStage(NamedTuple):
    """负载阶段定义"""
    users: int          # 用户数
    duration: int       # 持续时间(秒)
    spawn_rate: float   # 生成速率

class StageLoadShape(LoadTestShape):
    """阶段式负载模式"""

    def __init__(self, stages: List[LoadStage]):
        """
        初始化阶段式负载模式

        Args:
            stages: 负载阶段列表
        """
        super().__init__()
        self.stages = stages
        self.current_stage = 0
        self.stage_start_time = None
        self.test_start_time = None

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        计算当前负载

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = time.time()

        # 初始化时间
        if self.test_start_time is None:
            self.test_start_time = current_time
            self.stage_start_time = current_time

        # 检查是否完成所有阶段
        if self.current_stage >= len(self.stages):
            return None

        current_stage = self.stages[self.current_stage]
        stage_elapsed = current_time - self.stage_start_time

        # 检查当前阶段是否完成
        if stage_elapsed >= current_stage.duration:
            self.current_stage += 1
            self.stage_start_time = current_time

            # 检查是否还有下一阶段
            if self.current_stage >= len(self.stages):
                return None

            current_stage = self.stages[self.current_stage]

        return current_stage.users, current_stage.spawn_rate

    def get_current_stage_info(self) -> dict:
        """
        获取当前阶段信息

        Returns:
            dict: 阶段信息
        """
        if self.current_stage < len(self.stages):
            stage = self.stages[self.current_stage]
            elapsed = time.time() - self.stage_start_time if self.stage_start_time else 0
            return {
                "stage_index": self.current_stage,
                "stage_users": stage.users,
                "stage_duration": stage.duration,
                "stage_elapsed": elapsed,
                "stage_remaining": max(0, stage.duration - elapsed)
            }
        return {}
```

## 🌊 高级负载模式开发

### 1. 自适应负载模式

```python
from locust import stats
import statistics

class AdaptiveLoadShape(LoadTestShape):
    """自适应负载模式 - 根据性能指标动态调整负载"""

    def __init__(self, initial_users: int = 10, max_users: int = 500,
                 target_response_time: float = 1000, adjustment_interval: int = 30,
                 spawn_rate: float = 10):
        """
        初始化自适应负载模式

        Args:
            initial_users: 初始用户数
            max_users: 最大用户数
            target_response_time: 目标响应时间(ms)
            adjustment_interval: 调整间隔(秒)
            spawn_rate: 生成速率
        """
        super().__init__()
        self.initial_users = initial_users
        self.max_users = max_users
        self.target_response_time = target_response_time
        self.adjustment_interval = adjustment_interval
        self.spawn_rate = spawn_rate

        # 状态变量
        self.current_users = initial_users
        self.last_adjustment_time = None
        self.performance_history = []
        self.adjustment_factor = 1.1  # 调整因子

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        自适应负载计算

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = time.time()

        # 初始化调整时间
        if self.last_adjustment_time is None:
            self.last_adjustment_time = current_time

        # 检查是否需要调整负载
        if current_time - self.last_adjustment_time >= self.adjustment_interval:
            self._adjust_load()
            self.last_adjustment_time = current_time

        return self.current_users, self.spawn_rate

    def _adjust_load(self):
        """根据性能指标调整负载"""
        try:
            # 获取当前性能指标
            current_stats = self._get_current_performance()

            if current_stats is None:
                return

            avg_response_time = current_stats.get('avg_response_time', 0)
            error_rate = current_stats.get('error_rate', 0)

            # 记录性能历史
            self.performance_history.append({
                'timestamp': time.time(),
                'users': self.current_users,
                'avg_response_time': avg_response_time,
                'error_rate': error_rate
            })

            # 保持历史记录在合理范围内
            if len(self.performance_history) > 10:
                self.performance_history.pop(0)

            # 调整逻辑
            if error_rate > 5:  # 错误率过高，减少负载
                self.current_users = max(1, int(self.current_users * 0.8))
                print(f"High error rate ({error_rate}%), reducing users to {self.current_users}")
            elif avg_response_time > self.target_response_time * 1.5:  # 响应时间过高
                self.current_users = max(1, int(self.current_users * 0.9))
                print(f"High response time ({avg_response_time}ms), reducing users to {self.current_users}")
            elif avg_response_time < self.target_response_time * 0.7:  # 响应时间良好
                new_users = min(self.max_users, int(self.current_users * self.adjustment_factor))
                if new_users > self.current_users:
                    self.current_users = new_users
                    print(f"Good performance, increasing users to {self.current_users}")

        except Exception as e:
            print(f"Error in load adjustment: {e}")

    def _get_current_performance(self) -> Optional[dict]:
        """
        获取当前性能指标

        Returns:
            Optional[dict]: 性能指标字典
        """
        try:
            # 从Locust统计信息获取性能数据
            total_stats = stats.total

            if total_stats.num_requests == 0:
                return None

            return {
                'avg_response_time': total_stats.avg_response_time,
                'error_rate': (total_stats.num_failures / total_stats.num_requests) * 100,
                'rps': total_stats.current_rps,
                'total_requests': total_stats.num_requests
            }
        except Exception as e:
            print(f"Error getting performance stats: {e}")
            return None

    def get_performance_summary(self) -> dict:
        """
        获取性能摘要

        Returns:
            dict: 性能摘要
        """
        if not self.performance_history:
            return {}

        response_times = [h['avg_response_time'] for h in self.performance_history]
        error_rates = [h['error_rate'] for h in self.performance_history]

        return {
            'avg_response_time': statistics.mean(response_times),
            'max_response_time': max(response_times),
            'avg_error_rate': statistics.mean(error_rates),
            'max_error_rate': max(error_rates),
            'adjustments_made': len(self.performance_history),
            'current_users': self.current_users
        }
```

### 2. 事件驱动负载模式

```python
from typing import Callable, Dict, Any
from enum import Enum

class LoadEvent(Enum):
    """负载事件类型"""
    SPIKE_START = "spike_start"
    SPIKE_END = "spike_end"
    RAMP_UP = "ramp_up"
    RAMP_DOWN = "ramp_down"
    MAINTAIN = "maintain"

class EventDrivenLoadShape(LoadTestShape):
    """事件驱动负载模式"""

    def __init__(self, base_users: int = 50, spawn_rate: float = 10):
        """
        初始化事件驱动负载模式

        Args:
            base_users: 基础用户数
            spawn_rate: 生成速率
        """
        super().__init__()
        self.base_users = base_users
        self.spawn_rate = spawn_rate
        self.current_users = base_users

        # 事件系统
        self.events = []
        self.event_handlers = {}
        self.start_time = None

    def add_event(self, trigger_time: int, event_type: LoadEvent,
                  params: Dict[str, Any] = None):
        """
        添加负载事件

        Args:
            trigger_time: 触发时间(秒)
            event_type: 事件类型
            params: 事件参数
        """
        self.events.append({
            'trigger_time': trigger_time,
            'event_type': event_type,
            'params': params or {},
            'triggered': False
        })

        # 按时间排序
        self.events.sort(key=lambda x: x['trigger_time'])

    def register_event_handler(self, event_type: LoadEvent,
                             handler: Callable[[Dict[str, Any]], int]):
        """
        注册事件处理器

        Args:
            event_type: 事件类型
            handler: 事件处理函数，返回新的用户数
        """
        self.event_handlers[event_type] = handler

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        事件驱动负载计算

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = time.time()

        # 初始化开始时间
        if self.start_time is None:
            self.start_time = current_time

        elapsed_time = current_time - self.start_time

        # 处理事件
        for event in self.events:
            if not event['triggered'] and elapsed_time >= event['trigger_time']:
                self._handle_event(event)
                event['triggered'] = True

        return self.current_users, self.spawn_rate

    def _handle_event(self, event: Dict[str, Any]):
        """
        处理负载事件

        Args:
            event: 事件信息
        """
        event_type = event['event_type']
        params = event['params']

        print(f"Triggering event: {event_type.value} with params: {params}")

        # 调用注册的事件处理器
        if event_type in self.event_handlers:
            new_users = self.event_handlers[event_type](params)
            if new_users is not None:
                self.current_users = max(1, new_users)
        else:
            # 默认事件处理
            self._default_event_handler(event_type, params)

    def _default_event_handler(self, event_type: LoadEvent, params: Dict[str, Any]):
        """
        默认事件处理器

        Args:
            event_type: 事件类型
            params: 事件参数
        """
        if event_type == LoadEvent.SPIKE_START:
            spike_users = params.get('users', self.current_users * 2)
            self.current_users = spike_users
        elif event_type == LoadEvent.SPIKE_END:
            self.current_users = self.base_users
        elif event_type == LoadEvent.RAMP_UP:
            factor = params.get('factor', 1.5)
            self.current_users = int(self.current_users * factor)
        elif event_type == LoadEvent.RAMP_DOWN:
            factor = params.get('factor', 0.7)
            self.current_users = max(1, int(self.current_users * factor))
        elif event_type == LoadEvent.MAINTAIN:
            users = params.get('users', self.current_users)
            self.current_users = users

# 使用示例
def create_event_driven_load():
    """创建事件驱动负载模式示例"""
    load_shape = EventDrivenLoadShape(base_users=20, spawn_rate=5)

    # 添加事件
    load_shape.add_event(60, LoadEvent.RAMP_UP, {'factor': 2})    # 1分钟后增加负载
    load_shape.add_event(120, LoadEvent.SPIKE_START, {'users': 200})  # 2分钟后开始尖峰
    load_shape.add_event(180, LoadEvent.SPIKE_END)                # 3分钟后结束尖峰
    load_shape.add_event(240, LoadEvent.RAMP_DOWN, {'factor': 0.5})  # 4分钟后减少负载

    # 注册自定义事件处理器
    def custom_spike_handler(params):
        users = params.get('users', 100)
        print(f"Custom spike: setting users to {users}")
        return users

    load_shape.register_event_handler(LoadEvent.SPIKE_START, custom_spike_handler)

    return load_shape
```

## 🧪 测试和验证

### 1. 负载模式测试框架

```python
import unittest
from unittest.mock import patch, MagicMock

class LoadShapeTestCase(unittest.TestCase):
    """负载模式测试基类"""

    def setUp(self):
        """测试初始化"""
        self.load_shape = None

    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.load_shape)

    def test_tick_returns_valid_values(self):
        """测试tick方法返回有效值"""
        result = self.load_shape.tick()

        if result is not None:
            users, spawn_rate = result
            self.assertIsInstance(users, int)
            self.assertIsInstance(spawn_rate, (int, float))
            self.assertGreater(users, 0)
            self.assertGreater(spawn_rate, 0)

    def test_load_progression(self):
        """测试负载变化"""
        results = []

        # 模拟时间推进
        with patch('time.time') as mock_time:
            for i in range(10):
                mock_time.return_value = i * 30  # 每30秒
                result = self.load_shape.tick()
                if result:
                    results.append(result)

        # 验证负载变化合理性
        self.assertGreater(len(results), 0)

    def test_termination_condition(self):
        """测试终止条件"""
        # 模拟长时间运行
        with patch('time.time') as mock_time:
            mock_time.return_value = 10000  # 很长时间后
            result = self.load_shape.tick()

            # 某些负载模式应该在长时间后终止
            # 这取决于具体的负载模式实现

class LinearLoadShapeTest(LoadShapeTestCase):
    """线性负载模式测试"""

    def setUp(self):
        self.load_shape = LinearLoadShape(max_users=100, duration=300, spawn_rate=10)

    def test_linear_progression(self):
        """测试线性增长"""
        with patch('time.time') as mock_time:
            # 测试开始
            mock_time.return_value = 0
            self.load_shape.tick()  # 初始化start_time

            # 测试中间点
            mock_time.return_value = 150  # 50%进度
            users, spawn_rate = self.load_shape.tick()
            self.assertAlmostEqual(users, 50, delta=5)  # 允许小误差

            # 测试结束点
            mock_time.return_value = 300
            result = self.load_shape.tick()
            self.assertIsNone(result)  # 应该终止

# 运行测试
if __name__ == '__main__':
    unittest.main()
```

### 2. 性能验证工具

```python
class LoadShapeValidator:
    """负载模式验证器"""

    @staticmethod
    def validate_load_shape(load_shape_class, config: Dict[str, Any],
                          simulation_duration: int = 600) -> Dict[str, Any]:
        """
        验证负载模式

        Args:
            load_shape_class: 负载模式类
            config: 配置参数
            simulation_duration: 模拟持续时间

        Returns:
            Dict[str, Any]: 验证结果
        """
        try:
            # 创建负载模式实例
            load_shape = load_shape_class(**config)

            # 模拟运行
            results = []
            with patch('time.time') as mock_time:
                for second in range(simulation_duration):
                    mock_time.return_value = second
                    result = load_shape.tick()

                    if result is None:
                        break

                    users, spawn_rate = result
                    results.append({
                        'time': second,
                        'users': users,
                        'spawn_rate': spawn_rate
                    })

            # 分析结果
            return LoadShapeValidator._analyze_results(results)

        except Exception as e:
            return {'error': str(e), 'valid': False}

    @staticmethod
    def _analyze_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析验证结果"""
        if not results:
            return {'error': 'No results generated', 'valid': False}

        users_list = [r['users'] for r in results]
        spawn_rates = [r['spawn_rate'] for r in results]

        return {
            'valid': True,
            'duration': len(results),
            'max_users': max(users_list),
            'min_users': min(users_list),
            'avg_users': sum(users_list) / len(users_list),
            'max_spawn_rate': max(spawn_rates),
            'min_spawn_rate': min(spawn_rates),
            'user_changes': len(set(users_list)),
            'results': results[:10]  # 前10个结果作为样本
        }
```

## 📦 集成和部署

### 1. 负载模式注册

```python
# 在框架中注册自定义负载模式
from src.model.load_shapes.load_shape_manager import load_shape_manager

# 注册负载模式
load_shape_manager.register_shape("linear", LinearLoadShape)
load_shape_manager.register_shape("stage", StageLoadShape)
load_shape_manager.register_shape("adaptive", AdaptiveLoadShape)
load_shape_manager.register_shape("event_driven", EventDrivenLoadShape)

# 使用负载模式
linear_shape = load_shape_manager.create_shape("linear",
                                              max_users=200,
                                              duration=600,
                                              spawn_rate=15)
```

### 2. 配置文件集成

```yaml
# load_shapes.yaml
load_shapes:
  linear_growth:
    type: "linear"
    config:
      max_users: 200
      duration: 600
      spawn_rate: 15

  stage_test:
    type: "stage"
    config:
      stages:
        - users: 10
          duration: 60
          spawn_rate: 5
        - users: 50
          duration: 120
          spawn_rate: 10
        - users: 100
          duration: 180
          spawn_rate: 15

  adaptive_test:
    type: "adaptive"
    config:
      initial_users: 20
      max_users: 500
      target_response_time: 1000
      adjustment_interval: 30
      spawn_rate: 10
```

## 📚 最佳实践

### 1. 设计原则

- **单一职责**: 每个负载模式专注于特定的负载控制逻辑
- **可配置性**: 通过参数控制负载模式行为
- **可测试性**: 提供充分的测试覆盖
- **性能优化**: 避免在tick方法中进行重计算
- **错误处理**: 优雅处理异常情况

### 2. 代码规范

- 使用类型提示提高代码可读性
- 提供详细的文档字符串
- 遵循PEP 8代码风格
- 使用有意义的变量和方法名
- 添加适当的日志记录

### 3. 性能考虑

- tick方法应该快速执行
- 避免在tick中进行IO操作
- 缓存计算结果
- 使用高效的数据结构
- 考虑内存使用情况

## 🎉 总结

通过本指南，您已经学会了：

1. **基础开发**: 创建简单的负载模式
2. **高级功能**: 实现自适应和事件驱动负载模式
3. **测试验证**: 编写测试确保负载模式正确性
4. **集成部署**: 将负载模式集成到框架中
5. **最佳实践**: 遵循设计原则和代码规范

## 📚 相关文档

- [负载模式API](../api/load-shapes.md) - 详细API参考
- [基础示例](../examples/basic-examples.md) - 负载模式使用示例
- [高级示例](../examples/advanced-usage.md) - 复杂场景实现
- [测试指南](testing.md) - 测试开发指南
