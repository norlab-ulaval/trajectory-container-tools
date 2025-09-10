# coding=utf-8
from typing import List, Type, Union

import numpy as np
import pandas as pd
from rclpy.time import Time as ROSTime

from ..trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass
from ..trj_dataclasses.rosbag_feature_dataclass import RosBagFeatureDataclass


def timestamp_causal_ordering_sanity_check(shadow_data_container: dict,
                                           nanoseconds: bool = True) -> List[int]:
    """ Checks the causal order of timestamps in the given data container to ensure they are
    sequentially increasing.

    This sanity check function validates that each timestamp in the timestamp array is less
    than the next timestamp. If a causal order violation is detected, the function identifies
    and reports the offending timestamps and raises an assertion error.

    Usage example:

    >>> mock_shadow_data_container = {
    >>>     'feature_name': "/mock_teleop",
    >>>     "timestamps": mock_trajectory_timestamp_in_ros_time,
    >>> }
    >>> offending_index = timestamp_causal_ordering_sanity_check(mock_shadow_data_container)
    >>> # AssertionError: Timestamp causal ordering sanity check failed! Number of offending timestamps 4/3409
    >>> # [TCT error] Timestamp causal ordering violations:
    >>> #
    >>> #     Offending /mock_teleop timestamps:
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #                   nanoseconds [  T  ]                          nanoseconds [ T+1 ]
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #           1711047163876963111 [  302]     !<                             0 [  303]
    >>> #                             0 [  511]     !<                             0 [  512]
    >>> #           1711047175850442468 [  631]     !<                             0 [  632]
    >>> #           1711047237203461717 [ 3334]     !<                             0 [ 3335]
    >>> #
    >>> #     Rosbag timestamps metadate:
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #                             nanoseconds    ( seconds nanoseconds )
    >>> #           start:    1711047156311350031    (1711047156, 311350031)
    >>> #           stop:     1711047241134490773    (1711047241, 134490773)
    >>> #       duration:             84823140742
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> assert len(offending_index) == 4

    :param shadow_data_container: A dictionary containing a "timestamps" entry which is a list
    of ROS time instances.
    :param nanoseconds: Display in nanosecond or ( seconds nanoseconds ). Default nanoseconds
    :return: The list of offending timestamps indexes.
    :raises AssertionError: Raises an AssertionError if the "timestamps" array is empty
        or if any timestamp violates the causal ordering.
    """
    # .... Pre-conditions .........................................................................
    assert "feature_name" in shadow_data_container, "[TCT error] missing required key 'feature_name'!"
    if "timestamps" in shadow_data_container or "header" in shadow_data_container:
        if "timestamps" in shadow_data_container:
            timestamps_ = shadow_data_container["timestamps"]
        else:
            timestamps_ = shadow_data_container["header"].__getattribute__("timestamps")
    else:
        raise AssertionError("[TCT error] missing required key 'timestamps' or 'header'!")

    assert len(timestamps_) > 0, "[TCT error] timestamp array is empty!"
    assert isinstance(timestamps_[0], ROSTime), "[TCT error] timestamp are not ros time objects!"

    # .... Begin ..................................................................................
    offending_idx = []
    offending_ts = ""
    for ts_idx in np.arange(start=1, stop=len(timestamps_)):
        previous_timestamp: ROSTime = timestamps_[ts_idx - 1]
        current_timestamp: ROSTime = timestamps_[ts_idx]

        try:
            assert previous_timestamp < current_timestamp
        except AssertionError:
            if nanoseconds:
                previous_timestamp = previous_timestamp.nanoseconds
                current_timestamp = current_timestamp.nanoseconds
            else:
                previous_timestamp = previous_timestamp.seconds_nanoseconds()
                current_timestamp = current_timestamp.seconds_nanoseconds()
            offending_idx.append(ts_idx)
            offending_ts += (
                    f"    {str(previous_timestamp):>25} [{ts_idx - 1:>5}]     !<     "
                    f"{str(current_timestamp):>25} [{ts_idx:>5}]\n")

    if len(offending_idx) > 0:
        if nanoseconds:
            timestamp_display = "nanoseconds"
        else:
            timestamp_display = "( seconds nanoseconds )"
        offending_ts_header = (
                f"    {'—' * 78}\n"
                f"    {timestamp_display:>25} [  T  ]            {timestamp_display:>25} [ T+1 ]\n"
                f"    {'—' * 78}"
        )
        error_msg = (
                f"Timestamp causal ordering sanity check failed! "
                f"Number of offending timestamps {len(offending_idx)}/{len(timestamps_)}\n"
                f"[TCT error] Timestamp causal ordering violations:\n\n"
                f"    Offending {shadow_data_container['feature_name']} timestamps:\n"
                f"{offending_ts_header}\n"
                f"{offending_ts}\n"
                f"    Rosbag timestamps metadate:\n"
                f"    {'—' * 78}\n"
                f"                            nanoseconds    ( seconds nanoseconds )\n"
                f"          start: {timestamps_[0].nanoseconds:>22}  "
                f"{str(timestamps_[0].seconds_nanoseconds()):>25} \n"
                f"          stop:  {timestamps_[-1].nanoseconds:>22}  "
                f"{str(timestamps_[-1].seconds_nanoseconds()):>25} \n"
                f"      duration:  "
                f"{(timestamps_[-1].nanoseconds - timestamps_[0].nanoseconds):>22}  \n"
                f"    {'—' * 78}\n"
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
                f"[TCT error] The timestep index is either missing a step or not monotonicaly "
                f"increassing"
                )

    return timestep_index


def fix_sequence_ordering_base_on_timestamps(
        shadow_data_container: dict,
        data_container_type_: Type[RosBagFeatureDataclass]) -> dict:
    """Fix trajectory data sequence ordering with respect to timestamps values

    Note that the 'shadow_data_container' object is an intermediate step before instanciating a
    'AbstractTrajectoryDataclass' object

    :param shadow_data_container: a dictionary of trajectory data
    :param data_container_type_: the type of AbstractTrajectoryDataclass subclass
    :return: the fixed shadow_data_container
    """
    ts_: np.ndarray
    if "timestamps" in shadow_data_container or "header" in shadow_data_container:
        if "timestamps" in shadow_data_container:
            ts_ = shadow_data_container["timestamps"]
        else:
            ts_ = shadow_data_container["header"].__getattribute__("timestamps")
    else:
        raise AssertionError("[TCT error] missing required key 'timestamps' or 'header'!")

    assert isinstance(ts_, np.ndarray), "[TCT] timestamps where not converted to numpy array!"

    # If ts_ contains ROS2 Time objects, convert them to nanoseconds first
    if len(ts_) > 0 and hasattr(ts_[0], 'nanoseconds'):
        # Convert ROS2 Time objects to nanoseconds for sorting
        ts_nanoseconds = np.array([t.nanoseconds for t in ts_])
        sorted_ts_idx = ts_nanoseconds.argsort()
    else:
        # Assume ts_ already contains numeric timestamps
        sorted_ts_idx = ts_.argsort()

    shadow_data_container = _fix_container_array_timestamps(
            data_container_type_, sorted_ts_idx,
            shadow_data_container)
    return shadow_data_container


def _fix_container_array_timestamps(
        data_container_type_: Union[
            Type[RosBagFeatureDataclass], Type[NestedBaseTrajectoryDataclass]],
        sorted_ts_idx: np.ndarray,
        shadow_data_container: dict):
    for each_property_name in data_container_type_.get_dimension_names():
        each_property = shadow_data_container[each_property_name]
        if not each_property.get_dimension_type(each_property_name):
            return shadow_data_container

        if isinstance(each_property, np.ndarray):
            shadow_data_container[each_property_name] = each_property[sorted_ts_idx]
        elif isinstance(each_property, NestedBaseTrajectoryDataclass):
            shadow_data_container[each_property_name] = _fix_container_array_timestamps(
                    data_container_type_=each_property.get_dimension_type(each_property_name),
                    sorted_ts_idx=sorted_ts_idx,
                    shadow_data_container=shadow_data_container[each_property_name]
                    )
    return shadow_data_container
