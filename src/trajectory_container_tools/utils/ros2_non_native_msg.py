# coding=utf-8
from typing import Optional

from rosbags.typesys import get_types_from_msg
from rosbags.typesys.store import Typestore

from trajectory_container_tools.utils.ros2_utils import get_rosbag_typestore_auto_distro

# from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive
# from vesc_msgs.msg import VescStateStamped

# from std_msgs.msg import Float64
# from geometry_msgs.msg import PoseStamped, PoseArray, PoseWithCovarianceStamped, PointStamped
# from sensor_msgs.msg import Joy

# Execute for more info: $ ros2 interface show ackermann_msgs/msg/AckermannDriveStamped
ACKERMAN_STAMPED_MSG = """
std_msgs/Header header
AckermannDrive  drive
"""

# Execute for more info: $ ros2 interface show ackermann_msgs/msg/AckermannDrive
ACKERMAN_MSG = """
float32 steering_angle
float32 steering_angle_velocity
float32 speed
float32 acceleration
float32 jerk
"""


def register_ros2_non_native_msg(typestore: Optional[Typestore] = None) -> Typestore:
    if not typestore:
        typestore = get_rosbag_typestore_auto_distro()

    if not typestore.types.get('ackermann_msgs/msg/AckermannDrive'):
        typestore.register(
                get_types_from_msg(ACKERMAN_MSG, 'ackermann_msgs/msg/AckermannDrive')
                )

    if not typestore.types.get('ackermann_msgs/msg/AckermannDriveStamped'):
        typestore.register(
                get_types_from_msg(ACKERMAN_STAMPED_MSG, 'ackermann_msgs/msg/AckermannDriveStamped')
                )

    return typestore
