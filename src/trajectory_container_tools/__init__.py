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
    >>> data = tct.from_rosbag(rosbag_path, features_config)
    >>>
    >>> # Extract from DataFrame
    >>> data = tct.from_dataframe(df, features_config)
    >>>
    >>> # Access dataclasses
    >>> odom_class = tct.dataclasses.NavMsgsOdometry
    >>>
    >>> # Utilities
    >>> tct.ros.check_bag_topics(rosbag_path)
"""

# Version info
from .version import __version__

# Main API - Top-level convenience functions
from trajectory_container_tools.extractor.rosbag_to_tct import from_rosbag, extract_rosbag_feature, check_bag_topics

from trajectory_container_tools.extractor.dataframe_to_tct import (
    from_dataframe,
    extract_dataframe_feature,
    unpack_dataframe_and_show_topic,
)

# Core abstract classes
from .dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass,
    AbstractNoTrajectoryDataclass,
)
from .dataclasses.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
    BaseNoTrajectoryDataclass,
)

# Common exceptions
from trajectory_container_tools.temporal import TimestampCausalOrderingError

# Submodule imports for namespace organization (moved to end to avoid circular imports)
from . import dataclasses as dataclasses
from . import ros
from . import factory
from . import temporal
from . import utils

__all__ = [
    # Version
    "__version__",

    # Main API functions
    "from_rosbag",
    "from_dataframe",
    "extract_rosbag_feature",
    "extract_dataframe_feature",
    "check_bag_topics",
    "unpack_dataframe_and_show_topic",

    # Core classes
    "AbstractTrajectoryDataclass",
    "AbstractMultifeatureDataclass",
    "AbstractNoTrajectoryDataclass",
    "BaseTrajectoryDataclass",
    "NestedBaseTrajectoryDataclass",
    "BaseNoTrajectoryDataclass",

    # Namespaces
    "dataclasses",
    "ros",
    "factory",
    "temporal",
    "utils",

    # Common exceptions
    "TimestampCausalOrderingError",
]
