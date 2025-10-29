# coding=utf-8
import os
from pathlib import Path

import pandas as pd
from typing import Dict, Tuple, Union
from dataclasses import make_dataclass

from trajectory_container_tools.utils.typing.new_types_and_aliases import TrajectoryFeaturesBag
from trajectory_container_tools import AbstractTrajectoryFeaturesBag
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    BaseDataframeFeatureDataclass,
)

from trajectory_container_tools.temporal.timestep_indexing import (
    validate_dataframe_timesteps_indexing,
)
from trajectory_container_tools.utils import dn_sanitize_path
from trajectory_container_tools.utils.factory import parse_feature_spec


def unpack_dataframe_and_show_topic(
    dataframe_path: Union[str, Path]
) -> Tuple[pd.DataFrame, Path]:
    """
    Unpack a dataframe from a given file path. Display its columns and content for convenience.

    This function processes a given path to a dataframe file, resolves the absolute path,
    handles potential Docker environment adjustments, loads the dataframe, and prints its
    available column labels and a preview of its content. The function finally returns the
    loaded dataframe and its resolved absolute path.

    :param dataframe_path: Path to the dataframe file.
    :return: A tuple containing the unpacked dataframe as a `pd.DataFrame` object
        and the resolved absolute `Path` of the dataframe file.
    """

    dataframe_path = dn_sanitize_path(dataframe_path)

    # .... Introspect dataframe header ............................................................
    print(f"Using dataframe bag: {dataframe_path}")

    print("Available column label:")
    dataframe_ = pd.read_pickle(dataframe_path)
    print(dataframe_.head())

    return dataframe_, Path(dataframe_path)


def from_dataframe(
    dataset_frame: pd.DataFrame,
    dataset_info: str,
    features_config: Dict[
        str, Union[type[BaseDataframeFeatureDataclass], Tuple[str, ...]]
    ],
    header_mix_label_and_timesteps: bool = True,
) -> TrajectoryFeaturesBag:
    """Extract multiple features from a dataset (formated in a dataframe) based on a
    configuration dictionary.

    Requirement: the dataframe must contain one trajectory or a batch of trajectories (one per row)
    with some features (column) containing a timestep index in there name
    e.g., `feature_1, feature_2, feature_3 ...


    The `features_config` specify the feature name to lookout in the `rosbag` header and
    agregate them in a `TrajectoryFeaturesBag` dataclass. Feature dimensions such as 'x', 'y' 'z'
    are specified either by using existing `BaseDataframeFeatureDataclass` subclass such as
        `StatePose2D`, `CmdStandard`, `CmdSkidSteer`, `Velocity`, `VelocitySkidSteer`
    or by using tuple of strings such as ('<new feature dataclass type name>', '<dimension
        names 1>', '<dimension names 2>', ...).

    >>> feature_config = {
    >>>             'icp_interpolated': StatePose2D,
    >>>             'idd_vel':          StatePose2D,
    >>>             'icp':              ('StatePose3D', 'x', 'y', 'z', 'roll', 'pitch', 'yaw')
    >>>             }

    :param dataset_frame: Dataset as a panda dataframe.
    :param dataset_info: Any relevant information about the dataset (location, robot,
     condition...).
    :param features_config: The features to agregate from the dataset as a configuration
     dictionary.
    :param header_mix_label_and_timesteps: A flag indicating whether the dataset's column names
        append timestep details to the feature name (e.g., `<feature_name>_<timestep>`).
        Default is True.
    :return: An instance of TrajectoryFeaturesBag containing the extracted data by
     feature.
    """

    features = []
    features_type = []

    for feature_name, feature_dataclass in features_config.items():
        if isinstance(feature_dataclass, tuple):
            feature_dataclass = parse_feature_spec(
                feature_dataclass,
                target_subclass=BaseDataframeFeatureDataclass,
                feature_name=feature_name,
            )

        feature = extract_dataframe_feature(
            dataset=dataset_frame,
            feature_name=feature_name,
            data_container_type=feature_dataclass,
            header_mix_label_and_timesteps=header_mix_label_and_timesteps,
        )

        features_type.append((feature_name, type(feature)))
        features.append(feature)

    trajectory_features_bag = make_dataclass(
        "TrajectoryFeaturesBag", bases=(AbstractTrajectoryFeaturesBag,), fields=features_type
    )
    return trajectory_features_bag(dataset_info, *features)


def extract_dataframe_feature(
    dataset: pd.DataFrame,
    feature_name: str,
    data_container_type: type[BaseDataframeFeatureDataclass],
    header_mix_label_and_timesteps: bool = True,
) -> BaseDataframeFeatureDataclass:
    """
    Dataframe feature extractor automation function. Extracts a single feature from a pandas
    DataFrame while organizing it into a dataclass compatible with the specified container type.

    This function attempts to retrieve a feature from the provided dataset by filtering the column
    names for matches to the specified feature prefix. If the column names include timesteps as a
    postfix, it handles the extraction of such structures as well. The extracted data is organized
    into the provided dataclass type.

    `header_mix_label_and_timesteps=True` requirement: the dataframe must contain one trajectory
    or a batch of trajectories (one per row) with some features (column) containing a timestep
    index in there name e.g., `feature_1, feature_2, feature_3 ...

    Usage:
     1. Suposing the dataframe head contains column `body_vel_disturption_x_0` to
     `body_vel_disturption_x_39`.
     2. The `feature_name` and `data_container_type` properties specify which data will be
     extracted from the `dataset_frame`.
     3. `feature_name` must be the same name prefix used in the dataframe head
     e.g:`body_vel_disturption`.
     4. `data_container.<property name>` must be a postfix to `feature_name_<property
     name>_<index>` used in the dataframe head.


    :param dataset: The pandas DataFrame from which a feature is to be extracted.
    :param feature_name: The prefix of the column names representing the feature to be
        extracted from the dataset.
    :param data_container_type: The class/type of the dataclass container where the extracted
        feature will be organized. Must inherit from `BaseDataframeFeatureDataclass`.
    :param header_mix_label_and_timesteps: A flag indicating whether the dataset's column names
        append timestep details to the feature name (e.g., `<feature_name>_<timestep>`).
        Default is True.
    :return: An instance of the provided dataclass type containing the extracted feature organized
        as specified.
    """
    # (NICE TO HAVE) ToDo: implement nested trajectory-dataclass support for dataframe extraction
    # (NICE TO HAVE) ToDo: implement extract arbitrary trajectory length (ref task SWMRD-12)
    #     with param: `extract_trajectory_timesteps: Optional[slice] = None`

    try:
        if not issubclass(data_container_type, BaseDataframeFeatureDataclass):
            raise ValueError(
                f"[TCT error] `{data_container_type}` must be a subclass of "
                f"`BaseDataframeFeatureDataclass`"
            )
    except TypeError as e:
        raise AttributeError(
            f"[TCT error] `{data_container_type}` must not be instanciated, just pass the "
            f"class as "
            "attribute."
        )
    else:
        try:
            df_features: pd.DataFrame = dataset.filter(like=feature_name)
            if df_features.empty:
                raise ValueError(
                    f"[TCT error] The parameter `{feature_name}` does not exist in "
                    f"`dataset_frame` as a column header prefix"
                )

            # (NICE TO HAVE) ToDo: refactor using "shadow_data_container" module
            tmp_container = {
                each_field: None
                for each_field in data_container_type.get_cls_public_field_names(include_non_init_dim=False)
            }

            for each_property in data_container_type.get_cls_public_field_names(include_non_init_dim=False):
                if each_property == "timestamps":
                    print(
                        "Be advised timestamps sanity check is not supported yet with "
                        "dataframe "
                        "to tct extraction"
                    )

                df_header_field = f"{feature_name}_{each_property}"
                empty_property_error_msg = (
                    f"[TCT error] The column `{df_header_field}` does not exist in "
                    "`dataset_frame`."
                    f"Check that property `{each_property}` in {str(data_container_type)} "
                    f"is a `{feature_name}` postfix in the dataset_frame"
                )

                df_property: pd.DataFrame = df_features.filter(items=[df_header_field])
                if df_property.empty and header_mix_label_and_timesteps:
                    df_property: pd.DataFrame = df_features.filter(regex=f"{df_header_field}_\\d+")
                    if df_property.empty:
                        raise ValueError(empty_property_error_msg)

                    try:
                        timestep_index = validate_dataframe_timesteps_indexing(
                            df_property, df_header_field
                        )
                        tmp_container["timesteps_indices"] = timestep_index
                    except IndexError as e:
                        raise ValueError(
                            "[TCT error] There is a problem with the `dataset_frame` column "
                            "label "
                            f"`{df_header_field}_` timestep index. << {e}"
                        )
                elif not header_mix_label_and_timesteps:
                    if df_property.empty:
                        raise ValueError(empty_property_error_msg)
                    if tmp_container["timesteps_indices"] is None:
                        tmp_container["timesteps_indices"] = dataset.index.array

                tmp_container[each_property] = df_property.to_numpy()

        except ValueError as e:
            raise

    # noinspection PyArgumentList
    return data_container_type(
        feature_name=feature_name, **tmp_container, batch=header_mix_label_and_timesteps
    )
