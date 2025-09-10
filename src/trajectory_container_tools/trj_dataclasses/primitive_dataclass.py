# coding=utf-8
from dataclasses import dataclass, field
from typing import Type

import numpy as np

from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass


@dataclass()
class Point(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Point
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray

@dataclass()
class Vector3(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Vector3
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass()
class Quaternion(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Quaternion
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    w: np.ndarray

@dataclass()
class Header(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: std_msgs/msg/Header
    frame_id: str
    timestamps: np.ndarray

