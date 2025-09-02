# coding=utf-8
import os
from pathlib import Path
from tqdm import tqdm
import numpy as np
from dataclasses import fields as fields, make_dataclass
from typing import Dict, List, Tuple, Type, Union

from rosbags.rosbag2 import Reader
from rosbags.serde import deserialize_cdr

from .dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass,
)
from .dataclasses.rosbag_feature_dataclass import (
    NavMsgsOdometry,
    RosBagFeatureDataclass, Tf2MsgsTFMessage,
    )
from .utils.factory import (
    TrjDataClassFeatureSpecification,
    trajectory_dataclass_factory,
)
from .utils.general import set_timestamp
from .utils.data_sanity_checks import timestamp_sanity_check


def aggregate_multiple_features_from_rosbag(
    rosbag_path: Path,
    dataset_info: str,
    features_config: Dict[str, Union[Type[RosBagFeatureDataclass], Tuple[str, ...]]],
) -> AbstractMultifeatureDataclass:
    """Extract multiple features (i.e. topics) from a rosbag_path based on a configuration
    dictionary.

    Notes:

    The `features_config` parameter specify the feature name and type (i.e. topic name and type)
    to lookout in the rosbag topic list and agregate them in a *multifeature* dataclass.

    Feature dimensions such as 'pose.position.x' or 'twist.linear.y' are specified either by
    using existing
    `RosBagFeatureDataclass` subclass such as: `NavMsgsOdometry`,
    `AckermannMsgsAckermannDriveStamped`, `Tf2MsgsTFMessage`, `SensorMsgsImu` or by using tuple
    of strings such as `('<NewFeatureDataclassTypeName>', '<topic_property_name_1>',
    '<topic_property_name_2>', ...)`.

    `NewFeatureDataclassTypeName` is the ros topic type in camelback notation, without the
    `/msg` directory e.g. tf2_msgs/msg/TFMessage = Tf2MsgsTFMessage.

    Topic property `transform_translation_x` would convert to ros topic msg
    `topic_message.transform.translation.x`

        >>> feature_config = {
        >>>             '/pf/pose/odom': NavMsgsOdometry,
        >>>             '/odom':         NavMsgsOdometry,
        >>>             '/tf':           ('Tf2MsgsTFMessage', 'transform_translation_x',
        >>>                                                   'transform_translation_y',
        >>>                                                   'transform_translation_z')
        >>>             }

    :param rosbag_path: Path to rosbag
    :param dataset_info: Any relevant information on the rosbag (location, robot, condition)
    :param features_config: The features to agregate from the rosbag as a configuration dictionary
    """

    features = []
    features_type = []

    for feature_name, feature_dataclass in features_config.items():
        if isinstance(feature_dataclass, tuple):
            if len(feature_dataclass) == 1:
                raise KeyError(
                    "(!) Check your `features_config` dict. You forgot to specify the '"
                    f"{feature_name}' dimensions."
                )

            new_type, *dims = feature_dataclass
            feat_spec = TrjDataClassFeatureSpecification(
                new_feature_dataclass_type=new_type, dimension_names=tuple(dims)
            )

            feature_dataclass = trajectory_dataclass_factory(
                specification=feat_spec, trj_dataclass_subclass=RosBagFeatureDataclass
            )

            feature = extract_single_feature_from_rosbag(
                rosbag_path=rosbag_path,
                feature_name=feature_name,
                data_container_type=feature_dataclass,
            )

        elif issubclass(feature_dataclass, RosBagFeatureDataclass):
            feature = extract_single_feature_from_rosbag(
                rosbag_path=rosbag_path,
                feature_name=feature_name,
                data_container_type=feature_dataclass,
            )

        features_type.append((f"topic{feature_name.replace('/', '_')}", type(feature)))
        features.append(feature)

    rosbag_multifeature = make_dataclass(
        "multifeature",
        bases=(AbstractMultifeatureDataclass,),
        fields=features_type,
    )
    return rosbag_multifeature(dataset_info, *features)


def extract_single_feature_from_rosbag(
    rosbag_path: Path,
    feature_name: str,
    data_container_type: Type[RosBagFeatureDataclass],
    start=None,
    stop=None,
) -> RosBagFeatureDataclass:
    """
    Rosbag feature extractor automation function.

    Usage:
    TODO

    :param rosbag_path:
    :param feature_name: the ros2 topic name to extract
    :param data_container_type: the ros2 topic type as a RosBagFeatureDataclass child
    :param start: The rosbag timestamp where to start in nanosecond
    :param stop: The rosbag timestamp where to stop in nanosecond

    """

    try:
        if not issubclass(data_container_type, RosBagFeatureDataclass):
            raise ValueError(
                f"(!) `{data_container_type}` must be a subclass of `RosBagFeatureDataclass`"
            )
    except TypeError as e:
        raise AttributeError(
            f"(!) `{data_container_type}` must not be instanciated, just pass the class as "
            "attribute."
        )
    else:
        try:
            container_properties = fields(data_container_type)[1:]  # Remove 'feature_name'
            tmp_container: Dict[str, Union[None, List, np.ndarray]] = {
                each_field.name: None for each_field in container_properties
            }

            with Reader(rosbag_path) as reader:
                connections = [conn for conn in reader.connections if conn.topic == feature_name]
                _selected_topic_msg_count = len(connections)
                if _selected_topic_msg_count == 0:
                    raise ValueError(
                        f"(!) Topic `{feature_name}` does not exist in "
                        f"{os.path.basename(rosbag_path)} "
                    )

                # ... Initialize temporary container ..........................................
                for each_property_name in data_container_type.get_dimension_names():
                    if each_property_name in ["header_FrameId", "childFrameId"]:
                        tmp_container[each_property_name] = None
                    else:
                        tmp_container[each_property_name] = []

                print(f"\n[Rosbag crawler in progress]\n")
                progressbar = tqdm(total=_selected_topic_msg_count)
                for connection, timestamp, rawdata in reader.messages(
                    connections=connections, start=start, stop=stop
                ):
                    progressbar.update(1)
                    msg = deserialize_cdr(rawdata, connection.msgtype)

                    # Note: this is a quick hack for dealing with topic msg with embedded msg type
                    #       (ref task RLRP-95)
                    if _dataclass_type_is_type_name(data_container_type, "Tf2MsgsTFMessage"):
                        msg = getattr(msg, "transforms")
                        msg = msg.pop()

                    # ... Fetch properties from rosbag ............................................
                    for each_property_name in data_container_type.get_dimension_names():
                        try:
                            if each_property_name in ["header_FrameId", "childFrameId"]:
                                if tmp_container[each_property_name] is None:
                                    if each_property_name == "header_FrameId":
                                        tmp_container[each_property_name] = msg.header.frame_id
                                    elif each_property_name == "childFrameId":
                                        tmp_container[each_property_name] = msg.child_frame_id
                            elif each_property_name == "timestamps":
                                tmp_container[each_property_name].append(
                                    set_timestamp(msg, timestamp, use_msg_header_time=True)
                                )
                            else:
                                attribute_list = str(each_property_name).split("_")
                                attribute_parent = msg

                                # Recurse classe attribute
                                # Example: msg.pose.pose.position.x
                                for each_child in attribute_list:
                                    attribute_parent = getattr(attribute_parent, each_child)

                                tmp_container[each_property_name].append(attribute_parent)

                        except KeyError as e:
                            raise KeyError(
                                f"(!) The property `{each_property_name}` does not exist in "
                                f"{feature_name}. Check that property `{each_property_name}` "
                                "in "
                                f"{str(data_container_type)} exist in `{feature_name}`."
                            )
                progressbar.close()

                # Convert properties to numpy array
                for each_property_name in data_container_type.get_dimension_names():
                    if each_property_name in ["header_FrameId", "childFrameId"]:
                        pass
                    else:
                        tmp_container[each_property_name] = np.array(
                            tmp_container[each_property_name]
                        )

                try:
                    try:
                        timestamp_sanity_check(tmp_container)
                    except AssertionError:
                        tmp_container = _fix_sequence_ordering_base_on_timestamps(
                            tmp_container, data_container_type
                        )

                    timestamp_sanity_check(tmp_container)

                    timestep_index = np.arange(len(tmp_container["timestamps"]))
                    if tmp_container["timestep_index"] is None:
                        tmp_container["timestep_index"] = timestep_index

                except AssertionError as e:
                    raise ValueError(
                        "(!) There's a problem with the `rosbag` timestamp"
                        f" `{each_property_name}`.\n<< {e}"
                    )

        except ValueError as e:
            raise

    # noinspection PyArgumentList
    return data_container_type(feature_name=feature_name, **tmp_container)


def _dataclass_type_is_type_name(
    data_container_type_: Type[RosBagFeatureDataclass], type_as_str: str
):
    data_container_type_to_str = str(data_container_type_).split(".")[-1].strip("'>")
    return data_container_type_to_str == type_as_str


def _fix_sequence_ordering_base_on_timestamps(
    trajectory_dict: Dict[str, Union[str, int, np.ndarray]],
    data_container_type_: Type[RosBagFeatureDataclass],
) -> Dict[str, Union[str, int, np.ndarray]]:
    # data_container_type_: Type[RosBagFeatureDataclass],
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
