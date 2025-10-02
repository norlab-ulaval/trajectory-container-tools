# coding=utf-8
from typing import Optional, Tuple, Union
import os
from pathlib import Path
import numpy as np

from rosbags.rosbag2 import Reader
from rosbags.typesys.store import Typestore

import trajectory_container_tools as tct


def rosbag_log_file_name(
    bag_path_abs: Path, file_postfix: Optional[Union[str, int]] = None
) -> str:
    if file_postfix is not None:
        return (
            f"{os.path.basename(bag_path_abs)}-{file_postfix}.log"
        )
    else:
        return f"{os.path.basename(bag_path_abs)}.log"


def collect_bag_lvl_timestamps(
    bag_path_abs: Path,
    features_config: dict,
    mf_container: tct.typing.MultifeatureTrajectoryDataclass,
    start: Optional[int],
    stop: Optional[int],
) -> tct.typing.MultifeatureTrajectoryDataclass:
    # (Priority) ToDo: RLRP-449 refactor: move bag lvl timestamps collecting to TCT mf dataclass
    with Reader(bag_path_abs) as reader:
        bag_timestamps = []
        for connection, timestamp, _ in reader.messages(start=start, stop=stop):
            if connection.topic in features_config:
                bag_timestamps.append(timestamp)

        if len(bag_timestamps) > 0:
            mf_container.set_dynamic_field(
                "bag_timestamps", tct.temporal.Timestamps(np.array(bag_timestamps))
            )
    return mf_container


def gather_rosbag_informations(bag_path_abs: Path) -> Tuple[int, int, int, str]:
    """
    Fetch timestamp related information from a rosbag

    :param bag_path_abs: The rosbag absolute path
    :return: Ros bag start time, end time, duration and the rosbag information string
    """
    bag_start_time = None
    bag_end_time = None
    bag_duration = None
    info_str = ""
    with Reader(bag_path_abs) as reader:
        bag_start_time = reader.start_time
        bag_end_time = reader.end_time
        bag_duration = reader.duration

        MSG = "Rosbag information"
        info_str += f"\n===={MSG:=<80}\n"
        info_str += f"Bag name: {os.path.basename(bag_path_abs)}\n"

        MSG = "Bag time (nanosecond)"
        info_str += f"\n...{MSG:.<80}\n"
        info_str += (
            f"    start_time: {bag_start_time}\n"
            f"      end_time: {bag_end_time}\n"
            f"      duration: {bag_duration}\n"
        )

        MSG = "Topic and message"
        info_str += f"\n...{MSG:.<80}\n\n"
        info_str += f"{'MSGCOUNT':>8}  {'TOPIC':<25} {'MSGTYPE'} \n"
        for connection in reader.connections:
            info_str += f"{connection.msgcount:>8}  {connection.topic:<25} {connection.msgtype} \n"

        info_str += f"\n===={'='*80}\n"

    print(info_str)
    return bag_start_time, bag_end_time, bag_duration, info_str


def gather_rosbag_trajectory_window_informations(
    bag_path_abs: Path, features_config: dict, start: Optional[int], stop: Optional[int]
) -> str:
    with Reader(bag_path_abs) as reader:

        # .... Gather topics trajectory window information ........................................
        selected_topic_info = {}
        for connection in reader.connections:
            if connection.topic in features_config:
                selected_topic_info.setdefault(
                    str(connection.topic), {"count": 0, "type": connection.msgtype}
                )

        for connection, timestamp, _ in reader.messages(start=start, stop=stop):
            if connection.topic in features_config:
                selected_topic_info[str(connection.topic)]["count"] += 1

        selected_topic_info_str = ""
        selected_topic_info_str += f"{'MSGCOUNT':>8}  {'TOPIC':<25} {'MSGTYPE'} \n"
        for k, v in selected_topic_info.items():
            selected_topic_info_str += f"{v['count']:>8}  {k:<25} {v['type']} \n"

        # .... Gather window related information ..................................................
        bag_start_time = reader.start_time
        bag_end_time = reader.end_time
        bag_duration = reader.duration

        MSG = f"Crawler trajectory window configuration"
        _str = f"\n...{MSG:.<80}\n"
        _str += (
            f"\nCrawl bag (nanosecond):\n        start: {start or bag_start_time} ns\n      "
            f"   stop: {stop or bag_end_time} ns\n"
        )
        if stop is not None and start is not None:
            _str += f"       window: {stop - start} ns\n"

        if start is not None:
            _str += f"\nCrawl bag (second):\n        start: {tct.temporal.to_seconds(start)} s\n"

        if stop is not None:
            _str += f"         stop: {tct.temporal.to_seconds(stop)} s\n"
        if stop is not None and start is not None:
            _str += f"       window: {tct.temporal.to_seconds(stop - start)} s\n"

        MSG = "Selected topics"
        _str += f"\n...{MSG:.<80}\n\n"
        _str += selected_topic_info_str + "\n"

        print(_str)
    return _str


def compute_window_start_and_stop(
    bag_end_time: int,
    bag_start_time_: int,
    each_idx: int,
    fast_forward_ns: Optional[int],
    window_ns: Optional[int],
) -> tuple[int, int]:
    """
    Compute the start and stop times of a rosbag trajectory window based on the provided parameters.

    This function calculates the start and stop times considering the fast-forward and
    the window duration values, ensuring that the returned values are sanitized as integers.

    :param bag_end_time: The end time of the bag recording.
    :param bag_start_time_: The start time of the bag recording.
    :param each_idx: The current step/index value.
    :param fast_forward_ns: Optional fast-forward duration in nanoseconds, used for
        adjusting the starting time.
    :param window_ns: Optional window duration in nanoseconds, used for determining
        the stop time.
    :return: A tuple containing the computed start and stop times as integers.
    """
    if fast_forward_ns is None:
        start = bag_start_time_
    else:
        start = bag_start_time_ + fast_forward_ns * each_idx

    if window_ns is None:
        stop = bag_end_time
    else:
        stop = start + window_ns

    # Sanitize output e.g., 1e9 -> float
    start = int(start)
    stop = int(stop)
    return start, stop


def compute_bag_target_window_nb(
    bag_duration_: int, fast_forward_ns: Optional[Union[int, float]]
) -> int:
    """Compute the number of iterations to span the bag target window based on the provided bag
    duration and fast-forward duration.

    :param bag_duration_: The total duration of the bag in nanoseconds.
    :param fast_forward_ns: The duration to fast-forward in nanoseconds. If None, the fast-forward step is considered as the full bag duration.
    :return: The number of iterations required to cover the target window.
    """

    if fast_forward_ns is None:
        num_iterations = 1
    else:
        # Sanitize input e.g., 1e9 -> float
        fast_forward_ns = int(fast_forward_ns)
        num_iterations = bag_duration_ // fast_forward_ns
    return num_iterations


def find_max_timestamp_delta_over_all_topics(
    bag_path_abs: Path, features_config: dict, typestore: Typestore
) -> int:
    """
    Finds the maximum timestamp delta across all topics in a ROS bag file.

    This function extracts topic's data from a given ROS bag file. It computes and returns the largest delta
    between consecutive timestamps for all topics specified in the feature configuration dictionary.

    Note: AbstractTrajectoryDataclass subclasses are evaluated

    :param bag_path_abs: Path to the ROS bag file.
    :param features_config: Dictionary containing configuration for extracting features.
    :param typestore: Typestore object for managing type-related information.
    :return: The maximum timestamp delta across all qualifying topics.
    """
    mf_container = tct.extractor.from_rosbag(
        rosbag_path=bag_path_abs,
        dataset_info=None,
        features_config=features_config,
        typestore=typestore,
    )

    topics_max_delta_stamp = []
    for each in mf_container.topic_key_list:
        if issubclass(
            mf_container.get_dimension_type(each)[0],
            tct.AbstractTrajectoryDataclass,
        ):
            topics_max_delta_stamp.append(
                np.max(
                    mf_container.get_dynamic_field(each).header.timestamps.delta_stamps
                )
            )
    return np.max(np.array(topics_max_delta_stamp))
