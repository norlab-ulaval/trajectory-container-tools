# coding=utf-8
from pathlib import Path
from io import TextIOWrapper
from typing import Optional

from rosbags.typesys.store import Typestore

import trajectory_container_tools as tct

from .general_utils import gather_rosbag_trajectory_window_informations


def crawl_rosbag_window(
    bag_path_abs: Path,
    log_file: TextIOWrapper,
    features_config: dict,
    typestore: Optional[Typestore] = None,
    start: int = None,
    stop: int = None,
) -> tct.typing.MultifeatureTrajectoryDataclass:
    """
    Crawls a ROS bag within a specified window to gather trajectory information
    and perform feature extraction.

    :param bag_path_abs: Absolute path to the ROS bag file.
    :param log_file: File stream for logging the process output.
    :param features_config: Configuration dictionary for features extraction.
    :param typestore: Optional typestore for dynamic topic handling.
    :param start: Start timestamp (in nanoseconds) for the window.
    :param stop: Stop timestamp (in nanoseconds) for the window.
    :return: Multifeature trajectory dataclass encompassing the extracted data.
    """
    # Sanitize input e.g., 1e9 -> float
    start = int(start)
    stop = int(stop)

    window_info = gather_rosbag_trajectory_window_informations(
        bag_path_abs, features_config, start, stop
    )

    print(window_info, file=log_file)

    MSG = "Begin extracting trajectory window from message stream"
    print(f"\n...{MSG:.<80}\n", file=log_file)

    mf_container = tct.extractor.from_rosbag(rosbag_path=bag_path_abs, dataset_info=None,
                                             features_config=features_config, start=start,
                                             stop=stop, typestore=typestore)

    print(mf_container, file=log_file)

    MSG = "Topic trajectory window timestamps logs"
    window_info_final = f"\n===={MSG:=<80}\n"
    for each_topic_name in mf_container.topic_key_list:
        each_topic: tct.dataclasses.RosStampedDataclass = (
            mf_container.get_dynamic_field(each_topic_name)
        )
        window_info_final += f"\nTopic log: {each_topic.feature_name}\n"

        if "header" in each_topic.get_dimension_names():
            timestamps_ = each_topic.header.timestamps
            delta_stamps = timestamps_.delta_stamps[1:]
            if len(timestamps_) > 0:
                window_info_final += (
                    f"  trajectory len: {len(timestamps_)}\n"
                    f"  timestamp delta:\n"
                    f"       max: {delta_stamps.max()}\n"
                    f"      mean: {delta_stamps.mean():.2f}\n"
                    f"       min: {delta_stamps.min()}\n"
                    f"    values:\n    {delta_stamps}\n"
                )
    print(window_info_final, file=log_file)

    MSG = "Finish reading rosbag trajectory window"
    print(f"\n===={MSG:=<80}\n", file=log_file)

    return mf_container
