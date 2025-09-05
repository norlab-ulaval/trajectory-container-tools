# coding=utf-8
from dataclasses import dataclass, field

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass
from .base_trajectory_dataclass import BaseTrajectoryDataclass, NestedBaseTrajectoryDataclass


@dataclass()
class RosBagFeatureDataclass(BaseTrajectoryDataclass):
    """ Represents RosBag feature data attributes and related metadata.

    This data class is designed to hold attributes related to RosBag features, including frame
    identifiers and time stamps, for trajectory processing.

    :ivar header_FrameId: Identifier of the frame associated with the data.
    :type header_FrameId: str
    :ivar timestamps: Array of timestamps associated with the trajectory data.
    :type timestamps: numpy.ndarray
    """
    header_FrameId: str
    timestamps: np.ndarray

    @property
    def _init_trj_axe(self) -> int:
        return 0


@dataclass()
class Pose(NestedBaseTrajectoryDataclass):
    position_x: np.ndarray
    position_y: np.ndarray
    position_z: np.ndarray
    orientation_x: np.ndarray
    orientation_y: np.ndarray
    orientation_z: np.ndarray
    orientation_w: np.ndarray


@dataclass()
class PoseWithCovariance(NestedBaseTrajectoryDataclass):
    pose: Pose
    covariance: np.ndarray


@dataclass()
class Twist(NestedBaseTrajectoryDataclass):
    linear_x: np.ndarray
    linear_y: np.ndarray
    linear_z: np.ndarray
    angular_x: np.ndarray
    angular_y: np.ndarray
    angular_z: np.ndarray


@dataclass()
class TwistWithCovariance(NestedBaseTrajectoryDataclass):
    twist: Twist
    covariance: np.ndarray


# .... Odometry messages ..........................................................................
@dataclass()
class NavMsgsOdometry(RosBagFeatureDataclass):
    """ Data container for navigation messages odometry (nested data container version).

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
