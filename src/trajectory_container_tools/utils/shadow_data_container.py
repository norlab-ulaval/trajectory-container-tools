# coding=utf-8
from typing import Optional, Union

import numpy as np
from tqdm import tqdm

from .general import extract_class_name_from_type, setup_progressbar
from .typing.new_types_and_aliases import ShadowDataContainer
from ..dataclasses import RosFeature, RosFeatureArray, RosStampedFeature
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeatureUnboundedArray,
    BaseTrajectoryFeature,
)
from trajectory_container_tools.temporal import Timestamps


def instanciate_shadow_data_container(
    data_container_type: Union[
        type[RosFeature],
        type[RosStampedFeature],
        type[RosFeatureArray],
    ],
    nested_lvl: int = 0,
) -> ShadowDataContainer:
    """
    Instantiates a shadow data container for storing data corresponding to the given
    data container type. This function recursively initializes each property of the
    provided data container type and its sub-properties.

    :param data_container_type: The data container type for which the shadow data container is to be instantiated.
    :param nested_lvl: The nested container depth.
    :return: A shadow data container.
    """
    shadow_data_container: ShadowDataContainer

    shadow_data_container = {
        each_field: None
        for each_field in data_container_type.get_cls_public_field_names(
            include_non_init_dim=False
        )
    }

    # Internal logic
    shadow_data_container["type"] = data_container_type
    shadow_data_container["nested_lvl"] = nested_lvl

    for each_property_name in data_container_type.get_cls_public_field_names(
        include_non_init_dim=False
    ):

        dimension_type, is_list_of_type = data_container_type.get_cls_public_field_type(
            each_property_name
        )

        if is_list_of_type:
            shadow_data_container[each_property_name] = [
                instanciate_shadow_data_container(dimension_type, nested_lvl + 1),
            ]

        elif issubclass(
            dimension_type,
            (RosFeature, RosFeatureArray, RosStampedFeature, BaseTrajectoryFeature),
        ):
            shadow_data_container[each_property_name] = (
                instanciate_shadow_data_container(dimension_type, nested_lvl + 1)
            )
        elif issubclass(dimension_type, (np.ndarray, Timestamps)):
            # Note: Using a list to temporary aggregate data and then convert to numpy array when
            #       done is faster than directly append to a numpy array
            shadow_data_container[each_property_name] = {
                "type": dimension_type,
                "data": [],
            }
        else:
            shadow_data_container[each_property_name] = {
                "type": dimension_type,
                "data": None,
            }
    return shadow_data_container


def post_process_shadown_data_container(
    shadow_data_container: ShadowDataContainer,
    data_container_type: Union[
        type[RosFeature],
        type[RosFeatureArray],
        type[RosStampedFeature],
    ],
    feature_name: Optional[str],
    fail_causal_ordering_violation=True,
    progressbar_enabled=True,
) -> ShadowDataContainer:
    """
    Post-processes a ShadowDataContainer containing various data elements while ensuring proper
    handling of nested data types and arrays.

    This function processes a ShadowDataContainer by removing unused keys, validating data
    integrity based on the provided data container type, and managing different cases for nested
    and array-like data.

    :param shadow_data_container: The data container shadowing data_container_type.
    :param data_container_type: The expected type of data container.
    :param feature_name: The name of the specific feature process by non-nested data container.
    :param progressbar_enabled:
    :param fail_causal_ordering_violation:
    :return: The processed ShadowDataContainer with the updated structure and values.
    """
    # (NICE TO HAVE) ToDo: unit-test explicitly (ref task RLRP-83). Its indirectly tested for now.
    for each in data_container_type.container_internal_field():
        if each == "feature_name":
            if (
                issubclass(
                    data_container_type,
                    (BaseTrajectoryFeature, BaseTrajectoryFeatureUnboundedArray),
                )
                and shadow_data_container["nested_lvl"] == 0
            ):
                shadow_data_container["feature_name"] = feature_name
            else:
                # Nested trj container should not populate 'feature_name'
                if "feature_name" in shadow_data_container:
                    del shadow_data_container["feature_name"]
        else:
            if each in shadow_data_container:
                del shadow_data_container[each]

    del shadow_data_container["type"]
    del shadow_data_container["nested_lvl"]

    progressbar: Optional[tqdm] = None
    if progressbar_enabled:
        print(
            f"[TCT] Post-process rosbag data and configure "
            f"{extract_class_name_from_type(data_container_type)} container"
        )
        progressbar = setup_progressbar(len(list(shadow_data_container.items())))

    for k, v in shadow_data_container.items():

        if isinstance(v, list):
            for idx, each in enumerate(v):
                target_type = each.get("type")
                ppsdc = post_process_shadown_data_container(
                    each,
                    data_container_type=target_type,
                    feature_name=None,
                    fail_causal_ordering_violation=fail_causal_ordering_violation,
                    progressbar_enabled=False,
                )
                if "type" in ppsdc:
                    del ppsdc["type"]
                if "nested_lvl" in ppsdc:
                    del ppsdc["nested_lvl"]
                shadow_data_container[k][idx] = target_type(
                    **ppsdc, fail_causal_ordering_violation=fail_causal_ordering_violation
                )
        elif not issubclass(
            data_container_type, BaseTrajectoryFeatureUnboundedArray
        ) and (
            k in data_container_type.non_trajectory_field()
            or k in data_container_type.container_internal_field()
        ):
            pass
        elif k == "type" or k == "nested_lvl":
            pass
        elif isinstance(v, dict) and v.get("type") is not None:
            target_type = v.get("type")
            if issubclass(target_type, np.ndarray):
                assert isinstance(v["data"], list)
                shadow_data_container[k] = np.array(v["data"])
            elif issubclass(target_type, Timestamps):
                if k == "bag_recorded_timestamps" and len(v["data"]) == 0:
                    shadow_data_container[k] = None
                else:
                    shadow_data_container[k] = Timestamps(v["data"])
            elif (
                issubclass(
                    target_type, (RosFeature, RosStampedFeature, BaseTrajectoryFeature)
                )
                and v.get("nested_lvl") > 0
            ):
                ppsdc = post_process_shadown_data_container(
                    v,
                    data_container_type=target_type,
                    feature_name=None,
                    fail_causal_ordering_violation=fail_causal_ordering_violation,
                    progressbar_enabled=False,
                )
                if "type" in ppsdc:
                    del ppsdc["type"]
                if "nested_lvl" in ppsdc:
                    del ppsdc["nested_lvl"]
                shadow_data_container[k] = target_type(
                    **ppsdc, fail_causal_ordering_violation=fail_causal_ordering_violation
                )
            else:
                shadow_data_container[k] = v["data"]
        else:
            shadow_data_container[k] = v

        if progressbar_enabled:
            progressbar.update(1)

    if progressbar_enabled:
        progressbar.close()
    return shadow_data_container
