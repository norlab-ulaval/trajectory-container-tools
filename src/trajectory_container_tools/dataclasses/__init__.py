# coding=utf-8
"""
Trajectory dataclasses for different data sources and formats.

Available dataclasses:
- ROS2 message types (NavMsgsOdometry, SensorMsgsImu, etc.)
- Generic containers (BaseTrajectoryDataclass, etc.)
- Primitive containers (Point2D, Vector2D, Pose2D, etc.)
- Simulation environments (F110Gym, MathGymnasium, etc.)

Usage example:

>>> import trajectory_container_tools as tct
>>> odom_class = tct.dataclasses.NavMsgsOdometry
>>> imu_class = tct.dataclasses.ros_msgs.stamped_dataclass.SensorMsgsImu

"""

# Abstract base classes and base classes
from trajectory_container_tools.dataclasses.core import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass,
    AbstractMultifeatureStampedDataclass,
    AbstractNoTrajectoryDataclass,
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
    BaseNoTrajectoryDataclass,
)


# ROS2 dataclasses
from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    Tf2MsgsTFMessage,
)
from .ros_msgs.stamped_dataclass import (
    AckermannMsgsAckermannDriveStamped,
    NavMsgsOdometry,
    Scan,
    SensorMsgsImu,
    VescMsgsVescImuStamped,
)
from .ros_msgs.nested_dataclass import AckermannMsgsAckermannDrive
from .ros_msgs.core_dataclass import (
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import Header

# Simulation environment dataclasses
from .f110_gym_trajectory_dataclass import (
    F110MotionDynamicDataclass,
    F110MotionDynamicDataclassNested,
    F110observations,
    F110actions,
)
from .math_gymnasium_trajectory_dataclass import (
    MathEnvTrajectoryDataclass,
    StateAxDataclass,
    TimeAxDataclass,
    AxBaseDataclass,
)
from .erll_trajectory_dataclass import (
    TestTrajectoryDataclass,
    TestMotionTrajectoryDataclass,
)

# DataFrame dataclasses
from .panda_dataframe_feature_dataclass import (
    BaseDataframeFeatureDataclass,
    NestedBaseDataframeFeatureDataclass,
    StatePose2D,
    CmdStandard,
    CmdSkidSteer,
    Velocity,
    VelocitySkidSteer,
)

# Primitive types
from .primitive_dataclass import (
    Point2D,
    Vector2D,
    Pose2D,
    Velocity2D,
    Pose2DSA,
    Point2DSA,
    Vector2DSA,
    Velocity2DSA,
)

__all__ = [
    # Abstract classes
    "AbstractTrajectoryDataclass",
    "AbstractNoTrajectoryDataclass",
    "AbstractMultifeatureDataclass",
    "AbstractMultifeatureStampedDataclass",
    # Base classes
    "BaseTrajectoryDataclass",
    "NestedBaseTrajectoryDataclass",
    "BaseNoTrajectoryDataclass",
    # ROS2 dataclasses
    "NavMsgsOdometry",
    "SensorMsgsImu",
    "AckermannMsgsAckermannDriveStamped",
    "AckermannMsgsAckermannDrive",
    "Tf2MsgsTFMessage",
    "VescMsgsVescImuStamped",
    "Scan",
    "RosStampedDataclass",
    "RosDataclass",
    "NestedRosStampedDataclass",
    "Header",
    # Simulation environments
    "F110MotionDynamicDataclass",
    "F110MotionDynamicDataclassNested",
    "F110observations",
    "F110actions",
    "MathEnvTrajectoryDataclass",
    "StateAxDataclass",
    "TimeAxDataclass",
    "AxBaseDataclass",
    "TestTrajectoryDataclass",
    "TestMotionTrajectoryDataclass",
    # DataFrame
    "BaseDataframeFeatureDataclass",
    "NestedBaseDataframeFeatureDataclass",
    "StatePose2D",
    "CmdStandard",
    "CmdSkidSteer",
    "Velocity",
    "VelocitySkidSteer",
    # Primitives
    "Point2D",
    "Vector2D",
    "Pose2D",
    "Velocity2D",
    "Point2DSA",
    "Vector2DSA",
    "Pose2DSA",
    "Velocity2DSA",
]
