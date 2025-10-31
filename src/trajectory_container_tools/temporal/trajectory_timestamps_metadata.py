# coding=utf-8
from dataclasses import dataclass
from typing import Optional


@dataclass
class TrajectoryTimestampsMetadata:
    """Represents a trajectory timestamps metadata.

    This class encapsulates the start time, end time, and duration of a trajectory. The `duration`
    is automatically calculated if not provided during initialization. It can be used for various
    time-based operations related to trajectory handling.

    :ivar start_time: The start time of the trajectory.
    :type start_time: int
    :ivar end_time: The end time of the trajectory.
    :type end_time: int
    :ivar duration: The total duration of the trajectory.
    :type duration: Optional[int]
    """

    start_time: int
    end_time: int
    duration: Optional[int] = None

    def __post_init__(self):
        if self.duration is None:
            self.duration = self.end_time - self.start_time

@dataclass
class TrajectoryTimestampsMetadataBag:
    recorded: TrajectoryTimestampsMetadata | None
    published: TrajectoryTimestampsMetadata | None
