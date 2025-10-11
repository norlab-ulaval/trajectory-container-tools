# coding=utf-8
"""
Temporal analysis tools for trajectory data.

Includes timestamp handling, sequence ordering, and temporal indexing.

Usage:

>>> import trajectory_container_tools as tct
>>> trajectory_timestamps = tct.temporal.Timestamps(data)
>>> tct.temporal.validate_timestamps_ordering(trajectory_timestamps)

"""

from .timestamps import (
    Timestamps,
    TimestampCausalOrderingError,
    validate_timestamps_ordering,
    compute_delta_timestamp,
    to_seconds,
    to_seconds_nanoseconds,
)
from .timestep_indexing import (
    validate_timestep_indices,
    validate_dataframe_timesteps_indexing,
)

__all__ = [
    "Timestamps",
    "TimestampCausalOrderingError",
    "validate_timestamps_ordering",
    "compute_delta_timestamp",
    "to_seconds_nanoseconds",
    "to_seconds",
    "validate_timestep_indices",
    "validate_dataframe_timesteps_indexing",
]
