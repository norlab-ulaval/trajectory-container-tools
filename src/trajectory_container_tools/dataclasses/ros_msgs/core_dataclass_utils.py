# coding=utf-8
from typing import Optional

from trajectory_container_tools.temporal import Timestamps


def get_timestamps_slice(
    timestamps: Timestamps,
    start: int,
    stop: Optional[int] = None,
    startpoint: bool = True,
    endpoint: bool = False,
) -> slice:
    """
    Extracts a slice of timestamps based on given start, stop, and boundary inclusions.

    This function calculates a slice object to index into a `Timestamps` object
    based on the nearest timestamp to the specified start and optionally,
    the stop time. It can include or exclude the start and stop boundaries
    based on the `startpoint` and `endpoint` flags.

    :param timestamps: Timestamps object to retrieve nearest time indices.
    :param start: The starting timestamp from which to slice.
    :param stop: Optional stopping timestamp up to which to slice.
    :param startpoint: Boolean indicating whether to include the start boundary.
    :param endpoint: Boolean indicating whether to include the stop boundary.
    :return: A slice object representing the calculated index range.
    """
    nearest_stamp = timestamps.get_nearest_stamp(start, future=True, include=True)
    nearest_idx = timestamps.get_indexes(nearest_stamp)

    if stop is None:
        timestamps_slice = slice(
            nearest_idx + int(not startpoint), nearest_idx + int(startpoint)
        )
    else:
        next_nearest_stamp = timestamps.get_nearest_stamp(
            stop, future=True, include=True
        )
        if _is_the_last_value_in_timestamps_array(next_nearest_stamp):
            timestamps_slice = slice(nearest_idx + int(not startpoint), len(timestamps))
        else:
            next_nearest_idx = timestamps.get_indexes(next_nearest_stamp)
            timestamps_slice = slice(
                nearest_idx + int(not startpoint), next_nearest_idx + int(endpoint)
            )
    return timestamps_slice


def _is_the_last_value_in_timestamps_array(next_nearest_stamp: int | None) -> bool:
    return next_nearest_stamp is None
