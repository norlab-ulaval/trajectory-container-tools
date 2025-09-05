# coding=utf-8
import os
import re
from pathlib import Path
from tqdm import tqdm
import numpy as np
from dataclasses import make_dataclass
from typing import Any, Dict, Optional, Tuple, Type, Union

from rosbags.rosbag2 import Reader
from rosbags.typesys import Stores, get_typestore

from .trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractMultifeatureDataclass,
    )
from .trj_dataclasses.base_trajectory_dataclass import BaseTrajectoryDataclass
from .trj_dataclasses.rosbag_feature_dataclass import (
    NavMsgsOdometry,
    RosBagFeatureDataclass,
    )
from .utils.factory import (
    TrjDataClassFeatureSpecification,
    trajectory_dataclass_factory,
    )
from .utils.general import set_timestamp
from .utils.shadow_data_container import (
    ShadowDataContainer, data_container_type_to_str, instanciate_shadow_data_container,
    post_process_shadown_data_container, validate_timestamp_integrity,
    )


def aggregate_multiple_features_from_rosbag(
        rosbag_path: Path,
        dataset_info: Optional[str],
        features_config: Dict[str, Union[Type[RosBagFeatureDataclass], Tuple[str, ...]]],
        start: Optional[int] = None,
        stop: Optional[int] = None,
        ) -> AbstractMultifeatureDataclass:
    """Extract multiple features (i.e. topics) from a rosbag_path based on a configuration
    dictionary.

    Notes:

    The `features_config` parameter specify the feature name and type (i.e. topic name and type)
    to lookout in the rosbag topic list and agregate them in a *multifeature* dataclass.

    Feature dimensions such as 'pose.position.x' or 'twist.linear.y' are specified either by
    using existing `RosBagFeatureDataclass` subclass such as `NavMsgsOdometry`,
    `AckermannMsgsAckermannDriveStamped`, `Tf2MsgsTFMessage`, `SensorMsgsImu` or by using tuple
    of strings such as `('<NewFeatureDataclassTypeName>', '<topic_property_name_1>',
    '<topic_property_name_2>', ...)`.

    `NewFeatureDataclassTypeName` is the ros topic type in camelback notation, without the
    `/msg` directory e.g. tf2_msgs/msg/TFMessage = Tf2MsgsTFMessage.

    Topic property name `drive_steeringAngleVelocity` would convert to ros topic msg
    `drive.steering_angle_velocity`. The parsing rule for topic property name is the following
    underscore `_` convert to dot `.` and `CamelCase` convert to `snake_case`.

        >>> feature_config = {
        >>>     '/pf/pose/odom': NavMsgsOdometry,
        >>>     '/odom':         NavMsgsOdometry,
        >>>     '/tf':           ('Tf2MsgsTFMessage', 'transform_translation_x',
        >>>                                           'transform_translation_y',
        >>>                                           'transform_translation_z')
        >>> }

    :param rosbag_path: Path to rosbag
    :param dataset_info: Any relevant information on the rosbag (location, robot, condition)
    :param features_config: The features to agregate from the rosbag as a configuration dictionary
    :param start: The rosbag timestamp where to start in nanosecond
    :param stop: The rosbag timestamp where to stop in nanosecond
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
                    start=start,
                    stop=stop
                    )

        elif issubclass(feature_dataclass, RosBagFeatureDataclass):
            feature = extract_single_feature_from_rosbag(
                    rosbag_path=rosbag_path,
                    feature_name=feature_name,
                    data_container_type=feature_dataclass,
                    start=start,
                    stop=stop
                    )
        else:
            raise

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
        start: Optional[int] = None,
        stop: Optional[int] = None,
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
            # ... Create and initialize temporary container .......................................
            shadow_data_container = instanciate_shadow_data_container(data_container_type)

            # .... Crawl topic msgs ...............................................................
            with Reader(rosbag_path) as reader:
                connections = [conn for conn in reader.connections if conn.topic == feature_name]
                _selected_topic_msg_count = len(connections)
                if _selected_topic_msg_count == 0:
                    raise ValueError(
                            f"(!) Topic `{feature_name}` does not exist in "
                            f"{os.path.basename(rosbag_path)} "
                            )

                print(f"\n[Rosbag crawler in progress]\n")
                progressbar = tqdm(total=_selected_topic_msg_count)
                for connection, timestamp, rawdata in reader.messages(
                        connections=connections, start=start, stop=stop
                        ):
                    progressbar.update(1)

                    # ⚠️ Note: "deserialize_cdr(rawdata, connection.msgtype)" is deprecated
                    # msg = deserialize_cdr(rawdata, connection.msgtype)
                    # (CRITICAL) inprogress: validate refactoring (ref task RLRP-83)
                    typestore = get_typestore(Stores[f"ros2_{os.getenv('ROS_DISTRO')}".upper()])
                    msg = typestore.deserialize_cdr(rawdata, connection.msgtype)

                    # Note: this is a quick hack for dealing with topic msg with embedded msg type
                    #       (ref task RLRP-95)
                    if _dataclass_type_is_type_name(data_container_type, "Tf2MsgsTFMessage"):
                        msg = getattr(msg, "transforms")
                        msg = msg.pop()

                    # ... Fetch properties from rosbag ............................................
                    shadow_data_container = _collect_properties_from_rosbag(
                            data_container_type,
                            feature_name, msg,
                            timestamp, shadow_data_container)

                progressbar.close()

                # .... Convert properties to numpy arrays .........................................
                # for each_property_name in data_container_type.get_dimension_names():
                #     if each_property_name in ["header_FrameId", "childFrameId"]:
                #         pass
                #     else:
                #         # (CRITICAL) ToDo: implement shadow data container depth search
                #         # mechanism (ref task RLRP-83)
                #         # (CRITICAL) ToDo: implement nested ndarray type conditional execution
                #         # logic (ref task RLRP-83)
                #         shadow_data_container[each_property_name] = np.array(
                #                 shadow_data_container[each_property_name]
                #                 )
                shadow_data_container = post_process_shadown_data_container(shadow_data_container,
                                                                            data_container_type,
                                                                            feature_name)

                # .... Validate data integrity ....................................................
                shadow_data_container = validate_timestamp_integrity(data_container_type, feature_name,
                                                                     shadow_data_container)

        except ValueError as e:
            raise

    # (CRITICAL) ToDo: implement nested trj dataclass instanciation case (ref task RLRP-83)

    # noinspection PyArgumentList
    return data_container_type(**shadow_data_container)


def _collect_properties_from_rosbag(
        data_container_type: Union[Type[RosBagFeatureDataclass], Type[BaseTrajectoryDataclass]],
        feature_name: str,
        msg: object | Any,
        timestamp: int,
        shadow_data_container: ShadowDataContainer) -> ShadowDataContainer:

    for each_property_name in data_container_type.get_dimension_names():
        try:
            if each_property_name in ["header_FrameId", "childFrameId"]:
                if shadow_data_container[each_property_name] is None:
                    if each_property_name == "header_FrameId":
                        shadow_data_container[each_property_name] = msg.header.frame_id
                    elif each_property_name == "childFrameId":
                        shadow_data_container[each_property_name] = msg.child_frame_id
            elif each_property_name == "timestamps":
                shadow_data_container[each_property_name]['data'].append(
                        set_timestamp(msg, timestamp, use_msg_header_time=True)
                        )
            elif issubclass(shadow_data_container[each_property_name]['type'], (RosBagFeatureDataclass, BaseTrajectoryDataclass)):
                attribute_list = str(each_property_name).split("_")
                attribute_parent = msg

                # Recurse classe attribute
                # Example:
                #  - 'msg_pose_pose_position_x' -> 'msg.pose.pose.position.x'
                #  - 'drive_SteeringAngleVelocity' ->
                #  'drive.steering_angle_velocity'
                for each_child in attribute_list:

                    # Handle case where key is multi-word e.g.,
                    # 'SteeringAngleVelocity' -> 'steering_angle_velocity'
                    each_child = _camelcase_to_snake_case(each_child)

                    attribute_parent = getattr(attribute_parent, each_child)

                shadow_data_container[each_property_name] = _collect_properties_from_rosbag(
                        data_container_type=shadow_data_container[each_property_name]['type'],
                        feature_name=each_property_name,
                        msg=attribute_parent,
                        timestamp=timestamp,
                        shadow_data_container=shadow_data_container[each_property_name])
            elif issubclass(shadow_data_container[each_property_name]['type'], (list, np.ndarray)):
                attribute_list = str(each_property_name).split("_")
                attribute_parent = msg

                # Recurse classe attribute
                # Example:
                #  - 'msg_pose_pose_position_x' -> 'msg.pose.pose.position.x'
                #  - 'drive_SteeringAngleVelocity' ->
                #  'drive.steering_angle_velocity'
                for each_child in attribute_list:

                    # Handle case where key is multi-word e.g.,
                    # 'SteeringAngleVelocity' -> 'steering_angle_velocity'
                    each_child = _camelcase_to_snake_case(each_child)

                    attribute_parent = getattr(attribute_parent, each_child)

                shadow_data_container[each_property_name]['data'].append(attribute_parent)
            else:
                raise NotImplementedError("(Priority) ToDo: implement (ref task RLR-83P)")

        except KeyError as e:
            raise KeyError(
                    f"(!) The property `{each_property_name}` does not exist in "
                    f"{feature_name}. Check that property `{each_property_name}` "
                    "in "
                    f"{str(data_container_type)} exist in `{feature_name}`."
                    )

    return shadow_data_container


def _dataclass_type_is_type_name(
        data_container_type_: Type, type_as_str: str
        ):
    return data_container_type_to_str(data_container_type_) == type_as_str


def _camelcase_to_snake_case(name: str) -> str:
    """ Converts a string from camelCase to snake_case.

    This function processes a string assumed to be in camelCase format and transforms
    it into snake_case format by inserting underscores before uppercase letters and
    lowercasing all characters.

        >>> _camelcase_to_snake_case("drive_steeringAngleVelocity")
        >>> # drive_steering_angle_velocity
        >>> _camelcase_to_snake_case("drive_SteeringAngleVelocity")
        >>> # drive__steering_angle_velocity

    :param name: The camelCase formatted string that needs to be converted to snake_case.
    :return: A string formatted in snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
