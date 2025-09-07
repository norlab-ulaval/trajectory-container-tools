# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .base_trajectory_dataclass import BaseReverseAxisTrajectoryDataclass


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Note: nested trajectory-dataclass is not yet supported for dataframe extraction.
#       Use flat layout in the mean time
# /////////////////////////////////////////////////////////////////////////////////////////////////

@dataclass()
class DataframeFeatureDataclass(BaseReverseAxisTrajectoryDataclass):
    """
    Represents a dataclass for handling trajectory data fetched from a Panda dataframe.

    This class is utilized as a specialized data structure that inherits features from the
    BaseReverseAxisTrajectoryDataclass, aiming to encapsulate and manage properties related to
    dataframe features.

    It can be extended or utilized wherever structured data for dataframe processing or
    trajectory computation is necessary.
    """
    pass


@dataclass()
class StatePose2D(DataframeFeatureDataclass):
    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray


@dataclass()
class CmdStandard(DataframeFeatureDataclass):
    linear_vel: np.ndarray
    angular_vel: np.ndarray


@dataclass()
class CmdSkidSteer(DataframeFeatureDataclass):
    left: np.ndarray
    right: np.ndarray


@dataclass()
class Velocity(CmdStandard):
    # Same properties as CmdStandard
    pass


@dataclass()
class VelocitySkidSteer(CmdSkidSteer):
    # Same properties as CmdSkidSteer
    pass
