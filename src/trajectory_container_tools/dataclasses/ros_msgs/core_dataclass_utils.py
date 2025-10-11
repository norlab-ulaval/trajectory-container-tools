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
    :param startpoint: Indicating whether to include the start boundary.
    :param endpoint: Indicating whether to include the stop boundary.
    :return: A slice object representing the calculated index range.
    """
    try:
        nearest_stamp = timestamps.get_nearest_stamp(start, future=True, include=True)
        nearest_idx = timestamps.get_indexes(nearest_stamp) + int(not startpoint)
    except IndexError as e:
        nearest_idx = len(timestamps) - 1

    if stop is None:
        endpoint_idx = nearest_idx + int(startpoint)
    else:
        try:
            next_nearest_stamp = timestamps.get_nearest_stamp(
                stop, future=True, include=True
            )

            next_nearest_idx = timestamps.get_indexes(next_nearest_stamp)

            if not nearest_idx < next_nearest_idx:
                next_nearest_idx += 1

            endpoint_idx = next_nearest_idx + int(endpoint)

            if not endpoint_idx <= len(timestamps):
                endpoint_idx = len(timestamps)

        except IndexError as e:
            endpoint_idx = len(timestamps)

    assert nearest_idx < endpoint_idx, f"{nearest_idx} !< {endpoint_idx}"
    timestamps_slice = slice(nearest_idx, endpoint_idx)
    return timestamps_slice
