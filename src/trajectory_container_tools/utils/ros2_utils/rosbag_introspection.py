# coding=utf-8
import os
from pathlib import Path
from typing import Optional, Tuple

from rosbags.rosbag2 import Reader

import trajectory_container_tools.temporal
from trajectory_container_tools.temporal.trajectory_timestamps_metadata import (
    TrajectoryTimestampsMetadata,
)
from trajectory_container_tools.utils import dn_sanitize_path, setup_progressbar


def gather_rosbag_informations(
    bag_path_abs: str | Path,
) -> Tuple[str, TrajectoryTimestampsMetadata]:
    """This function reads a rosbag file to extract trajectory timestamps metadata information in
    addition to detailing all topics, message types, and message counts.

    :param bag_path_abs: The absolute file path of the ROS bag to read.
    :return: A formatted string summarizing the bag's information and a
        TrajectoryTimestampsMetadata object.
    """
    assert os.path.exists(bag_path_abs)

    info_str = ""
    with Reader(bag_path_abs) as reader:
        bag_time_metadata = TrajectoryTimestampsMetadata(
            start_time=reader.start_time,
            end_time=reader.end_time,
            duration=reader.duration,
        )

        MSG = "Rosbag information"
        info_str += f"\n===={MSG:=<80}\n"
        # MSG = f"Bag"
        # info_str += f"\n....{MSG:.<80}\n"
        info_str += f"Name: {os.path.basename(bag_path_abs)}\n"
        info_str += f"Path: {os.path.dirname(bag_path_abs)}\n"

        MSG = "Bag time (nanosecond)"
        info_str += f"\n....{MSG:.<80}\n"
        info_str += (
            f"      Start: {bag_time_metadata.start_time} (ns)\n"
            f"        End: {bag_time_metadata.end_time} (ns)\n"
            f"   Duration: {bag_time_metadata.duration} (ns)\n"
        )

        MSG = "Topic and message"
        info_str += f"\n....{MSG:.<80}\n"
        info_str += f"Total count: {reader.message_count}\n\n"
        info_str += f"{'MSGCOUNT':>8}  {'TOPIC':<35} {'MSGTYPE'} \n"
        for connection in reader.connections:
            info_str += f"{connection.msgcount:>8}  {connection.topic:<35} {connection.msgtype} \n"

        info_str += f"\n===={'='*80}\n"

    return info_str, bag_time_metadata


def gather_rosbag_trajectory_window_informations(
    bag_path_abs: Path, features_config: dict, start: Optional[int], stop: Optional[int]
) -> str:
    """Analyzes a ROS bag file to extract and summarize trajectory windows and specific topic information.

    This function inspects a ROS bag file, extracts information about messages within a specific time
    window (if specified), and gathers metadata about selected topics of interest. It formats and
    returns a detailed summary of the results.

    :param bag_path_abs: The absolute path to the ROS bag file being analyzed.
    :param features_config: A dictionary mapping topic names to configurations for selected topics.
    :param start: The start timestamp for the time window in nanoseconds. If None, the bag's start time is used.
    :param stop: The stop timestamp for the time window in nanoseconds. If None, the bag's end time is used.
    :return: A formatted string summarizing the trajectory window configuration and selected topic information.
    """
    print(
        f"[TCT] Gather rosbag trajectory window informations for selected topic from start={start} to stop={stop})"
    )

    with Reader(bag_path_abs) as reader:
        # .... Gather window related information ..................................................
        bag_start_time = reader.start_time
        bag_end_time = reader.end_time
        bag_duration = reader.duration

        MSG = f"Crawler trajectory window configuration"
        info_str_main = f"\n...{MSG:.<80}\n"
        info_str_main += (
            f"\nCrawl bag (nanosecond):\n        start: {start or bag_start_time} ns\n      "
            f"   stop: {stop or bag_end_time} ns\n"
        )
        if stop is not None and start is not None:
            info_str_main += f"       window: {stop - start} ns\n"

        if start is not None:
            info_str_main += f"\nCrawl bag (second):\n        start: {trajectory_container_tools.temporal.timestamps.to_seconds(start)} s\n"

        if stop is not None:
            info_str_main += f"         stop: {trajectory_container_tools.temporal.timestamps.to_seconds(stop)} s\n"
        if stop is not None and start is not None:
            info_str_main += f"       window: {trajectory_container_tools.temporal.timestamps.to_seconds(stop - start)} s\n"

        # .... Gather topics trajectory window information ........................................
        progressbar_topic = setup_progressbar(len(reader.connections))
        selected_topic_info = {}
        for connection in reader.connections:
            if connection.topic in features_config:
                selected_topic_info.setdefault(
                    str(connection.topic), {"count": 0, "type": connection.msgtype}
                )

                counter = 0
                for window_connection, _, _ in reader.messages(
                    (connection,), start=start, stop=stop
                ):
                    counter += 1

                selected_topic_info[str(connection.topic)]["count"] = counter

            progressbar_topic.update(1)
        progressbar_topic.close()

        info_str_selected_topic = ""
        info_str_selected_topic += f"{'MSGCOUNT':>8}  {'TOPIC':<35} {'MSGTYPE'} \n"
        for k, v in selected_topic_info.items():
            info_str_selected_topic += f"{v['count']:>8}  {k:<35} {v['type']} \n"

        MSG = "Selected topics"
        info_str_main += f"\n...{MSG:.<80}\n\n"
        info_str_main += info_str_selected_topic + "\n"

    return info_str_main


def show_rosbag_summary_info(rosbag_path: str | Path) -> Path:
    """Display available topics and messages in a specified ROS bag file.

    This function reads a ROS bag file from the specified path and lists all the available
    topics along with their message types. Additionally, it provides the total number of
    messages in the ROS bag. If the provided path is unreachable and the function is running in a
    Dockerized-NorLab docker container, it attempts to resolve the correct path.

    :param rosbag_path: Path to the ROS bag file (absolute or relative).
    :return: the real ros bag path if the input was a relative path
    """
    rosbag_path = dn_sanitize_path(rosbag_path)

    info_str, bag_time_metadata = gather_rosbag_informations(rosbag_path)
    print(info_str)

    return rosbag_path
