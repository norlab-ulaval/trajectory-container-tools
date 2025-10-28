# coding=utf-8
from typing import Optional, Union
import os
from pathlib import Path
import numpy as np

import trajectory_container_tools as tct
from trajectory_container_tools.dataclasses import (
    RosFeature,
    RosFeatureArray,
    RosStampedFeature,
)
from trajectory_container_tools.utils.typing.new_types_and_aliases import TrajectoryFeaturesBag
from trajectory_container_tools.utils.general import RosImportError

try:
    from rosbags.rosbag2 import Reader
    from rosbags.typesys.store import Typestore
except (ImportError, ModuleNotFoundError):
    raise RosImportError


def rosbag_log_file_name(
    bag_path_abs: Path, file_postfix: Optional[Union[str, int]] = None
) -> str:
    """Generates a log file name for a given ROS bag path with an optional file postfix.

    :param bag_path_abs: The absolute path of the ROS bag file.
    :param file_postfix: An optional postfix value (string or integer) to include in the
        generated log file name.
    :return: A string representing the generated log file name.
    """
    if file_postfix is not None:
        return f"{os.path.basename(bag_path_abs)}-{file_postfix}.log"
    else:
        return f"{os.path.basename(bag_path_abs)}.log"


def compute_window_start_and_stop(
    trajectory_start_time: int,
    trajectory_end_time: int,
    each_idx: int,
    fast_forward_ns: Optional[int],
    window_ns: Optional[int],
) -> tuple[int, int]:
    """
    Compute the start and stop times of a rosbag trajectory window based on the provided parameters.

    This function calculates the start and stop times considering the fast-forward and
    the window duration values, ensuring that the returned values are sanitized as integers.

    :param trajectory_start_time: The start time of the bag recording.
    :param trajectory_end_time: The end time of the bag recording.
    :param each_idx: The current step/index value.
    :param fast_forward_ns: Optional fast-forward duration in nanoseconds, used for
        adjusting the starting time.
    :param window_ns: Optional window duration in nanoseconds, used for determining
        the stop time.
    :return: A tuple containing the computed start and stop times as integers.
    """
    if fast_forward_ns is None:
        start = trajectory_start_time
    else:
        start = trajectory_start_time + fast_forward_ns * each_idx

    if window_ns is None:
        stop = trajectory_end_time
    else:
        stop = start + window_ns

    # Sanitize output e.g., 1e9 -> float
    start = int(start)
    stop = int(stop)
    return start, stop


def compute_bag_target_window_nb(
    bag_duration: int, fast_forward_ns: Optional[Union[int, float]]
) -> int:
    """Compute the number of iterations to span the bag target window based on the provided bag
    duration and fast-forward duration.

    :param bag_duration: The total duration of the bag in nanoseconds.
    :param fast_forward_ns: The duration to fast-forward in nanoseconds. If None, the fast-forward step is considered as the full bag duration.
    :return: The number of iterations required to cover the target window.
    """

    if fast_forward_ns is None:
        num_iterations = 1
    else:
        # Sanitize input e.g., 1e9 -> float
        fast_forward_ns = int(fast_forward_ns)
        num_iterations = bag_duration // fast_forward_ns
    return num_iterations


def find_max_timestamp_delta_over_all_topics(feature_bag_trajectory_container: TrajectoryFeaturesBag) -> int:
    """
    Finds the maximum timestamp delta across all topics in a ROS bag file.

    This function extracts topic's data from a given ROS bag file. It computes and returns the largest delta
    between consecutive timestamps for all topics specified in the feature configuration dictionary.

    Note: AbstractTrajectoryFeature subclasses are evaluated

    :param feature_bag_trajectory_container: A trajectory stamped features bag
    :return: The maximum timestamp delta across all qualifying topics.
    """

    topics_max_delta_stamp = []
    for each in feature_bag_trajectory_container.topic_key_list:
        if issubclass(
            feature_bag_trajectory_container.get_cls_public_field_type(each)[0],
            tct.AbstractTrajectoryFeature,
        ):
            each_field: Union[RosFeature, RosStampedFeature, RosFeatureArray] = (
                feature_bag_trajectory_container.get_dynamic_attribute(each)
            )
            if isinstance(each_field, tct.dataclasses.StdMsgsHeader):
                delta_stamps = each_field.header.timestamps.delta_stamps
            else:
                delta_stamps = each_field.bag_recorded_timestamps.delta_stamps

            topics_max_delta_stamp.append(np.max(delta_stamps))
    return np.max(np.array(topics_max_delta_stamp))
