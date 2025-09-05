# coding=utf-8
from dataclasses import dataclass

import numpy as np

from ..trj_dataclasses.abstract_trajectory_dataclass import AbstractTrajectoryDataclass


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
    pass


@dataclass()
class VelocitySkidSteer(CmdSkidSteer):
    pass




@dataclass()
class DisturbanceQueryState:
    # (NICE TO HAVE) ToDo: validate nested trajectory dataclass
    state_pose_k: StatePose2D
    velocity_skid_steer_k_previous: VelocitySkidSteer
    cmd_skid_steer_k: CmdSkidSteer
    cmd_skid_steer_k_previous: CmdSkidSteer
