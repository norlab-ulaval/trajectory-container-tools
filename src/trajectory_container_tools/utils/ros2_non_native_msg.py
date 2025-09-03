# coding=utf-8
from rosbags.typesys import get_types_from_msg, register_types

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


def register_ros2_non_native_msg():
    register_types(
        get_types_from_msg(ACKERMAN_STAMPED_MSG, 'ackermann_msgs/msg/AckermannDriveStamped')
    )

    register_types(get_types_from_msg(ACKERMAN_MSG, 'ackermann_msgs/msg/AckermannDrive'))
    return None
