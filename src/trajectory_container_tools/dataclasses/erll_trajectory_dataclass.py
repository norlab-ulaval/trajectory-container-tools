# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import BaseTrajectoryFeature


@dataclass()
class TestTrajectoryDataclass(BaseTrajectoryFeature):
    """
    Experience replay learning loop test-time trajectory dataclass

    Note: assume data are flattened as received or outputed by the tested model
    """

    observations: np.ndarray
    actions: np.ndarray


@dataclass()
class TestMotionTrajectoryDataclass(TestTrajectoryDataclass):
    pose: np.ndarray
