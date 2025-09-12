# coding=utf-8
from typing import Type, Union

import numpy as np

from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass
from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import RosBagFeatureDataclass


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
