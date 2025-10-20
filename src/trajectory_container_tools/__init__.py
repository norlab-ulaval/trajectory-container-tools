# coding=utf-8
"""
Trajectory Container Tools (TCT)

A library for managing trajectory-related data with support for:
- ROS bag data extraction
- Pandas DataFrame processing
- Multiple trajectory dataclass types
- Temporal analysis tools
- Visualization utilities

Quick Start:

>>> import trajectory_container_tools as tct
>>>
>>> features_config = {
>>>     '/odom': tct.dataclasses.NavMsgsOdometry,
>>>     '/tf': tct.dataclasses.Tf2MsgsTFMessage,
>>> }
>>>
>>> # Extract from ROS bag
>>> data = tct.extractor.from_rosbag("/rosbag/path", features_config)
>>>
>>> # Extract from DataFrame
>>> data = tct.extractor.from_dataframe(df, features_config)
>>>
>>> # Access dataclasses
>>> odom_class = tct.dataclasses.ros_msgs.stamped_dataclass.NavMsgsOdometry
>>>
>>> # Utilities
>>> tct.extractor.check_bag_topics(rosbag_path)

"""
import warnings

# Version info
from .version import __version__

# Core abstract classes
from .dataclasses.core.abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from .dataclasses.core.abstract_array_trajectory_dataclass import (
    AbstractTrajectoryArray,
)
from .dataclasses.core.abstract_trajectory_features_bag_dataclass import (
    AbstractTrajectoryFeaturesBag,
)
from .dataclasses.core.abstract_trajectory_stamped_features_bag_dataclass import (
    AbstractTrajectoryStampedFeaturesBag,
)
from .dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeature,
    NestedBaseTrajectory,
    BaseTrajectoryArray,
)

from .utils.containers_sanity_checks import containers_timestep_alignment_sanity_check
from .utils.general import RosImportError

# Common exceptions
from .temporal import TimestampCausalOrderingError

# Submodule imports for namespace organization (moved to end to avoid circular imports)
from . import dataclasses as dataclasses
from . import factory
from . import temporal
from . import typing
from . import utils


__all__ = [
    # Version
    "__version__",
    # Core classes
        "AbstractTrajectoryFeature",
        "AbstractTrajectoryFeaturesBag",
        "AbstractTrajectoryStampedFeaturesBag",
        "AbstractTrajectoryArray",
        "BaseTrajectoryFeature",
        "NestedBaseTrajectory",
        "BaseTrajectoryArray",
    # Namespaces
    "dataclasses",
    "factory",
    "temporal",
    "typing",
    "utils",
    # Container level check
    "containers_timestep_alignment_sanity_check",
    # Common exceptions
    "TimestampCausalOrderingError",
]

try:
    from . import extractor
    from . import ros

    __all__ += [
        "extractor",
        "ros",
    ]

except RosImportError as e:
    warnings.warn(
        (
            f"Be advised 'trajectory_container_tools' was installed without ros2 support "
            f"enabled. {e.messages}"
        ),
        stacklevel=2,
    )
