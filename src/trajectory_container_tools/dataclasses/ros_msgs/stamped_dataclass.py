# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .core_dataclass import RosStampedDataclass
from trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass import (
    PoseWithCovariance,
    TwistWithCovariance,
    VescMsgsVescImu,
    AckermannMsgsAckermannDrive,
)
from .primitive_dataclass import Quaternion, Vector3


@dataclass()
class NavMsgsOdometry(RosStampedDataclass):
    """Data container for navigation messages odometry (nested data container version).

    Compatible ros2 message interface: nav_msgs/msg/Odometry

    This class serves as a structured container for navigation message data related to odometry
    in ROS. It captures the pose and twist information along with their covariance data. The
    purpose of this container is to facilitate organized and consistent handling of these
    odometry-related data structures. Useful in systems where readability and maintainability of
    the navigation-related data are critical.

    :ivar pose: Contains the pose along with its associated covariance information.
    :type pose: trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass.PoseWithCovariance
    :ivar twist: Contains the twist along with its associated covariance information.
    :type twist: trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass.TwistWithCovariance
    """

    pose: PoseWithCovariance
    twist: TwistWithCovariance


@dataclass()
class AckermannMsgsAckermannDriveStamped(RosStampedDataclass):
    """
    Represents a stamped message for an Ackermann drive message.

    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDriveStamped

    This class is used to wrap an `AckermannMsgsAckermannDrive` message with a
    timestamp and frame ID information for use in robotic systems.

    :ivar drive: The Ackermann drive message containing driving instructions
        such as speed and steering angle.
    :type drive: trajectory_container_tools.dataclasses.AckermannMsgsAckermannDrive
    """

    drive: AckermannMsgsAckermannDrive


@dataclass()
class Scan(RosStampedDataclass):
    """Represents a LaserScan message containing range and intensity data.

    Compatible ros2 message interface: sensor_msgs/msg/LaserScan

    This class encapsulates data from a laser scanner, including information
    about the angular range, time increments between measurements, range values,
    and intensities. The range and intensity values provide important details
    about the surrounding environment being scanned by the laser scanner.

    :ivar angleMin: Start angle of the scan in radians.
    :ivar angleMax: End angle of the scan in radians.
    :ivar angleIncrement: Angular distance between consecutive measurements in radians.
    :ivar timeIncrement: Time between measurements in seconds. For a moving scanner,
        this can be used to interpolate the position of 3D points.
    :ivar scanTime: Total time between scans in seconds.
    :ivar rangeMin: Minimum range value in meters.
    :ivar rangeMax: Maximum range value in meters.
    :ivar ranges: Range data in meters. Values outside the [range_min, range_max]
        bounds should be discarded.
    :type ranges: numpy.ndarray
    :ivar intensities: Intensity data in device-specific units.
    :type intensities: numpy.ndarray
    """

    angleMin: float  # [rad]
    angleMax: float  # [rad]
    angleIncrement: float  # [rad]
    timeIncrement: float  # [seconds]
    scanTime: float  # [seconds]
    rangeMin: float  # [m]
    rangeMax: float  # [m]
    ranges: np.ndarray  # multi-dimensional ndarray [m]
    intensities: np.ndarray  # multi-dimensional ndarray [device-specific units]


@dataclass()
class VescMsgsVescImuStamped(RosStampedDataclass):
    """
    Represents stamped IMU data related to VESC (Vedder Electronic Speed Controller).

    Compatible ros2 message interface: vesc_msgs/msg/VescImuStamped

    This class encapsulates data for a VESC IMU message with timestamping,
    extending the RosStampedDataclass structure. It is compatible
    with the `vesc_msgs/msg/VescImuStamped` ROS2 message interface.
    The primary purpose of this class is to provide a structured data
    representation of IMU measurements retrieved from a VESC-based system.

    :ivar imu: Instance of the VescMsgsVescImu class, representing IMU data.
    :type imu: trajectory_container_tools.dataclasses.ros_msgs.nested_dataclass.VescMsgsVescImu
    """

    imu: VescMsgsVescImu


@dataclass()
class SensorMsgsImu(RosStampedDataclass):
    """Represents IMU (Inertial Measurement Unit) sensor data with orientation,
    angular velocity, and
    linear acceleration, including their covariance values.

    Compatible ros2 message interface: sensor_msgs/msg/Imu

    This dataclass is used to store data typically obtained from an IMU sensor. It contains
    information about the orientation, angular velocity, and linear acceleration of a body, along
    with their respective covariance matrices to represent variability or uncertainty in
    measurements.

    :ivar orientation: The orientation of the sensor expressed as a quaternion.
    :type orientation: Quaternion
    :ivar orientationCovariance: The covariance matrix of the orientation measurement.
    :type orientationCovariance: np.ndarray
    :ivar angularVelocity: The angular velocity of the sensor.
    :type angularVelocity: Vector3
    :ivar angularVelocityCovariance: The covariance matrix of the angular velocity measurement.
    :type angularVelocityCovariance: np.ndarray
    :ivar linearAcceleration: The linear acceleration of the sensor.
    :type linearAcceleration: Vector3
    :ivar linearAccelerationCovariance: The covariance matrix of the linear acceleration
    measurement.
    :type linearAccelerationCovariance: np.ndarray
    """

    orientation: Quaternion
    orientationCovariance: np.ndarray
    angularVelocity: Vector3
    angularVelocityCovariance: np.ndarray
    linearAcceleration: Vector3
    linearAccelerationCovariance: np.ndarray
