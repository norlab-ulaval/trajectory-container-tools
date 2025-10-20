# coding=utf-8
from typing import Optional, Union

import numpy as np
from tqdm import tqdm

from .general import extract_class_name_from_type, setup_progressbar
from trajectory_container_tools.typing import ShadowDataContainer
from ..dataclasses import RosFeaturesArray, RosStampedFeature
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryArray,
    NestedBaseTrajectory,
)
from trajectory_container_tools.temporal import Timestamps


def instanciate_shadow_data_container(
    data_container_type: Union[
        type[RosFeaturesArray],
        type[RosStampedFeature],
        type[NestedBaseTrajectory],
    ],
) -> ShadowDataContainer:
    """
    Instantiates a shadow data container for storing data corresponding to the given
    data container type. This function recursively initializes each property of the
    provided data container type and its sub-properties.

    :param data_container_type: The data container type for which the shadow
        data container is to be instantiated. It should be either `RosStampedFeature`
        or `NestedBaseTrajectory` or their derived types.
    :return: A shadow data container.
    """
    shadow_data_container: ShadowDataContainer

    shadow_data_container = {
        each_field: None for each_field in data_container_type.get_dimension_names()
    }

    shadow_data_container["type"] = data_container_type

    for each_property_name in data_container_type.get_dimension_names():

        dimension_type, is_list_of_type = data_container_type.get_dimension_type(
            each_property_name
        )

        if is_list_of_type:
            shadow_data_container[each_property_name] = [
                instanciate_shadow_data_container(dimension_type),
            ]

        elif issubclass(dimension_type, (RosFeaturesArray, NestedBaseTrajectory)):
            shadow_data_container[each_property_name] = (
                instanciate_shadow_data_container(dimension_type)
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
        type[RosFeaturesArray],
        type[RosStampedFeature],
        type[NestedBaseTrajectory],
    ],
    feature_name: Optional[str],
    progressbar_enabled=True,
) -> ShadowDataContainer:
    """
    Post-processes a ShadowDataContainer containing various data elements while ensuring proper
    handling of nested data types and arrays.

    This function processes a ShadowDataContainer by removing unused keys, validating data
    integrity based on the provided data container type, and managing different cases for nested
    and array-like data.

    :param shadow_data_container: The data container shadowing data_container_type.
    :param data_container_type: The expected type of data container. It must
        be a class type that is either RosStampedFeature or NestedBaseTrajectory.
    :param feature_name: The name of the specific feature process by non-nested data container.
    :param progressbar_enabled:
    :return: The processed ShadowDataContainer with the updated structure and values.
    """
    # (NICE TO HAVE) ToDo: unit-test explicitly (ref task RLRP-83). Its indirectly tested for now.

    for each in data_container_type._dataclass_internal_field():
        if each == "feature_name":
            if not issubclass(data_container_type, NestedBaseTrajectory):
                shadow_data_container["feature_name"] = feature_name
            else:
                # Nested trj container should not populate 'feature_name'
                if "feature_name" in shadow_data_container:
                    del shadow_data_container["feature_name"]
        else:
            if each in shadow_data_container:
                del shadow_data_container[each]

    del shadow_data_container["type"]

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
                    progressbar_enabled=False,
                )
                if "type" in ppsdc:
                    del ppsdc["type"]
                shadow_data_container[k][idx] = target_type(**ppsdc)
        elif not issubclass(data_container_type, BaseTrajectoryArray) and (
            k in data_container_type.non_trajectory_field()
            or k in data_container_type._dataclass_internal_field()
        ):
            pass
        elif k == "type":
            pass
        elif isinstance(v, dict) and v.get("type") is not None:
            target_type = v.get("type")
            if issubclass(target_type, np.ndarray):
                assert isinstance(v["data"], list)
                shadow_data_container[k] = np.array(v["data"])
            elif issubclass(target_type, Timestamps):
                shadow_data_container[k] = Timestamps(v["data"])
            elif issubclass(target_type, NestedBaseTrajectory):
                ppsdc = post_process_shadown_data_container(
                    v,
                    data_container_type=target_type,
                    feature_name=None,
                    progressbar_enabled=False,
                )
                if "type" in ppsdc:
                    del ppsdc["type"]
                shadow_data_container[k] = target_type(**ppsdc)
            else:
                shadow_data_container[k] = v["data"]
        else:
            shadow_data_container[k] = v

        if progressbar_enabled:
            progressbar.update(1)

    if progressbar_enabled:
        progressbar.close()
    return shadow_data_container


def fetch_timestamps_from_shadow_data_container(
    shadow_data_container: dict,
) -> Timestamps:
    assert "feature_name" in shadow_data_container, (
        "[TCT error] missing required key " "'feature_name'!"
    )
    if "timestamps" in shadow_data_container or "header" in shadow_data_container:
        if "timestamps" in shadow_data_container:
            timestamps_ = shadow_data_container["timestamps"]
        else:
            timestamps_ = shadow_data_container["header"].__getattribute__("timestamps")
    else:
        raise AssertionError(
            "[TCT error] missing required key 'timestamps' or 'header'!"
        )

    assert isinstance(
        timestamps_, Timestamps
    ), "[TCT] timestamps where not converted to a Timestamps object!"
    return timestamps_
