# coding=utf-8
"""
ROS-specific utilities and functions.

This module provides ROS-related functionality including:
- Topic inspection
- Message type registration
- ROS bag utilities
- Type store management

Usage:
    >>> import trajectory_container_tools as tct
    >>> tct.ros.check_bag_topics(rosbag_path)
    >>> tct.ros.register_non_native_msgs()
"""

# ROS utilities
from trajectory_container_tools.extractor.rosbag_to_tct import check_bag_topics
from .utils.ros2_non_native_msg import register_non_native_msgs
from .utils.ros2_utils import (
    get_rosbag_typestore_auto_distro,
    rosbag_topic_time_to_timestamp,
    get_ros2_distro,
)

__all__ = [
    # Utilities
    "check_bag_topics",
    "register_non_native_msgs",
    "get_rosbag_typestore_auto_distro",
    "rosbag_topic_time_to_timestamp",
    'get_ros2_distro',
]
