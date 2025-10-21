# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.ros_msgs.std_msgs_dataclass import StdMsgsHeader
from trajectory_container_tools.dataclasses.ros_msgs.core_dataclass import (
    RosFeature,
    RosStampedFeature,
)


@dataclass()
class GeometryMsgsPoint(RosFeature):
    """
    Represents a 3D point defined by x, y, and z coordinates.

    Compatible ros2 message interface: geometry_msgs/msg/Point

    This class is a part of a trajectory data structure. It captures the three-dimensional
    coordinates of a point, which can be used in various geometric and spatial computations.

    :ivar x: The x-coordinate of the point.
    :type x: np.ndarray
    :ivar y: The y-coordinate of the point.
    :type y: np.ndarray
    :ivar z: The z-coordinate of the point.
    :type z: np.ndarray
    """
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass()
class GeometryMsgsPointStamped(RosStampedFeature):
    """
    Represents a ROS2 compatible message interface for a stamped 3D point.

    Compatible ros2 message interface: geometry_msgs/msg/PointStamped

    This class combines point data with a timestamped header to represent
    a specific point in time and space within a given coordinate frame.
    It is designed to interface seamlessly with ROS2 message interfaces
    and can be utilized in trajectory systems where points coupled with
    temporal and spatial data are needed.

    :ivar header: Standard ROS2 message header containing timestamp and
        coordinate frame information.
    :type header: StdMsgsHeader
    :ivar point: The geometric point data representing a location in
        the specified coordinate frame.
    :type point: GeometryMsgsPoint
    """
    header: StdMsgsHeader
    point: GeometryMsgsPoint


@dataclass()
class GeometryMsgsVector3(RosFeature):
    """
    Represents a 3D vector defined by three numpy arrays.

    Compatible ros2 message interface: geometry_msgs/msg/Vector3

    This class models a vector with x, y, and z coordinates, where each coordinate
    is represented as a numpy array. It is compatible with the ROS2 message
    interface: geometry_msgs/msg/Vector3. The class is designed for use in
    trajectory computations and other operations requiring multidimensional data.

    :ivar x: The x-coordinate of the vector.
    :type x: np.ndarray
    :ivar y: The y-coordinate of the vector.
    :type y: np.ndarray
    :ivar z: The z-coordinate of the vector.
    :type z: np.ndarray
    """
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass()
class GeometryMsgsVector3Stamped(RosStampedFeature):
    """
    Represents a ROS2 compatible message interface for a stamped 3D vector.

    Compatible ros2 message interface: geometry_msgs/msg/Vector3Stamped

    The GeometryMsgsVector3Stamped class encapsulates a 3D vector with an associated
    header containing a timestamp and frame information. It adheres to the ROS2
    message structure and is intended for use in applications involving time-stamped
    vector data, such as 3D motion or navigation systems.

    :ivar header: The standard header containing timestamp and frame ID.
    :type header: trajectory_container_tools.dataclasses.StdMsgsHeader
    :ivar vector: The 3D vector data.
    :type vector: GeometryMsgsVector3
    """
    header: StdMsgsHeader
    vector: GeometryMsgsVector3


@dataclass()
class GeometryMsgsQuaternion(RosFeature):
    """
    Represents a Quaternion in 3D space.

    Compatible ros2 message interface: geometry_msgs/msg/Quaternion

    A quaternion is used for representing orientations and rotations in 3D
    space without the ambiguity of Euler angles. This class allows seamless
    interaction with ROS2-based systems that utilize quaternion messages.

    :ivar x: Represents the x-component of the quaternion.
    :type x: np.ndarray
    :ivar y: Represents the y-component of the quaternion.
    :type y: np.ndarray
    :ivar z: Represents the z-component of the quaternion.
    :type z: np.ndarray
    :ivar w: Represents the w-component (scalar component) of the quaternion.
    :type w: np.ndarray
    """
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    w: np.ndarray


@dataclass()
class GeometryMsgsTransform(RosFeature):
    """
    Represents a 3D transform consisting of translation and rotation.

    Compatible ros2 message interface: geometry_msgs/msg/Transform

    This dataclass models a transform in three-dimensional space, which is a
    combination of a translation vector and a rotational quaternion. It is
    compatible with the ROS 2 message interface `geometry_msgs/msg/Transform`.

    :ivar translation: Represents a 3D vector for the translation component
        of the transform.
    :type translation: GeometryMsgsVector3
    :ivar rotation: Represents a quaternion for the rotational component
        of the transform.
    :type rotation: GeometryMsgsQuaternion
    """
    # Compatible ros2 message interface: geometry_msgs/msg/Transform
    translation: GeometryMsgsVector3
    rotation: GeometryMsgsQuaternion


@dataclass()
class GeometryMsgsTransformStampedFeature(RosStampedFeature):
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


@dataclass()
class GeometryMsgsPose(RosFeature):
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
class GeometryMsgsPoseStamped(RosStampedFeature):
    """
    Represents a stamped Pose message in ROS.

    Compatible ros2 message interface: geometry_msgs/msg/PoseStamped

    This class is used for storing a pose with an associated timestamp and frame of reference. It
    extends the `RosStampedFeature` to integrate stamped ROS message functionality.
    Primarily, it stores a `GeometryMsgsPose` object which contains detailed pose data.

    :ivar pose: The pose data associated with this stamped message.
    :type pose: GeometryMsgsPose
    """
    pose: GeometryMsgsPose


@dataclass()
class GeometryMsgsPoseWithCovariance(RosFeature):
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
class GeometryMsgsPoseWithCovarianceStamped(RosStampedFeature):
    """
    Represents a ROS message for a Pose with covariance and timestamp.

    Compatible ros2 message interface: geometry_msgs/msg/PoseWithCovarianceStamped

    This class encapsulates a geometric Pose with an associated timestamp and frame identification
    as used in ROS (Robot Operating System) messages. It extends the functionality of the
    `RosStampedFeature` to include positional and orientational data with covariance, which is
    usually employed in navigation, robotics, and related fields to represent 6-DOF (Degrees of
    Freedom) poses with quantified uncertainty.

    :ivar pose: The pose with associated covariance information.
    :type pose: GeometryMsgsPoseWithCovariance
    """
    pose: GeometryMsgsPoseWithCovariance


@dataclass()
class GeometryMsgsTwist(RosFeature):
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
class GeometryMsgsTwistStamped(RosStampedFeature):
    """
    Represents a ROS Stamped Dataclass including a Twist message.

    Compatible ros2 message interface: geometry_msgs/msg/TwistStamped

    This class encapsulates a ROS stamped message containing a geometry_msgs type
    Twist message. It provides a structured and standardized way of handling
    timestamped velocity data in ROS systems.

    :ivar twist: The Twist message containing linear and angular velocity data.
    :type twist: GeometryMsgsTwist
    """
    twist: GeometryMsgsTwist


@dataclass()
class GeometryMsgsTwistWithCovariance(RosFeature):
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
class GeometryMsgsTwistWithCovarianceStamped(RosStampedFeature):
    """
    Represents a ROS-compatible TwistWithCovarianceStamped message.

    Compatible ros2 message interface: geometry_msgs/msg/TwistWithCovarianceStamped

    This dataclass is used to encapsulate the representation of a twist with
    covariance paired with a standard ROS header. It provides an interface
    for associating a velocity and angular twist in a covariance matrix with a
    timestamp and frame information.

    :ivar twist: The twist message containing linear/angular velocity with
                 covariance information.
    :type twist: GeometryMsgsTwistWithCovariance
    """
    twist: GeometryMsgsTwistWithCovariance
