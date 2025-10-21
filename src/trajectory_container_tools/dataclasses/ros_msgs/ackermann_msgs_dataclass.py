# coding=utf-8
from dataclasses import dataclass

import numpy as np

from .core_dataclass import RosFeature, RosStampedFeature


# .... Ackermann msgs .............................................................................
@dataclass()
class AckermannMsgsAckermannDrive(RosFeature):
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


# .... Vesc msgs ..................................................................................
@dataclass()
class AckermannMsgsAckermannDriveStamped(RosStampedFeature):
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
