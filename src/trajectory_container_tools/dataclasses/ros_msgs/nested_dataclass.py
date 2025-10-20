# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .core_dataclass import NestedRosStampedFeature, NestedBaseTrajectory
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import GeometryMsgsPoint, \
    GeometryMsgsQuaternion, GeometryMsgsTransform, GeometryMsgsVector3


# .... Geometry msgs ..............................................................................
@dataclass()
class GeometryMsgsPose(NestedBaseTrajectory):
    """
    Represents a pose with position and orientation.

    Compatible ros2 message interface: geometry_msgs/msg/Pose

    A `Pose` class combines position and orientation to define the state or
    configuration of an object in a 3-dimensional space. This is often used
    in robotics, graphics, or physics simulations where both the location
    (point) and the spatial orientation (rotation) of an object are required.

    :ivar position: Spatial position of the object.
    :type position: GeometryMsgsPoint
    :ivar orientation: Orientation of the object defined as a quaternion.
    :type orientation: GeometryMsgsQuaternion
    """

    position: GeometryMsgsPoint
    orientation: GeometryMsgsQuaternion


@dataclass()
class GeometryMsgsPoseWithCovariance(NestedBaseTrajectory):
    """Represents a pose with its covariance data.

    Compatible ros2 message interface: geometry_msgs/msg/PoseWithCovariance

    This class is used to encapsulate a pose along with its associated covariance matrix,
    which provides information about the uncertainty of the pose observations. The pose
    describes position and orientation, and the covariance matrix quantifies the uncertainty in
    these observations. It is useful in robotics, navigation, and computer vision applications
    where pose estimation is required.

    :ivar pose: The pose represented as a position and orientation.
    :type pose: GeometryMsgsPose
    :ivar covariance: The covariance matrix associated with the pose,
        representing the uncertainty in the pose observations.
    :type covariance: numpy.ndarray
    """

    pose: GeometryMsgsPose
    covariance: np.ndarray


@dataclass()
class GeometryMsgsTwist(NestedBaseTrajectory):
    """
    Represents a 6DOF twist with linear and angular components.

    Compatible ros2 message interface: geometry_msgs/msg/Twist

    This class is used to encapsulate both linear and angular velocity
    components in 3D space. It is a fundamental representation in various
    robotic systems for describing motion or spatial velocity.

    :ivar linear: The linear velocity vector.
    :type linear: GeometryMsgsVector3
    :ivar angular: The angular velocity vector.
    :type angular: GeometryMsgsVector3
    """

    linear: GeometryMsgsVector3
    angular: GeometryMsgsVector3


@dataclass()
class GeometryMsgsTwistWithCovariance(NestedBaseTrajectory):
    """Represents a twist with an associated covariance matrix.

    Compatible ros2 message interface: geometry_msgs/msg/TwistWithCovariance

    This dataclass encapsulates a twist (which typically includes linear and angular velocity
    components) along with a covariance matrix. It is used in contexts where both the twist and
    its uncertainty are required, such as motion modeling or state estimation in robotics and
    related applications.

    :ivar twist: The twist, including linear and angular components.
    :type twist: GeometryMsgsTwist
    :ivar covariance: The covariance matrix associated with the twist.
    :type covariance: np.ndarray
    """

    twist: GeometryMsgsTwist
    covariance: np.ndarray


@dataclass()
class GeometryMsgsTransformStampedFeature(NestedRosStampedFeature):
    """
    Represents a ROS2-compatible TransformStamped message structure.

    Compatible ros2 message interface: geometry_msgs/msg/TransformStamped

    This class models a `TransformStamped` message from the `geometry_msgs` ROS2
    package, designed to handle transformations between coordinate frames. It
    includes a child frame identifier and a transformation object that specifies
    the translation and rotation.

    :ivar childFrameId: The name of the child coordinate frame.
    :type childFrameId: str
    :ivar transform: The transformation object defining translation and rotation
        between frames.
    :type transform: GeometryMsgsTransform
    """
    childFrameId: str
    transform: GeometryMsgsTransform


# .... Ackermann msgs .............................................................................
@dataclass()
class AckermannMsgsAckermannDrive(NestedBaseTrajectory):
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


# .... Vesc msgs ..................................................................................
@dataclass()
class VescMsgsVescImu(NestedBaseTrajectory):
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
