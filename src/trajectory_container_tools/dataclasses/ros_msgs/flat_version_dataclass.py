# coding=utf-8
from dataclasses import dataclass

import numpy as np

from trajectory_container_tools.dataclasses import RosStampedFeature


@dataclass()
class NavMsgsOdometryFlat(RosStampedFeature):
    """Data container for navigation messages odometry (flat structure data container version).

    Compatible ros2 message interface: nav_msgs/msg/Odometry

    This class provides a structured data representation of odometry messages with flattened
    arrays for position, orientation, linear and angular velocities, as well as their respective
    covariances. It is designed to facilitate efficient handling and processing of odometry
    information in robotics applications.

    :ivar pose_pose_position_x: The x-coordinate of the position.
    :type pose_pose_position_x: numpy.ndarray
    :ivar pose_pose_position_y: The y-coordinate of the position.
    :type pose_pose_position_y: numpy.ndarray
    :ivar pose_pose_position_z: The z-coordinate of the position.
    :type pose_pose_position_z: numpy.ndarray
    :ivar pose_pose_orientation_x: The x-component of the orientation quaternion.
    :type pose_pose_orientation_x: numpy.ndarray
    :ivar pose_pose_orientation_y: The y-component of the orientation quaternion.
    :type pose_pose_orientation_y: numpy.ndarray
    :ivar pose_pose_orientation_z: The z-component of the orientation quaternion.
    :type pose_pose_orientation_z: numpy.ndarray
    :ivar pose_pose_orientation_w: The w-component (scalar) of the orientation quaternion.
    :type pose_pose_orientation_w: numpy.ndarray
    :ivar pose_covariance: The pose covariance matrix.
    :type pose_covariance: numpy.ndarray
    :ivar twist_twist_linear_x: The linear velocity in the x-direction.
    :type twist_twist_linear_x: numpy.ndarray
    :ivar twist_twist_linear_y: The linear velocity in the y-direction.
    :type twist_twist_linear_y: numpy.ndarray
    :ivar twist_twist_linear_z: The linear velocity in the z-direction.
    :type twist_twist_linear_z: numpy.ndarray
    :ivar twist_twist_angular_x: The angular velocity around the x-axis.
    :type twist_twist_angular_x: numpy.ndarray
    :ivar twist_twist_angular_y: The angular velocity around the y-axis.
    :type twist_twist_angular_y: numpy.ndarray
    :ivar twist_twist_angular_z: The angular velocity around the z-axis.
    :type twist_twist_angular_z: numpy.ndarray
    :ivar twist_covariance: The twist covariance matrix.
    :type twist_covariance: numpy.ndarray
    """

    pose_pose_position_x: np.ndarray
    pose_pose_position_y: np.ndarray
    pose_pose_position_z: np.ndarray
    pose_pose_orientation_x: np.ndarray
    pose_pose_orientation_y: np.ndarray
    pose_pose_orientation_z: np.ndarray
    pose_pose_orientation_w: np.ndarray
    pose_covariance: np.ndarray
    twist_twist_linear_x: np.ndarray
    twist_twist_linear_y: np.ndarray
    twist_twist_linear_z: np.ndarray
    twist_twist_angular_x: np.ndarray
    twist_twist_angular_y: np.ndarray
    twist_twist_angular_z: np.ndarray
    twist_covariance: np.ndarray


@dataclass()
class AckermannMsgsAckermannDriveStampedFlat(RosStampedFeature):
    """AckermannMsgsAckermannDriveStamped flat version
    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDriveStamped
    """

    drive_steeringAngle: np.ndarray  # desired virtual angle (radians)
    drive_steeringAngleVelocity: np.ndarray  # desired rate of change (radians/s)
    drive_speed: np.ndarray  # desired forward speed (m/s)
    drive_acceleration: np.ndarray  # desired acceleration (m/s^2)
    drive_jerk: np.ndarray  # desired jerk (m/s^3)


@dataclass()
class SensorMsgsImuFlat(RosStampedFeature):
    """SensorMsgsImu flat version

    Compatible ros2 message interface: sensor_msgs/msg/Imu
    """

    orientation_x: np.ndarray
    orientation_y: np.ndarray
    orientation_z: np.ndarray
    orientation_w: np.ndarray
    orientationCovariance: np.ndarray
    angularVelocity_x: np.ndarray
    angularVelocity_y: np.ndarray
    angularVelocity_z: np.ndarray
    angularVelocityCovariance: np.ndarray
    linearAcceleration_x: np.ndarray
    linearAcceleration_y: np.ndarray
    linearAcceleration_z: np.ndarray
    linearAccelerationCovariance: np.ndarray
