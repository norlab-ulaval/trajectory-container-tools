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
    >>> # Extract from ROS bag
    >>> data = tct.extractor.from_rosbag(rosbag_path, features_config)
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

# Version info
from .version import __version__


# Core abstract classes
from .dataclasses.core.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass,
    AbstractNoTrajectoryDataclass,
)
from .dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
    BaseNoTrajectoryDataclass,
)

from .utils.containers_sanity_checks import containers_timestep_alignment_sanity_check

# Common exceptions
from .temporal import TimestampCausalOrderingError

# Submodule imports for namespace organization (moved to end to avoid circular imports)
from . import dataclasses as dataclasses
from . import extractor
from . import ros
from . import factory
from . import temporal
from . import typing
from . import utils

__all__ = [
    # Version
    "__version__",

    # Core classes
    "AbstractTrajectoryDataclass",
    "AbstractMultifeatureDataclass",
    "AbstractNoTrajectoryDataclass",
    "BaseTrajectoryDataclass",
    "NestedBaseTrajectoryDataclass",
    "BaseNoTrajectoryDataclass",

    # Namespaces
    "dataclasses",
    "extractor",
    "ros",
    "factory",
    "temporal",
    "typing",
    "utils",

    # Container level check
    "containers_timestep_alignment_sanity_check",

    # Common exceptions
    "TimestampCausalOrderingError",
]
