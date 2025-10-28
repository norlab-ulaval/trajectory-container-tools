# coding=utf-8
from typing import Dict, NewType, TypeAlias, Union

import numpy as np

from trajectory_container_tools import (
    AbstractTrajectoryFeature,
    AbstractTrajectoryFeaturesBag,
)
from trajectory_container_tools.dataclasses import (
    RosFeature,
    RosFeatureArray,
    RosStampedFeature,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass_common import (
    AbstractTrajectoryCommon,
)
from trajectory_container_tools.temporal import Timestamps

# (☕minor) ToDo: TCT-90 chore: assess naming convention for the hierarchy highest class,
#   either TrajectoryContainer or TrajectoryDataclass
TrajectoryContainer = NewType("TrajectoryContainer", AbstractTrajectoryCommon)

TrajectoryFeature = NewType("TrajectoryFeature", AbstractTrajectoryFeature)
TrajectoryFeaturesBag = NewType("TrajectoryFeaturesBag", AbstractTrajectoryFeaturesBag)

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
