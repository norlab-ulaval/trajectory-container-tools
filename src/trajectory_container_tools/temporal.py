# coding=utf-8
"""
Temporal analysis tools for trajectory data.

Includes timestamp handling, sequence ordering, and temporal indexing.

Usage:
    >>> import trajectory_container_tools as tct
    >>> timestamps = tct.temporal.Timestamps(data)
    >>> tct.temporal.validate_ordering(timestamps)
"""

from .utils.temporal_tools.timestamps import (
    Timestamps,
    TimestampCausalOrderingError
)
from .utils.temporal_tools.timestep_indexing import (
    dataframe_timestep_indexing_sanity_check as validate_dataframe_indexing
)

__all__ = [
    'Timestamps',
    'TimestampCausalOrderingError',
    'validate_dataframe_indexing',
]
