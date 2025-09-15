# coding=utf-8
from dataclasses import dataclass, field

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass


@dataclass()
class BaseTrajectoryDataclass(AbstractTrajectoryDataclass):
    """Represents a base trajectory data structure.

    This class is intended to serve as a base class for specialized trajectory dataclasses,
    providing core functionalities and attributes to manage data related to trajectories. It
    builds upon the abstract trajectory dataclass and can be extended further to meet specific
    requirements.

    **Usage example**:

    Note: this example would represent a flat data representation as oposed to a nested one
    (see `NestedBaseTrajectoryDataclass` usage example).

        >>> @dataclass()
        >>> class MockContainer(BaseTrajectoryDataclass):
        >>>     timestamps: np.ndarray
        >>>     position_x: np.ndarray
        >>>     position_y: np.ndarray
        >>>     position_z: np.ndarray

    """

    pass


@dataclass()
class NestedBaseTrajectoryDataclass(BaseTrajectoryDataclass):
    """Represents a nested base trajectory dataclass which extends the functionality of the
    BaseTrajectoryDataclass.

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

    :ivar feature_name: This attribute is set to None by default and is immutable.
    :type feature_name: str
    """

    feature_name: str = field(default=None, init=False)
    _nested: str = field(default=True, init=False)
