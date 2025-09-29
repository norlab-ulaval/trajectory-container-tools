# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .base_trajectory_dataclass import BaseTrajectoryDataclass


@dataclass()
class TestTrajectoryDataclass(BaseTrajectoryDataclass):
    """
    Experience replay learning loop test-time trajectory dataclass

    Note: assume data are flattened as received or outputed by the tested model
    """

    observations: np.ndarray
    actions: np.ndarray


@dataclass()
class TestMotionTrajectoryDataclass(TestTrajectoryDataclass):
    pose: np.ndarray
