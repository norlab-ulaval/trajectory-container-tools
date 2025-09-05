# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .base_trajectory_dataclass import BaseTrajectoryDataclass


@dataclass()
class F110MotionDynamicDataclass(BaseTrajectoryDataclass):
    """
    F110-gym motion dynamic trajectory dataclass
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
