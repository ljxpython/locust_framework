"""
负载模式类

提供各种负载模式的实现，支持不同的性能测试场景
"""

from .advanced_shapes import (
    AdaptiveLoadShape,
    CustomStageLoadShape,
    LoadStage,
    RampUpDownLoadShape,
    RandomLoadShape,
    SpikeLoadShape,
    StairStepLoadShape,
    WaveLoadShape,
)
from .step_load import StepLoadShape as BasicStepLoadShape
from .wait_user_count import StepLoadShape as WaitUserCountShape

__all__ = [
    "BasicStepLoadShape",
    "WaitUserCountShape",
    "WaveLoadShape",
    "SpikeLoadShape",
    "StairStepLoadShape",
    "CustomStageLoadShape",
    "RampUpDownLoadShape",
    "AdaptiveLoadShape",
    "RandomLoadShape",
    "LoadStage",
]
