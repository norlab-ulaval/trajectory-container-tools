# coding=utf-8
from dataclasses import dataclass
from typing import Optional, Union

from rclpy.time import Time as RosTime
from rosbags.typesys.stores.empty import builtin_interfaces__msg__Time


@dataclass
class TrajectoryTimestampsMetadata:
    """Represents a trajectory timestamps metadata.

    This class encapsulates the start time, end time, and duration of a trajectory. The `duration`
    is automatically calculated if not provided during initialization. It can be used for various
    time-based operations related to trajectory handling.

    :ivar start_time: The start time of the trajectory.
    :type start_time: int
    :ivar end_time: The end time of the trajectory.
    :type end_time: int
    :ivar duration: The total duration of the trajectory.
    :type duration: Optional[int]
    """

    start_time: int
    end_time: int
    duration: Optional[int] = None

    def __post_init__(self):
        if self.duration is None:
            self.duration = self.end_time - self.start_time


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
    """
    Converts a ROS2 message timestamp to an integer timestamp in nanoseconds.

    This function processes a rosbag time object, and calculates an integer representation in
    nanoseconds by combining its `sec` (seconds) and `nanosec` (nanoseconds) fields.

    :param msg_timestamp: A rosbag time object containing separate fields for seconds
        and nanoseconds.
    :return: An integer representation of the given timestamp in nanoseconds.
    """
    NANOSECONDS_CONVERSION_CONSTANT = 10**9

    assert isinstance(msg_timestamp, builtin_interfaces__msg__Time)

    nanoseconds = msg_timestamp.nanosec
    seconds = msg_timestamp.sec
    _timestamp = (seconds * NANOSECONDS_CONVERSION_CONSTANT) + nanoseconds
    return _timestamp


def rosbag_timestamp_to_ros_time(
    msg_timestamp: builtin_interfaces__msg__Time,
    bag_timestamp: int,
    use_msg_timestamp: bool,
) -> RosTime:
    """
    Converts bag and topic level timestamps from a rosbag time object to ROS2 time object.

    This function converts a message timestamp from a rosbag time object into a ROS2 time object.
    The conversion can use either the message's inherent timestamp or the bag's timestamp depending
     on the `use_msg_timestamp` flag.

    :param msg_timestamp: The timestamp from the message, given in ROS message time type.
    :param bag_timestamp: The bag timestamp, given as an integer in nanoseconds.
    :param use_msg_timestamp: A boolean flag indicating whether to use the message's
        timestamp (if True) or the bag's timestamp (if False).
    :return: The converted ROS time object.
    """
    if use_msg_timestamp:
        _timestamp = rosbag_topic_time_to_ros_time(msg_timestamp)
    else:
        _timestamp = RosTime(nanoseconds=bag_timestamp)
    return _timestamp


def rosbag_topic_time_to_ros_time(
    msg_timestamp: builtin_interfaces__msg__Time,
) -> RosTime:
    """
    Converts a rosbag time object to a ROS2 time object.

    This function takes a rosbag time object, extracts its seconds and nanoseconds components,
    and constructs a ROS2 time object (`RosTime`) which encapsulates these components.

    :param msg_timestamp: ROS 2 timestamp to convert.
    :type msg_timestamp: builtin_interfaces__msg__Time
    :return: The equivalent ROS time object.
    :rtype: RosTime
    """
    assert isinstance(msg_timestamp, builtin_interfaces__msg__Time)

    _timestamp = RosTime(seconds=msg_timestamp.sec, nanoseconds=msg_timestamp.nanosec)
    return _timestamp
