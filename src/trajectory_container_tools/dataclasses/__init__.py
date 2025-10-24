# coding=utf-8
"""
Trajectory dataclasses for different data sources and formats.

Available dataclasses:
- ROS2 message types (NavMsgsOdometry, SensorMsgsImu, etc.)
- Generic containers (BaseTrajectoryFeature, etc.)
- Primitive containers (Point2D, Vector2D, Pose2D, etc.)
- Simulation environments (F110Gym, MathGymnasium, etc.)

Usage example:

>>> import trajectory_container_tools as tct
>>> odom_class = tct.dataclasses.NavMsgsOdometry
or
>>> odom_class = tct.dataclasses.ros_msgs.nav_msgs_dataclass.NavMsgsOdometry

"""
__all__ = []

# .... Abstract base classes and base classes .....................................................
from trajectory_container_tools.dataclasses.core import (
    AbstractTrajectoryFeature,
    AbstractTrajectoryFeaturesBag,
    AbstractTrajectoryStampedFeaturesBag,
    AbstractTrajectoryUnboundedArray,
    BaseTrajectoryFeature,
    BaseTrajectoryFeatureUnboundedArray,
)

__all__ += [
    "AbstractTrajectoryFeature",
    "AbstractTrajectoryFeaturesBag",
    "AbstractTrajectoryStampedFeaturesBag",
    "AbstractTrajectoryUnboundedArray",
    "BaseTrajectoryFeature",
    "BaseTrajectoryFeatureUnboundedArray",
]

# .... ROS2 dataclasses ...........................................................................
from trajectory_container_tools.dataclasses.ros_msgs.tf_dataclass import (
    Tf2MsgsTFMessage,
)
from .ros_msgs.sensor_msgs_dataclass import (
    SensorMsgsLaserScan,
    SensorMsgsImu,
    )
from .ros_msgs.nav_msgs_dataclass import NavMsgsOdometry
from .ros_msgs.ackermann_msgs_dataclass import (
    AckermannMsgsAckermannDrive, AckermannMsgsAckermannDriveStamped,
    )
from .ros_msgs.vesc_msgs_dataclass import VescMsgsVescImu, VescMsgsVescImuStamped
from .ros_msgs.core_dataclass import (
    RosFeature,
    RosStampedFeature,
    RosFeatureArray,
)

from trajectory_container_tools.dataclasses.ros_msgs.geometry_msgs_dataclass import (
    GeometryMsgsPoint,
    GeometryMsgsPose, GeometryMsgsPoseStamped, GeometryMsgsPoseWithCovariance,
    GeometryMsgsPoseWithCovarianceStamped, GeometryMsgsTransformStampedFeature,
    GeometryMsgsTwist, GeometryMsgsTwistStamped, GeometryMsgsTwistWithCovariance,
    GeometryMsgsTwistWithCovarianceStamped, GeometryMsgsVector3,
    GeometryMsgsVector3Stamped,
    GeometryMsgsPointStamped,
    GeometryMsgsQuaternion,
    GeometryMsgsTransform,
)
from .ros_msgs.std_msgs_dataclass import StdMsgsHeader

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
    "GeometryMsgsTransformStampedFeature",
    "RosFeatureArray",
    "RosFeature",
    "RosStampedFeature",
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

