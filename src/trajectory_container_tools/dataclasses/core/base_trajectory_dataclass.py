# coding=utf-8
import abc
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np

from .abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
)
from .abstract_no_trajectory_dataclass import AbstractNoTrajectoryDataclass


@dataclass()
class BaseTrajectoryDataclass(AbstractTrajectoryDataclass):
    """Represents a base trajectory data structure.

    This class is intended to serve as a base class for specialized trajectory dataclasses,
    providing core functionalities and attributes to manage data related to trajectories. It
    builds upon the abstract trajectory dataclass and can be extended further to meet specific
    requirements.

    **Usage example**:

    Note: this example would represent a flat data representation as oposed to a nested one
    (see ``NestedBaseTrajectoryDataclass`` usage example).

    >>> @dataclass()
    >>> class MockContainer(BaseTrajectoryDataclass):
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


@dataclass()
class NestedBaseTrajectoryDataclass(BaseTrajectoryDataclass):
    """Represents a nested base trajectory dataclass which extends the functionality of the
    ``BaseTrajectoryDataclass``.

    This class summarizes the concept of a derived dataclass with specific attributes associated
    with nested trajectory-related features.

    **Usage example**:

    1. Define the nested trajectory container

    >>> @dataclass()
    >>> class MockNestedContainer(NestedBaseTrajectoryDataclass):
    >>>     x: np.ndarray
    >>>     y: np.ndarray
    >>>     z: np.ndarray

    2. Define the main trajectory container

    >>> @dataclass()
    >>> class MockContainer(BaseTrajectoryDataclass):
    >>>     timestamps: np.ndarray
    >>>     position: MockNestedContainer

    :ivar timesteps_indices: Represent the indices of timesteps in the trajectory which can pertain
        to a subset of a larger trajectory (Automaticaly generated if set to None).
    :type timesteps_indices: numpy ndarray
    :ivar batch: Boolean indicating if the data is batched (True) or pertaining to a
        single trajectory (False).
    :type batch: bool
    """

    feature_name: str = field(default=None, init=False)
    _nested: str = field(default=True, init=False)


@dataclass()
class BaseNoTrajectoryDataclass(AbstractNoTrajectoryDataclass):
    """
    Represents a base data structure without trajectory handling.

    This class inherits from ``AbstractNoTrajectoryDataclass`` and serves as
    a foundation for non-trajectory-based data classes. It is designed to hold
    and manage data that does not involve trajectory-specific information at top-level but might
    in nested ones e.g., `Tf2MsgsTFMessage.transforms` a list of `GeometryMsgsTransformStamped` trj container

    :ivar feature_name: Name of the feature associated with the trajectory.
    :type feature_name: str
    """

    pass
