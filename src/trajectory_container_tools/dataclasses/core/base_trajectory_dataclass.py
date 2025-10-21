# coding=utf-8
import abc
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
from deprecated import deprecated

from .abstract_trajectory_feature_dataclass import (
    AbstractTrajectoryFeature,
)
from .abstract_trajectory_array_dataclass import (
    AbstractTrajectoryArray,
)


@dataclass()
class BaseTrajectoryFeature(AbstractTrajectoryFeature):
    """
    Represents a base trajectory data structure.

    This class is intended to serve as a base class for specialized trajectory dataclasses,
    providing core functionalities and attributes to manage data related to trajectories. It
    builds upon the abstract trajectory dataclass and can be extended further to meet specific
    requirements.

    **Usage example**:

    Note: this example would represent a flat data representation as oposed to a nested one

    >>> @dataclass()
    >>> class MockContainer(BaseTrajectoryFeature):
    >>>     timestamps: np.ndarray
    >>>     position_x: np.ndarray
    >>>     position_y: np.ndarray
    >>>     position_z: np.ndarray

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    pass


@deprecated(
    reason="NestedBaseTrajectory dataclass is deprecated now that all TrajectoryFeature dataclass "
           "support parent container reference tracking. Use `is_nested()` method to test if a "
           "trajectory dataclass is nested or not."
)
@dataclass()
class NestedBaseTrajectory(BaseTrajectoryFeature):
    """
    Represents a nested base trajectory dataclass which extends the functionality of the
    ``BaseTrajectoryDataclass``.

    This class summarizes the concept of a derived dataclass with specific attributes associated
    with nested trajectory-related features.

    **Usage example**:

    1. Define the nested trajectory container

    >>> @dataclass()
    >>> class MockNestedContainer(NestedBaseTrajectory):
    >>>     x: np.ndarray
    >>>     y: np.ndarray
    >>>     z: np.ndarray

    2. Define the main trajectory container

    >>> @dataclass()
    >>> class MockContainer(BaseTrajectoryFeature):
    >>>     timestamps: np.ndarray
    >>>     position: MockNestedContainer

    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    pass


@dataclass()
class BaseTrajectoryFeatureArray(
    AbstractTrajectoryArray
):
    """
    Represents a base data structure without trajectory handling.

    This class inherits from ``AbstractTrajectoryArray`` and serves as
    a foundation for non-trajectory-based data classes. It is designed to hold
    and manage data that does not involve trajectory-specific information at top-level but might
    in nested ones e.g., `Tf2MsgsTFMessage.transforms` a list of `GeometryMsgsTransformStampedFeature` trj container

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    """

    pass
