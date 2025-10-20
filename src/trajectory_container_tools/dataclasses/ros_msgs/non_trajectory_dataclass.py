# coding=utf-8
from dataclasses import dataclass, field

from .nested_dataclass import GeometryMsgsTransformStampedFeature
from .core_dataclass import RosFeaturesArray


@dataclass()
class Tf2MsgsTFMessage(RosFeaturesArray):
    """Represents a message used in coordinate transformation tasks in ROS.

    Compatible ros2 message interface: tf2_msgs/msg/TFMessage

    This dataclass encapsulates information about a transformation (e.g., translation,
    rotation) for a specific frame in the ROS ecosystem. It is used specifically
    to store messages that relate to frame IDs and their associated transformations.

    :ivar transforms: Stamped Transformation data
    :type transforms: trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass.GeometryMsgsTransformStampedFeature
    """

    transforms: list[GeometryMsgsTransformStampedFeature]

    @property
    def registred_trajectory_object_list(self) -> str:
        return 'transforms'

