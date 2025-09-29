# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import BaseTrajectoryDataclass
from ..utils.general import check_is_finite


@dataclass()
class AxBaseDataclass(BaseTrajectoryDataclass):
    obs: np.ndarray
    noise: Optional[np.ndarray] = field(default=None, init=False)
    obs_noise: Optional[np.ndarray] = field(default=None, init=False)

    @property
    def obs_with_noise(self) -> np.ndarray:
        check_is_finite(self.obs + self.obs_noise)
        return self.obs + self.obs_noise

    def on_begin_post_init_callback(self) -> None:
        if not self.noise:
            self.noise = np.zeros_like(self.obs)
            self.obs_noise = np.zeros_like(self.obs)
        return None


@dataclass()
class StateAxDataclass(AxBaseDataclass):
    poses: np.ndarray
    vels: np.ndarray
    feature_name: str = field(default="State axes", init=False)

    @property
    def poses_with_noise(self) -> np.ndarray:
        check_is_finite(self.poses + self.noise)
        return self.poses + self.noise


@dataclass()
class TimeAxDataclass(AxBaseDataclass):
    wall: np.ndarray
    delta: np.ndarray
    feature_name: str = field(default="Time axis", init=False)

    @property
    def wall_with_noise(self) -> np.ndarray:
        check_is_finite(self.wall + self.noise)
        return self.wall + self.noise


@dataclass()
class MathEnvTrajectoryDataclass(BaseTrajectoryDataclass):
    """
    Math gymnasium environment trajectory dataclass
    """

    state_axes: StateAxDataclass
    time_axis: TimeAxDataclass
