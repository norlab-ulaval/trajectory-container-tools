# coding=utf-8

from typing import NewType

from ..trj_dataclasses.abstract_trajectory_dataclass import AbstractMultifeatureDataclass, AbstractTrajectoryDataclass

TrajectoryDataclass = NewType('TrajectoryDataclass', AbstractTrajectoryDataclass)
MultifeatureTrajectoryDataclass = NewType('MultifeatureTrajectoryDataclass', AbstractMultifeatureDataclass)
MultifeatureTrajectoryDataclass = NewType('MultifeatureTrajectoryDataclass', AbstractMultifeatureDataclass)

