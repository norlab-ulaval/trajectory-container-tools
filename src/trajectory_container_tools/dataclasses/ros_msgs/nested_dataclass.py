# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .core_dataclass import NestedRosStampedDataclass, NestedBaseTrajectoryDataclass
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Point, \
    Quaternion, Transform, Vector3


@dataclass()
class Pose(NestedBaseTrajectoryDataclass):
    """
    Represents a pose with position and orientation.

    Compatible ros2 message interface: geometry_msgs/msg/Pose

    A `Pose` class combines position and orientation to define the state or
    configuration of an object in a 3-dimensional space. This is often used
    in robotics, graphics, or physics simulations where both the location
    (point) and the spatial orientation (rotation) of an object are required.

    :ivar position: Spatial position of the object.
    :type position: Point
    :ivar orientation: Orientation of the object defined as a quaternion.
    :type orientation: Quaternion
    """

    position: Point
    orientation: Quaternion


@dataclass()
class PoseWithCovariance(NestedBaseTrajectoryDataclass):
    """Represents a pose with its covariance data.

    Compatible ros2 message interface: geometry_msgs/msg/PoseWithCovariance

    This class is used to encapsulate a pose along with its associated covariance matrix,
    which provides information about the uncertainty of the pose observations. The pose
    describes position and orientation, and the covariance matrix quantifies the uncertainty in
    these observations. It is useful in robotics, navigation, and computer vision applications
    where pose estimation is required.

    :ivar pose: The pose represented as a position and orientation.
    :type pose: Pose
    :ivar covariance: The covariance matrix associated with the pose,
        representing the uncertainty in the pose observations.
    :type covariance: numpy.ndarray
    """

    pose: Pose
    covariance: np.ndarray


@dataclass()
class Twist(NestedBaseTrajectoryDataclass):
    """
    Represents a 6DOF twist with linear and angular components.

    Compatible ros2 message interface: geometry_msgs/msg/Twist

    This class is used to encapsulate both linear and angular velocity
    components in 3D space. It is a fundamental representation in various
    robotic systems for describing motion or spatial velocity.

    :ivar linear: The linear velocity vector.
    :type linear: Vector3
    :ivar angular: The angular velocity vector.
    :type angular: Vector3
    """

    linear: Vector3
    angular: Vector3


@dataclass()
class TwistWithCovariance(NestedBaseTrajectoryDataclass):
    """Represents a twist with an associated covariance matrix.

    Compatible ros2 message interface: geometry_msgs/msg/TwistWithCovariance

    This dataclass encapsulates a twist (which typically includes linear and angular velocity
    components) along with a covariance matrix. It is used in contexts where both the twist and
    its uncertainty are required, such as motion modeling or state estimation in robotics and
    related applications.

    :ivar twist: The twist, including linear and angular components.
    :type twist: Twist
    :ivar covariance: The covariance matrix associated with the twist.
    :type covariance: np.ndarray
    """

    twist: Twist
    covariance: np.ndarray


@dataclass()
class AckermannMsgsAckermannDrive(NestedBaseTrajectoryDataclass):
    """
    Represents the desired Ackermann drive trajectory parameters with specified
    steering angle, velocity, speed, acceleration, and jerk.

    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDrive

    :ivar steeringAngle: Desired virtual steering angle in radians.
    :type steeringAngle: numpy.ndarray
    :ivar steeringAngleVelocity: Desired rate of change of steering angle in radians per second.
    :type steeringAngleVelocity: numpy.ndarray
    :ivar speed: Desired forward speed in meters per second.
    :type speed: numpy.ndarray
    :ivar acceleration: Desired acceleration in meters per second squared.
    :type acceleration: numpy.ndarray
    :ivar jerk: Desired jerk in meters per second cubed.
    :type jerk: numpy.ndarray
    """

    steeringAngle: np.ndarray  # desired virtual angle (radians)
    steeringAngleVelocity: np.ndarray  # desired rate of change (radians/s)
    speed: np.ndarray  # desired forward speed (m/s)
    acceleration: np.ndarray  # desired acceleration (m/s^2)
    jerk: np.ndarray  # desired jerk (m/s^3)


@dataclass()
class VescMsgsVescImu(NestedBaseTrajectoryDataclass):
    """
    Represents IMU data related to VESC (Vedder Electronic Speed Controller).

    Compatible ros2 message interface: vesc_msgs/msg/VescImu

    This dataclass encapsulates IMU information, such as yaw-pitch-roll, angular
    velocity, linear acceleration, compass readings, and orientation as a ROS2
    message interface.

    :ivar ypr: The yaw, pitch, and roll data as a 3D vector.
    :type ypr: Vector3
    :ivar angularVelocity: The angular velocity readings as a 3D vector.
    :type angularVelocity: Vector3
    :ivar linearAcceleration: The linear acceleration readings as a 3D vector.
    :type linearAcceleration: Vector3
    :ivar compass: The compass data represented as a 3D vector.
    :type compass: Vector3
    :ivar orientation: The orientation represented as a quaternion.
    :type orientation: Quaternion
    """

    ypr: Vector3
    angularVelocity: Vector3
    linearAcceleration: Vector3
    compass: Vector3
    orientation: Quaternion

# ==== Nested and stamped =========================================================================
@dataclass()
class TransformStamped(NestedRosStampedDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/TransformStamped
    childFrameId: str
    transform: Transform
