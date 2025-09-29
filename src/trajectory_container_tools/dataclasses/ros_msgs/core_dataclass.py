# coding=utf-8
from dataclasses import dataclass

from ..core.base_trajectory_dataclass import (
    BaseNoTrajectoryDataclass,
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
)
from ..ros_msgs.primitive_dataclass import Header


@dataclass()
class RosDataclass(BaseNoTrajectoryDataclass):
    """
    Represents a ROS dataclass containing trajectory information.

    This dataclass is used to store trajectory data. This class inherits from
    `BaseTrajectoryDataclass` to provide trajectory-specific attributes and behaviors.
    """

    pass


@dataclass()
class RosStampedDataclass(BaseTrajectoryDataclass):
    """
    Represents a ROS-stamped dataclass containing trajectory information.

    Compatible ros2 message interface: std_msgs/msg/Header

    This dataclass is used to store trajectory data alongside its ROS message
    header. The header contains information such as timestamp and frame of
    reference, which are critical for synchronizing data within ROS-based
    systems. This class inherits from `BaseTrajectoryDataclass` to provide
    trajectory-specific attributes and behaviors.

    :ivar header: The ROS message header, which includes timestamp and frame of
        reference information.
    :type header: Header
    """

    header: Header


@dataclass()
class NestedRosStampedDataclass(NestedBaseTrajectoryDataclass):
    """
    Represents a ROS-stamped dataclass containing trajectory information (nested version).

    Compatible ros2 message interface: std_msgs/msg/Header

    :ivar header: The ROS message header, which includes timestamp and frame of
        reference information.
    :type header: Header
    :ivar feature_name: This attribute is set to None by default and is immutable.
    :type feature_name: str
    """

    header: Header
