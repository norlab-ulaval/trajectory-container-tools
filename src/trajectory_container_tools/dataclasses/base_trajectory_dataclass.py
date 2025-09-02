# coding=utf-8
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from trajectory_container_tools.dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
)


@dataclass()
class BaseTrajectoryDataclass(AbstractTrajectoryDataclass):
    timestep_index: Optional[np.ndarray] = field(default=None, init=False)

    @property
    def _init_trj_axe(self) -> int:
        return 0








