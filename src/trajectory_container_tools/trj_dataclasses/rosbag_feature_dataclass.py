# coding=utf-8
from dataclasses import dataclass, field

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass
from .base_trajectory_dataclass import BaseTrajectoryDataclass


@dataclass()
class RosBagFeatureDataclass(AbstractTrajectoryDataclass):
    header_FrameId: str
    timestamps: np.ndarray

    @property
    def _init_trj_axe(self) -> int:
        return 0

@dataclass()
class Pose(BaseTrajectoryDataclass):
    position_x: np.ndarray
    position_y: np.ndarray
    position_z: np.ndarray
    orientation_x: np.ndarray
    orientation_y: np.ndarray
    orientation_z: np.ndarray
    orientation_w: np.ndarray
    # feature_name: str = field(default="Nested Pose", init=False)

@dataclass()
class PoseWithCovariance(BaseTrajectoryDataclass):
    pose: Pose
    covariance: np.ndarray
#     # feature_name: str = field(default="geometry_msgs/PoseWithCovariance", init=False)
#     feature_name: str = field(default="Nested PoseWithCovariance", init=False)

@dataclass()
class Twist(BaseTrajectoryDataclass):
    linear_x: np.ndarray
    linear_y: np.ndarray
    linear_z: np.ndarray
    angular_x: np.ndarray
    angular_y: np.ndarray
    angular_z: np.ndarray
#     feature_name: str = field(default="Nested Twist", init=False)

@dataclass()
class TwistWithCovariance(BaseTrajectoryDataclass):
    twist: Twist
    covariance: np.ndarray
#     # feature_name: str = field(default="geometry_msgs/TwistWithCovariance", init=False)
#     feature_name: str = field(default="Nested TwistWithCovariance", init=False)


# (CRITICAL) New version ToDo: on task end >> UN-MUTE next bloc ↓↓
@dataclass()
class NavMsgsOdometry(RosBagFeatureDataclass):
    pose: PoseWithCovariance
    twist: TwistWithCovariance


# # (CRITICAL) Legacy version ToDo: on task end >> delete next bloc ↓↓
# @dataclass()
# class NavMsgsOdometry(RosBagFeatureDataclass):
#     pose_pose_position_x: np.ndarray
#     pose_pose_position_y: np.ndarray
#     pose_pose_position_z: np.ndarray
#     pose_pose_orientation_x: np.ndarray
#     pose_pose_orientation_y: np.ndarray
#     pose_pose_orientation_z: np.ndarray
#     pose_pose_orientation_w: np.ndarray
#     pose_covariance: np.ndarray
#     twist_twist_linear_x: np.ndarray
#     twist_twist_linear_y: np.ndarray
#     twist_twist_linear_z: np.ndarray
#     twist_twist_angular_x: np.ndarray
#     twist_twist_angular_y: np.ndarray
#     twist_twist_angular_z: np.ndarray
#     twist_covariance: np.ndarray


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


@dataclass()
class SensorMsgsImu(RosBagFeatureDataclass):
    # (Priority) ToDo: implement and test >> manage case 'orientation_covariance'
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
