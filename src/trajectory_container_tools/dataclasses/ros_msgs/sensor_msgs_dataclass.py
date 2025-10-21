# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .core_dataclass import RosStampedFeature
from .geometry_msgs_dataclass import GeometryMsgsQuaternion, GeometryMsgsVector3


@dataclass()
class SensorMsgsImu(RosStampedFeature):
    """Represents IMU (Inertial Measurement Unit) sensor data with orientation,
    angular velocity, and
    linear acceleration, including their covariance values.

    Compatible ros2 message interface: sensor_msgs/msg/Imu

    This dataclass is used to store data typically obtained from an IMU sensor. It contains
    information about the orientation, angular velocity, and linear acceleration of a body, along
    with their respective covariance matrices to represent variability or uncertainty in
    measurements.

    :ivar orientation: The orientation of the sensor expressed as a quaternion.
    :type orientation: GeometryMsgsQuaternion
    :ivar orientationCovariance: The covariance matrix of the orientation measurement.
    :type orientationCovariance: np.ndarray
    :ivar angularVelocity: The angular velocity of the sensor.
    :type angularVelocity: GeometryMsgsVector3
    :ivar angularVelocityCovariance: The covariance matrix of the angular velocity measurement.
    :type angularVelocityCovariance: np.ndarray
    :ivar linearAcceleration: The linear acceleration of the sensor.
    :type linearAcceleration: GeometryMsgsVector3
    :ivar linearAccelerationCovariance: The covariance matrix of the linear acceleration
    measurement.
    :type linearAccelerationCovariance: np.ndarray
    """

    orientation: GeometryMsgsQuaternion
    orientationCovariance: np.ndarray
    angularVelocity: GeometryMsgsVector3
    angularVelocityCovariance: np.ndarray
    linearAcceleration: GeometryMsgsVector3
    linearAccelerationCovariance: np.ndarray


@dataclass()
class SensorMsgsLaserScan(RosStampedFeature):
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
