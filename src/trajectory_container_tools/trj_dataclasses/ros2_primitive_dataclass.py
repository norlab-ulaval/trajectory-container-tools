# coding=utf-8
from dataclasses import dataclass
from typing import Union

import numpy as np

from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import \
    NestedBaseTrajectoryDataclass
from trajectory_container_tools.utils.temporal_tools.timestamps import Timestamps


@dataclass()
class Header(NestedBaseTrajectoryDataclass):
    """ Represents a ros header containing frame information and time-related data.

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
class Point(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Point
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass()
class Vector3(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Vector3
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray


@dataclass()
class Vector3Stamped(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Vector3Stamped
    header: Header
    vector: Vector3


@dataclass()
class PointStamped(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/PointStamped
    header: Header
    point: Point


@dataclass()
class Quaternion(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Quaternion
    x: np.ndarray
    y: np.ndarray
    z: np.ndarray
    w: np.ndarray


@dataclass()
class Transform(NestedBaseTrajectoryDataclass):
    # Compatible ros2 message interface: geometry_msgs/msg/Transform
    translation: Vector3
    rotation: Quaternion
