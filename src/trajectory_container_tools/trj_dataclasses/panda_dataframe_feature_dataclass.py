# coding=utf-8
from dataclasses import dataclass

import numpy as np

from ..trj_dataclasses.abstract_trajectory_dataclass import AbstractTrajectoryDataclass

# Note: nested trajectory-dataclass is not yet supported for dataframe extraction.
#       Use flat layout for now

# ::: Marmotte slip Dataframe dataset related :::::::::::::::::::::::::::::::::::::::::::::::::::::
@dataclass()
class DataframeFeatureDataclass(AbstractTrajectoryDataclass):

    @property
    def _init_trj_axe(self) -> int:
        return -1


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

