# coding=utf-8
from dataclasses import dataclass

from .core_dataclass import RosFeature
from .geometry_msgs_dataclass import (
    GeometryMsgsQuaternion,
    GeometryMsgsVector3,
    RosStampedFeature,
)


@dataclass()
class VescMsgsVescImu(RosFeature):
    """
    Represents IMU data related to VESC (Vedder Electronic Speed Controller).

    Compatible ros2 message interface: vesc_msgs/msg/VescImu

    This dataclass encapsulates IMU information, such as yaw-pitch-roll, angular
    velocity, linear acceleration, compass readings, and orientation as a ROS2
    message interface.

    :ivar ypr: The yaw, pitch, and roll data as a 3D vector.
    :type ypr: GeometryMsgsVector3
    :ivar angularVelocity: The angular velocity readings as a 3D vector.
    :type angularVelocity: GeometryMsgsVector3
    :ivar linearAcceleration: The linear acceleration readings as a 3D vector.
    :type linearAcceleration: GeometryMsgsVector3
    :ivar compass: The compass data represented as a 3D vector.
    :type compass: GeometryMsgsVector3
    :ivar orientation: The orientation represented as a quaternion.
    :type orientation: GeometryMsgsQuaternion
    """

    ypr: GeometryMsgsVector3
    angularVelocity: GeometryMsgsVector3
    linearAcceleration: GeometryMsgsVector3
    compass: GeometryMsgsVector3
    orientation: GeometryMsgsQuaternion


@dataclass()
class VescMsgsVescImuStamped(RosStampedFeature):
    """
    Represents stamped IMU data related to VESC (Vedder Electronic Speed Controller).

    Compatible ros2 message interface: vesc_msgs/msg/VescImuStamped

    This class encapsulates data for a VESC IMU message with timestamping,
    extending the RosStampedFeature structure. It is compatible
    with the `vesc_msgs/msg/VescImuStamped` ROS2 message interface.
    The primary purpose of this class is to provide a structured data
    representation of IMU measurements retrieved from a VESC-based system.

    :ivar imu: Instance of the VescMsgsVescImu class, representing IMU data.
    :type imu: trajectory_container_tools.dataclasses.VescMsgsVescImu
    """

    imu: VescMsgsVescImu
