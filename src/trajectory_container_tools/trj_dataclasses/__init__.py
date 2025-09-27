# coding=utf-8
"""
Trajectory dataclasses for different data sources and formats.

Available dataclasses:
- ROS2 message types (NavMsgsOdometry, SensorMsgsImu, etc.)
- Simulation environments (F110Gym, MathGymnasium, etc.) 
- Generic containers (BaseTrajectoryDataclass, etc.)

Usage:
    import trajectory_container_tools as tct
    odom_class = tct.dataclasses.NavMsgsOdometry
    imu_class = tct.dataclasses.SensorMsgsImu
"""

# Abstract base classes
from .abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass
)

# Base implementations
from .base_trajectory_dataclass import (
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass
)

# ROS2 dataclasses
from .ros2_feature_dataclass import (
    NavMsgsOdometry,
    SensorMsgsImu,
    AckermannMsgsAckermannDriveStamped,
    AckermannMsgsAckermannDrive,
    Tf2MsgsTFMessage,
    VescMsgsVescImuStamped,
    Scan,
    RosStampedDataclass,
    RosDataclass,
    NestedRosStampedDataclass
)

from .ros2_primitive_dataclass import Header

# Simulation environment dataclasses  
from .f110_gym_trajectory_dataclass import (
    F110MotionDynamicDataclass,
    F110MotionDynamicDataclassNested,
    F110observations,
    F110actions
)
from .math_gymnasium_trajectory_dataclass import (
    MathEnvTrajectoryDataclass,
    StateAxDataclass,
    TimeAxDataclass,
    AxBaseDataclass
)
from .erll_trajectory_dataclass import (
    TestTrajectoryDataclass,
    TestMotionTrajectoryDataclass
)

# DataFrame dataclasses
from .panda_dataframe_feature_dataclass import (
    BaseDataframeFeatureDataclass,
    NestedBaseDataframeFeatureDataclass,
    StatePose2D,
    CmdStandard,
    CmdSkidSteer,
    Velocity,
    VelocitySkidSteer
)

# Primitive types
from .primitive_dataclass import (
    Point2D,
    Vector2D,
    Pose2D,
    Velocity2D
)

__all__ = [
    # Abstract classes
    'AbstractTrajectoryDataclass',
    'AbstractMultifeatureDataclass',
    
    # Base classes
    'BaseTrajectoryDataclass', 
    'NestedBaseTrajectoryDataclass',
    
    # ROS2 dataclasses
    'NavMsgsOdometry',
    'SensorMsgsImu', 
    'AckermannMsgsAckermannDriveStamped',
    'AckermannMsgsAckermannDrive',
    'Tf2MsgsTFMessage',
    'VescMsgsVescImuStamped',
    'Scan',
    'RosStampedDataclass',
    'RosDataclass',
    'NestedRosStampedDataclass',
    'Header',
    
    # Simulation environments
    'F110MotionDynamicDataclass',
    'F110MotionDynamicDataclassNested',
    'F110observations',
    'F110actions',
    'MathEnvTrajectoryDataclass',
    'StateAxDataclass',
    'TimeAxDataclass',
    'AxBaseDataclass',
    'TestTrajectoryDataclass',
    'TestMotionTrajectoryDataclass',
    
    # DataFrame
    'BaseDataframeFeatureDataclass',
    'NestedBaseDataframeFeatureDataclass',
    'StatePose2D',
    'CmdStandard',
    'CmdSkidSteer',
    'Velocity',
    'VelocitySkidSteer',
    
    # Primitives
    'Point2D',
    'Vector2D',
    'Pose2D',
    'Velocity2D',
]
