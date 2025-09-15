# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
)
from .primitive_dataclass import Pose2D, Velocity2D


@dataclass()
class F110observations(NestedBaseTrajectoryDataclass):
    timestamp: np.ndarray
    pose: Pose2D
    vel: Velocity2D


@dataclass()
class F110actions(NestedBaseTrajectoryDataclass):
    timestamp: np.ndarray
    steer: np.ndarray
    speed: np.ndarray


@dataclass()
class F110MotionDynamicDataclassNested(BaseTrajectoryDataclass):
    """
    F110-gym motion dynamic trajectory dataclass (nested version)
    """

    actions: F110actions
    obs: F110observations
    next_obs: F110observations
    # .... other ..................................................................................
    done: np.ndarray
    reward: np.ndarray


@dataclass()
class F110MotionDynamicDataclass(BaseTrajectoryDataclass):
    """
    F110-gym motion dynamic trajectory dataclass (flat version)
    """

    # .... actions ................................................................................
    steer: np.ndarray
    speed: np.ndarray
    # .... obs ....................................................................................
    timestamp: np.ndarray
    pose_x: np.ndarray
    pose_y: np.ndarray
    pose_theta: np.ndarray
    vel_x: np.ndarray
    vel_y: np.ndarray
    vel_ang: np.ndarray
    # .... next obs ...............................................................................
    next_timestamp: np.ndarray
    next_pose_x: np.ndarray
    next_pose_y: np.ndarray
    next_pose_theta: np.ndarray
    next_vel_x: np.ndarray
    next_vel_y: np.ndarray
    next_vel_ang: np.ndarray
    # .... other ..................................................................................
    done: np.ndarray
    reward: np.ndarray
