# coding=utf-8

"""
Usage:

    1. execute example: $ python src/trajectory_container_tools/utils/ros2_utils/rosbag_eda/rosbag_timestamp_eda.py
    2. analyze the plots and logs at "artifact/rosbag_eda/<EXPERIMENT_NAME>/"

"""

from typing import Optional, Tuple, Union
import os
from pathlib import Path

import trajectory_container_tools as tct
from trajectory_container_tools.utils.general import dn_sanitize_path, setup_progressbar
from trajectory_container_tools.temporal.timestamps import to_seconds
from trajectory_container_tools.utils.ros2_utils.ros2_non_native_msg import (
    register_non_native_msgs,
)
from trajectory_container_tools.dataclasses.core import (
    AbstractTrajectoryStampedFeaturesBag,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.general_utils import (
    compute_bag_target_window_nb,
    compute_window_start_and_stop,
    find_max_timestamp_delta_over_all_topics,
    rosbag_log_file_name,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_introspection import (
    gather_rosbag_informations,
    gather_rosbag_trajectory_window_informations,
)
from trajectory_container_tools.utils.ros2_utils.rosbag_eda.eda_utils.plot import (
    plot_bag_timestamp_delta,
)
from trajectory_container_tools.utils.general import RosImportError

try:
    from rosbags.typesys.store import Typestore
except (ImportError, ModuleNotFoundError):
    raise RosImportError


def run_rosbag_timestamp_eda(
    bag_path: Union[str, Path],
    eda_dir_path: Union[str, Path],
    features_config: dict,
    chunk_on: str,
    fast_forward_ns: Optional[Union[int, float]] = 0.1e9,
    window_ns: Optional[Union[int, float]] = 0.5e9,
    show_stamps_type="both",
    plot_ylim: Optional[float] = None,
    experiment_dir: Optional[str] = None,
    show_plot=True,
    save_plot=True,
    figsize: Tuple[int, int] = (28, 10),
    save_dpi: int = 100,
    typestore: Optional[Typestore] = None,
    window_start: Optional[int] = None,
    window_stop: Optional[int] = None,
) -> AbstractTrajectoryStampedFeaturesBag:
    """
    Executes timestamp-based Exploratory Data Analysis (EDA) on a ROSbag file by analyzing
    specific time window chunks, generating logs, and plotting timestamp data.

    :param bag_path: Path to the ROSbag file to be analyzed.
    :param eda_dir_path: Directory where EDA artifacts and logs will be saved.
    :param features_config: Configuration dictionary containing feature extraction settings.
    :param chunk_on: Topic in the ROSbag to monitor for chunk split e.g., '/teleop'.
    :param fast_forward_ns: Time in nanoseconds to fast-forward for each data chunk.
        Defaults to 0.1e9 nanoseconds (1/10 of a second).
    :param window_ns: Duration of the time window in nanoseconds for analyzing data chunks.
        Defaults to 0.5e9 nanoseconds (half a second).
    :param show_stamps_type: either 'published', 'recorded' or 'both' (default).
    :param plot_ylim: Optional vertical limits for the plots. Defaults to None.
    :param experiment_dir: Directory to group all outputs for the analysis. If None, the
        bag name will be used. Defaults to None.
    :param show_plot: Determines whether the plot should be displayed interactively.
    :param save_plot: Determines whether the plot should be saved to disk.
    :param figsize: The target figure size. Default to (28, 10)
    :param save_dpi: Dpi of the saved figures. Default to matplotlib default i.e., dpi=100
    :param typestore: Optional. The typestore instance to register the non-native
        messages. If not provided, a default typestore will be initialized.
    :param window_start: The start timestamp for the time window in nanoseconds. If None, the bag's start time is used.
    :param window_stop: The stop timestamp for the time window in nanoseconds. If None, the bag's end time is used.
    :return: None
    """
    # .... Setup path .............................................................................
    if experiment_dir is None:
        bag_name = os.path.basename(bag_path)
        experiment_dir = bag_name

    experiment_dir_path = Path(os.path.join(eda_dir_path, experiment_dir))
    log_file_path = Path(
        os.path.join(experiment_dir_path, rosbag_log_file_name(bag_path))
    )
    os.makedirs(experiment_dir_path, exist_ok=True)

    print(
        (
            f"\nBegin rosbag timestamp eda:\n\n"
            f"   bag path: {bag_path}\n\n"
            f"   crawler artifact path: {experiment_dir_path}\n"
        )
    )

    # .... Setup general ..........................................................................

    # Sanitize input e.g., 1e9 -> float
    if fast_forward_ns is not None:
        fast_forward_ns = int(fast_forward_ns)
    if window_ns is not None:
        window_ns = int(window_ns)

    typestore = register_non_native_msgs(typestore)

    rosbag_info_str, bag_timestamps_meta = gather_rosbag_informations(bag_path)
    print(rosbag_info_str)

    if window_start is None:
        window_start = bag_timestamps_meta.start_time

    if window_stop is None:
        window_stop = bag_timestamps_meta.end_time

    window_info = gather_rosbag_trajectory_window_informations(
        bag_path,
        features_config,
        window_start,
        window_stop,
    )
    print("\n", window_info)

    mf_container = tct.extractor.from_rosbag(
        rosbag_path=bag_path,
        dataset_info=None,
        features_config=features_config,
        chunk_on=chunk_on,
        start=window_start,
        stop=window_stop,
        typestore=typestore,
    )

    print(mf_container)

    # .... Collect rosbag information .............................................................
    with open(log_file_path, "w") as log_file:

        print(rosbag_info_str, file=log_file)

        print("\n", window_info, file=log_file)

        MSG = "Multi-feature trajectory container"
        print(f"\n...{MSG:.<80}\n", file=log_file)

        print(mf_container, file=log_file)

        MSG = "Topic trajectory window timestamps logs"
        window_info_final = f"\n===={MSG:=<80}\n"

        for each_topic_name in mf_container.topic_key_list:
            each_topic: tct.dataclasses.RosStampedFeature = (
                mf_container.get_dynamic_attribute(each_topic_name)
            )
            window_info_final += f"\nTopic log: {each_topic.feature_name}\n"

            if "header" in each_topic.get_public_attribute_names():
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

        MSG = "Finish reading rosbag trajectory"
        print(f"\n===={MSG:=<80}\n", file=log_file)

    # .... Setup plot .............................................................................
    if plot_ylim is None:
        print("[TCT] No plot_ylim → find max timestamp delta over all topics.")
        plot_ylim = find_max_timestamp_delta_over_all_topics(mf_container)

    # .... Begin trajectory window crawling .......................................................
    window_duration = (
        # mf_container.get_chunk_on_timestamps().max()
        mf_container.get_trajectory_last_timestamp(include_bag_record=True)
        - mf_container.get_trajectory_first_timestamp(include_bag_record=False)
    )
    num_iterations = compute_bag_target_window_nb(
        window_duration, fast_forward_ns, window_ns
    )

    print(f"\n[TCT] Trajectory window crawling")
    progressbar = setup_progressbar(num_iterations)
    try:
        for each_idx in range(num_iterations):

            idx_window_start, idx_window_stop = compute_window_start_and_stop(
                # mf_container.get_chunk_on_timestamps().min(),
                mf_container.get_trajectory_first_timestamp(include_bag_record=False),
                mf_container.get_trajectory_last_timestamp(include_bag_record=True),
                each_idx,
                fast_forward_ns,
                window_ns,
            )

            mf_container_at_timestamps = mf_container.get_timestamps_interval(
                start=idx_window_start,
                stop=idx_window_stop,
                startpoint=True,
                endpoint=True,
                resolve_out_of_bounds=True,
            )

            plot_bag_timestamp_delta(
                bag_timestamps_meta.start_time,
                mf_container_at_timestamps,
                bag_path,
                experiment_dir_path,
                chunk_on=chunk_on,
                show_stamps_type=show_stamps_type,
                append_to_title=f"plot {each_idx + 1}/{num_iterations}",
                comment=None,
                plot_ylim=plot_ylim,
                plot_postfix=each_idx,
                show_plot=show_plot,
                save_plot=save_plot,
                figsize=figsize,
                save_dpi=save_dpi,
            )
            progressbar.update(1)
    except KeyboardInterrupt:
        pass
    except Exception:
        # Exception scope is large on purpose
        raise
    finally:
        progressbar.close()

    return mf_container


if __name__ == "__main__":
    """
    Rosbag timestamp Exploratory Data Analysis example
    """

    bag_name_ = "rosbag2_2023_09_24-20_30_12-filtered-short"
    bag_path_ = dn_sanitize_path(
        os.path.join(
            "data/repository_data/tests_data/rosbag_test_data",
            "bags_vaul-f1tenth-nx-orin",
            bag_name_,
        )
    )

    artifact_path = "artifact/rosbag_eda"
    dn_project_path = os.getenv("DN_PROJECT_PATH")
    if dn_project_path is not None and os.path.exists(dn_project_path):
        artifact_path = os.path.join(dn_project_path, artifact_path)

    run_rosbag_timestamp_eda(
        bag_path_,
        eda_dir_path=artifact_path,
        features_config={
            "/teleop": tct.dataclasses.AckermannMsgsAckermannDriveStamped,
            "/odom": tct.dataclasses.NavMsgsOdometry,
            "/tf": tct.dataclasses.Tf2MsgsTFMessage,
            "/scan": tct.dataclasses.SensorMsgsLaserScan,
            "/sensors/imu/raw": tct.dataclasses.SensorMsgsImu,
            "/sensors/imu": tct.dataclasses.VescMsgsVescImuStamped,
        },
        chunk_on="/teleop",
        fast_forward_ns=0.1e9,
        window_ns=0.5e9,
        show_stamps_type="both",
        plot_ylim=1.2e8,
        show_plot=True,
    )
