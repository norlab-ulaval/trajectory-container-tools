# coding=utf-8
from dataclasses import dataclass, field

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Note: nested trajectory-dataclass is not yet supported for dataframe extraction.
#       Use flat layout in the mean time
# /////////////////////////////////////////////////////////////////////////////////////////////////

@dataclass()
class BaseDataframeFeatureDataclass(AbstractTrajectoryDataclass):
    """
    Represents a dataclass for handling trajectory data fetched from a Panda dataframe.

    This class is utilized as a specialized data structure that inherits features from the
    BaseReverseAxisTrajectoryDataclass, aiming to encapsulate and manage properties related to
    dataframe features.

    It can be extended or utilized wherever structured data for dataframe processing or
    trajectory computation is necessary.
    """
    timesteps: np.ndarray

    @property
    def _init_trj_axe(self) -> int:
        return -1


@dataclass()
class NestedBaseDataframeFeatureDataclass(BaseDataframeFeatureDataclass):
    """
    # (NICE TO HAVE) ToDo: implement nested trajectory-dataclass support for dataframe extraction
    """
    feature_name: str = field(default=None, init=False)

    def on_begin_post_init_callback(self):
        super().on_begin_post_init_callback()
        raise NotImplementedError("Nested trajectory for dataframe is not supported yet.")


@dataclass()
class StatePose2D(BaseDataframeFeatureDataclass):
    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray


@dataclass()
class CmdStandard(BaseDataframeFeatureDataclass):
    linear_vel: np.ndarray
    angular_vel: np.ndarray


@dataclass()
class CmdSkidSteer(BaseDataframeFeatureDataclass):
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
