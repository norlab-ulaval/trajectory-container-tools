# coding=utf-8
from typing import List, Optional

import numpy as np
import pandas as pd


def timestep_indices_sanity_check(
    timestep_index: np.ndarray, trajectory_expected_len: Optional[int] = None
) -> np.ndarray:
    """
    Checks and validates if the provided timestep index satisfies monotonicity
    and constant increment constraints.

    This function ensures that the elements in the timestep index are monotonically increasing
    and verify that the trajectory length corresponds to a constant increment sequence. If these
    conditions are not met, an `IndexError` is raised.

    :param timestep_index: The array representing the timestep indices to be validated.
    :param trajectory_expected_len: Optional; Expected trajectory length. If not provided, it is
        derived from the shape of `timestep_index`.
    :return: The validated timestep index.
    :raises IndexError: If the `timestep_index` is not monotonically increasing, or
        the trajectory length does not correspond to a constant increment.
    """
    np_diff = np.diff(timestep_index)

    index_is_monoticaly_increasing = np.all(np_diff > 0)

    if not trajectory_expected_len:
        trajectory_expected_len = timestep_index.shape[-1]

    index_start = timestep_index[0]
    index_start -= 1
    index_end = timestep_index[-1]
    delta = index_end - index_start
    index_has_constant_increment = trajectory_expected_len == delta

    is_timestep_index_good_to_go = all(
        (index_is_monoticaly_increasing, index_has_constant_increment)
    )
    if not is_timestep_index_good_to_go:
        raise IndexError(
            f"[TCT error] The timestep index is either missing a step or not monotonicaly "
            f"increassing"
        )

    return timestep_index


def dataframe_timestep_indexing_sanity_check(
    the_dataframe: pd.DataFrame, indexed_column_label: str
) -> np.ndarray:
    """Utility for validating timestep index in column label by checking if it is either
    missing a step or not monotonicaly increassing.

    :param the_dataframe:
    :param indexed_column_label:
    :return: the timestep index as a numpy ndarray
    :raises IndexError: If the dataframe timestep index is not monotonically increasing, or
        the trajectory length does not correspond to a constant increment.
    """
    column_labels: List[str] = the_dataframe.columns.to_list()
    col_index = [
        int(each_label.strip(indexed_column_label)) for each_label in column_labels
    ]
    timestep_index = np.array(col_index)
    column_nb = the_dataframe.shape[1]

    timestep_index = timestep_indices_sanity_check(timestep_index, column_nb)

    return timestep_index
