# coding=utf-8
import numpy as np
from rclpy.time import Time as RosTime


def set_timestamp(msg, bag_timestamp, use_msg_header_time: bool = True) -> int:
    if use_msg_header_time:
        # _timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 10e-9
        # _timestamp = msg.header.stamp.sec * 10e9 + msg.header.stamp.nanosec
        _timestamp = RosTime(seconds=msg.header.stamp.sec, nanoseconds=msg.header.stamp.nanosec)
    else:
        _timestamp = bag_timestamp
    
    return _timestamp


def check_is_finite(x: np.ndarray) -> None:
    assert np.all(
        np.isfinite(x)
    ), f"non finite value(s) in {np.argwhere(np.isfinite(x) == False)=}"
    return None


def extract_class_name_from_type(the_object: object) -> str:
    """Take an object and return the class name as a string

    Example:
        >>> aaa = np.ones((2,2))
        >>> extract_class_name_from_type(aaa)
        # "ndarray"

    :param the_object: an instance
    """
    return str(type(the_object)).strip("<'>").split(".")[-1]
