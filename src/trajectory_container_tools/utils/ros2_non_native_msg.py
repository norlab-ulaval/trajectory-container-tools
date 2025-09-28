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

# Execute for more info: $ ros2 interface show ackermann_msgs/msg/AckermannDrive
ACKERMAN_MSG = """
float32 steering_angle
float32 steering_angle_velocity
float32 speed
float32 acceleration
float32 jerk
"""

# Execute for more info: $ ros2 interface show ackermann_msgs/msg/AckermannDriveStamped
ACKERMAN_STAMPED_MSG = """
std_msgs/Header header
AckermannDrive  drive
"""


# Execute for more info: $ ros2 interface show vesc_msgs/msg/VescImu
VESC_MSG = """
geometry_msgs/Vector3  ypr
geometry_msgs/Vector3  linear_acceleration
geometry_msgs/Vector3  angular_velocity
geometry_msgs/Vector3  compass
geometry_msgs/Quaternion orientation
"""

# Execute for more info: $ ros2 interface show vesc_msgs/msg/VescImuStamped
VESC_STAMPED_MSG = """
std_msgs/Header header
VescImu imu
"""


def register_non_native_msgs(typestore: Optional[Typestore] = None) -> Typestore:
    if not typestore:
        typestore = get_rosbag_typestore_auto_distro()

    if not typestore.types.get("ackermann_msgs/msg/AckermannDrive"):
        typestore.register(
            get_types_from_msg(ACKERMAN_MSG, "ackermann_msgs/msg/AckermannDrive")
        )

    if not typestore.types.get("ackermann_msgs/msg/AckermannDriveStamped"):
        typestore.register(
            get_types_from_msg(
                ACKERMAN_STAMPED_MSG, "ackermann_msgs/msg/AckermannDriveStamped"
            )
        )

    if not typestore.types.get("vesc_msgs/msg/VescImu"):
        typestore.register(
            get_types_from_msg(VESC_MSG, "vesc_msgs/msg/VescImu")
        )

    if not typestore.types.get("vesc_msgs/msg/VescImuStamped"):
        typestore.register(
            get_types_from_msg(
                VESC_STAMPED_MSG, "vesc_msgs/msg/VescImuStamped"
            )
        )

    return typestore
