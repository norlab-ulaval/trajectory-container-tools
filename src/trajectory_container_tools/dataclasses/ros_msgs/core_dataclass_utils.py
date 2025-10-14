# coding=utf-8
from typing import Optional

from trajectory_container_tools.temporal import Timestamps
from trajectory_container_tools.temporal.timestamps import TimestampOutOfBoundError


def get_timestamps_slice(
    timestamps: Timestamps,
    start: int,
    stop: Optional[int] = None,
    startpoint: bool = True,
    endpoint: bool = False,
    resolve_out_of_bounds: bool = True,
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
    :param startpoint: Indicating whether to include the start boundary.
    :param endpoint: Indicating whether to include the stop boundary.
    :param resolve_out_of_bounds: (Default True) Disable out of bound check and resolve to the nearest
        timestamps bound. (False) Raise TimestampOutOfBoundError on bound violation.
    :return: A slice object representing the calculated index range.
    :raises TimestampOutOfBoundError: if start or stop is outside timestamps and their corresponing
     startpoint/endpoint parameter is set to False and resolve_out_of_bounds is set to False.
    """

    if not resolve_out_of_bounds and not startpoint:
        if not timestamps.is_timestamps_in_bounds(start):
            raise TimestampOutOfBoundError(start)

    if not resolve_out_of_bounds and not endpoint:
        if not timestamps.is_timestamps_in_bounds(stop):
            raise TimestampOutOfBoundError(stop)

    try:
        nearest_start_stamp = timestamps.get_nearest_stamp(
            start, future=True, include=startpoint
        )
        slice_start_idx = timestamps.get_indexes(nearest_start_stamp)
    except IndexError as e:
        slice_start_idx = len(timestamps) - 1

    if stop is None:
        slice_endpoint_idx = slice_start_idx + 1
    else:
        try:
            nearest_stop_stamp = timestamps.get_nearest_stamp(
                stop, future=False, include=endpoint
            )

            slice_endpoint_idx = timestamps.get_indexes(nearest_stop_stamp)

            slice_endpoint_idx = slice_endpoint_idx + 1

            if slice_start_idx >= slice_endpoint_idx:
                slice_endpoint_idx = slice_start_idx + 1

        except IndexError as e:
            slice_endpoint_idx = None

    if slice_endpoint_idx is not None:
        assert (
            slice_start_idx < slice_endpoint_idx
        ), f"{slice_start_idx} !< {slice_endpoint_idx}"
    timestamps_slice = slice(slice_start_idx, slice_endpoint_idx)
    return timestamps_slice
