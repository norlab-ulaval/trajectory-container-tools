# coding=utf-8
from dataclasses import dataclass
from typing import Optional

from ..core.base_trajectory_dataclass import (
    BaseNoTrajectoryDataclass,
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
)
from ..ros_msgs.primitive_dataclass import Header
from trajectory_container_tools.temporal.timestamps import Timestamps


def get_timestamps_slice(
    timestamps: Timestamps,
    start: int,
    stop: Optional[int] = None,
    startpoint: bool = True,
    endpoint: bool = False,
) -> slice:
    """
    Extracts a slice of timestamps based on given start, stop, and boundary inclusions.

    This function calculates a slice object to index into a `Timestamps` object
    based on the nearest timestamp to the specified start and optionally,
    the stop time. It can include or exclude the start and stop boundaries
    based on the `startpoint` and `endpoint` flags.

    :param timestamps: Timestamps object to retrieve nearest time indices.
    :param start: The starting timestamp from which to slice.
    :param stop: Optional stopping timestamp up to which to slice.
    :param startpoint: Boolean indicating whether to include the start boundary.
    :param endpoint: Boolean indicating whether to include the stop boundary.
    :return: A slice object representing the calculated index range.
    """
    nearest_stamp = timestamps.get_nearest_stamp(start, future=True, include=True)
    nearest_idx = timestamps.get_indexes(nearest_stamp)

    if stop is None:
        timestamps_slice = slice(
            nearest_idx + int(not startpoint), nearest_idx + int(startpoint)
        )
    else:
        next_nearest_stamp = timestamps.get_nearest_stamp(
            stop, future=True, include=True
        )
        next_nearest_idx = timestamps.get_indexes(next_nearest_stamp)
        timestamps_slice = slice(
            nearest_idx + int(not startpoint), next_nearest_idx + int(endpoint)
        )
    return timestamps_slice


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
    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    header: Header

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
    ):
        """
        Retrieve a trajectory interval within a specified timestamps range.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the
        inclusion of the range startpoint and endpoint.

        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :return: A data slice corresponding to the timestamps within the specified range.
        """
        timestamps_slice = get_timestamps_slice(
            self.header.timestamps, start, stop, startpoint, endpoint
        )
        return self[timestamps_slice]


@dataclass()
class NestedRosStampedDataclass(NestedBaseTrajectoryDataclass):
    """
    Represents a ROS-stamped dataclass containing trajectory information (nested version).

    Compatible ros2 message interface: std_msgs/msg/Header

    :ivar header: The ROS message header, which includes timestamp and frame of
        reference information.
    :type header: Header
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    header: Header

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
    ):
        """
        Retrieve a trajectory interval within a specified timestamps range.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the
        inclusion of the range startpoint and endpoint.

        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :return: A data slice corresponding to the timestamps within the specified range.
        """
        timestamps_slice = get_timestamps_slice(
            self.header.timestamps, start, stop, startpoint, endpoint
        )
        return self[timestamps_slice]


@dataclass()
class RosDataclass(BaseNoTrajectoryDataclass):
    """
    Represents a ROS dataclass containing trajectory information.

    This dataclass is used to store trajectory data. This class inherits from
    `BaseTrajectoryDataclass` to provide trajectory-specific attributes and behaviors.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    """

    pass
