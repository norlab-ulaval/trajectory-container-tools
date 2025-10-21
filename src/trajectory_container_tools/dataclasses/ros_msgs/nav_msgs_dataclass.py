# coding=utf-8
from dataclasses import dataclass

from trajectory_container_tools.dataclasses.ros_msgs.geometry_msgs_dataclass import (
    GeometryMsgsPoseWithCovariance,
    GeometryMsgsTwistWithCovariance,
    RosStampedFeature,
)


@dataclass()
class NavMsgsOdometry(RosStampedFeature):
    """Data container for navigation messages odometry (nested data container version).

    Compatible ros2 message interface: nav_msgs/msg/Odometry

    This class serves as a structured container for navigation message data related to odometry
    in ROS. It captures the pose and twist information along with their covariance data. The
    purpose of this container is to facilitate organized and consistent handling of these
    odometry-related data structures. Useful in systems where readability and maintainability of
    the navigation-related data are critical.

    :ivar pose: Contains the pose along with its associated covariance information.
    :type pose: trajectory_container_tools.dataclasses.GeometryMsgsPoseWithCovariance
    :ivar twist: Contains the twist along with its associated covariance information.
    :type twist: trajectory_container_tools.dataclasses.GeometryMsgsTwistWithCovariance
    """

    pose: GeometryMsgsPoseWithCovariance
    twist: GeometryMsgsTwistWithCovariance
