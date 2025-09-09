# coding=utf-8
import os
from pathlib import Path
from dataclasses import make_dataclass
from typing import Any, Dict, Optional, Tuple, Type, Union

import numpy as np

from rosbags.rosbag2 import Reader
from rclpy.time import Time as RosTime
from rosbags.typesys.store import Typestore

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
from .utils.general import camelcase_to_snake_case, extract_class_name_from_type, setup_progressbar
from .utils.ros2_non_native_msg import register_ros2_non_native_msg
from .utils.ros2_utils import get_rosbag_typestore_auto_distro
from .utils.shadow_data_container import (
    ShadowDataContainer, instanciate_shadow_data_container,
    post_process_shadown_data_container,
    )


def check_rosbag_path_and_show_available_topics(rosbag_path: Union[str, Path]) -> Path:
    """ Display available topics and messages in a specified ROS bag file.

    This function reads a ROS bag file from the specified path and lists all the available
    topics along with their message types. Additionally, it provides the total number of
    messages in the ROS bag. If the provided path is unreachable and the function is running in a
    Dockerized-NorLab docker container, it attempts to resolve the correct path.

    :param rosbag_path: Path to the ROS bag file (absolute or relative).
    :return: the real ros bag path if the input was a relative path
    """
    # .... Construct absolute path to selected ros bag ............................................
    # Handle cases: pycharm-born dna run and shell-born dna run
    try:
        assert os.path.exists(rosbag_path)
    except AssertionError:
        dn_project_path = os.getenv('DN_PROJECT_PATH')
        if os.path.exists(dn_project_path):
            # Case running in a Dockerized-NorLab docker container
            rosbag_path = os.path.join(dn_project_path, rosbag_path)

        assert os.path.exists(rosbag_path), f"[TCT] rosbag path is unreachable at {rosbag_path}"

    rosbag_path = os.path.realpath(rosbag_path)

    # .... Introspect ros bag contents ............................................................
    print(f"Using ROS bag: {rosbag_path}")
    assert os.path.exists(rosbag_path)

    with Reader(rosbag_path) as reader:
        print("Available topics:")
        for connection in reader.connections:
            print(f"  {connection.topic}: {connection.msgtype}")
        print(f"Total messages: {reader.message_count}")

    return Path(rosbag_path)


def aggregate_multiple_features_from_rosbag(
        rosbag_path: Path,
        dataset_info: Optional[str],
        features_config: Dict[str, Union[Type[RosBagFeatureDataclass], Tuple[str, ...]]],
        start: Optional[int] = None,
        stop: Optional[int] = None,
        typestore: Optional[Typestore] = None
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

    :param rosbag_path: Path to rosbag.
    :param dataset_info: Any relevant information on the rosbag (location, robot, condition).
    :param features_config: The features to agregate from the rosbag as a configuration dictionary.
    :param start: The rosbag timestamp where to start in nanosecond.
    :param stop: The rosbag timestamp where to stop in nanosecond.
    :param typestore: Optional overrides the custom TCT rosbag typestore.
    :return: An instance of the `AbstractMultifeatureDataclass` containing the processed data
        for all features.
    """

    features = []
    features_type = []

    if not typestore:
        typestore = get_rosbag_typestore_auto_distro()
        typestore = register_ros2_non_native_msg(typestore)

    for feature_name, feature_dataclass in features_config.items():
        if isinstance(feature_dataclass, tuple):
            if len(feature_dataclass) == 1:
                raise KeyError(
                        "[TCT error] Check your `features_config` dict. You forgot to specify "
                        "the '"
                        f"{feature_name}' dimensions."
                        )

            new_type, *dims = feature_dataclass
            feat_spec = TrjDataClassFeatureSpecification(
                    new_feature_dataclass_type=new_type, dimension_names=tuple(dims)
                    )

            feature_dataclass = trajectory_dataclass_factory(
                    specification=feat_spec, trj_dataclass_subclass=RosBagFeatureDataclass
                    )

            feature = extract_single_feature_from_rosbag(rosbag_path=rosbag_path,
                                                         feature_name=feature_name,
                                                         data_container_type=feature_dataclass,
                                                         start=start, stop=stop,
                                                         typestore=typestore)

        elif issubclass(feature_dataclass, RosBagFeatureDataclass):
            feature = extract_single_feature_from_rosbag(rosbag_path=rosbag_path,
                                                         feature_name=feature_name,
                                                         data_container_type=feature_dataclass,
                                                         start=start, stop=stop,
                                                         typestore=typestore)
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


def extract_single_feature_from_rosbag(rosbag_path: Path, feature_name: str,
                                       data_container_type: Type[RosBagFeatureDataclass],
                                       start: Optional[int] = None,
                                       stop: Optional[int] = None,
                                       typestore: Optional[Typestore] = None
                                       ) -> RosBagFeatureDataclass:
    """
    Extracts a specific feature from a ROS bag file and returns it in a structured data container.

    This function retrieves messages from a specified topic within a ROS bag, processes them, and
    organizes the extracted data into a provided custom dataclass that inherits from the
    `RosBagFeatureDataclass`. Handles data integrity checks and enables customization for
    specialized message types.

    Usage:

        >>> from trajectory_container_tools.trj_dataclasses.rosbag_feature_dataclass import \
        >>>     NavMsgsOdometry
        >>>
        >>> extract_single_feature_from_rosbag(
        >>>     rosbag_path=Path("</path/to/rosbag>"),
        >>>     feature_name="/odom",data_container_type=NavMsgsOdometry
        >>> )

    :param rosbag_path: Path to the input ROS bag file.
    :param feature_name: Name of the topic to extract data from.
    :param data_container_type: Custom dataclass type inheriting from `RosBagFeatureDataclass`
        used to construct the final structured data container.
    :param start: Optional start time for filtering messages, measured in nanoseconds.
    :param stop: Optional stop time for filtering messages, measured in nanoseconds.
    :param typestore: Optional overrides the custom TCT rosbag typestore.
    :return: An instance of the `data_container_type` containing the processed feature data.
    """
    try:
        if not issubclass(data_container_type, RosBagFeatureDataclass):
            raise ValueError(
                    f"[TCT error] `{data_container_type}` must be a subclass of "
                    f"`RosBagFeatureDataclass`"
                    )
    except TypeError as e:
        raise AttributeError(
                f"[TCT error] `{data_container_type}` must not be instanciated, just pass the "
                f"class as attribute."
                )
    else:
        # ... Create and initialize temporary container ...........................................
        shadow_data_container = instanciate_shadow_data_container(data_container_type)

        # .... Crawl topic msgs ...................................................................
        if not typestore:
            typestore = get_rosbag_typestore_auto_distro()
            typestore = register_ros2_non_native_msg(typestore)

        with Reader(rosbag_path) as reader:

            connections = [conn for conn in reader.connections if conn.topic == feature_name]
            selected_topic_msg_count = len(connections)
            if selected_topic_msg_count == 0:
                raise ValueError(
                        f"[TCT error] Topic `{feature_name}` does not exist in "
                        f"{os.path.basename(rosbag_path)} "
                        )

            print(f"[TCT] Extract single feature from rosbag › seeking {feature_name}")
            if _dataclass_type_is_type_name(data_container_type, "Tf2MsgsTFMessage"):
                # This is a one-time warning (ref task TCT-11)
                print("[TCT] Skipping msg type 'transforms'")

            feature_msg_len = len(
                    list(reader.messages(connections=connections, start=start, stop=stop)))
            print(f"[TCT] Collect topic {feature_name} msg from rosbag")
            progressbar = setup_progressbar(feature_msg_len)

            # (NICE TO HAVE) ToDo: Move rosbag msg reader logic to recursive loop leaf (ref task
            # TCT-40)
            for connection, timestamp, rawdata in reader.messages(connections=connections,
                                                                  start=start, stop=stop):
                progressbar.update(1)

                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)

                # Note: this is a tmp quick-hack for dealing with Tf2MsgsTFMessage topic msg with
                #       embedded msg type (ref task TCT-11)
                # (NICE TO HAVE) ToDo: add nested logic to Tf2MsgsTFMessage and delete
                # quick-hack (ref task TCT-11)
                if _dataclass_type_is_type_name(data_container_type, "Tf2MsgsTFMessage"):
                    msg = getattr(msg, "transforms")
                    msg = msg.pop()

                # ... Fetch properties from rosbag ................................................
                shadow_data_container = _collect_properties_from_rosbag(
                        data_container_type,
                        feature_name, msg,
                        timestamp, shadow_data_container)

            progressbar.close()

        # .... Post-process rosbag data and create data container .................................
        shadow_data_container = post_process_shadown_data_container(
                shadow_data_container,
                data_container_type,
                feature_name)

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
                # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling non-trj data
                if shadow_data_container[each_property_name] is None:
                    if each_property_name == "header_FrameId":
                        shadow_data_container["header_FrameId"] = msg.header.frame_id
                    elif each_property_name == "childFrameId":
                        shadow_data_container["childFrameId"] = msg.child_frame_id
            elif each_property_name == "timestamps":
                # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling trj data
                shadow_data_container["timestamps"]['data'].append(
                        _set_timestamp(msg, timestamp, use_msg_header_time=True)
                        )
            else:
                attribute_list = str(each_property_name).split("_")
                attribute_parent = msg
                for each_child in attribute_list:
                    # Recurse classes attribute e.g.,:
                    #  - 'msg_pose_pose_position_x' -> 'msg.pose.pose.position.x'
                    #  - 'drive_SteeringAngleVelocity' -> 'drive.steering_angle_velocity'

                    # Handle case where key is multi-word e.g.,
                    #  'SteeringAngleVelocity' -> 'steering_angle_velocity'
                    each_child = camelcase_to_snake_case(each_child)

                    attribute_parent = getattr(attribute_parent, each_child)

                if issubclass(shadow_data_container[each_property_name]['type'],
                              (RosBagFeatureDataclass, BaseTrajectoryDataclass)):
                    shadow_data_container[each_property_name] = _collect_properties_from_rosbag(
                            data_container_type=shadow_data_container[each_property_name]['type'],
                            feature_name=each_property_name,
                            msg=attribute_parent,
                            timestamp=timestamp,
                            shadow_data_container=shadow_data_container[each_property_name])
                elif issubclass(shadow_data_container[each_property_name]['type'],
                                (list, np.ndarray)):
                    # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling trj data
                    shadow_data_container[each_property_name]['data'].append(attribute_parent)
                else:
                    # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling trj data
                    shadow_data_container[each_property_name]['data'] = attribute_parent

        except KeyError as e:
            raise KeyError(
                    f"[TCT error] The property `{each_property_name}` does not exist in "
                    f"{feature_name}. Check that property `{each_property_name}` "
                    "in " f"{str(data_container_type)} exist in `{feature_name}`."
                    )

    return shadow_data_container


def _set_timestamp(msg, bag_timestamp, use_msg_header_time: bool = True) -> RosTime:
    # (NICE TO HAVE) ToDo: unit-test (curently indirectly tested)
    if use_msg_header_time:
        _timestamp = RosTime(seconds=msg.header.stamp.sec, nanoseconds=msg.header.stamp.nanosec)
    else:
        _timestamp = RosTime(nanoseconds=bag_timestamp)

    return _timestamp


def _dataclass_type_is_type_name(
        data_container_type_: Type, type_as_str: str
        ):
    return extract_class_name_from_type(data_container_type_) == type_as_str
