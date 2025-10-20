# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeature,
    NestedBaseTrajectory,
)


@dataclass()
class Point2D(NestedBaseTrajectory):
    """
    Represents a 2D Point with coordinates x and y.

    This class is used to encapsulate x and y coordinates of a point in
    a 2D space. It inherits functionality from NestedBaseTrajectory.

    :ivar x: Represents the x-coordinate of the 2D point.
    :type x: np.ndarray
    :ivar y: Represents the y-coordinate of the 2D point.
    :type y: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray


@dataclass()
class Point2DSA(BaseTrajectoryFeature):
    """
    Represents a 2D Point with coordinates x and y.
    Note: This is a standalone version of Point2D for non nested use cases.

    This class is used to encapsulate x and y coordinates of a point in
    a 2D space. It inherits functionality from NestedBaseTrajectory.

    :ivar x: Represents the x-coordinate of the 2D point.
    :type x: np.ndarray
    :ivar y: Represents the y-coordinate of the 2D point.
    :type y: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray


@dataclass()
class Vector2D(NestedBaseTrajectory):
    """
    Represents a two-dimensional vector with x and y components.

    This class is a dataclass that provides a representation of
    two-dimensional vectors and stores their x and y components
    as numpy arrays. It can be used to manipulate vector data
    within nested trajectory systems.

    :ivar x: The component of the vector in the x-direction.
    :type x: numpy.ndarray
    :ivar y: The component of the vector in the y-direction.
    :type y: numpy.ndarray
    """

    x: np.ndarray
    y: np.ndarray


@dataclass()
class Vector2DSA(BaseTrajectoryFeature):
    """
    Represents a two-dimensional vector with x and y components.
    Note: This is a standalone version of Vector2D for non nested use cases.

    This class is a dataclass that provides a representation of
    two-dimensional vectors and stores their x and y components
    as numpy arrays. It can be used to manipulate vector data
    within nested trajectory systems.

    :ivar x: The component of the vector in the x-direction.
    :type x: numpy.ndarray
    :ivar y: The component of the vector in the y-direction.
    :type y: numpy.ndarray
    """

    x: np.ndarray
    y: np.ndarray


@dataclass()
class Pose2D(NestedBaseTrajectory):
    """
    Represents a 2D pose with x, y coordinates and orientation angle.

    This class is used to handle and store 2D pose data, including
    the x and y position coordinates, as well as the orientation (theta)
    represented in radians. It provides a structured approach to work
    with pose data within computational frameworks.

    :ivar x: Array representing the x-coordinates of the pose.
    :type x: np.ndarray
    :ivar y: Array representing the y-coordinates of the pose.
    :type y: np.ndarray
    :ivar theta: Array representing the orientation angles (in radians).
    :type theta: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray


@dataclass()
class Pose2DSA(BaseTrajectoryFeature):
    """
    Represents a 2D pose with x, y coordinates and orientation angle.
    Note: This is a standalone version of Pose2D for non nested use cases.

    This class is used to handle and store 2D pose data, including
    the x and y position coordinates, as well as the orientation (theta)
    represented in radians. It provides a structured approach to work
    with pose data within computational frameworks.

    :ivar x: Array representing the x-coordinates of the pose.
    :type x: np.ndarray
    :ivar y: Array representing the y-coordinates of the pose.
    :type y: np.ndarray
    :ivar theta: Array representing the orientation angles (in radians).
    :type theta: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    theta: np.ndarray


@dataclass()
class Velocity2D(NestedBaseTrajectory):
    """
    Represents a 2D velocity with components along x, y axes, and an angular component.

    Handles the storage and management of velocity values across
    x-coordinate, y-coordinate, and angular direction.

    :ivar x: 1D array containing the velocity components along the x-axis.
    :type x: numpy.ndarray
    :ivar y: 1D array containing the velocity components along the y-axis.
    :type y: numpy.ndarray
    :ivar ang: 1D array containing the angular velocity components.
    :type ang: numpy.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    ang: np.ndarray


@dataclass()
class Velocity2DSA(BaseTrajectoryFeature):
    """
    Represents a 2D velocity with components along x, y axes, and an angular component.
    Note: This is a standalone version of Velocity2D for non nested use cases.

    Handles the storage and management of velocity values across
    x-coordinate, y-coordinate, and angular direction.

    :ivar x: 1D array containing the velocity components along the x-axis.
    :type x: numpy.ndarray
    :ivar y: 1D array containing the velocity components along the y-axis.
    :type y: numpy.ndarray
    :ivar ang: 1D array containing the angular velocity components.
    :type ang: numpy.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    ang: np.ndarray
