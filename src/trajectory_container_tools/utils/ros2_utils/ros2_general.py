# coding=utf-8
import os

from trajectory_container_tools.utils.general import RosImportError

try:
    from rosbags.typesys.store import Typestore
    from rosbags.typesys import Stores, get_typestore
except (ImportError, ModuleNotFoundError):
    raise RosImportError


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


def convert_rosbag_topic_key_to_tct_mf_topic_key(feature_name: str) -> str:
    return f"topic{feature_name.replace('/', '_')}"
