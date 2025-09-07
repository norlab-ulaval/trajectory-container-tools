# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass


# :::: General ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@dataclass()
class BaseTrajectoryDataclass(AbstractTrajectoryDataclass):
    """ Represents a base trajectory data structure.

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

    :ivar timestep_index: Trajectory data temporal index.
    :type timestep_index: Optional[np.ndarray]
    """
    timestep_index: Optional[np.ndarray] = field(default=None, init=False)

    @property
    def _init_trj_axe(self) -> int:
        return 0


@dataclass()
class NestedBaseTrajectoryDataclass(BaseTrajectoryDataclass):
    """ Represents a nested base trajectory dataclass which extends the functionality of the
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


# :::: Dataframe related ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
@dataclass()
class BaseReverseAxisTrajectoryDataclass(AbstractTrajectoryDataclass):
    """ Represents a base trajectory data structure with inverted array axes
    with respect to 'BaseTrajectoryDataclass'

    This class is intended to serve as a base class for specialized trajectory dataclasess where
    the data is fetched from sources that assign features to column and time step to row.
    It builds upon the abstract trajectory dataclass and can be extended further to meet
    specific requirements.

    Note:

    **Usage example**:

        >>> @dataclass()
        >>> class MockContainer(BaseReverseAxisTrajectoryDataclass):
        >>>     timestamps: np.ndarray
        >>>     position_x: np.ndarray
        >>>     position_y: np.ndarray
        >>>     position_z: np.ndarray

    """

    @property
    def _init_trj_axe(self) -> int:
        return -1


@dataclass()
class NestedBaseReverseAxisTrajectoryDataclass(BaseReverseAxisTrajectoryDataclass):
    """
    # (NICE TO HAVE) ToDo: implement nested trajectory-dataclass support for dataframe extraction
    """
    feature_name: str = field(default=None, init=False)

    def on_begin_post_init_callback(self):
        super().on_begin_post_init_callback()
        raise NotImplementedError("Nested trajectory for dataframe is not supported yet.")
