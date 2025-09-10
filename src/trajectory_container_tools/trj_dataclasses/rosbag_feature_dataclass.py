# coding=utf-8
from dataclasses import dataclass, field

import numpy as np

from .base_trajectory_dataclass import BaseTrajectoryDataclass, NestedBaseTrajectoryDataclass
from .primitive_dataclass import Header, Point, Quaternion


@dataclass()
class RosBagFeatureDataclass(BaseTrajectoryDataclass):
    header: Header

    @property
    def _init_trj_axe(self) -> int:
        return 0


@dataclass()
class Pose(NestedBaseTrajectoryDataclass):
    """ Represents the pose of an object in 3D space.

    Compatible ros2 message interface: geometry_msgs/msg/Pose

    This class models the translational and rotational parameters of an object's pose in a
    three-dimensional coordinate system. The translational components are represented by the
    `position_x`, `position_y`, and `position_z` attributes, corresponding to the x, y,
    and z axes respectively. The rotational components are represented by the quaternion values
    `orientation_x`, `orientation_y`, `orientation_z`, and `orientation_w`.

    :ivar position_x: Array representing the x-coordinate(s) of the object's position.
    :type position_x: np.ndarray
    :ivar position_y: Array representing the y-coordinate(s) of the object's position.
    :type position_y: np.ndarray
    :ivar position_z: Array representing the z-coordinate(s) of the object's position.
    :type position_z: np.ndarray
    :ivar orientation_x: Array representing the x-component(s) of the object's orientation
    quaternion.
    :type orientation_x: np.ndarray
    :ivar orientation_y: Array representing the y-component(s) of the object's orientation
    quaternion.
    :type orientation_y: np.ndarray
    :ivar orientation_z: Array representing the z-component(s) of the object's orientation
    quaternion.
    :type orientation_z: np.ndarray
    :ivar orientation_w: Array representing the w-component(s) of the object's orientation
    quaternion.
    :type orientation_w: np.ndarray
    """
    position_x: np.ndarray
    position_y: np.ndarray
    position_z: np.ndarray
    orientation_x: np.ndarray
    orientation_y: np.ndarray
    orientation_z: np.ndarray
    orientation_w: np.ndarray
    # position: Point
    # orientation: Quaternion



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
    """ Represents a dataclass for trajectory containing linear and angular velocity components.

    Compatible ros2 message interface: geometry_msgs/msg/Twist

    The `Twist` class is used to encapsulate the movement information for trajectories in terms
    of linear and angular velocity  components along x, y, and z axes.

    :ivar linear_x: Linear velocity component along the x-axis.
    :type linear_x: np.ndarray
    :ivar linear_y: Linear velocity component along the y-axis.
    :type linear_y: np.ndarray
    :ivar linear_z: Linear velocity component along the z-axis.
    :type linear_z: np.ndarray
    :ivar angular_x: Angular velocity component along the x-axis.
    :type angular_x: np.ndarray
    :ivar angular_y: Angular velocity component along the y-axis.
    :type angular_y: np.ndarray
    :ivar angular_z: Angular velocity component along the z-axis.
    :type angular_z: np.ndarray
    """
    linear_x: np.ndarray
    linear_y: np.ndarray
    linear_z: np.ndarray
    angular_x: np.ndarray
    angular_y: np.ndarray
    angular_z: np.ndarray


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
class NavMsgsOdometry(RosBagFeatureDataclass):
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
class NavMsgsOdometryFlat(RosBagFeatureDataclass):
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
class AckermannMsgsAckermannDriveStamped(RosBagFeatureDataclass):
    """
    Compatible ros2 message interface: ackermann_msgs/msg/AckermannDriveStamped
    """
    drive_steeringAngle: np.ndarray
    drive_steeringAngleVelocity: np.ndarray
    drive_speed: np.ndarray
    drive_acceleration: np.ndarray
    drive_jerk: np.ndarray


@dataclass()
class AckermannMsgsAckermannDriveStampedMinimal(RosBagFeatureDataclass):
    drive_steeringAngle: np.ndarray
    drive_steeringAngleVelocity: np.ndarray
    drive_speed: np.ndarray


# .... TF messages ................................................................................
@dataclass()
class Tf2MsgsTFMessage(RosBagFeatureDataclass):
    """
    Compatible ros2 message interface: tf2_msgs/msg/TFMessage
    """
    childFrameId: str
    transform_translation_x: np.ndarray
    transform_translation_y: np.ndarray
    transform_translation_z: np.ndarray
    transform_rotation_x: np.ndarray
    transform_rotation_y: np.ndarray
    transform_rotation_z: np.ndarray
    transform_rotation_w: np.ndarray


# .... Sensor messages ............................................................................
@dataclass()
class SensorMsgsImu(RosBagFeatureDataclass):
    """
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
