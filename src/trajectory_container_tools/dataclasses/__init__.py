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
__all__ = []

# .... Abstract base classes and base classes .....................................................
from trajectory_container_tools.dataclasses.core import (
    AbstractTrajectoryDataclass,
    AbstractMultifeatureDataclass,
    AbstractMultifeatureStampedDataclass,
    AbstractNoTrajectoryDataclass,
    BaseTrajectoryDataclass,
    NestedBaseTrajectoryDataclass,
    BaseNoTrajectoryDataclass,
)

__all__ += [
    "AbstractTrajectoryDataclass",
    "AbstractMultifeatureDataclass",
    "AbstractMultifeatureStampedDataclass",
    "AbstractNoTrajectoryDataclass",
    "BaseTrajectoryDataclass",
    "NestedBaseTrajectoryDataclass",
    "BaseNoTrajectoryDataclass",
]

# .... ROS2 dataclasses ...........................................................................
from trajectory_container_tools.dataclasses.ros_msgs.non_trajectory_dataclass import (
    Tf2MsgsTFMessage,
)
from .ros_msgs.stamped_dataclass import (
    NavMsgsOdometry,
    AckermannMsgsAckermannDriveStamped,
    SensorMsgsLaserScan,
    VescMsgsVescImuStamped,
    SensorMsgsImu,
    GeometryMsgsPoseStamped,
    GeometryMsgsPoseWithCovarianceStamped,
    GeometryMsgsTwistStamped,
    GeometryMsgsTwistWithCovarianceStamped,
)
from .ros_msgs.nested_dataclass import (
    GeometryMsgsPose,
    GeometryMsgsPoseWithCovariance,
    GeometryMsgsTwist,
    GeometryMsgsTwistWithCovariance,
    AckermannMsgsAckermannDrive,
    VescMsgsVescImu,
    GeometryMsgsTransformStamped,
)
from .ros_msgs.core_dataclass import (
    NestedRosStampedDataclass,
    RosDataclass,
    RosStampedDataclass,
)

from trajectory_container_tools.dataclasses.ros_msgs.primitive_dataclass import (
    StdMsgsHeader,
    GeometryMsgsPoint,
    GeometryMsgsVector3,
    GeometryMsgsVector3Stamped,
    GeometryMsgsPointStamped,
    GeometryMsgsQuaternion,
    GeometryMsgsTransform,
)

__all__ += [
    "Tf2MsgsTFMessage",
    "NavMsgsOdometry",
    "AckermannMsgsAckermannDriveStamped",
    "SensorMsgsLaserScan",
    "VescMsgsVescImuStamped",
    "SensorMsgsImu",
    "GeometryMsgsPoseStamped",
    "GeometryMsgsPoseWithCovarianceStamped",
    "GeometryMsgsTwistStamped",
    "GeometryMsgsTwistWithCovarianceStamped",
    "GeometryMsgsPose",
    "GeometryMsgsPoseWithCovariance",
    "GeometryMsgsTwist",
    "GeometryMsgsTwistWithCovariance",
    "AckermannMsgsAckermannDrive",
    "VescMsgsVescImu",
    "GeometryMsgsTransformStamped",
    "NestedRosStampedDataclass",
    "RosDataclass",
    "RosStampedDataclass",
    "StdMsgsHeader",
    "GeometryMsgsPoint",
    "GeometryMsgsVector3",
    "GeometryMsgsVector3Stamped",
    "GeometryMsgsPointStamped",
    "GeometryMsgsQuaternion",
    "GeometryMsgsTransform",
]

# .... Simulation environment dataclasses .........................................................
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

__all__ += [
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
]

# .... DataFrame dataclasses ......................................................................
from .panda_dataframe_feature_dataclass import (
    BaseDataframeFeatureDataclass,
    NestedBaseDataframeFeatureDataclass,
    StatePose2D,
    CmdStandard,
    CmdSkidSteer,
    Velocity,
    VelocitySkidSteer,
)

__all__ += [
    "BaseDataframeFeatureDataclass",
    "NestedBaseDataframeFeatureDataclass",
    "StatePose2D",
    "CmdStandard",
    "CmdSkidSteer",
    "Velocity",
    "VelocitySkidSteer",
]

# .... Primitive types ............................................................................
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

__all__ += [
    "Point2D",
    "Vector2D",
    "Pose2D",
    "Velocity2D",
    "Pose2DSA",
    "Point2DSA",
    "Vector2DSA",
    "Velocity2DSA",
]

