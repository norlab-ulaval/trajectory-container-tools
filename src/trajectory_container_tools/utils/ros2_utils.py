# coding=utf-8
import os
from typing import Union

from rclpy.time import Time as RosTime
from rosbags.typesys.store import Typestore
from rosbags.typesys.stores.empty import builtin_interfaces__msg__Time
from rosbags.typesys import Stores, get_typestore


def get_ros2_distro() -> str:
    """Retrieve the current ROS 2 distribution from the environment.

    This function retrieves the value of the `ROS_DISTRO` environment variable. If the
    `ROS_DISTRO` variable is not set, an `EnvironmentError` is raised. It ensures that the user
    has sourced the appropriate ROS2 setup before proceeding.

    :raises EnvironmentError: If the `ROS_DISTRO` environment variable is not set.
    :return: The currently active ROS2 distribution.
    """
    distro = os.getenv("ROS_DISTRO")
    if not distro:
        raise EnvironmentError(
            "ROS_DISTRO environment variable is not set. Make sure ROS2 is sourced."
        )
    return distro


def get_rosbag_typestore_auto_distro() -> Typestore:
    """Fetches the typestore for the current ROS 2 distribution.

    The function attempts to dynamically determine the current ROS 2 distribution and fetch the
    corresponding typestore. If the ROS 2 distribution environment is not set or cannot be
    determined, an exception is raised.

    :return: The typestore corresponding to the determined ROS 2 distribution.
    :raises EnvironmentError: If the ROS 2 distribution environment is not set or
        cannot be determined.
    """
    try:
        ros2_distro = get_ros2_distro()
        print(f"Fetch rosbag typestore for ros2 {ros2_distro}")
        typestore = get_typestore(Stores[f"ros2_{ros2_distro}".upper()])
    except EnvironmentError:
        raise
    return typestore


def convert_timestamp_from_rosbag_message(
    msg_timestamp: builtin_interfaces__msg__Time,
    bag_timestamp: int,
    use_topic_timestamp: bool = True,
    output_rostime: bool = False,
) -> Union[int, RosTime]:
    """Converts timestamps from a ROS bag message to ros timestamp format or ros time object.

    This function processes timestamps obtained from ROS bag messages, providing
    the ability to determine output either as ros `rclpy` `Time` objects or as integers compatible
    with ros `Time` nanosecond format. It optionally uses the topic message's timestamp or falls
    back to the bag's timestamp based on the input parameters.

    :param msg_timestamp: The message timestamp from the ROS topic message
    :param bag_timestamp: The timestamp associated with the ROS bag's write operation
    :param use_topic_timestamp: Uses topic message timestamp or the bag’s timestamp. Default True.
    :param output_rostime: The returned timestamp format. Returns a ros `Time` object if true or an
     integers compatible with ros `Time` nanosecond format. Default is `False`.
    :return: Returns the appropriate timestamp in the specified format based on the provided
     arguments.
    """

    if output_rostime:
        _timestamp = rosbag_timestamp_to_ros_time(
            msg_timestamp, bag_timestamp, use_topic_timestamp
        )
    else:
        if use_topic_timestamp:
            _timestamp = rosbag_topic_time_to_timestamp(msg_timestamp)
        else:
            _timestamp = bag_timestamp

    return _timestamp


def rosbag_topic_time_to_timestamp(msg_timestamp: builtin_interfaces__msg__Time) -> int:
    NANOSECONDS_CONVERSION_CONSTANT = 10**9

    nanoseconds = msg_timestamp.nanosec
    seconds = msg_timestamp.sec
    _timestamp = (seconds * NANOSECONDS_CONVERSION_CONSTANT) + nanoseconds
    return _timestamp


def rosbag_timestamp_to_ros_time(
    msg_timestamp: builtin_interfaces__msg__Time,
    bag_timestamp: int,
    use_msg_timestamp: bool,
) -> RosTime:
    if use_msg_timestamp:
        _timestamp = rosbag_topic_time_to_ros_time(msg_timestamp)
    else:
        _timestamp = RosTime(nanoseconds=bag_timestamp)
    return _timestamp


def rosbag_topic_time_to_ros_time(
    msg_timestamp: builtin_interfaces__msg__Time,
) -> RosTime:
    _timestamp = RosTime(seconds=msg_timestamp.sec, nanoseconds=msg_timestamp.nanosec)
    return _timestamp
