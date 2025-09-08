# coding=utf-8
from dataclasses import fields as fields
from typing import Dict, List, Optional, Type, Union, TypeAlias

import numpy as np
from tqdm import tqdm

from .general import extract_class_name_from_type, setup_progressbar
from ..trj_dataclasses.rosbag_feature_dataclass import RosBagFeatureDataclass
from ..trj_dataclasses.base_trajectory_dataclass import NestedBaseTrajectoryDataclass
from .data_sanity_checks import timestamp_causal_ordering_sanity_check

ShadowDataContainer: TypeAlias = Dict[str, Union[None, List, np.ndarray, Dict, Union[
    Type[RosBagFeatureDataclass], Type[NestedBaseTrajectoryDataclass]]]]


def instanciate_shadow_data_container(
        data_container_type: Union[
            Type[RosBagFeatureDataclass], Type[NestedBaseTrajectoryDataclass]]
        ) -> ShadowDataContainer:
    """
    Instantiates a shadow data container for storing data corresponding to the given
    data container type. This function recursively initializes each property of the
    provided data container type and its sub-properties.

    :param data_container_type: The data container type for which the shadow
        data container is to be instantiated. It should be either `RosBagFeatureDataclass`
        or `NestedBaseTrajectoryDataclass` or their derived types.
    :return: A shadow data container.
    """

    container_properties = fields(data_container_type)
    shadow_data_container: ShadowDataContainer = {each_field.name: None for each_field in
                                                  container_properties}

    shadow_data_container['type'] = data_container_type

    for each_property_name in data_container_type.get_dimension_names():
        dimension_type = data_container_type.get_dimension_type(each_property_name)
        if each_property_name in ["header_FrameId", "childFrameId"]:
            shadow_data_container[each_property_name] = None
        elif issubclass(dimension_type, np.ndarray):
            # Note: Using a list to temporary aggregate data and then convert to numpy array when
            #       done is faster than directly append to a numpy array
            shadow_data_container[each_property_name] = {'type': np.ndarray, 'data': []}
        elif issubclass(dimension_type, (RosBagFeatureDataclass, NestedBaseTrajectoryDataclass)):
            shadow_data_container[each_property_name] = instanciate_shadow_data_container(
                    dimension_type)
        else:
            shadow_data_container[each_property_name] = {
                    'type': str(dimension_type),
                    'data': None,
                    }
    return shadow_data_container


def post_process_shadown_data_container(shadow_data_container: ShadowDataContainer,
                                        data_container_type: Union[
                                            Type[RosBagFeatureDataclass], Type[
                                                NestedBaseTrajectoryDataclass]],
                                        feature_name: Optional[str],
                                        progressbar_enabled=True) -> ShadowDataContainer:
    """
    Post-processes a ShadowDataContainer containing various data elements while ensuring proper
    handling of nested data types and arrays.

    This function processes a ShadowDataContainer by removing unused keys, validating data
    integrity based on the provided data container type, and managing different cases for nested
    and array-like data.

    :param shadow_data_container: The data container shadowing data_container_type.
    :param data_container_type: The expected type of data container. It must
        be a class type that is either RosBagFeatureDataclass or NestedBaseTrajectoryDataclass.
    :param feature_name: The name of the specific feature process by non-nested data container.
    :param progressbar_enabled:
    :return: The processed ShadowDataContainer with the updated structure and values.
    """
    # (NICE TO HAVE) ToDo: unit-test explicitly (ref task RLRP-83). Its indirectly tested for now.

    if not issubclass(data_container_type, NestedBaseTrajectoryDataclass):
        shadow_data_container["feature_name"] = feature_name
    else:
        # Nested trj container should not populate 'feature_name'
        del shadow_data_container['feature_name']
    del shadow_data_container['timestep_index']

    if issubclass(data_container_type, RosBagFeatureDataclass):
        shadow_data_container["timestamps"] = shadow_data_container["timestamps"]['data']
        validate_timestamp_integrity(data_container_type, feature_name, shadow_data_container)
        del shadow_data_container['type']

    if progressbar_enabled:
        print(
            f"[TCT] Post-process rosbag data and configure "
            f"{extract_class_name_from_type(data_container_type)} container")
        progressbar = setup_progressbar(len(list(shadow_data_container.items())))

    for k, v in shadow_data_container.items():
        if isinstance(v, dict) and v.get('type') is not None:
            target_type = v.get('type')
            if issubclass(target_type, np.ndarray):
                assert isinstance(v['data'], list)
                shadow_data_container[k] = np.array(v['data'])
            elif issubclass(target_type, NestedBaseTrajectoryDataclass):
                ppsdc = post_process_shadown_data_container(v, data_container_type=target_type,
                                                            feature_name=None,
                                                            progressbar_enabled=False
                                                            )
                del ppsdc['type']
                shadow_data_container[k] = target_type(**ppsdc)
        elif isinstance(v, list):
            shadow_data_container[k] = np.array(v)

        if progressbar_enabled:
            progressbar.update(1)

    if progressbar_enabled:
        progressbar.close()
    return shadow_data_container


def validate_timestamp_integrity(
        data_container_type: type[RosBagFeatureDataclass],
        feature_name: str,
        shadow_data_container: ShadowDataContainer) -> ShadowDataContainer:
    """
    Validates the integrity of the timestamp for a specific `rosbag` feature by ensuring timestamps
    are properly aligned and ordering is correct. If issues are detected in the sequence's
    timestamp order, it attempts to fix them and rechecks the sanity of timestamps. This
    validation process ensures the shadow data container content does not break causality.

    :param data_container_type: The container type used for the `rosbag` data feature.
    :param feature_name: The name of the feature being validated.
    :param shadow_data_container: The shadow data container which holds the data
        being validated and possibly corrected.
    :return: A validated shadow data container with corrections applied as necessary.
    """
    try:
        try:
            timestamp_causal_ordering_sanity_check(shadow_data_container)
        except AssertionError:
            shadow_data_container = fix_sequence_ordering_base_on_timestamps(
                    shadow_data_container, data_container_type
                    )
            # Re-check after the fix attempt
            timestamp_causal_ordering_sanity_check(shadow_data_container)

    except AssertionError as e:
        raise ValueError(
                f"[TCT error] There's a problem with the `rosbag` timestamp `{feature_name}`.")
    return shadow_data_container


def fix_sequence_ordering_base_on_timestamps(
        trajectory_dict: Dict[str, Union[str, int, np.ndarray]],
        data_container_type_: Type[RosBagFeatureDataclass],
        ) -> Dict[str, Union[str, int, np.ndarray]]:
    # data_container_type: Type[RosBagFeatureDataclass],
    """Fix trajectory data sequence ordering with respect to timestamps values

    Note that the 'trajectory_dict' object is an intermediate step before instanciating a
    'AbstractTrajectoryDataclass' object

    :param trajectory_dict: a dictionary of trajectory data
    :param data_container_type_: the type of AbstractTrajectoryDataclass subclass
    :return: the fixed trajectory_dict
    """
    ts_: np.ndarray = trajectory_dict["timestamps"]
    sorted_ts_idx = ts_.argsort()
    for each_property_name in data_container_type_.get_dimension_names():
        each_property = trajectory_dict[each_property_name]
        if isinstance(each_property, np.ndarray):
            trajectory_dict[each_property_name] = each_property[sorted_ts_idx]
    return trajectory_dict
