# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .abstract_trajectory_dataclass import AbstractTrajectoryDataclass


@dataclass()
class BaseTrajectoryDataclass(AbstractTrajectoryDataclass):
    """ Represents a base trajectory data structure with additional functionality for trajectory handling and manipulation.

    This class is intended to serve as a base class for specific trajectory dataclasses, providing core functionalities and attributes to manage data related to trajectories. It builds upon the abstract trajectory dataclass and can be extended further to meet specific requirements.

    :ivar timestep_index: Trajectory data temporal index.
    :type timestep_index: Optional[np.ndarray]
    """
    timestep_index: Optional[np.ndarray] = field(default=None, init=False)

    @property
    def _init_trj_axe(self) -> int:
        return 0


@dataclass()
class NestedBaseTrajectoryDataclass(BaseTrajectoryDataclass):
    """ Represents a nested base trajectory dataclass which extends the functionality of the BaseTrajectoryDataclass.

    This class summarizes the concept of a derived dataclass with specific attributes associated with trajectory-related features. It includes additional specific field initializations while being immutable and leveraging the `dataclass` module.

    :ivar feature_name: This attribute is set to None by default and is immutable.
    :type feature_name: str
    """
    feature_name: str = field(default=None, init=False)
