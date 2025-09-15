# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from .temporal_tools.timestamps import Timestamps
from ..trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass

from ..trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
    AbstractTrajectoryDataclass,
)
from ..trj_dataclasses.ros2_feature_dataclass import RosStampedDataclass

TrajectoryDataclass = NewType("TrajectoryDataclass", AbstractTrajectoryDataclass)

MultifeatureTrajectoryDataclass = NewType(
    "MultifeatureTrajectoryDataclass", AbstractMultifeatureDataclass
)

ShadowDataContainer: TypeAlias = Dict[
    str,
    Union[
        None,
        List,
        np.ndarray,
        Dict,
        Union[
            type[RosStampedDataclass],
            type[NestedBaseTrajectoryDataclass],
            type[Timestamps],
        ],
        Union[RosStampedDataclass, NestedBaseTrajectoryDataclass, Timestamps],
    ],
]
