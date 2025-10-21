# coding=utf-8
from dataclasses import dataclass
from typing import Union

import numpy as np

from trajectory_container_tools.dataclasses.core.base_trajectory_dataclass import (
    BaseTrajectoryFeature,
)
from trajectory_container_tools.temporal import Timestamps


@dataclass()
class StdMsgsHeader(BaseTrajectoryFeature):
    """Represents a ros header containing frame information and time-related data.

    Compatible ros2 message interface: std_msgs/msg/Header

    This class ensures that timestamps are processed properly, converting numpy arrays to the
    specified `Timestamps` type and validating causal ordering to maintain data consistency.

    The `timestamps` target type is Timestamps but accept numpy array for convenience which will be
    converted to the target type at instanciation.

    :ivar frame_id: Identifier for the coordinate frame.
    :ivar timestamps: Time-related information, either a Timestamps object or a numpy array
                      (converted to Timestamps internally at instanciation).
    :type timestamps: Timestamps
    """

    frame_id: str
    timestamps: Union[Timestamps, np.ndarray]

    def on_begin_post_init_callback(self) -> None:
        timestamps: Union[Timestamps, np.ndarray]

        if isinstance(self.timestamps, np.ndarray):
            self.timestamps = Timestamps(self.timestamps)

        self.timestamps.causal_ordering_sanity_check(show_offending_in_nanoseconds=True)
