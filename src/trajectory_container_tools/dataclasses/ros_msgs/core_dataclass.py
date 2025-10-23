# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional, Union

from deprecated import deprecated

from .core_dataclass_utils import get_timestamps_slice
from ..core.base_trajectory_dataclass import (
    BaseTrajectoryFeatureArray,
    BaseTrajectoryFeature,
    NestedBaseTrajectory,
)
from .std_msgs_dataclass import StdMsgsHeader
import numpy as np

from ...temporal import Timestamps


@dataclass()
class RosFeature(BaseTrajectoryFeature):
    """
    Represents a ROS (Robot Operating System) feature that extends the base trajectory
    feature functionality.

    This class is primarily designed to serve as a data container or behavior extension
    for managing traits related to trajectories in a ROS environment or similar use cases.
    It inherits from `BaseTrajectoryFeature`, which provides common features for trajectory
    representations.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    :ivar bag_recorded_timestamps: Time-related information, either a Timestamps object or a numpy
                                    array (converted to Timestamps internally at instanciation).
    :type bag_recorded_timestamps: Timestamps | numpy ndarray
    """

    bag_recorded_timestamps: Union[Timestamps, np.ndarray] = field(
        default=None, kw_only=True
    )

    def on_begin_post_init_callback(self) -> None:
        if self.bag_recorded_timestamps is not None:
            if isinstance(self.bag_recorded_timestamps, np.ndarray):
                self.bag_recorded_timestamps = Timestamps(self.bag_recorded_timestamps)

            self.bag_recorded_timestamps.causal_ordering_sanity_check(
                show_offending_in_nanoseconds=True
            )

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
        resolve_out_of_bounds=True,
    ) -> "RosFeature":
        """
        Retrieve a trajectory interval within a specified timestamps range.

        Note: This method used the bag topic recording stamps, not the topic publishing stamps since its a non-stamped topic.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the
        inclusion of the range startpoint and endpoint.

        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the
            nearest 'bag_recorded_timestamps' bound. (False) Raise TimestampOutOfBoundError on bound violation.
        :return: A data slice corresponding to the timestamps within the specified range.
        :raises TimestampOutOfBoundError: if start or stop is outside 'bag_recorded_timestamps' and their corresponing
            startpoint/endpoint parameter is set to 'False' and 'resolve_out_of_bounds' is set to 'False'.
        """
        if self.bag_recorded_timestamps is not None:
            use_timestamps = self.bag_recorded_timestamps
        else:
            use_timestamps = self.get_container_root(
                include_feature_bag=False
            ).bag_recorded_timestamps

        if use_timestamps is None:
            return self

        timestamps_slice = get_timestamps_slice(
            use_timestamps,
            start,
            stop,
            startpoint,
            endpoint,
            resolve_out_of_bounds,
        )
        return self[timestamps_slice]


@dataclass()
class RosStampedFeature(RosFeature):
    """
    Represents a ROS-stamped dataclass containing trajectory information.

    Compatible ros2 message interface: any interface containing std_msgs/msg/Header

    This dataclass is used to store trajectory data alongside its ROS message
    header. The header contains information such as timestamp and frame of
    reference, which are critical for synchronizing data within ROS-based
    systems. This class inherits from `BaseTrajectoryFeature` to provide
    trajectory-specific attributes and behaviors.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    :ivar bag_recorded_timestamps: Time-related information, either a Timestamps object or a numpy
                                    array (converted to Timestamps internally at instanciation).
    :type bag_recorded_timestamps: Timestamps | numpy ndarray
    :ivar header: The ROS message header, which includes timestamp and frame of
        reference information.
    :type header: StdMsgsHeader
    """

    header: StdMsgsHeader

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
        resolve_out_of_bounds=True,
        use_msg_publishing_timestamps: bool = True,
    ) -> "RosStampedFeature":
        """
        Retrieve a trajectory interval within a specified timestamps range.
        Use message publishing stamps by default or optionaly the rosbag message recording stamps.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the
        inclusion of the range startpoint and endpoint.

        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the
            nearest header.timestamps bound. (False) Raise TimestampOutOfBoundError on bound violation.
        :param use_msg_publishing_timestamps: Use the ros message publishing timestamps (True) or the rosbag message recording timestamps (False).
        :return: A data slice corresponding to the timestamps within the specified range.
        :raises TimestampOutOfBoundError: if start or stop is outside 'header.timestamps' and their corresponing
            startpoint/endpoint parameter is set to False and resolve_out_of_bounds is set to False.
        """
        use_timestamps = self.header.timestamps
        if not use_msg_publishing_timestamps:
            if self.bag_recorded_timestamps is not None:
                use_timestamps = self.bag_recorded_timestamps
            else:
                use_timestamps = self.get_container_root(
                    include_feature_bag=False
                ).bag_recorded_timestamps

        timestamps_slice = get_timestamps_slice(
            use_timestamps,
            start,
            stop,
            startpoint,
            endpoint,
            resolve_out_of_bounds,
        )
        return self[timestamps_slice]


@dataclass()
class RosFeatureArray(BaseTrajectoryFeatureArray):
    """
    Represents a ROS dataclass containing trajectory information.

    Note: This method used the bag topic recording stamps, not the topic publishing stamps since its a non-stamped topic.

    This dataclass is used to store trajectory data. This class inherits from
    `BaseTrajectoryFeature` to provide trajectory-specific attributes and behaviors.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    :ivar bag_recorded_timestamps: Time-related information, either a Timestamps object or a numpy
                                    array (converted to Timestamps internally at instanciation).
    :type bag_recorded_timestamps: Timestamps | numpy ndarray
    """

    pass

    # (CRITICAL) inprogress: extend test case for bag_recorded_timestamps (ref task TCT-87)
    # (CRITICAL) inprogress: add test case for get_timestamps (ref task TCT-87)
    bag_recorded_timestamps: Union[Timestamps, np.ndarray] = field(
        default=None, kw_only=True
    )

    def on_begin_post_init_callback(self) -> None:
        if isinstance(self.bag_recorded_timestamps, np.ndarray):
            self.bag_recorded_timestamps = Timestamps(self.bag_recorded_timestamps)

        self.bag_recorded_timestamps.causal_ordering_sanity_check(
            show_offending_in_nanoseconds=True
        )

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
        resolve_out_of_bounds=True,
    ) -> Union[RosStampedFeature, RosFeature, None]:
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
        :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the
            nearest 'bag_recorded_timestamps' bound. (False) Raise TimestampOutOfBoundError on bound violation.
        :return: A data slice corresponding to the timestamps within the specified range.
        :raises TimestampOutOfBoundError: if start or stop is outside 'bag_recorded_timestamps' and their corresponing
            startpoint/endpoint parameter is set to 'False' and 'resolve_out_of_bounds' is set to 'False'.
        """
        raise NotImplementedError(
            "(Priority) ToDo: implement 'get_timestamps' support for trj feature array (ref task TCT-87)"
        )
        if self.bag_recorded_timestamps is not None:
            use_timestamps = self.bag_recorded_timestamps
        else:
            use_timestamps = self.get_container_root(include_feature_bag=False).bag_recorded_timestamps

        timestamps_slice = get_timestamps_slice(
            self.bag_recorded_timestamps,
            start,
            stop,
            startpoint,
            endpoint,
            resolve_out_of_bounds,
        )
        return self[timestamps_slice]


@deprecated(
    reason="NestedRosStampedFeature dataclass is deprecated now that all TrajectoryFeature dataclass "
    "support parent container reference tracking. Use `is_nested()` method to test if a "
    "trajectory dataclass is nested or not."
)
@dataclass()
class NestedRosStampedFeature(NestedBaseTrajectory):
    """
    Represents a ROS-stamped dataclass containing trajectory information (nested version).

    Compatible ros2 message interface: any interface containing std_msgs/msg/Header

    :ivar header: The ROS message header, which includes timestamp and frame of
        reference information.
    :type header: StdMsgsHeader
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    header: StdMsgsHeader

    def get_timestamps(
        self,
        start: int,
        stop: Optional[int] = None,
        startpoint: bool = True,
        endpoint: bool = False,
        resolve_out_of_bounds=True,
    ):
        """
        Retrieve a trajectory interval within a specified timestamps range.

        This function allows extracting trajectory associated data from a given timestamps range
        defined by the start, stop, and optional parameters controlling the
        inclusion of the range startpoint and endpoint.

        :param resolve_out_of_bounds:
        :param start: The starting timestamp value of the slice.
        :param stop: The optional stopping timestamp value of the slice. If not specified,
            the slice will retrive a trajectory of length 1.
        :param startpoint: A boolean indicating whether to include the starting point in the slice.
        :param endpoint: A boolean indicating whether to include the stopping point in the slice.
        :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the
            nearest header.timestamps bound. (False) Raise TimestampOutOfBoundError on bound violation.
        :return: A data slice corresponding to the timestamps within the specified range.
        :raises TimestampOutOfBoundError: if start or stop is outside header.timestamps and their corresponing
            startpoint/endpoint parameter is set to False and resolve_out_of_bounds is set to False.
        """
        timestamps_slice = get_timestamps_slice(
            self.header.timestamps,
            start,
            stop,
            startpoint,
            endpoint,
            resolve_out_of_bounds,
        )
        return self[timestamps_slice]
