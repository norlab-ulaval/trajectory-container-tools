# coding=utf-8
from dataclasses import dataclass

from .nested_dataclass import TransformStamped
from .core_dataclass import RosDataclass


@dataclass()
class Tf2MsgsTFMessage(RosDataclass):
    """Represents a message used in coordinate transformation tasks in ROS.

    Compatible ros2 message interface: tf2_msgs/msg/TFMessage

    This dataclass encapsulates information about a transformation (e.g., translation,
    rotation) for a specific frame in the ROS ecosystem. It is used specifically
    to store messages that relate to frame IDs and their associated transformations.

    :ivar transforms: Stamped Transformation data
    :type transforms: trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass.TransformStamped
    """

    transforms: list[TransformStamped]
