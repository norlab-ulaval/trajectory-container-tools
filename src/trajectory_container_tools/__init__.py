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
    import trajectory_container_tools as tct
    
    # Extract from ROS bag
    data = tct.from_rosbag(rosbag_path, features_config)
    
    # Extract from DataFrame
    data = tct.from_dataframe(df, features_config)
    
    # Access dataclasses
    odom_class = tct.dataclasses.NavMsgsOdometry
    
    # Utilities
    tct.ros.check_topics(rosbag_path)
"""

# Version info
from .version import __version__

# Main API - Top-level convenience functions
from .rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag as from_rosbag,
    extract_single_feature_from_rosbag as extract_rosbag_feature,
    check_rosbag_path_and_show_available_topics as check_rosbag
)

from .dataframe_to_tct import (
    aggregate_multiple_features_from_dataframe as from_dataframe,
    extract_single_feature_from_dataframe as extract_dataframe_feature,
    unpack_dataframe_and_show_topic as check_dataframe
)

# Backward compatibility - keep original names
from .rosbag_to_tct import (
    aggregate_multiple_features_from_rosbag,
    extract_single_feature_from_rosbag,
    check_rosbag_path_and_show_available_topics
)

from .dataframe_to_tct import (
    aggregate_multiple_features_from_dataframe,
    extract_single_feature_from_dataframe,
    unpack_dataframe_and_show_topic
)

# Core abstract classes
from .trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass
)
from .trj_dataclasses.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass
)

# Common exceptions
from .utils.temporal_tools.timestamps import TimestampCausalOrderingError

# Submodule imports for namespace organization (moved to end to avoid circular imports)
from . import trj_dataclasses as dataclasses
from . import ros  
from . import factory
from . import temporal
from . import utils
from . import plot

__all__ = [
    # Version
    '__version__',
    
    # Main API functions (new names)
    'from_rosbag',
    'from_dataframe', 
    'extract_rosbag_feature',
    'extract_dataframe_feature',
    'check_rosbag',
    'check_dataframe',
    
    # Backward compatibility (original names)
    'aggregate_multiple_features_from_rosbag',
    'extract_single_feature_from_rosbag',
    'check_rosbag_path_and_show_available_topics',
    'aggregate_multiple_features_from_dataframe',
    'extract_single_feature_from_dataframe',
    'unpack_dataframe_and_show_topic',
    
    # Core classes
    'AbstractTrajectoryDataclass',
    'AbstractMultifeatureDataclass', 
    'BaseTrajectoryDataclass',
    'NestedBaseTrajectoryDataclass',
    
    # Namespaces
    'dataclasses',
    'ros',
    'factory', 
    'temporal',
    'utils',
    'plot',
    
    # Common exceptions
    'TimestampCausalOrderingError',
]


