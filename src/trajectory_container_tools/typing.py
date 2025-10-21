# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from trajectory_container_tools.temporal import Timestamps

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from trajectory_container_tools import AbstractTrajectoryFeaturesBag
from trajectory_container_tools.dataclasses import (
    RosFeature,
    RosFeatureArray,
    RosStampedFeature,
)

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
