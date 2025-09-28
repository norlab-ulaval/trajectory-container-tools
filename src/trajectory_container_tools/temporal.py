# coding=utf-8
"""
Temporal analysis tools for trajectory data.

Includes timestamp handling, sequence ordering, and temporal indexing.

Usage:
    >>> import trajectory_container_tools as tct
    >>> timestamps = tct.temporal.Timestamps(data)
    >>> tct.temporal.validate_timestamps_ordering(timestamps)
"""

from .utils.temporal_tools.timestamps import (
    Timestamps,
    TimestampCausalOrderingError,
    validate_timestamps_ordering
)
from .utils.temporal_tools.timestep_indexing import (
    validate_timestep_indices,
    validate_dataframe_timesteps_indexing
)

__all__ = [
    'Timestamps',
    'TimestampCausalOrderingError',
    'validate_timestamps_ordering',
    'validate_timestep_indices',
    'validate_dataframe_timesteps_indexing',
]
