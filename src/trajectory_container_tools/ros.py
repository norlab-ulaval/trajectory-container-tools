# coding=utf-8
"""
ROS-specific utilities and functions.

This module provides ROS-related functionality including:
- Topic inspection
- Message type registration
- ROS bag utilities
- Type store management

Usage:
    import trajectory_container_tools as tct
    tct.ros.check_topics(rosbag_path)
    tct.ros.register_non_native_msgs()
"""

# ROS utilities
from .rosbag_to_tct import check_rosbag_path_and_show_available_topics as check_topics
from .utils.ros2_non_native_msg import register_ros2_non_native_msg as register_non_native_msgs
from .utils.ros2_utils import (
    get_rosbag_typestore_auto_distro,
    rosbag_topic_time_to_timestamp
)

# ROS dataclasses (convenient access)
from .trj_dataclasses.ros2_feature_dataclass import (
    NavMsgsOdometry,
    SensorMsgsImu,
    AckermannMsgsAckermannDriveStamped,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
    Scan
)

__all__ = [
    # Utilities
    'check_topics',
    'register_non_native_msgs', 
    'get_rosbag_typestore_auto_distro',
    'rosbag_topic_time_to_timestamp',
    
    # Common ROS dataclasses
    'NavMsgsOdometry',
    'SensorMsgsImu',
    'AckermannMsgsAckermannDriveStamped', 
    'Tf2MsgsTFMessage',
    'VescMsgsVescImuStamped',
    'Scan',
]
