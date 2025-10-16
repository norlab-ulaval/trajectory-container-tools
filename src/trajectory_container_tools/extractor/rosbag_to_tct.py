# coding=utf-8
import os
from pathlib import Path
from dataclasses import make_dataclass
from typing import Any, Dict, Optional, Tuple, Union

import numpy as np

from trajectory_container_tools.dataclasses.core.abstract_multifeature_stamped_dataclass import AbstractMultifeatureStampedDataclass
from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
)
from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Header
from trajectory_container_tools.dataclasses import (
    NavMsgsOdometry,
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)
from trajectory_container_tools.utils.factory import (
    parse_feature_spec,
)
from trajectory_container_tools.utils.general import (
    RosImportError,
    camelcase_to_snake_case,
    extract_class_name_from_type,
    setup_progressbar,
    dn_validate_path,
)
from trajectory_container_tools.utils.ros2_utils.ros2_non_native_msg import (
    register_non_native_msgs,
)
from trajectory_container_tools.utils.ros2_utils.ros2_general import (
    convert_rosbag_topic_key_to_tct_mf_topic_key,
    get_rosbag_typestore_auto_distro,
)
from trajectory_container_tools.utils.ros2_utils.ros2_timestamps import (
    rosbag_topic_time_to_timestamp,
)

from trajectory_container_tools.utils.shadow_data_container import (
    instanciate_shadow_data_container,
    post_process_shadown_data_container,
)
from trajectory_container_tools.temporal.timestamps import (
    TimestampCausalOrderingError,
    Timestamps,
)
from trajectory_container_tools.typing import (
    MultifeatureTrajectoryDataclass,
    ShadowDataContainer,
)

try:
    from rosbags.rosbag2 import Reader
    from rosbags.typesys.store import Typestore
except (ImportError, ModuleNotFoundError):
    raise RosImportError


def check_bag_topics(rosbag_path: Union[str, Path]) -> Path:
    """Display available topics and messages in a specified ROS bag file.

    This function reads a ROS bag file from the specified path and lists all the available
    topics along with their message types. Additionally, it provides the total number of
    messages in the ROS bag. If the provided path is unreachable and the function is running in a
    Dockerized-NorLab docker container, it attempts to resolve the correct path.

    :param rosbag_path: Path to the ROS bag file (absolute or relative).
    :return: the real ros bag path if the input was a relative path
    """
    rosbag_path = dn_validate_path(rosbag_path)

    # .... Introspect ros bag contents ............................................................
    print(f"ROS bag path: {rosbag_path}\n")
    assert os.path.exists(rosbag_path)

    with Reader(rosbag_path) as reader:
        print(f"Total messages: {reader.message_count}")
        print(
            f"Rosbag time:\n  start: {reader.start_time} (ns)\n"
            f"  end: {reader.end_time} (ns)\n"
            f"  duration: {reader.duration} (ns)\n"
        )
        print("Available topics:")
        for connection in reader.connections:
            print(f"  {connection.topic}: {connection.msgtype}")

    return Path(rosbag_path)


def from_rosbag(
    rosbag_path: Path,
    dataset_info: Optional[str],
    features_config: Dict[
        str, Union[type[RosDataclass], type[RosStampedDataclass], Tuple[str, ...]]
    ],
    chunk_on="/teleop",
    start: Optional[int] = None,
    stop: Optional[int] = None,
    typestore: Optional[Typestore] = None,
) -> AbstractMultifeatureStampedDataclass:
    """Extract multiple features (i.e. topics) from a rosbag_path based on a configuration
    dictionary.

    Notes:

    The `features_config` parameter specify the feature name and type (i.e. topic name and type)
    to lookout in the rosbag topic list and agregate them in a *multifeature* dataclass.

    Feature dimensions such as 'pose.position.x' or 'twist.linear.y' are specified either by
    using existing `RosStampedDataclass` subclass such as `NavMsgsOdometry`,
    `AckermannMsgsAckermannDriveStamped`, `Tf2MsgsTFMessage`, `SensorMsgsImu` or by using tuple
    of strings such as `('<NewFeatureDataclassTypeName>', '<topic_property_name_1>',
    '<topic_property_name_2>', ...)`.

    `NewFeatureDataclassTypeName` is the ros topic type in camelback notation, without the
    `/msg` directory e.g., `NavMsgsOdometry` = `nav_msgs/msg/Odometry`.

    Topic property name `drive_steeringAngleVelocity` would convert to ros topic msg
    `drive.steering_angle_velocity`. The parsing rule for topic property name is the following
    underscore `_` convert to dot `.` and `CamelCase` convert to `snake_case`.

    >>> feature_config = {
    >>>     '/pf/pose/odom': NavMsgsOdometry,
    >>>     '/odom':         NavMsgsOdometry,
    >>>     '/sensors/imu/raw':     ('SensorMsgsImu2D', 'linearAcceleration_x',
    >>>                                                 'linearAcceleration_y',
    >>>                                                 'angularVelocity_z')
    >>> }

    :param rosbag_path: Path to rosbag.
    :param dataset_info: Any relevant information on the rosbag (location, robot, condition).
    :param features_config: The features to agregate from the rosbag as a configuration dictionary.
    :param chunk_on: The topic in the ROSbag to monitor for chunk split. Defaults to "/teleop".
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
        typestore = register_non_native_msgs(typestore)

    for feature_name, feature_dataclass in features_config.items():
        # Case: features_config require parsing topic msg property
        if isinstance(feature_dataclass, tuple):
            feature_dataclass = parse_feature_spec(
                feature_dataclass,
                target_subclass=RosStampedDataclass,
                feature_name=feature_name,
            )

        feature = extract_rosbag_feature(
            rosbag_path=rosbag_path,
            feature_name=feature_name,
            data_container_type=feature_dataclass,
            start=start,
            stop=stop,
            typestore=typestore,
        )

        features_type.append(
            (convert_rosbag_topic_key_to_tct_mf_topic_key(feature_name), type(feature))
        )
        features.append(feature)

    with Reader(rosbag_path) as reader:
        bag_timestamps = []
        for connection, timestamp, _ in reader.messages(start=start, stop=stop):
            if connection.topic in features_config:
                bag_timestamps.append(timestamp)

    rosbag_multifeature = make_dataclass(
        "multifeature",
        bases=(AbstractMultifeatureStampedDataclass,),
        fields=features_type,
    )
    return rosbag_multifeature(
        dataset_info,
        *features,
        bag_timestamps=Timestamps(np.array(bag_timestamps)),
        chunk_on=convert_rosbag_topic_key_to_tct_mf_topic_key(chunk_on),
    )


def extract_rosbag_feature(
    rosbag_path: Path,
    feature_name: str,
    data_container_type: Union[type[RosDataclass], type[RosStampedDataclass]],
    start: Optional[int] = None,
    stop: Optional[int] = None,
    typestore: Optional[Typestore] = None,
) -> Union[RosDataclass, RosStampedDataclass]:
    """
    Extracts a specific feature from a ROS bag file and returns it in a structured data container.

    This function retrieves messages from a specified topic within a ROS bag, processes them, and
    organizes the extracted data into a provided custom dataclass that inherits from the
    `RosStampedDataclass`. Handles data integrity checks and enables customization for
    specialized message types.

    Usage:

    >>> from trajectory_container_tools.dataclasses import NavMsgsOdometry
    >>>
    >>> extract_rosbag_feature(
    >>>     rosbag_path=Path("</path/to/rosbag>"),
    >>>     feature_name="/odom",data_container_type=NavMsgsOdometry
    >>> )

    :param rosbag_path: Path to the input ROS bag file.
    :param feature_name: Name of the topic to extract data from.
    :param data_container_type: Custom dataclass type inheriting from `RosStampedDataclass`
        used to construct the final structured data container.
    :param start: Optional start time for filtering messages, measured in nanoseconds.
    :param stop: Optional stop time for filtering messages, measured in nanoseconds.
    :param typestore: Optional overrides the custom TCT rosbag typestore.
    :return: An instance of the `data_container_type` containing the processed feature data.
    """
    try:
        if not issubclass(data_container_type, (RosDataclass, RosStampedDataclass)):
            raise ValueError(
                f"[TCT error] `{data_container_type}` must be a subclass of "
                f"`RosStampedDataclass` or `RosDataclass`"
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
            typestore = register_non_native_msgs(typestore)

        with Reader(rosbag_path) as reader:
            connections = [
                conn for conn in reader.connections if conn.topic == feature_name
            ]
            selected_topic_msg_count = len(connections)
            if selected_topic_msg_count == 0:
                raise ValueError(
                    f"[TCT error] Topic `{feature_name}` does not exist in "
                    f"{os.path.basename(rosbag_path)} "
                )

            print(f"[TCT] Extract single feature from rosbag › seeking {feature_name}")

            feature_msg_len = len(
                list(reader.messages(connections=connections, start=start, stop=stop))
            )
            print(f"[TCT] Collect topic {feature_name} msg from rosbag")
            progressbar = setup_progressbar(feature_msg_len)

            # (NICE TO HAVE) ToDo: Move rosbag msg reader logic to recursive loop leaf (ref task
            # TCT-40)
            for connection, timestamp, rawdata in reader.messages(
                connections=connections, start=start, stop=stop
            ):
                progressbar.update(1)

                msg = typestore.deserialize_cdr(rawdata, connection.msgtype)

                # ... Fetch properties from rosbag ................................................
                shadow_data_container = _collect_properties_from_rosbag(
                    data_container_type, feature_name, msg, shadow_data_container
                )

            progressbar.close()

        # .... Post-process rosbag data and create data container .................................
        try:
            shadow_data_container = post_process_shadown_data_container(
                shadow_data_container, data_container_type, feature_name
            )

            # noinspection PyArgumentList
            feature_instance = data_container_type(**shadow_data_container)

        except TimestampCausalOrderingError as e:
            error_msg = (
                f"Detected timestamps causal ordering violation in rosbag {feature_name} "
                f"topic message!\n\n{e}"
            )
            raise TimestampCausalOrderingError(error_msg)

    return feature_instance


def _collect_properties_from_rosbag(
    data_container_type: Union[
        type[RosDataclass],
        type[RosStampedDataclass],
        type[NestedRosStampedDataclass],
        type[BaseTrajectoryDataclass],
    ],
    feature_name: str,
    msg: object | Any,
    shadow_data_container: ShadowDataContainer,
) -> ShadowDataContainer:
    for each_property_name in data_container_type.get_dimension_names():
        try:
            if isinstance(shadow_data_container[each_property_name], list):
                # Case list of nested container

                msg_property_value = getattr(msg, each_property_name)
                assert isinstance(msg_property_value, list)
                assert isinstance(shadow_data_container[each_property_name], list)
                nested_shadow_container_replicate_target_len = len(msg_property_value)
                replicat = shadow_data_container[each_property_name][0]
                while (
                    len(shadow_data_container[each_property_name])
                    < nested_shadow_container_replicate_target_len
                ):
                    shadow_data_container[each_property_name].append(replicat)
                assert (
                    len(shadow_data_container[each_property_name])
                    == nested_shadow_container_replicate_target_len
                ), (
                    f"{len(shadow_data_container[each_property_name])} !="
                    f" {nested_shadow_container_replicate_target_len}"
                )

                for idx, each in enumerate(shadow_data_container[each_property_name]):
                    shadow_data_container[each_property_name][idx] = (
                        _collect_properties_from_rosbag(
                            data_container_type=each["type"],
                            feature_name=each_property_name,
                            msg=msg_property_value[idx],
                            shadow_data_container=each,
                        )
                    )

            elif issubclass(shadow_data_container[each_property_name]["type"], Header):
                # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling non-trj data
                if not shadow_data_container["header"]["frame_id"]["data"]:
                    shadow_data_container["header"]["frame_id"][
                        "data"
                    ] = msg.header.frame_id

                shadow_data_container["header"]["timestamps"]["data"].append(
                    rosbag_topic_time_to_timestamp(msg.header.stamp)
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

                if issubclass(
                    shadow_data_container[each_property_name]["type"],
                    (RosDataclass, BaseTrajectoryDataclass),
                ):
                    shadow_data_container[each_property_name] = (
                        _collect_properties_from_rosbag(
                            data_container_type=shadow_data_container[
                                each_property_name
                            ]["type"],
                            feature_name=each_property_name,
                            msg=attribute_parent,
                            shadow_data_container=shadow_data_container[
                                each_property_name
                            ],
                        )
                    )
                elif issubclass(
                    shadow_data_container[each_property_name]["type"],
                    (list, np.ndarray),
                ):
                    # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling trj data
                    shadow_data_container[each_property_name]["data"].append(
                        attribute_parent
                    )
                else:
                    # (NICE TO HAVE) ToDo: TCT-40 move rosbag msg reader here for handling trj data
                    shadow_data_container[each_property_name]["data"] = attribute_parent

        except KeyError as e:
            raise KeyError(
                f"[TCT error] The property `{each_property_name}` does not exist in "
                f"{feature_name}. Check that property `{each_property_name}` "
                f"in {str(data_container_type)} exist in `{feature_name}`."
            )

    return shadow_data_container


def _dataclass_type_is_type_name(data_container_type_: type, type_as_str: str):
    return extract_class_name_from_type(data_container_type_) == type_as_str
