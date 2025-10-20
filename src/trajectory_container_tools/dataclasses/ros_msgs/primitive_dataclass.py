# coding=utf-8
from dataclasses import dataclass
from typing import Union

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    NestedBaseTrajectory,
)
from trajectory_container_tools.temporal.timestamps import Timestamps


@dataclass()
class StdMsgsHeader(NestedBaseTrajectory):
    """Represents a ros header containing frame information and time-related data.

    Compatible ros2 message interface: std_msgs/msg/Header

    This class ensures that timestamps are processed properly, converting numpy arrays to the
    specified `Timestamps` type and validating causal ordering to maintain data consistency.

    The `timestamps` target type is Timestamps but accept numpy array for convenience which will be
    converted to the target type at instanciation.

    :ivar frame_id: Identifier for the coordinate frame.
    :ivar timestamps: Time-related information, either a Timestamps object or a numpy array
                      (converted to Timestamps internally at instanciation).
    :type timestamps: Timestamps
    """

    frame_id: str
    timestamps: Union[Timestamps, np.ndarray]

    def on_begin_post_init_callback(self) -> None:
        timestamps: Union[Timestamps, np.ndarray]

        if isinstance(self.timestamps, np.ndarray):
            self.timestamps = Timestamps(self.timestamps)

        self.timestamps.causal_ordering_sanity_check(show_offending_in_nanoseconds=True)


@dataclass()
class GeometryMsgsPoint(NestedBaseTrajectory):
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
class GeometryMsgsVector3(NestedBaseTrajectory):
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
class GeometryMsgsVector3Stamped(NestedBaseTrajectory):
    """
    Represents a ROS2 compatible message interface for a stamped 3D vector.

    Compatible ros2 message interface: geometry_msgs/msg/Vector3Stamped

    The GeometryMsgsVector3Stamped class encapsulates a 3D vector with an associated
    header containing a timestamp and frame information. It adheres to the ROS2
    message structure and is intended for use in applications involving time-stamped
    vector data, such as 3D motion or navigation systems.

    :ivar header: The standard header containing timestamp and frame ID.
    :type header: StdMsgsHeader
    :ivar vector: The 3D vector data.
    :type vector: GeometryMsgsVector3
    """
    header: StdMsgsHeader
    vector: GeometryMsgsVector3


@dataclass()
class GeometryMsgsPointStamped(NestedBaseTrajectory):
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
class GeometryMsgsQuaternion(NestedBaseTrajectory):
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
class GeometryMsgsTransform(NestedBaseTrajectory):
    """
    Represents a 3D transform consisting of translation and rotation.

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
