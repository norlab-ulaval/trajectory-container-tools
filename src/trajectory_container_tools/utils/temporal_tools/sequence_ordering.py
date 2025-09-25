# coding=utf-8
from typing import Any, Union

import numpy as np

from trajectory_container_tools.trj_dataclasses.base_trajectory_dataclass import (
    NestedBaseTrajectoryDataclass,
)
from trajectory_container_tools.trj_dataclasses.ros2_feature_dataclass import (
    RosStampedDataclass,
)
from trajectory_container_tools.utils.temporal_tools.timestamps import (
    Timestamps,
)
from trajectory_container_tools.utils.shadow_data_container import (
    fetch_timestamps_from_shadow_data_container,
)


def fix_sequence_ordering_base_on_timestamps(
    shadow_data_container: dict, data_container_type_: type[RosStampedDataclass]
) -> dict:
    """Fix trajectory data sequence ordering with respect to timestamps values

    Note that the 'shadow_data_container' object is an intermediate step before instanciating a
    'AbstractTrajectoryDataclass' object

    :param shadow_data_container: a dictionary of trajectory data
    :param data_container_type_: the type of AbstractTrajectoryDataclass subclass
    :return: the fixed shadow_data_container
    """
    ts_ = fetch_timestamps_from_shadow_data_container(shadow_data_container)

    sorted_ts_idx = ts_.stamps.argsort()

    shadow_data_container = _fix_container_array_timestamps(
        data_container_type_, sorted_ts_idx, shadow_data_container
    )
    return shadow_data_container


def _fix_container_array_timestamps(
    data_container_type_: Union[
        type[RosStampedDataclass], type[NestedBaseTrajectoryDataclass], type[Any]
    ],
    sorted_ts_idx: np.ndarray,
    shadow_data_container: dict,
):
    for each_property_name in data_container_type_.get_dimension_names():
        each_property = shadow_data_container[each_property_name]
        dimension_type, is_list_of_type = each_property.get_dimension_type(each_property_name)
        if is_list_of_type:
            raise NotImplementedError("(NICE TO HAVE) ToDo: support list of type (ref TCT-61)")

        if not dimension_type:
            return shadow_data_container

        if isinstance(each_property, np.ndarray):
            shadow_data_container[each_property_name] = each_property[sorted_ts_idx]
        elif isinstance(each_property, NestedBaseTrajectoryDataclass):
            dimension_type, is_list_of_type = each_property.get_dimension_type(each_property_name)
            if is_list_of_type:
                raise NotImplementedError(
                    "(NICE TO HAVE) ToDo: support list of type (ref TCT-61)"
                )

            shadow_data_container[each_property_name] = _fix_container_array_timestamps(
                data_container_type_=dimension_type,
                sorted_ts_idx=sorted_ts_idx,
                shadow_data_container=shadow_data_container[each_property_name],
            )
    return shadow_data_container
