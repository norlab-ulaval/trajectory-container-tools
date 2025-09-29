# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .base_trajectory_dataclass import NestedBaseTrajectoryDataclass


@dataclass()
class Point2D(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray


@dataclass()
class Vector2D(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray


@dataclass()
class Pose2D(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray


@dataclass()
class Velocity2D(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray
    ang: np.ndarray
