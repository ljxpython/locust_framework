"""
高级负载模式

提供更多复杂的负载模式实现
"""

import math
import time
from collections import namedtuple
from typing import List, Optional, Tuple

from locust import LoadTestShape

from src.utils.log_moudle import logger

# 负载阶段定义
LoadStage = namedtuple("LoadStage", ["users", "spawn_rate", "duration"])


class WaveLoadShape(LoadTestShape):
    """
    波浪形负载模式

    模拟用户访问的波峰波谷，适合测试系统在负载变化时的表现
    """

    def __init__(
        self,
        min_users: int = 10,
        max_users: int = 100,
        wave_period: int = 300,
        spawn_rate: int = 10,
        time_limit: int = 1800,
    ):
        """
        初始化波浪负载

        Args:
            min_users: 最小用户数
            max_users: 最大用户数
            wave_period: 波浪周期(秒)
            spawn_rate: 用户生成速率
            time_limit: 测试时间限制(秒)
        """
        super().__init__()
        self.min_users = min_users
        self.max_users = max_users
        self.wave_period = wave_period
        self.spawn_rate = spawn_rate
        self.time_limit = time_limit

        logger.info(f"波浪负载模式: {min_users}-{max_users} 用户, 周期: {wave_period}s")

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # 计算当前波浪位置 (0-1)
        wave_position = (run_time % self.wave_period) / self.wave_period

        # 使用正弦函数生成波浪
        wave_value = math.sin(2 * math.pi * wave_position)

        # 将波浪值映射到用户数范围
        user_range = self.max_users - self.min_users
        current_users = self.min_users + int((wave_value + 1) / 2 * user_range)

        return (current_users, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    尖峰负载模式

    在基础负载上周期性地产生负载尖峰，测试系统的突发处理能力
    """

    def __init__(
        self,
        base_users: int = 50,
        spike_users: int = 200,
        spike_duration: int = 60,
        spike_interval: int = 300,
        spawn_rate: int = 20,
        time_limit: int = 1800,
    ):
        """
        初始化尖峰负载

        Args:
            base_users: 基础用户数
            spike_users: 尖峰用户数
            spike_duration: 尖峰持续时间(秒)
            spike_interval: 尖峰间隔时间(秒)
            spawn_rate: 用户生成速率
            time_limit: 测试时间限制(秒)
        """
        super().__init__()
        self.base_users = base_users
        self.spike_users = spike_users
        self.spike_duration = spike_duration
        self.spike_interval = spike_interval
        self.spawn_rate = spawn_rate
        self.time_limit = time_limit

        logger.info(f"尖峰负载模式: 基础{base_users}用户, 尖峰{spike_users}用户")

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # 计算当前在尖峰周期中的位置
        cycle_position = run_time % self.spike_interval

        if cycle_position < self.spike_duration:
            # 在尖峰期间
            return (self.spike_users, self.spawn_rate)
        else:
            # 在基础负载期间
            return (self.base_users, self.spawn_rate)


class StairStepLoadShape(LoadTestShape):
    """
    阶梯负载模式

    逐步增加负载，每个阶梯保持一定时间，适合容量测试
    """

    def __init__(
        self,
        start_users: int = 10,
        step_users: int = 20,
        step_duration: int = 120,
        max_users: int = 200,
        spawn_rate: int = 10,
    ):
        """
        初始化阶梯负载

        Args:
            start_users: 起始用户数
            step_users: 每阶梯增加的用户数
            step_duration: 每阶梯持续时间(秒)
            max_users: 最大用户数
            spawn_rate: 用户生成速率
        """
        super().__init__()
        self.start_users = start_users
        self.step_users = step_users
        self.step_duration = step_duration
        self.max_users = max_users
        self.spawn_rate = spawn_rate

        # 计算总阶梯数
        self.total_steps = math.ceil((max_users - start_users) / step_users) + 1
        self.time_limit = self.total_steps * step_duration

        logger.info(
            f"阶梯负载模式: {start_users}-{max_users}用户, {self.total_steps}阶梯"
        )

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # 计算当前阶梯
        current_step = math.floor(run_time / self.step_duration)
        current_users = min(
            self.start_users + current_step * self.step_users, self.max_users
        )

        return (current_users, self.spawn_rate)


class CustomStageLoadShape(LoadTestShape):
    """
    自定义阶段负载模式

    允许定义复杂的多阶段负载场景
    """

    def __init__(self, stages: List[LoadStage]):
        """
        初始化自定义阶段负载

        Args:
            stages: 负载阶段列表，每个阶段包含用户数、生成速率和持续时间
        """
        super().__init__()
        self.stages = stages
        self.current_stage = 0
        self.stage_start_time = 0

        # 计算总测试时间
        self.time_limit = sum(stage.duration for stage in stages)

        logger.info(f"自定义阶段负载: {len(stages)}个阶段, 总时长{self.time_limit}秒")

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit or self.current_stage >= len(self.stages):
            return None

        # 获取当前阶段
        stage = self.stages[self.current_stage]
        stage_elapsed = run_time - self.stage_start_time

        # 检查是否需要切换到下一阶段
        if stage_elapsed >= stage.duration:
            self.current_stage += 1
            self.stage_start_time = run_time

            if self.current_stage >= len(self.stages):
                return None

            stage = self.stages[self.current_stage]

        return (stage.users, stage.spawn_rate)


class RampUpDownLoadShape(LoadTestShape):
    """
    爬升-保持-下降负载模式

    经典的负载测试模式：逐步增加到目标负载，保持一段时间，然后逐步减少
    """

    def __init__(
        self,
        target_users: int = 100,
        ramp_up_time: int = 300,
        hold_time: int = 600,
        ramp_down_time: int = 300,
        spawn_rate: int = 10,
    ):
        """
        初始化爬升-保持-下降负载

        Args:
            target_users: 目标用户数
            ramp_up_time: 爬升时间(秒)
            hold_time: 保持时间(秒)
            ramp_down_time: 下降时间(秒)
            spawn_rate: 用户生成速率
        """
        super().__init__()
        self.target_users = target_users
        self.ramp_up_time = ramp_up_time
        self.hold_time = hold_time
        self.ramp_down_time = ramp_down_time
        self.spawn_rate = spawn_rate

        self.time_limit = ramp_up_time + hold_time + ramp_down_time

        logger.info(
            f"爬升-保持-下降负载: 目标{target_users}用户, "
            f"爬升{ramp_up_time}s, 保持{hold_time}s, 下降{ramp_down_time}s"
        )

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        if run_time <= self.ramp_up_time:
            # 爬升阶段
            progress = run_time / self.ramp_up_time
            current_users = int(self.target_users * progress)
        elif run_time <= self.ramp_up_time + self.hold_time:
            # 保持阶段
            current_users = self.target_users
        else:
            # 下降阶段
            ramp_down_elapsed = run_time - self.ramp_up_time - self.hold_time
            progress = 1 - (ramp_down_elapsed / self.ramp_down_time)
            current_users = int(self.target_users * progress)

        return (current_users, self.spawn_rate)


class AdaptiveLoadShape(LoadTestShape):
    """
    自适应负载模式

    根据系统响应时间动态调整负载
    """

    def __init__(
        self,
        initial_users: int = 10,
        max_users: int = 200,
        target_response_time: float = 1.0,
        adjustment_interval: int = 30,
        spawn_rate: int = 10,
        time_limit: int = 1800,
    ):
        """
        初始化自适应负载

        Args:
            initial_users: 初始用户数
            max_users: 最大用户数
            target_response_time: 目标响应时间(秒)
            adjustment_interval: 调整间隔(秒)
            spawn_rate: 用户生成速率
            time_limit: 测试时间限制(秒)
        """
        super().__init__()
        self.initial_users = initial_users
        self.max_users = max_users
        self.target_response_time = target_response_time
        self.adjustment_interval = adjustment_interval
        self.spawn_rate = spawn_rate
        self.time_limit = time_limit

        self.current_users = initial_users
        self.last_adjustment_time = 0

        logger.info(
            f"自适应负载模式: 目标响应时间{target_response_time}s, "
            f"最大{max_users}用户"
        )

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # 检查是否需要调整负载
        if run_time - self.last_adjustment_time >= self.adjustment_interval:
            self._adjust_load()
            self.last_adjustment_time = run_time

        return (self.current_users, self.spawn_rate)

    def _adjust_load(self):
        """根据当前性能指标调整负载"""
        try:
            # 获取当前统计信息
            stats = self.runner.stats
            if not stats.entries:
                return

            # 计算平均响应时间
            total_response_time = sum(
                entry.avg_response_time for entry in stats.entries.values()
            )
            avg_response_time = total_response_time / len(stats.entries)

            # 根据响应时间调整用户数
            if avg_response_time > self.target_response_time * 1.2:
                # 响应时间过高，减少用户
                self.current_users = max(1, int(self.current_users * 0.9))
                logger.info(
                    f"响应时间过高({avg_response_time:.2f}s)，减少用户至{self.current_users}"
                )
            elif avg_response_time < self.target_response_time * 0.8:
                # 响应时间良好，增加用户
                self.current_users = min(self.max_users, int(self.current_users * 1.1))
                logger.info(
                    f"响应时间良好({avg_response_time:.2f}s)，增加用户至{self.current_users}"
                )

        except Exception as e:
            logger.error(f"调整负载失败: {e}")


class RandomLoadShape(LoadTestShape):
    """
    随机负载模式

    在指定范围内随机变化用户数，模拟不可预测的负载变化
    """

    def __init__(
        self,
        min_users: int = 10,
        max_users: int = 100,
        change_interval: int = 60,
        spawn_rate: int = 10,
        time_limit: int = 1800,
    ):
        """
        初始化随机负载

        Args:
            min_users: 最小用户数
            max_users: 最大用户数
            change_interval: 变化间隔(秒)
            spawn_rate: 用户生成速率
            time_limit: 测试时间限制(秒)
        """
        super().__init__()
        self.min_users = min_users
        self.max_users = max_users
        self.change_interval = change_interval
        self.spawn_rate = spawn_rate
        self.time_limit = time_limit

        self.current_users = min_users
        self.last_change_time = 0

        logger.info(
            f"随机负载模式: {min_users}-{max_users}用户, " f"变化间隔{change_interval}s"
        )

    def tick(self) -> Optional[Tuple[int, int]]:
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        # 检查是否需要改变用户数
        if run_time - self.last_change_time >= self.change_interval:
            import random

            self.current_users = random.randint(self.min_users, self.max_users)
            self.last_change_time = run_time
            logger.debug(f"随机调整用户数至: {self.current_users}")

        return (self.current_users, self.spawn_rate)
