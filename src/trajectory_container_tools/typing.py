# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import NestedBaseTrajectoryDataclass

from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
    AbstractTrajectoryDataclass,
)
from trajectory_container_tools.dataclasses import RosDataclass, RosStampedDataclass

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
