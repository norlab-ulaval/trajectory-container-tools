# coding=utf-8
import os
from pathlib import Path
from dataclasses import make_dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd

from trajectory_container_tools.dataclasses.core.abstract_trajectory_features_bag_dataclass import (
    AbstractTrajectoryFeaturesBag,
)
from trajectory_container_tools.dataclasses.core.abstract_trajectory_stamped_features_bag_dataclass import (
    AbstractTrajectoryStampedFeaturesBag,
)
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeature,
)
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    BaseDataframeStampedFeatureDataclass,
    StatePose2D,
)
from trajectory_container_tools.utils.factory import (
    parse_feature_spec,
)
from trajectory_container_tools.utils.general import (
    setup_progressbar,
)
from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
    post_process_shadown_data_container,
)
from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    Timestamps,
    TimestampsFloat,
)
from trajectory_container_tools.utils.typing.new_types_and_aliases import (
    ShadowDataContainer,
)
from trajectory_container_tools.utils import dn_sanitize_path


def from_csv(
    csv_path: Union[Path, str],
    dataset_info: Optional[str],
    features_config: Dict[
        str, Union[type[BaseDataframeStampedFeatureDataclass], Tuple[str, ...]]
    ],
    timestamp_column: str = "t",
    start: Optional[float] = None,
    stop: Optional[float] = None,
    fail_causal_ordering_violation: bool = True,
    pre_extraction_callback: Callable = None,
    verbose: bool = False
) -> AbstractTrajectoryFeaturesBag:
    """Extract multiple features (i.e. columns) from a CSV file based on a configuration
    dictionary.

    Notes:

    The `features_config` parameter specifies the feature name and type (i.e. column name and type)
    to extract from the CSV file and aggregate them in a `TrajectoryFeaturesBag` dataclass.

    Feature dimensions are specified either by using existing `BaseTrajectoryFeature` subclass
    or by using tuple of strings such as `('<NewFeatureDataclassTypeName>', '<column_name_1>',
    '<column_name_2>', ...)`.

    `NewFeatureDataclassTypeName` is the custom feature type name in CamelCase notation.

    Column names are specified exactly as they appear in the CSV file header. For nested
    properties, use underscore `_` to denote hierarchy levels.

    >>> feature_config = {
    >>>     'imu': ('SensorImu2D', 'acc x', 'acc y', 'ang vel z'),
    >>>     'position': ('Position3D', 'pos x', 'pos y', 'pos z'),
    >>>     'motors': ('MotorCommands', 'mot 1', 'mot 2', 'mot 3', 'mot 4')
    >>> }

    :param csv_path: Path to CSV file.
    :param dataset_info: Any relevant information on the CSV file (location, robot, condition).
    :param features_config: The features to aggregate from the CSV as a configuration dictionary.
    :param timestamp_column: The name of the column containing timestamps. Defaults to "t".
    :param start: The timestamp where to start (in seconds if float, otherwise same unit as CSV).
    :param stop: The timestamp where to stop (in seconds if float, otherwise same unit as CSV).
    :param fail_causal_ordering_violation: Option to disable ordering sanity check (default enabled)
    :param pre_extraction_callback: function respecting signature callback(df: Dataframe) -> df
    :param verbose:
    :return: An instance of the `AbstractTrajectoryStampedFeaturesBag` containing the processed data
        for all features.
    """
    # .... Setup ..................................................................................
    features: list[BaseDataframeStampedFeatureDataclass] = []
    features_type = []

    # .... Load CSV data ..........................................................................
    csv_path = dn_sanitize_path(csv_path)
    if verbose:
        print(f"[TCT] Loading CSV file: {csv_path}")
    df = pd.read_csv(csv_path)

    if pre_extraction_callback is not None:
        df = pre_extraction_callback(df)

    # Validate timestamp column exists
    if timestamp_column not in df.columns:
        raise ValueError(
            f"[TCT error] Timestamp column '{timestamp_column}' not found in CSV file. "
            f"Available columns: {list(df.columns)}"
        )

    # .... Feature extraction .....................................................................
    for feature_name, feature_dataclass in features_config.items():
        # Case: features_config require parsing feature specification
        if isinstance(feature_dataclass, tuple):
            feature_dataclass = parse_feature_spec(
                feature_dataclass,
                target_subclass=BaseDataframeStampedFeatureDataclass,
                feature_name=feature_name,
            )

        feature = extract_csv_feature(
            csv_dataframe=df,
            feature_name=feature_name,
            data_container_type=feature_dataclass,
            timestamp_column=timestamp_column,
            start=start,
            stop=stop,
            fail_causal_ordering_violation=fail_causal_ordering_violation,
            verbose=verbose
        )

        features_type.append((feature_name, type(feature)))
        features.append(feature)

    # .... Collect all unique timestamps from all features ........................................
    if verbose:
        print(f"[TCT] Collect all unique timestamps from features")
    progressbar = setup_progressbar(len(features))
    all_timestamps = []
    for each in features:
        if each.timestamps is not None:
            all_timestamps.append(each.timestamps.stamps)

        progressbar.update(1)

    all_timestamps = np.unique(np.concatenate(all_timestamps))
    progressbar.close()

    # .... TrajectoryFeatureBag declaration and instantiation .....................................
    trajectory_features_bag = make_dataclass(
        "TrajectoryFeaturesBag",
        bases=(AbstractTrajectoryFeaturesBag,),
        fields=features_type,
    )
    return trajectory_features_bag(
        dataset_info,
        *features,
        bag_timestamps=TimestampsFloat(all_timestamps, single_source=False),
        fail_causal_ordering_violation=fail_causal_ordering_violation,
    )


def extract_csv_feature(
    csv_dataframe: pd.DataFrame,
    feature_name: str,
    data_container_type: type[BaseTrajectoryFeature],
    timestamp_column: str = "t",
    start: Optional[float] = None,
    stop: Optional[float] = None,
    fail_causal_ordering_violation: bool = True,
    verbose: bool = False,
) -> BaseTrajectoryFeature:
    """
    Extracts a specific feature from a CSV DataFrame and returns it in a structured data container.

    This function retrieves columns from a CSV DataFrame based on the specified feature configuration,
    processes them, and organizes the extracted data into a provided custom dataclass that inherits
    from `BaseTrajectoryFeature`. Supports nested trajectory dataclasses.

    Usage:

    >>> from trajectory_container_tools.dataclasses.primitive_dataclass import Point2D
    >>>
    >>> df = pd.read_csv("data.csv")
    >>> extract_csv_feature(
    >>>     csv_dataframe=df,
    >>>     feature_name="position",
    >>>     data_container_type=Point2D,
    >>>     timestamp_column="t"
    >>> )

    :param csv_dataframe: DataFrame containing the CSV data.
    :param feature_name: Name of the feature to extract (used for error messages and identification).
    :param data_container_type: Custom dataclass type inheriting from `BaseTrajectoryFeature`
        used to construct the final structured data container.
    :param timestamp_column: Name of the column containing timestamps. Defaults to "t".
    :param start: Optional start time for filtering data (in same units as timestamp column).
    :param stop: Optional stop time for filtering data (in same units as timestamp column).
    :param fail_causal_ordering_violation: Option to disable ordering sanity check (default enabled)
    :param verbose:
    :return: An instance of the `data_container_type` containing the processed feature data.
    """
    try:
        if not issubclass(data_container_type, BaseTrajectoryFeature):
            raise ValueError(
                f"[TCT error] '{data_container_type}' must be a subclass of 'BaseTrajectoryFeature'"
            )
    except TypeError as e:
        raise AttributeError(
            f"[TCT error] '{data_container_type}' must not be instantiated, just pass the "
            f"class as attribute."
        )
    else:
        # .... Filter by time range if specified ......................................................
        df = csv_dataframe.copy()
        if start is not None:
            df = df[df[timestamp_column] >= start]
        if stop is not None:
            df = df[df[timestamp_column] <= stop]

        if len(df) == 0:
            raise ValueError(
                f"[TCT error] No data found in specified time range "
                f"(start={start}, stop={stop})"
            )

        # .... Create and initialize temporary container ..............................................
        shadow_data_container = instanciate_shadow_data_container(
            data_container_type, 0
        )

        # .... Crawl CSV columns ......................................................................
        if verbose:
            print(f"[TCT] Extract single feature from CSV › processing '{feature_name}'\n")

        shadow_data_container = _collect_columns_from_csv(
            data_container_type,
            feature_name,
            df,
            timestamp_column,
            shadow_data_container,
        )

        # .... Post-process CSV data and create data container ........................................
        try:
            shadow_data_container = post_process_shadown_data_container(
                shadow_data_container,
                data_container_type,
                feature_name,
                fail_causal_ordering_violation,
                progressbar_enabled=False
            )

            # noinspection PyArgumentList
            feature_instance = data_container_type(**shadow_data_container)

        except TimestampCausalOrderingError as e:
            error_msg = (
                f"Detected timestamps causal ordering violation in CSV {feature_name} "
                f"feature!\n\n{e}"
            )
            raise TimestampCausalOrderingError(error_msg)

    return feature_instance


def _collect_columns_from_csv(
    data_container_type: type[BaseTrajectoryFeature],
    feature_name: str,
    df: pd.DataFrame,
    timestamp_column: str,
    shadow_data_container: ShadowDataContainer,
) -> ShadowDataContainer:
    """
    Collects properties column-wise from a CSV DataFrame and populates the shadow data container.

    This function iterates over columns instead of rows, preserving the per-column source dtype
    (unlike ``df.iterrows`` which casts all values in a row to a common type).

    :param data_container_type: The dataclass type defining the structure to extract.
    :param feature_name: Name of the feature being extracted.
    :param df: The pandas DataFrame containing CSV data.
    :param timestamp_column: Name of the column containing timestamps.
    :param shadow_data_container: The shadow container being populated.
    :return: Updated shadow data container.
    """
    for each_property_name in data_container_type.get_cls_public_field_names(
        include_non_init_dim=False
    ):
        try:
            if each_property_name == "timestamps":
                # Handle timestamps: extract entire column preserving source dtype
                shadow_data_container["timestamps"]["data"] = list(
                    df[timestamp_column].to_numpy()
                )
            elif (
                isinstance(shadow_data_container[each_property_name], dict)
                and "type" in shadow_data_container[each_property_name]
            ):
                # Case: Simple property (scalar value from CSV column)
                target_type = shadow_data_container[each_property_name]["type"]

                if issubclass(target_type, (np.ndarray,)):
                    # This is a data field - extract entire column preserving source dtype
                    column_name = each_property_name

                    if column_name not in df.columns:
                        raise KeyError(
                            f"[TCT error] Column '{column_name}' not found in CSV. "
                            f"Available columns: {list(df.columns)}"
                        )

                    shadow_data_container[each_property_name]["data"] = list(
                        df[column_name].to_numpy()
                    )
                else:
                    # Other types (like strings, ints, etc.)
                    if each_property_name in df.columns:
                        shadow_data_container[each_property_name]["data"] = df[
                            each_property_name
                        ].iloc[0]

        except KeyError as e:
            raise KeyError(
                f"[TCT error] The property `{each_property_name}` does not exist in CSV "
                f"or in {feature_name}. Check that property `{each_property_name}` "
                f"in {str(data_container_type)} matches a column name in the CSV file. "
                f"Original error: {e}"
            )

    return shadow_data_container
