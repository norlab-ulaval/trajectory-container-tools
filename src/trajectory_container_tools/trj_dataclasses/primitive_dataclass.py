# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools import NestedBaseTrajectoryDataclass


@dataclass()
class Point2(NestedBaseTrajectoryDataclass):
    x: np.ndarray
    y: np.ndarray


@dataclass()
class Vector2(NestedBaseTrajectoryDataclass):
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
