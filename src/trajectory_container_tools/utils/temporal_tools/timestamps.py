# coding=utf-8
from typing import Any, List, Tuple

import numpy as np

class TimestampCausalOrderingError(Exception):
    """Exception raised when a causal order violation is detected."""
    pass


class Timestamps:
    """
    Handles timestamp management and provides iteration and validation methods
    for processing timestamp arrays.

    Align with ROS time format whitout requiring rclpy

    The `Timestamps` class is designed to work with a one-dimensional NumPy array of positive
    integer timestamps. It supports iteration, indexing, and validation to ensure the timestamps
    are in logical and causal order. This class enforces basic constraints on the timestamps and
    provides methods for further processing.
    """
    _stamps: np.ndarray[Any, np.dtype[int]]
    _trajectory_len: int
    _iter_index: int = 0

    def __init__(self, stamps: np.ndarray[Any, np.dtype[int]]):
        """
        Represents a class initializer for managing and validating a sequence of timestamps.

        The initializer takes a NumPy array of integer timestamps and performs validation to
        ensure the data's integrity. Specifically, it ensures that the array is not empty and
        that all timestamps are non-negative. If either validation check fails, an exception
        is raised.

        :param stamps: A NumPy array containing integer timestamps in nanosecond ros time format.

        :raises ValueError: If the stamp array is empty.
        :raises ValueError: If any value in the stamp array is negative.
        """
        self._trajectory_len = len(stamps)
        if self._trajectory_len == 0:
            raise ValueError("[TCT error] stamps array is empty!")

        if np.min(stamps) < 0:
            raise ValueError("[TCT error] stamps must be positive values")

        self._stamps = np.array(stamps)

    @property
    def stamps(self) -> np.ndarray[Any, np.dtype[int]]:
        return self._stamps

    @property
    def shape(self) -> Tuple:
        return self._stamps.shape

    def __len__(self):
        return len(self._stamps)

    def __iter__(self):
        self._iter_index = 0
        return self

    def __next__(self):
        if self._iter_index < self._trajectory_len:
            item = self[self._iter_index]
            self._iter_index += 1
            return item
        else:
            raise StopIteration

    def __getitem__(self, key) -> int:
        return self._stamps[key]

    def seconds_nanoseconds(self, key) -> Tuple[int, int]:
        """
        Converts the value associated with the given key into seconds and nanoseconds.

        Usage:

        >>> ts = Timestamps(np.array([1711047156311350031, 1711047156397750031]))
        >>> ts.seconds_nanoseconds(0)
        >>> # (1711047156, 311350031)

        :param key: The key whose associated value will be converted to seconds and
            nanoseconds. The key is used to access the data structure holding the value.
        :return: A tuple containing two integers, where the first integer represents
            seconds and the second represents nanoseconds.
        """
        return to_seconds_nanoseconds(self[key])

    def causal_ordering_sanity_check(self, show_offending_in_nanoseconds: bool = True) -> List[int]:
        """
        Performs a sanity check for causal ordering based on timestamps of events.

        This function verifies the causal ordering of events tied to a specific feature
        within a dataset. It ensures that the temporal sequence adheres to the expected
        causality rules and returns a list of IDs where violations occur, if any. The
        option to display the offending timestamps in nanoseconds is provided for finer
        granularity during debugging and analysis.

        :param show_offending_in_nanoseconds: Whether to display offending timestamps in
          nanoseconds or (seconds, nanoseconds ), default is True.
        :return: A list of integers representing IDs of events that violate causal ordering.
        """
        return timestamp_causal_ordering_sanity_check(self, show_offending_in_nanoseconds)


def timestamp_causal_ordering_sanity_check(timestamp_object: Timestamps,
                                           show_offending_in_nanoseconds: bool = True) -> List[int]:
    """ Checks the causal order of timestamps in the given data container to ensure they are
    monoticaly increasing.

    This sanity check function validates that each timestamp in the timestamp array is less
    than the next timestamp. If a causal order violation is detected, the function identifies
    and reports the offending timestamps and raises an TimestampCausalOrderingError error.

    Usage example:

    >>> mock_trajectory_timestamp_object: Timestamps
    >>> offending_index = timestamp_causal_ordering_sanity_check(mock_trajectory_timestamp_object)
    >>> # TimestampCausalOrderingError: Timestamp causal ordering violations:
    >>> #     Number of offending timestamps 4/3409
    >>> #
    >>> #     Offending timestamps:
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #                   nanoseconds [  T  ]                          nanoseconds [ T+1 ]
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #           1711047163876963111 [  302]     !<                             0 [  303]
    >>> #                             0 [  511]     !<                             0 [  512]
    >>> #           1711047175850442468 [  631]     !<                             0 [  632]
    >>> #           1711047237203461717 [ 3334]     !<                             0 [ 3335]
    >>> #
    >>> #     Rosbag timestamps metadate:
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> #                             nanoseconds    ( seconds nanoseconds )
    >>> #           start:    1711047156311350031    (1711047156, 311350031)
    >>> #           stop:     1711047241134490773    (1711047241, 134490773)
    >>> #       duration:             84823140742
    >>> #     ——————————————————————————————————————————————————————————————————————————————
    >>> assert len(offending_index) == 4

    :param timestamp_object: A Timestance object fill with trajectory stamp in nanosecond.
    :param show_offending_in_nanoseconds: Display in nanosecond or ( seconds nanoseconds ).
     Default nanoseconds
    :return: The list of offending timestamps indexes.
    :raises TimestampCausalOrderingError: Raises an TimestampCausalOrderingError if the
     "timestamps" array is empty or if any timestamp violates the causal ordering.
    """
    offending_idx = []
    offending_ts = ""
    for ts_idx in np.arange(start=1, stop=len(timestamp_object)):
        previous_timestamp = timestamp_object[ts_idx - 1]
        current_timestamp = timestamp_object[ts_idx]

        try:
            assert previous_timestamp < current_timestamp
        except AssertionError:
            if not show_offending_in_nanoseconds:
                previous_timestamp = to_seconds_nanoseconds(previous_timestamp)
                current_timestamp = to_seconds_nanoseconds(current_timestamp)
            offending_idx.append(ts_idx)
            offending_ts += (
                    f"    {str(previous_timestamp):>25} [{ts_idx - 1:>5}]     !<     "
                    f"{str(current_timestamp):>25} [{ts_idx:>5}]\n")

    if len(offending_idx) > 0:
        if show_offending_in_nanoseconds:
            timestamp_display = "nanoseconds"
        else:
            timestamp_display = "( seconds nanoseconds )"
        offending_ts_header = (
                f"    {'—' * 78}\n"
                f"    {timestamp_display:>25} [  T  ]            {timestamp_display:>25} [ T+1 ]\n"
                f"    {'—' * 78}"
        )
        error_msg = (
                f"Timestamp causal ordering violations:\n"
                f"    Number of offending timestamps {len(offending_idx)}/"
                f"{len(timestamp_object)}\n\n"
                f"    Offending timestamps:\n"
                f"{offending_ts_header}\n"
                f"{offending_ts}\n"
                f"    Rosbag timestamps metadate:\n"
                f"    {'—' * 78}\n"
                f"                            nanoseconds    ( seconds nanoseconds )\n"
                f"          start: {timestamp_object[0]:>22}  "
                f"{str(timestamp_object.seconds_nanoseconds(0)):>25} \n"
                f"          stop:  {timestamp_object[-1]:>22}  "
                f"{str(timestamp_object.seconds_nanoseconds(-1)):>25} \n"
                f"      duration:  "
                f"{(timestamp_object[-1] - timestamp_object[0]):>22}  \n"
                f"    {'—' * 78}\n"
        )
        raise TimestampCausalOrderingError(error_msg)

    return offending_idx


def to_seconds_nanoseconds(nanoseconds: int) -> Tuple[int, int]:
    """ Get time as separate seconds and nanoseconds components.

    Output is compatible with the ROS2 time (seconds nanoseconds) format

    :returns: 2-tuple seconds and nanoseconds
    """
    NANOSECONDS_CONVERSION_CONSTANT = 10 ** 9
    return (nanoseconds // NANOSECONDS_CONVERSION_CONSTANT, nanoseconds %
            NANOSECONDS_CONVERSION_CONSTANT)


