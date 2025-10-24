# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from trajectory_container_tools.temporal import Timestamps

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import AbstractTrajectoryCommon
from trajectory_container_tools import AbstractTrajectoryFeaturesBag
from trajectory_container_tools.dataclasses import (
    RosFeature,
    RosFeatureArray,
    RosStampedFeature,
)

# (☕minor) ToDo: TCT-90 chore: assess naming convention for the hierarchy highest class,
#   either TrajectoryContainer or TrajectoryDataclass
TrajectoryContainer = NewType("TrajectoryContainer", AbstractTrajectoryCommon)

TrajectoryFeature = NewType("TrajectoryFeature", AbstractTrajectoryFeature)

TrajectoryFeaturesBag = NewType(
    "TrajectoryFeaturesBag", AbstractTrajectoryFeaturesBag
)

ShadowDataContainer: TypeAlias = Dict[
    str,
    Union[
        None,
        int,
        list,
        np.ndarray,
        Dict,
        Union[
            type[RosFeature],
            type[RosFeatureArray],
            type[RosStampedFeature],
            type[Timestamps],
        ],
        Union[RosFeature, RosFeatureArray, RosStampedFeature, Timestamps],
    ],
]
