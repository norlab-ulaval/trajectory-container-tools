# coding=utf-8

from typing import Dict, List, NewType, TypeAlias, Union

import numpy as np

from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import NestedBaseTrajectory

from trajectory_container_tools.dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from trajectory_container_tools import AbstractTrajectoryFeaturesBag
from trajectory_container_tools.dataclasses import RosFeaturesArray, RosStampedFeature

TrajectoryFeature = NewType("TrajectoryFeature", AbstractTrajectoryFeature)

TrajectoryFeaturesBag = NewType(
    "TrajectoryFeaturesBag", AbstractTrajectoryFeaturesBag
)

ShadowDataContainer: TypeAlias = Dict[
    str,
    Union[
        None,
        List,
        np.ndarray,
        Dict,
        Union[
            type[RosFeaturesArray],
            type[RosStampedFeature],
            type[NestedBaseTrajectory],
            type[Timestamps],
        ],
        Union[RosFeaturesArray, RosStampedFeature, NestedBaseTrajectory, Timestamps],
    ],
]
