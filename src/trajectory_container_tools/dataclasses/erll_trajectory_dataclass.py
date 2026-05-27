# coding=utf-8
from dataclasses import dataclass
from typing import Optional

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeature,
)


@dataclass()
class TestTrajectoryDataclass(BaseTrajectoryFeature):
    """
    Represents a trajectory dataclass that stores observations and actions.

    This class encapsulates the observations and actions in a trajectory, providing structure
    to the data for further processing, analysis, or manipulation.

    :ivar observations: The sequence of observations in the trajectory.
    :type observations: numpy.ndarray
    :ivar actions: The sequence of actions corresponding to the observations.
    :type actions: numpy.ndarray
    :ivar timestamps: Timestamp associated to the data for further processing, analysis, or manipulation.
    :type timestamps: numpy.ndarray
    :ivar velocity_frame: The frame of reference for velocity measurements. Defaults to None.
    :type velocity_frame: Optional[str]
    """

    observations: np.ndarray
    actions: np.ndarray
    timestamps: np.ndarray
    obs_are_velocity: Optional[bool]
    velocity_frame: Optional[str]


@dataclass()
class TestMotionTrajectoryDataclass(TestTrajectoryDataclass):
    """
    Handles motion trajectory data, including both estimated and ground truth poses.

    This class is a data structure for managing trajectory information that includes
    estimated pose data and corresponding ground truth pose data. The purpose of
    this class is to store and organize pose-related data for use in motion trajectory
    analysis and comparison.

    :ivar observations: The sequence of observations in the trajectory.
    :type observations: numpy.ndarray
    :ivar actions: The sequence of actions corresponding to the observations.
    :type actions: numpy.ndarray
    :ivar timestamps: Timestamp associated to the data for further processing, analysis, or manipulation.
    :type timestamps: numpy.ndarray
    :ivar velocity_frame: The frame of reference for velocity measurements. Defaults to None.
    :type velocity_frame: Optional[str]
    :ivar pose: The estimated pose data represented as a numpy array.
    :type pose: np.ndarray
    :ivar pose_gt: The ground truth pose data represented as a numpy array.
    :type pose_gt: np.ndarray
    """

    pose: np.ndarray
    pose_gt: np.ndarray
    orientation_gt: Optional[np.ndarray] = None
