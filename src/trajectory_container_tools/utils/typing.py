# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from .temporal_tools.timestamps import Timestamps
from ..dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass

from ..dataclasses.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
    AbstractTrajectoryDataclass,
)
from ..dataclasses.ros2_feature_dataclass import RosDataclass, RosStampedDataclass

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
            type[RosDataclass],
            type[RosStampedDataclass],
            type[NestedBaseTrajectoryDataclass],
            type[Timestamps],
        ],
        Union[RosDataclass, RosStampedDataclass, NestedBaseTrajectoryDataclass, Timestamps],
    ],
]
