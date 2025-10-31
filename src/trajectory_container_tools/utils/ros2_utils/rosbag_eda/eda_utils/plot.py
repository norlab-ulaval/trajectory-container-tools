# coding=utf-8
import os
import pathlib
from typing import Optional, Tuple, Union

from matplotlib import pyplot as plt

import trajectory_container_tools as tct
from trajectory_container_tools.temporal import Timestamps

from ...ros2_general import convert_rosbag_topic_key_to_tct_mf_topic_key
from .plot_management import plot_manager


def plot_bag_timestamp_delta(
    bag_start_time: int,
    tct_container: tct.dataclasses.AbstractTrajectoryStampedFeaturesBag,
    bag_path_abs: pathlib.Path,
    experiment_dir_path: pathlib.Path,
    chunk_on: Optional[str] = "/teleop",
    show_stamps_type="both",
    append_to_title: Optional[str] = None,
    comment: Optional[str] = None,
    plot_ylim: float = 1e8,
    plot_postfix: Optional[Union[str, int]] = None,
    show_plot: bool = True,
    save_plot=True,
    headless: bool = False,
    figsize: Tuple[int, int] = (28, 10),
    save_dpi: int = 100,
) -> None:
    """
    Generates and saves a plot illustrating the delta between consecutive message
    timestamps from a ROS bag, with options for customization and display.

    :param save_plot:
    :param bag_start_time: The start time of the bag in nanoseconds.
    :param tct_container: Container holding topic information and data.
    :param bag_path_abs: Absolute path to the ROS bag file.
    :param experiment_dir_path: Path to the directory where results are saved.
    :param chunk_on: The topic name on which to add visual markers at timestamps.
    :param show_stamps_type: either 'published', 'recorded' or 'both' (default).
    :param append_to_title: Additional text appended to the plot title.
    :param comment: An optional text comment displayed on the plot.
    :param plot_ylim: Y-axis limit for the plot, if specified.
    :param plot_postfix: Optional string or integer to append to the plot filename to differentiate it.
    :param show_plot: Determines whether the plot should be displayed interactively.
    :param headless: If True, disables interactive plotting and saves the plot using a non-GUI backend.
    :param figsize: The target figure size. Default to (28, 10)
    :param save_dpi: Dpi of the saved figures. Default to matplotlib default i.e., dpi=100
    :return: None
    """
    LINEWIDTH = 1.5
    MARKERSIZE = 6

    _show_recorded_stamps = True
    _show_published_stamps = True
    if show_stamps_type == "recorded":
        _show_published_stamps = False
    elif show_stamps_type == "published":
        _show_recorded_stamps = False

    with plot_manager(show_plot, headless):

        fig = plt.figure(
            num=None, figsize=figsize, dpi=None, facecolor=None, edgecolor=None
        )
        if append_to_title:
            append_to_title = f", {append_to_title}"
        plt.title(
            r"Topic messages timestamps delta"
            + f" (bag: {os.path.basename(bag_path_abs)}{append_to_title})"
        )

        chunk_on = convert_rosbag_topic_key_to_tct_mf_topic_key(chunk_on)

        # .... Show bag timestamps ................................................................
        bag_timestamps = tct_container.get_dynamic_attribute("bag_timestamps")
        if isinstance(bag_timestamps, tct.temporal.Timestamps):
            topic_ts_stamps = bag_timestamps.stamps
            topic_ts_delta = bag_timestamps.delta_stamps
            if topic_ts_delta is not None and len(topic_ts_delta) > 0:
                x_main = topic_ts_stamps - bag_start_time
                x_main_in_second = tct.temporal.timestamps.to_seconds(x_main)

                plt.vlines(
                    x=x_main_in_second,
                    ymin=0,
                    ymax=plot_ylim,
                    # colors="lightgrey",
                    # alpha=0.6,
                    colors="whitesmoke",
                    alpha=1,
                    linewidth=1.2,
                    # colors="gainsboro",
                    # alpha=0.7,
                    # linewidth=0.6,
                    linestyles="-",
                )

        # .... Show first chunk start timestamp reference .........................................
        window_start_stamp = (
            tct_container.get_trajectory_first_timestamp(include_bag_record=True)
            - bag_start_time
        )
        plt.vlines(
            x=tct.temporal.timestamps.to_seconds(window_start_stamp),
            ymin=0,
            ymax=plot_ylim,
            colors="Gray",
            alpha=0.7,
            linewidth=0.5,
        )

        # ... Topics plots ........................................................................
        for each_topic_name in tct_container.topic_key_list:
            each_topic: Union[
                tct.dataclasses.RosFeatureArray, tct.dataclasses.RosStampedFeature
            ] = tct_container.get_dynamic_attribute(each_topic_name)

            if isinstance(
                each_topic,
                (
                    tct.dataclasses.RosFeature,
                    tct.dataclasses.RosStampedFeature,
                    tct.dataclasses.RosFeatureArray,
                ),
            ):

                if each_topic.has_dynamic_attribute("bag_recorded_timestamps"):
                    recorded_timestamps: Timestamps = each_topic.get_dynamic_attribute(
                        "bag_recorded_timestamps"
                    )
                    if recorded_timestamps is not None:
                        topic_record_ts_stamps = recorded_timestamps.stamps
                        topic_record_ts_delta = recorded_timestamps.delta_stamps
                        recorded_rate_metric = recorded_timestamps.compute_frequency_metric()

                if each_topic.has_dynamic_attribute("header.timestamps"):
                    published_timestamps: Timestamps = each_topic.get_dynamic_attribute(
                        "header.timestamps"
                    )
                    topic_ts_stamps = published_timestamps.stamps
                    topic_ts_delta = published_timestamps.delta_stamps
                    use_bag_stamps = False
                elif each_topic.has_dynamic_attribute("bag_recorded_timestamps"):
                    topic_ts_stamps = topic_record_ts_stamps
                    topic_ts_delta = topic_record_ts_delta
                    use_bag_stamps = True
                else:
                    raise AttributeError(
                        f"{each_topic_name} has no timestamps attribute!"
                    )

                if topic_ts_delta is not None:
                    y_main = topic_ts_delta
                    x_main = topic_ts_stamps - bag_start_time
                    y_main_in_second = tct.temporal.timestamps.to_seconds(y_main)
                    x_main_in_second = tct.temporal.timestamps.to_seconds(x_main)

                    y_recorded = topic_record_ts_delta
                    x_recorded = topic_record_ts_stamps - bag_start_time
                    y_recorded_in_second = tct.temporal.timestamps.to_seconds(
                        y_recorded
                    )
                    x_recorded_in_second = tct.temporal.timestamps.to_seconds(
                        x_recorded
                    )

                    if chunk_on in each_topic_name:
                        plt.vlines(
                            x=x_main_in_second,
                            ymin=0,
                            ymax=plot_ylim,
                            colors="Gray",
                            alpha=0.7,
                            linewidth=0.5,
                        )

                    if (
                        "ackermann" in each_topic_name
                        or "teleop" in each_topic_name
                        or "cmd" in each_topic_name
                    ):
                        _l = "-"
                        _m = ">"
                    elif "scan" in each_topic_name:
                        _l = ":"
                        _m = "+"
                    elif "_tf" in each_topic_name:
                        _l = "-"
                        _m = "1"
                    elif "imu_raw" in each_topic_name:
                        _l = ":"
                        _m = 6
                    elif "imu" in each_topic_name:
                        _l = "-"
                        _m = 6
                    elif "sensors" in each_topic_name or "data" in each_topic_name:
                        _l = "-"
                        _m = 7
                    elif "pf_pose_odom" in each_topic_name:
                        _l = "-"
                        _m = "*"
                    elif "odom" in each_topic_name:
                        _l = ":"
                        _m = "*"
                    else:
                        _l = "-"
                        _m = "."

                    if _show_recorded_stamps and not use_bag_stamps:
                        if recorded_rate_metric.mean_hz is not None:
                            re_rate_label = f" mean: {recorded_rate_metric.mean_hz:.2f} (hz) std: {recorded_rate_metric.std_hz:.2f} (hz)"
                        else:
                            re_rate_label = ""
                        label_name = f"{each_topic_name.removeprefix('topic_')}{re_rate_label}"
                        plt.plot(
                            x_recorded_in_second,
                            # y_recorded,
                            y_recorded_in_second,
                            alpha=0.3,
                            label=(
                                f"{label_name} (recorded)"
                                if not _show_published_stamps
                                else ""
                            ),
                            # label="",
                            linewidth=LINEWIDTH,
                            linestyle=_l,
                            marker=_m,
                            markersize=MARKERSIZE,
                            color="Gray",
                        )

                    if _is_case_show_published_stamps_types_only(
                        _show_published_stamps, _show_recorded_stamps, use_bag_stamps
                    ):
                        pass
                    elif _show_published_stamps:
                        if use_bag_stamps:
                            if recorded_rate_metric.mean_hz is not None:
                                re_rate_label = f" mean: {recorded_rate_metric.mean_hz:.2f} (hz) std: {recorded_rate_metric.std_hz:.2f} (hz)"
                            else:
                                re_rate_label = ""
                            label_name = f"{each_topic_name.removeprefix('topic_')}{re_rate_label}"
                            topic_main_label = f"{label_name} (recorded)"
                        else:
                            published_rate_metric = (
                                published_timestamps.compute_frequency_metric()
                            )
                            if published_rate_metric.mean_hz is not None:
                                pu_rate_label = f" mean: {published_rate_metric.mean_hz:.2f} (hz) std: {published_rate_metric.std_hz:.2f} (hz)"
                            else:
                                pu_rate_label = ""
                            label_name = f"{each_topic_name.removeprefix('topic_')}{pu_rate_label}"
                            if _show_recorded_stamps:
                                topic_main_label = (
                                    f"{label_name} (published + recorded (shaded))"
                                )
                            else:
                                topic_main_label = f"{label_name} (published)"

                        plt.plot(
                            x_main_in_second,
                            # y_main,
                            y_main_in_second,
                            alpha=0.4,
                            label=topic_main_label,
                            linewidth=LINEWIDTH,
                            linestyle=_l,
                            marker=_m,
                            markersize=MARKERSIZE,
                        )

        # ....Plot general config..................................................................
        # plt.ylabel(r"Timestamp $\Delta$ (ns)")
        plt.ylabel(r"Timestamp $\Delta$ (s)")
        plt.xlabel(f"Timestamp (s)")

        comment_ = (
            f"Vertical black lines: Chunk on {chunk_on} interval\n"
            f"Vertical gray lines: Bag recording event"
        )
        if comment:
            comment_ = comment_.join(f"\n{comment}")
        fig.text(
            0.035,
            0.94,
            comment_,
            bbox=dict(edgecolor="lightgray", facecolor="white", alpha=0.9),
            verticalalignment="top",
        )

        footer_comment_v = 0.024
        fig.text(0.018, footer_comment_v, "1e9 (ns) = 1 (s)")

        _window_size = tct.temporal.to_seconds(
            tct_container.get_trajectory_last_timestamp(include_bag_record=True)
            - tct_container.get_trajectory_first_timestamp(include_bag_record=True)
        )
        fig.text(
            0.99,
            footer_comment_v - 0.01,
            f"+ Trajectory start time: {tct.temporal.timestamps.to_seconds(bag_start_time)} (s)\nWindow size: ~{_window_size:.2f} (s)",
            horizontalalignment="right",
        )

        plt.legend(loc="upper right")

        if plot_ylim:
            # plt.ylim(0, plot_ylim)
            plt.ylim(0, tct.temporal.to_seconds(int(plot_ylim)))
        plt.tight_layout(pad=2)

        if save_plot:
            if plot_postfix is not None:
                plot_postfix = f"-window-{plot_postfix}"
            else:
                plot_postfix = ""

            os.makedirs(os.path.join(experiment_dir_path, "plots"), exist_ok=True)
            plt.savefig(
                os.path.join(
                    experiment_dir_path,
                    f"plots",
                    f"{os.path.basename(bag_path_abs)}{plot_postfix}.png",
                ),
                dpi=save_dpi,
            )

        return None


def _is_case_show_published_stamps_types_only(
    _show_published_stamps: bool, _show_recorded_stamps: bool, use_bag_stamps: bool
) -> bool:
    return _show_published_stamps and not _show_recorded_stamps and use_bag_stamps
