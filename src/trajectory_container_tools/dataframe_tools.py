# coding=utf-8

import pandas as pd
from typing import Dict, Tuple, Type, Union
from dataclasses import fields as fields, make_dataclass

from trajectory_container_tools.trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
)
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import \
    DataframeFeatureDataclass

from trajectory_container_tools.utils.data_sanity_checks import (
    timestep_indexing_sanity_check,
)
from trajectory_container_tools.utils.factory import (
    TrjDataClassFeatureSpecification,
    trajectory_dataclass_factory,
)


def aggregate_multiple_features_from_dataframe(
    dataset_frame: pd.DataFrame,
    dataset_info: str,
    features_config: Dict[str, Union[Type[DataframeFeatureDataclass], Tuple[str, ...]]],
) -> AbstractMultifeatureDataclass:
    """Extract multiple features from a dataset (formated in a dataframe) based on a
    configuration dictionary.

    Requirement: the dataframe must contain one trajectory or a batch of trajectories (one per row)
    with some features (column) containing a timestep index in there name
    eg: `feature_1, feature_2 ...


    The `features_config` specify the feature name to lookout in the `rosbag` header and
    agregate them in a `Multifeature` dataclass. Feature dimensions such as 'x', 'y' 'z' are
    specified either by using existing `DataframeFeatureDataclass` subclass such as:
        `StatePose2D`, `CmdStandard`, `CmdSkidSteer`, `Velocity`, `VelocitySkidSteer`
    or by using tuple of strings such as ('<new feature dataclass type name>', '<dimension
        names 1>', '<dimension names 2>', ...).

        >>> feature_config = {
        >>>             'icp_interpolated': StatePose2D,
        >>>             'idd_vel':          StatePose2D,
        >>>             'icp':              ('StatePose3D', 'x', 'y', 'z', 'roll', 'pitch', 'yaw')
        >>>             }

    :param dataset_frame: Dataset as a panda dataframe
    :param dataset_info: Any relevant information about the dataset (location, robot, condition...)
    :param features_config: The features to agregate from the dataset as a configuration dictionary
    """

    features = []
    features_type = []

    for feature_name, feature_dataclass in features_config.items():
        if isinstance(feature_dataclass, tuple):
            if len(feature_dataclass) == 1:
                raise KeyError(
                    "(!) Check your `features_config` dict. You forgot to specify the '"
                    f"{feature_name}' "
                    "dimensions."
                )

            new_type, *dims = feature_dataclass
            feat_spec = TrjDataClassFeatureSpecification(
                new_feature_dataclass_type=new_type, dimension_names=tuple(dims)
            )
            feature_dataclass = trajectory_dataclass_factory(
                    specification=feat_spec,
                    trj_dataclass_subclass=DataframeFeatureDataclass)
            feature = extract_single_feature_from_dataframe(
                dataset=dataset_frame,
                feature_name=feature_name,
                data_container_type=feature_dataclass,
            )
        elif issubclass(feature_dataclass, DataframeFeatureDataclass):
            feature = extract_single_feature_from_dataframe(
                dataset=dataset_frame,
                feature_name=feature_name,
                data_container_type=feature_dataclass,
            )

        features_type.append((feature_name, type(feature)))
        features.append(feature)

    multifeature = make_dataclass(
        "multifeature", bases=(AbstractMultifeatureDataclass,), fields=features_type
    )
    return multifeature(dataset_info, *features)


def extract_single_feature_from_dataframe(
    dataset: pd.DataFrame, feature_name: str, data_container_type: Type[DataframeFeatureDataclass]
) -> DataframeFeatureDataclass:
    # (Priority) ToDo: implement >> a variation of `extract_single_feature_from_dataframe()` for
    # extracting topics from a dataframe organized one timestep per row
    #   Note: `bagpy` is not compatible with ROS2
    """
    Dataframe feature extractor automation function.

    Requirement: the dataframe must contain one trajectory or a batch of trajectories (one per row)
    with some features (column) containing a timestep index in there name
    eg: `feature_1, feature_2 ...

    Usage:
     1. Suposing the dataframe head contain column `body_vel_disturption_x_0` to
     `body_vel_disturption_x_39`.
     2. The `feature_name` and `data_container_type` properties specify which data will be
     extracted from the `dataset_frame`.
     3. `feature_name` must be the same name prefix used in the dataframe head
     e.g:`body_vel_disturption`.
     4. `data_container.<property name>` must be a postfix to `feature_name_<property
     name>_<index>` used in the dataframe head.

    :param dataset:
    :param feature_name:
    :param data_container_type:

    (NICE TO HAVE) ToDo: implement extract arbitrary trajectory length (ref task SWMRD-12
    Implement feature extractor) with param: `extract_trajectory_timesteps: Optional[slice] = None`
    """

    try:
        if not issubclass(data_container_type, DataframeFeatureDataclass):
            raise ValueError(
                f"(!) `{data_container_type}` must be a subclass of "
                f"`DataframeFeatureDataclass`"
            )
    except TypeError as e:
        raise AttributeError(
            f"(!) `{data_container_type}` must not be instanciated, just pass the class as "
            "attribute."
        )
    else:
        try:
            df_features = dataset.filter(like=feature_name)
            if df_features.empty:
                raise ValueError(
                    f"(!) The parameter `{feature_name}` does not exist in `dataset_frame` "
                    "as a column header prefix"
                )

            container_properties = fields(data_container_type)[
                1:
            ]  # Remove 'feature_name'
            tmp_container = {each_field.name: None for each_field in container_properties}

            timestep_index = None
            for each_property in data_container_type.get_dimension_names():
                df_header_field = f"{feature_name}_{each_property}"
                df_property = df_features.filter(regex=f"{df_header_field}_\\d+")
                if df_property.empty:
                    raise ValueError(
                        f"(!) The column `{df_header_field}` does not exist in "
                        "`dataset_frame`."
                        f"Check that property `{each_property}` in {str(data_container_type)} "
                        f"is a `{feature_name}` postfix in the dataset_frame"
                    )

                try:
                    timestep_index = timestep_indexing_sanity_check(df_property, df_header_field)
                    if tmp_container["timestep_index"] is None:
                        tmp_container["timestep_index"] = timestep_index
                except IndexError as e:
                    raise ValueError(
                        "(!) There is a problem with the `dataset_frame` column label "
                        f"`{df_header_field}_` timestep index. "
                        f"<< {e}"
                    )

                tmp_container[each_property] = df_property.to_numpy()

        except ValueError as e:
            raise

    # noinspection PyArgumentList
    return data_container_type(feature_name=feature_name, **tmp_container)
