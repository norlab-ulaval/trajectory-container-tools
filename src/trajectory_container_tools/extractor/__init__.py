# coding=utf-8
"""
Extractor namespace for trajectory container tools.

This module provides functions for extracting trajectory data from various sources:
- ROS bag files
- Pandas DataFrames
- Feature extraction and validation utilities
"""

# Main extractor API functions
from trajectory_container_tools.extractor.rosbag_to_tct import from_rosbag, extract_rosbag_feature
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import \
    show_rosbag_summary_info

from trajectory_container_tools.extractor.dataframe_to_tct import (
    from_dataframe,
    extract_dataframe_feature,
    unpack_dataframe_and_show_topic,
)

__all__ = [
    # ROS bag extraction functions
    "from_rosbag",
    "extract_rosbag_feature",
        # DataFrame extraction functions
    "from_dataframe",
    "extract_dataframe_feature",
    "unpack_dataframe_and_show_topic",
]
