# coding=utf-8
from typing import List

import numpy as np
import pandas as pd
from rclpy.time import Time as ROSTime


def timestamp_causal_ordering_sanity_check(shadow_data_container: dict) -> List[int]:
    """ Checks the causal order of timestamps in the given data container to ensure they are
    sequentially increasing.

    This sanity check function validates that each timestamp in the timestamps array is less
    than the next timestamp. If a causal order violation is detected, the function identifies
    and reports the offending indices of the timestamps and raises an assertion error.

    :param shadow_data_container: A dictionary containing a "timestamps" entry which is a list of ROS time instances.
    :return: The list of offending timestamps indexes.
    :raises AssertionError: Raises an AssertionError if the "timestamps" array is empty
        or if any timestamp violates the causal ordering.
    """
    timestamps_ = shadow_data_container["timestamps"]
    assert len(timestamps_) > 0, "[TCT error] timestamp array is empty!"

    offending_idx = []
    error_msg_collect = ""
    for ts_idx in np.arange(start=1, stop=len(timestamps_)):
        previous_timestamp: ROSTime = timestamps_[ts_idx - 1]
        current_timestamp: ROSTime = timestamps_[ts_idx]
        previous_timestamp = previous_timestamp.seconds_nanoseconds()
        current_timestamp = current_timestamp.seconds_nanoseconds()
        try:
            assert previous_timestamp < current_timestamp
        except AssertionError as e:
            offending_idx.append(ts_idx)
            error_msg_collect += f"    timestamps[{ts_idx}] {previous_timestamp} !< {current_timestamp}\n"

    if len(offending_idx) > 0:
        print(f"[TCT error] Timestamp causal ordering violations:\n"
              f"{error_msg_collect}")

        error_msg = (
                f"[TCT error] Timestamp causal ordering sanity check failed! "
                f"Number of offending timestamp {len(offending_idx)}/{len(timestamps_)}"
        )
        raise AssertionError(error_msg)

    return offending_idx


def dataframe_timestep_indexing_sanity_check(
        the_dataframe: pd.DataFrame, unindexed_column_label: str
        ) -> np.ndarray:
    """Utility for validating timestep index in column label by checking if it is either
    missing a step or not monotonicaly increassing.

    :param the_dataframe:
    :param unindexed_column_label:
    :return: the timestep index as a numpy ndarray or raise a IndexError
    """
    column_labels: List[str] = the_dataframe.columns.to_list()
    col_index = [int(each_label.strip(unindexed_column_label)) for each_label in column_labels]
    timestep_index = np.array(col_index)
    np_diff = np.diff(timestep_index)

    index_is_monoticaly_increasing = np.all(np_diff > 0)

    column_nb = the_dataframe.shape[1]
    index_start = timestep_index[0]
    if index_start == 0:
        index_start = -1
    index_end = timestep_index[-1]
    delta = index_end - index_start
    index_has_constant_increment = column_nb == delta

    is_timestep_index_good_to_go = all(
            (index_is_monoticaly_increasing, index_has_constant_increment)
            )
    if not is_timestep_index_good_to_go:
        raise IndexError(
                f"[TCT error] The timestep index is either missing a step or not monotonicaly increassing"
                )

    return timestep_index
