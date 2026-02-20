# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import BaseTrajectoryFeature
from trajectory_container_tools.temporal.timestamps import Timestamps
from trajectory_container_tools.utils.typing.tct_custom_field import ContainerInternalField


# /////////////////////////////////////////////////////////////////////////////////////////////////
# Note: nested trajectory-dataclass is not yet supported for dataframe extraction.
#       Use flat layout in the mean time
# /////////////////////////////////////////////////////////////////////////////////////////////////


@dataclass()
class BaseDataframeFeatureDataclass(BaseTrajectoryFeature):
    """
    Represents a dataclass for handling trajectory data fetched from a Panda dataframe.

    It can be extended or utilized wherever structured data for dataframe processing or
    trajectory computation is necessary.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    """

    pass

@dataclass()
class BaseDataframeStampedFeatureDataclass(BaseDataframeFeatureDataclass):
    """
    Summary of what the class does.

    The `BaseDataframeStampedFeatureDataclass` is a specialized dataclass that
    extends the functionality of the `BaseDataframeFeatureDataclass`. Its purpose is
    to include and validate time-stamped features within the dataclass. This is done
    through seamless integration of timestamp management and causal ordering checks.

    :ivar feature_name: Name of the feature associated with the trajectory.
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :ivar timestamps: The timestamps associated with the dataframe features. If
        provided as a numpy array, it will be converted to a `Timestamps` object.
    :type timestamps: Union[Timestamps, np.ndarray]
    """
    timestamps: Union[Timestamps, np.ndarray] = field(
        default=None, kw_only=True
    )

    def on_begin_post_init_callback(self) -> None:
        if self.timestamps is not None:
            if isinstance(self.timestamps, np.ndarray):
                self.timestamps = Timestamps(self.timestamps)

            self.timestamps.causal_ordering_sanity_check(
                show_offending_in_nanoseconds=True,
                fail_causal_ordering_violation=self.fail_causal_ordering_violation,
            )

@dataclass()
class NestedBaseDataframeFeatureDataclass(BaseDataframeFeatureDataclass):
    """
    Represents a nested base feature dataclass for dataframe-related operations.

    This class is intended to serve as a specialization of `BaseDataframeFeatureDataclass`.
    Currently, it does not support nested trajectory dataclass functionality for dataframe
    extraction. It includes the `feature_name` attribute to store a unique identifier for the
    feature instance. The `on_begin_post_init_callback` method remains unimplemented and raises
    a `NotImplementedError` when invoked.

    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :ivar feature_name: The name of the feature, automatically assigned during initialization.
    :type feature_name: ContainerInternalField[Optional[str]]
    """

    # (NICE TO HAVE) ToDo: implement nested trajectory-dataclass support for dataframe extraction

    feature_name: ContainerInternalField[Optional[str]] = field(default=None, init=False)

    def on_begin_post_init_callback(self):
        raise NotImplementedError(
            "Nested trajectory for dataframe is not supported yet."
        )


@dataclass()
class StatePose2D(BaseDataframeFeatureDataclass):
    """
    Represents the pose state in a 2D coordinate system.

    This dataclass encapsulates the positional ('x', 'y') and angular ('yaw')
    components of pose data in a 2-dimensional space. It serves as a flexible
    and compact container for storing and processing 2D pose-related data,
    typically used in robotics, computer vision, or simulation environments.

    :ivar x: The x-coordinate of the pose in the 2D coordinate frame.
    :type x: np.ndarray
    :ivar y: The y-coordinate of the pose in the 2D coordinate frame.
    :type y: np.ndarray
    :ivar yaw: The rotational angle (in radians) of the pose in the 2D coordinate
        frame.
    :type yaw: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray

@dataclass()
class StatePose2DStamped(BaseDataframeStampedFeatureDataclass):
    """
    Represents the pose state in a 2D coordinate system.

    This dataclass encapsulates the positional ('x', 'y') and angular ('yaw')
    components of pose data in a 2-dimensional space along with timestamps. It serves as a flexible
    and compact container for storing and processing 2D pose-related data,
    typically used in robotics, computer vision, or simulation environments.

    :ivar x: The x-coordinate of the pose in the 2D coordinate frame.
    :type x: np.ndarray
    :ivar y: The y-coordinate of the pose in the 2D coordinate frame.
    :type y: np.ndarray
    :ivar yaw: The rotational angle (in radians) of the pose in the 2D coordinate
        frame.
    :type yaw: np.ndarray
    """

    x: np.ndarray
    y: np.ndarray
    yaw: np.ndarray

@dataclass()
class CmdStandard(BaseDataframeFeatureDataclass):
    """
    Represents a command structure containing linear and angular velocities.

    This dataclass is designed to encapsulate linear and angular velocity
    commands, providing a structured format for data storage and processing.

    :ivar linear_vel: Array containing linear velocity components.
    :type linear_vel: np.ndarray
    :ivar angular_vel: Array containing angular velocity components.
    :type angular_vel: np.ndarray
    """

    linear_vel: np.ndarray
    angular_vel: np.ndarray


@dataclass()
class CmdSkidSteer(BaseDataframeFeatureDataclass):
    """
    Represents commands for a skid steer mechanism, encapsulating left and right motor commands
    to control movement.

    This class is designed to hold and manage the values for left and right motor commands
    within a dataframe-like structure that facilitates operations and transformations.

    :ivar left: The array of commands for the left motor.
    :type left: numpy.ndarray
    :ivar right: The array of commands for the right motor.
    :type right: numpy.ndarray
    """

    left: np.ndarray
    right: np.ndarray


@dataclass()
class Velocity(CmdStandard):
    """
    Represents velocity commands used in standard command operations.

    This class serves as an extension of the CmdStandard class, inheriting its
    properties and functionalities. It is meant to be utilized in contexts
    where velocity command parameters are required, aligning with the structure
    and behavior of standard command implementations.

    :ivar linear_vel: Array containing linear velocity components.
    :type linear_vel: np.ndarray
    :ivar angular_vel: Array containing angular velocity components.
    :type angular_vel: np.ndarray
    """

    pass


@dataclass()
class VelocitySkidSteer(CmdSkidSteer):
    """
    Represents velocity commands for a skid steer robot.

    This class is a data structure derived from CmdSkidSteer and is used to
    define velocity-based control commands for skid steer robots. It
    encapsulates the data necessary to specify the velocity of each track
    or wheel, facilitating the control mechanisms in robotics applications.

    :ivar left: The array of commands for the left motor.
    :type left: numpy.ndarray
    :ivar right: The array of commands for the right motor.
    :type right: numpy.ndarray
    """

    pass
