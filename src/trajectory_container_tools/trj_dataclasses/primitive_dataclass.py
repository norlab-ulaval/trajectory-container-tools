# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools import NestedBaseTrajectoryDataclass


@dataclass()
class Point2(NestedBaseTrajectoryDataclass):
    # No ros2 compatible message
    x: np.ndarray
    y: np.ndarray


@dataclass()
class Vector2(NestedBaseTrajectoryDataclass):
    # No ros2 compatible message
    x: np.ndarray
    y: np.ndarray
