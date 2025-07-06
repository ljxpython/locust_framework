# 负载模式API

本文档详细介绍Locust性能测试框架的负载模式API接口。

## 📋 API概览

负载模式API提供了丰富的负载控制接口，支持多种负载模式：

- **基础负载模式**: 常量负载、阶梯负载
- **高级负载模式**: 波浪负载、尖峰负载、自适应负载
- **自定义负载模式**: 用户自定义负载曲线
- **负载模式管理**: 负载模式的注册和管理

## 🔧 基础负载模式API

### LoadShape

所有负载模式的基础类。

```python
from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict, Any
from locust import LoadTestShape

class LoadShape(LoadTestShape, ABC):
    """负载模式基类"""

    def __init__(self, **kwargs):
        """
        初始化负载模式

        Args:
            **kwargs: 负载模式参数
        """
        super().__init__()
        self.start_time = None
        self.config = kwargs

    @abstractmethod
    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前时刻的负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率) 或 None表示测试结束
        """
        pass

    def get_current_time(self) -> float:
        """
        获取当前运行时间(秒)

        Returns:
            float: 运行时间
        """
        import time
        if self.start_time is None:
            self.start_time = time.time()
        return time.time() - self.start_time

    def get_config(self) -> Dict[str, Any]:
        """
        获取负载模式配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        return self.config

    def validate_config(self) -> bool:
        """
        验证配置参数

        Returns:
            bool: 配置是否有效
        """
        return True
```

### ConstantLoadShape

常量负载模式，保持固定的用户数和生成速率。

```python
class ConstantLoadShape(LoadShape):
    """常量负载模式"""

    def __init__(self, users: int = 100, spawn_rate: float = 10,
                 duration: Optional[int] = None, **kwargs):
        """
        初始化常量负载模式

        Args:
            users: 用户数
            spawn_rate: 生成速率
            duration: 持续时间(秒)，None表示无限制
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.users = users
        self.spawn_rate = spawn_rate
        self.duration = duration

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = self.get_current_time()

        if self.duration and current_time >= self.duration:
            return None

        return self.users, self.spawn_rate

    def validate_config(self) -> bool:
        """验证配置"""
        return (self.users > 0 and self.spawn_rate > 0 and
                (self.duration is None or self.duration > 0))
```

### StepLoadShape

阶梯负载模式，按阶梯递增用户数。

```python
from typing import List, NamedTuple

class Step(NamedTuple):
    """阶梯定义"""
    users: int
    duration: int
    spawn_rate: float = 10

class StepLoadShape(LoadShape):
    """阶梯负载模式"""

    def __init__(self, steps: List[Step], **kwargs):
        """
        初始化阶梯负载模式

        Args:
            steps: 阶梯列表
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.steps = steps
        self.current_step = 0
        self.step_start_time = 0

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = self.get_current_time()

        if self.current_step >= len(self.steps):
            return None

        step = self.steps[self.current_step]
        step_elapsed = current_time - self.step_start_time

        if step_elapsed >= step.duration:
            self.current_step += 1
            self.step_start_time = current_time

            if self.current_step >= len(self.steps):
                return None

            step = self.steps[self.current_step]

        return step.users, step.spawn_rate

    def validate_config(self) -> bool:
        """验证配置"""
        if not self.steps:
            return False

        for step in self.steps:
            if step.users <= 0 or step.duration <= 0 or step.spawn_rate <= 0:
                return False

        return True
```

## 🌊 高级负载模式API

### WaveLoadShape

波浪负载模式，按正弦波形变化用户数。

```python
import math

class WaveLoadShape(LoadShape):
    """波浪负载模式"""

    def __init__(self, min_users: int = 10, max_users: int = 100,
                 wave_period: int = 300, spawn_rate: float = 10,
                 duration: Optional[int] = None, **kwargs):
        """
        初始化波浪负载模式

        Args:
            min_users: 最小用户数
            max_users: 最大用户数
            wave_period: 波浪周期(秒)
            spawn_rate: 生成速率
            duration: 持续时间(秒)
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.min_users = min_users
        self.max_users = max_users
        self.wave_period = wave_period
        self.spawn_rate = spawn_rate
        self.duration = duration

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = self.get_current_time()

        if self.duration and current_time >= self.duration:
            return None

        # 计算正弦波用户数
        wave_position = (current_time % self.wave_period) / self.wave_period
        sine_value = math.sin(2 * math.pi * wave_position)

        # 将正弦值映射到用户数范围
        user_range = self.max_users - self.min_users
        current_users = self.min_users + int((sine_value + 1) / 2 * user_range)

        return current_users, self.spawn_rate

    def validate_config(self) -> bool:
        """验证配置"""
        return (self.min_users > 0 and self.max_users > self.min_users and
                self.wave_period > 0 and self.spawn_rate > 0 and
                (self.duration is None or self.duration > 0))
```

### SpikeLoadShape

尖峰负载模式，在指定时间产生负载尖峰。

```python
from typing import List

class Spike(NamedTuple):
    """尖峰定义"""
    start_time: int
    peak_users: int
    duration: int
    spawn_rate: float = 50

class SpikeLoadShape(LoadShape):
    """尖峰负载模式"""

    def __init__(self, base_users: int = 50, spikes: List[Spike] = None,
                 base_spawn_rate: float = 10, total_duration: int = 600, **kwargs):
        """
        初始化尖峰负载模式

        Args:
            base_users: 基础用户数
            spikes: 尖峰列表
            base_spawn_rate: 基础生成速率
            total_duration: 总持续时间
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.base_users = base_users
        self.spikes = spikes or []
        self.base_spawn_rate = base_spawn_rate
        self.total_duration = total_duration

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = self.get_current_time()

        if current_time >= self.total_duration:
            return None

        # 检查是否在尖峰时间内
        for spike in self.spikes:
            spike_end = spike.start_time + spike.duration
            if spike.start_time <= current_time < spike_end:
                return spike.peak_users, spike.spawn_rate

        # 返回基础负载
        return self.base_users, self.base_spawn_rate

    def validate_config(self) -> bool:
        """验证配置"""
        if (self.base_users <= 0 or self.base_spawn_rate <= 0 or
            self.total_duration <= 0):
            return False

        for spike in self.spikes:
            if (spike.start_time < 0 or spike.peak_users <= 0 or
                spike.duration <= 0 or spike.spawn_rate <= 0):
                return False

            if spike.start_time + spike.duration > self.total_duration:
                return False

        return True
```

### AdaptiveLoadShape

自适应负载模式，根据性能指标动态调整负载。

```python
class AdaptiveLoadShape(LoadShape):
    """自适应负载模式"""

    def __init__(self, initial_users: int = 50, max_users: int = 500,
                 target_response_time: float = 1000, adjustment_interval: int = 30,
                 spawn_rate: float = 10, **kwargs):
        """
        初始化自适应负载模式

        Args:
            initial_users: 初始用户数
            max_users: 最大用户数
            target_response_time: 目标响应时间(ms)
            adjustment_interval: 调整间隔(秒)
            spawn_rate: 生成速率
            **kwargs: 其他参数
        """
        super().__init__(**kwargs)
        self.initial_users = initial_users
        self.max_users = max_users
        self.target_response_time = target_response_time
        self.adjustment_interval = adjustment_interval
        self.spawn_rate = spawn_rate

        self.current_users = initial_users
        self.last_adjustment_time = 0
        self.performance_history = []

    def tick(self) -> Optional[Tuple[int, float]]:
        """
        获取当前负载配置

        Returns:
            Optional[Tuple[int, float]]: (用户数, 生成速率)
        """
        current_time = self.get_current_time()

        # 检查是否需要调整负载
        if current_time - self.last_adjustment_time >= self.adjustment_interval:
            self._adjust_load()
            self.last_adjustment_time = current_time

        return self.current_users, self.spawn_rate

    def _adjust_load(self):
        """根据性能指标调整负载"""
        # 获取当前性能指标
        current_response_time = self._get_current_response_time()

        if current_response_time is None:
            return

        # 根据响应时间调整用户数
        if current_response_time > self.target_response_time * 1.2:
            # 响应时间过高，减少用户数
            self.current_users = max(1, int(self.current_users * 0.9))
        elif current_response_time < self.target_response_time * 0.8:
            # 响应时间良好，增加用户数
            self.current_users = min(self.max_users, int(self.current_users * 1.1))

        # 记录性能历史
        self.performance_history.append({
            'time': self.get_current_time(),
            'users': self.current_users,
            'response_time': current_response_time
        })

    def _get_current_response_time(self) -> Optional[float]:
        """
        获取当前平均响应时间

        Returns:
            Optional[float]: 平均响应时间(ms)
        """
        # 这里需要从Locust统计信息中获取实际的响应时间
        # 实际实现中需要访问Locust的stats对象
        try:
            from locust import stats
            if stats.total.num_requests > 0:
                return stats.total.avg_response_time
        except:
            pass
        return None

    def validate_config(self) -> bool:
        """验证配置"""
        return (self.initial_users > 0 and self.max_users > 0 and
                self.target_response_time > 0 and self.adjustment_interval > 0 and
                self.spawn_rate > 0)
```

## 🔧 负载模式管理API

### LoadShapeManager

负载模式管理器，用于注册和管理负载模式。

```python
from typing import Dict, Type, Optional

class LoadShapeManager:
    """负载模式管理器"""

    def __init__(self):
        self._shapes: Dict[str, Type[LoadShape]] = {}
        self._register_builtin_shapes()

    def register_shape(self, name: str, shape_class: Type[LoadShape]) -> bool:
        """
        注册负载模式

        Args:
            name: 负载模式名称
            shape_class: 负载模式类

        Returns:
            bool: 注册是否成功
        """
        if not issubclass(shape_class, LoadShape):
            return False

        self._shapes[name] = shape_class
        return True

    def get_shape(self, name: str) -> Optional[Type[LoadShape]]:
        """
        获取负载模式类

        Args:
            name: 负载模式名称

        Returns:
            Optional[Type[LoadShape]]: 负载模式类
        """
        return self._shapes.get(name)

    def create_shape(self, name: str, **kwargs) -> Optional[LoadShape]:
        """
        创建负载模式实例

        Args:
            name: 负载模式名称
            **kwargs: 负载模式参数

        Returns:
            Optional[LoadShape]: 负载模式实例
        """
        shape_class = self.get_shape(name)
        if shape_class:
            return shape_class(**kwargs)
        return None

    def list_shapes(self) -> List[str]:
        """
        列出所有注册的负载模式

        Returns:
            List[str]: 负载模式名称列表
        """
        return list(self._shapes.keys())

    def _register_builtin_shapes(self):
        """注册内置负载模式"""
        self.register_shape("constant", ConstantLoadShape)
        self.register_shape("step", StepLoadShape)
        self.register_shape("wave", WaveLoadShape)
        self.register_shape("spike", SpikeLoadShape)
        self.register_shape("adaptive", AdaptiveLoadShape)

# 全局负载模式管理器实例
load_shape_manager = LoadShapeManager()
```

## 📊 负载模式工具API

### LoadShapeValidator

负载模式验证器。

```python
class LoadShapeValidator:
    """负载模式验证器"""

    @staticmethod
    def validate_shape_config(shape_type: str, config: Dict[str, Any]) -> bool:
        """
        验证负载模式配置

        Args:
            shape_type: 负载模式类型
            config: 配置字典

        Returns:
            bool: 配置是否有效
        """
        shape_class = load_shape_manager.get_shape(shape_type)
        if not shape_class:
            return False

        try:
            shape = shape_class(**config)
            return shape.validate_config()
        except Exception:
            return False

    @staticmethod
    def estimate_duration(shape_type: str, config: Dict[str, Any]) -> Optional[int]:
        """
        估算负载模式持续时间

        Args:
            shape_type: 负载模式类型
            config: 配置字典

        Returns:
            Optional[int]: 估算的持续时间(秒)
        """
        if shape_type == "constant":
            return config.get("duration")
        elif shape_type == "step":
            steps = config.get("steps", [])
            return sum(step.duration for step in steps) if steps else None
        elif shape_type in ["wave", "spike", "adaptive"]:
            return config.get("duration") or config.get("total_duration")

        return None
```

## 📚 使用示例

### 创建自定义负载模式

```python
class CustomLoadShape(LoadShape):
    """自定义负载模式示例"""

    def __init__(self, pattern: str = "linear", **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.max_users = kwargs.get("max_users", 100)
        self.duration = kwargs.get("duration", 300)
        self.spawn_rate = kwargs.get("spawn_rate", 10)

    def tick(self) -> Optional[Tuple[int, float]]:
        current_time = self.get_current_time()

        if current_time >= self.duration:
            return None

        if self.pattern == "linear":
            # 线性增长
            progress = current_time / self.duration
            users = int(self.max_users * progress)
        elif self.pattern == "exponential":
            # 指数增长
            progress = current_time / self.duration
            users = int(self.max_users * (progress ** 2))
        else:
            users = self.max_users

        return max(1, users), self.spawn_rate

# 注册自定义负载模式
load_shape_manager.register_shape("custom", CustomLoadShape)

# 使用负载模式
shape = load_shape_manager.create_shape("custom",
                                       pattern="exponential",
                                       max_users=200,
                                       duration=600,
                                       spawn_rate=15)
```

## 📚 相关文档

- [负载模式开发](../development/load-shape-development.md) - 负载模式开发指南
- [基础示例](../examples/basic-examples.md) - 负载模式使用示例
- [高级示例](../examples/advanced-usage.md) - 高级负载模式示例
- [配置参考](../configuration/framework-config.md) - 负载模式配置
