# coding=utf-8
from dataclasses import dataclass, field
from typing import List

import numpy as np

from .base_trajectory_dataclass import BaseTrajectoryDataclass, NestedBaseTrajectoryDataclass
from .ros2_primitive_dataclass import Header, Point, Quaternion, Transform, Vector3


@dataclass()
class RosStampedDataclass(BaseTrajectoryDataclass):
    header: Header



@dataclass()
class Pose(NestedBaseTrajectoryDataclass):
    """
    Represents a pose with position and orientation.

    Compatible ros2 message interface: geometry_msgs/msg/Pose

    A `Pose` class combines position and orientation to define the state or
    configuration of an object in a 3-dimensional space. This is often used
    in robotics, graphics, or physics simulations where both the location
    (point) and the spatial orientation (rotation) of an object are required.

    :ivar position: Spatial position of the object.
    :type position: Point
    :ivar orientation: Orientation of the object defined as a quaternion.
    :type orientation: Quaternion
    """
    position: Point
    orientation: Quaternion


@dataclass()
class PoseWithCovariance(NestedBaseTrajectoryDataclass):
    """ Represents a pose with its covariance data.

    Compatible ros2 message interface: geometry_msgs/msg/PoseWithCovariance

    This class is used to encapsulate a pose along with its associated covariance matrix,
    which provides information about the uncertainty of the pose observations. The pose
    describes position and orientation, and the covariance matrix quantifies the uncertainty in
    these observations. It is useful in robotics, navigation, and computer vision applications
    where pose estimation is required.

    :ivar pose: The pose represented as a position and orientation.
    :type pose: Pose
    :ivar covariance: The covariance matrix associated with the pose,
        representing the uncertainty in the pose observations.
    :type covariance: numpy.ndarray
    """
    pose: Pose
    covariance: np.ndarray


@dataclass()
class Twist(NestedBaseTrajectoryDataclass):
    """
    Represents a 6DOF twist with linear and angular components.

    Compatible ros2 message interface: geometry_msgs/msg/Twist

    This class is used to encapsulate both linear and angular velocity
    components in 3D space. It is a fundamental representation in various
    robotic systems for describing motion or spatial velocity.

    :ivar linear: The linear velocity vector.
    :type linear: Vector3
    :ivar angular: The angular velocity vector.
    :type angular: Vector3
    """
    linear: Vector3
    angular: Vector3


@dataclass()
class TwistWithCovariance(NestedBaseTrajectoryDataclass):
    """ Represents a twist with an associated covariance matrix.

    Compatible ros2 message interface: geometry_msgs/msg/TwistWithCovariance

    This dataclass encapsulates a twist (which typically includes linear and angular velocity
    components) along with a covariance matrix. It is used in contexts where both the twist and
    its uncertainty are required, such as motion modeling or state estimation in robotics and
    related applications.

    :ivar twist: The twist, including linear and angular components.
    :type twist: Twist
    :ivar covariance: The covariance matrix associated with the twist.
    :type covariance: np.ndarray
    """
    twist: Twist
    covariance: np.ndarray


# .... Odometry messages ..........................................................................
@dataclass()
class NavMsgsOdometry(RosStampedDataclass):
    """ Data container for navigation messages odometry (nested data container version).

    Compatible ros2 message interface: nav_msgs/msg/Odometry

    This class serves as a structured container for navigation message data related to odometry
    in ROS. It captures the pose and twist information along with their covariance data. The
    purpose of this container is to facilitate organized and consistent handling of these
    odometry-related data structures. Useful in systems where readability and maintainability of
    the navigation-related data are critical.

    :ivar pose: Contains the pose along with its associated covariance information.
    :type pose: PoseWithCovariance
    :ivar twist: Contains the twist along with its associated covariance information.
    :type twist: TwistWithCovariance
    """
    pose: PoseWithCovariance
    twist: TwistWithCovariance


@dataclass()
class NavMsgsOdometryFlat(RosStampedDataclass):
    """ Data container for navigation messages odometry (flat structure data container version).

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


# .... Command messages ...........................................................................
@dataclass()
class AckermannMsgsAckermannDrive(NestedBaseTrajectoryDataclass):
    """
    Represents the desired Ackermann drive trajectory parameters with specified
    steering angle, velocity, speed, acceleration, and jerk.

    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDrive

    :ivar steeringAngle: Desired virtual steering angle in radians.
    :type steeringAngle: numpy.ndarray
    :ivar steeringAngleVelocity: Desired rate of change of steering angle in radians per second.
    :type steeringAngleVelocity: numpy.ndarray
    :ivar speed: Desired forward speed in meters per second.
    :type speed: numpy.ndarray
    :ivar acceleration: Desired acceleration in meters per second squared.
    :type acceleration: numpy.ndarray
    :ivar jerk: Desired jerk in meters per second cubed.
    :type jerk: numpy.ndarray
    """
    steeringAngle: np.ndarray  # desired virtual angle (radians)
    steeringAngleVelocity: np.ndarray  # desired rate of change (radians/s)
    speed: np.ndarray  # desired forward speed (m/s)
    acceleration: np.ndarray  # desired acceleration (m/s^2)
    jerk: np.ndarray  # desired jerk (m/s^3)


@dataclass()
class AckermannMsgsAckermannDriveStamped(RosStampedDataclass):
    """
    Represents a stamped message for an Ackermann drive message.

    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDriveStamped

    This class is used to wrap an `AckermannMsgsAckermannDrive` message with a
    timestamp and frame ID information for use in robotic systems.

    :ivar drive: The Ackermann drive message containing driving instructions
        such as speed and steering angle.
    :type drive: AckermannMsgsAckermannDrive
    """
    drive: AckermannMsgsAckermannDrive


@dataclass()
class AckermannMsgsAckermannDriveStampedFlat(RosStampedDataclass):
    """ AckermannMsgsAckermannDriveStamped flat version
    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDriveStamped
    """
    drive_steeringAngle: np.ndarray  # desired virtual angle (radians)
    drive_steeringAngleVelocity: np.ndarray  # desired rate of change (radians/s)
    drive_speed: np.ndarray  # desired forward speed (m/s)
    drive_acceleration: np.ndarray  # desired acceleration (m/s^2)
    drive_jerk: np.ndarray  # desired jerk (m/s^3)


# .... TF messages ................................................................................
@dataclass()
class Tf2MsgsTFMessage(RosStampedDataclass):
    """ Represents a message used in coordinate transformation tasks in ROS.

    Compatible ros2 message interface: tf2_msgs/msg/TFMessage

    This dataclass encapsulates information about a transformation (e.g., translation,
    rotation) for a specific frame in the ROS ecosystem. It is used specifically
    to store messages that relate to frame IDs and their associated transformations.

    :ivar childFrameId: Identifier for the child frame to which the transformation applies.
    :type childFrameId: str
    :ivar transform: Transformation data for the specified child frame, containing
        translation and rotation information.
    :type transform: Transform
    """
    childFrameId: str
    transform: Transform


# .... Sensor messages ............................................................................
@dataclass()
class Scan(RosStampedDataclass):
    """ Represents a LaserScan message containing range and intensity data.

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
    angleMin: float # [rad]
    angleMax: float # [rad]
    angleIncrement: float # [rad]
    timeIncrement: float # [seconds]
    scanTime: float # [seconds]
    rangeMin: float # [m]
    rangeMax: float # [m]
    ranges: np.ndarray # multi-dimensional ndarray [m]
    intensities: np.ndarray # multi-dimensional ndarray [device-specific units]


@dataclass()
class SensorMsgsImu(RosStampedDataclass):
    """ Represents IMU (Inertial Measurement Unit) sensor data with orientation,
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


@dataclass()
class SensorMsgsImuFlat(RosStampedDataclass):
    """ SensorMsgsImu flat version

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
