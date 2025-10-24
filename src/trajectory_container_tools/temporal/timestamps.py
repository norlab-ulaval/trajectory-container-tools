# coding=utf-8
from copy import copy, deepcopy
from typing import Any, List, Optional, Tuple, Union

import numpy as np


class TimestampCausalOrderingError(Exception):
    """Exception raised when a causal order violation is detected."""

    pass


class TimestampMissingError(Exception):
    """Exception raised when a timestamp is not in stamps but in stamps bound."""

    def __init__(self, timestamps: Optional[Union[int, np.integer, list]] = None):
        if timestamps is not None and isinstance(timestamps, (int, np.integer)):
            self.messages = f"{timestamps=} is not in stamps"
        else:
            self.messages = f"At least one value in timestamps is not in stamps"
        super().__init__(self.messages)


class TimestampOutOfBoundError(Exception):
    """Exception raised when a timestamp is outside the stamps bounds."""

    def __init__(self, timestamps: Optional[Union[int, np.integer, list]] = None):
        if timestamps is not None and isinstance(timestamps, (int, np.integer)):
            self.messages = f"{timestamps=} is out of stamps bounds"
        else:
            self.messages = f"At least one value in timestamps is out of stamps bounds"
        super().__init__(self.messages)


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

    _stamps: np.ndarray[int, np.dtype[int]]
    _delta_stamps: np.ndarray[int, np.dtype[int]]
    _trajectory_len: int
    _iter_index: int = 0

    def __init__(self, stamps: np.ndarray[int, np.dtype[int]]):
        """
        Represents a class initializer for managing and validating a sequence of timestamps.

        The initializer takes a NumPy array of integer timestamps and performs validation to
        ensure the data's integrity. Specifically, it ensures that the array is not empty and
        that all timestamps are non-negative. If either validation check fails, an exception
        is raised.

        :param stamps: A NumPy array containing integer timestamps in nanosecond ros time format.
        :raises ValueError: If the stamp array is empty or if any value is negative.
        """
        self._trajectory_len = len(stamps)
        if self._trajectory_len == 0:
            raise ValueError("[TCT error] stamps array is empty!")

        if np.min(stamps) < 0:
            raise ValueError("[TCT error] stamps must be positive values")

        self._stamps = np.array(stamps, dtype=int)
        self._delta_stamps = compute_delta_timestamp(self._stamps)

    @property
    def stamps(self) -> np.ndarray[int, np.dtype[int]]:
        return self._stamps

    @property
    def delta_stamps(self) -> np.ndarray[int, np.dtype[int]]:
        return self._delta_stamps

    @property
    def shape(self) -> Tuple:
        # (NICE TO HAVE) ToDo: assess if its still relevant now that there two dimensions
        #   to the Timestamps classs i.e., stamps and delta stamps
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

    def __getitem__(self, index):
        timestamps_at_t = deepcopy(self)
        for each_name in ["_stamps", "_delta_stamps"]:
            data_property = self.__getattribute__(each_name)
            data_value = data_property[index]
            timestamps_at_t.__setattr__(each_name, data_value)

        return timestamps_at_t

    def empty(self) -> "Timestamps":
        """
        Creates an empty copy of the current Timestamps object.

        :return: A new empty instance of Timestamps.
        """
        timestamps_empty = deepcopy(self)
        for each_name in ["_stamps", "_delta_stamps"]:
            timestamps_empty.__setattr__(each_name, np.array([], dtype=np.int64))

        return timestamps_empty

    def __contains__(
        self,
        timestamp: Union[int, np.integer, List[int], np.ndarray[int, np.dtype[int]]],
    ) -> bool:
        """
        Check whether a timestamp or collection of timestamps exists within the stored stamps.

        This method validates if the provided `timestamp`, which can be a single integer,
        a list of integers, or a numpy array of integers, is present in the internally
        stored `stamps`. It performs membership testing using numpy's efficient array operations.

        :param timestamp: A single timestamp, a list of timestamps, or a numpy array of
            integers to check against the internal collection of stamps.
        :return: A boolean indicating whether any of the given timestamps exist within
            the stored set of stamps.
        """
        assert isinstance(timestamp, (int, np.integer)) or (
            isinstance(timestamp, (list, np.ndarray))
            and isinstance(timestamp[0], (int, np.integer))
        )
        mask = np.isin(timestamp, self._stamps, assume_unique=True)
        if isinstance(timestamp, (int, np.integer)):
            return np.any(mask)
        else:
            return mask[mask == True].size == len(timestamp)

    def get_indexes(
        self, timestamps: Union[int, List[int], np.ndarray[int, np.dtype[int]]]
    ) -> Union[int, List[int]]:
        """
        Determines the indexes of given timestamps in the internal storage.

        This function checks for the existence of given timestamps in the internal
        storage and retrieves their respective indexes if found. It supports single
        timestamps or lists/arrays of timestamps as input. For lists or arrays, it
        returns a list of corresponding indexes. If the timestamps are not found, it
        raise a TimestampMissingError or a TimestampOutOfBoundError error.
        Timestamps must be in nanoseconds format as integers.

        :param timestamps: A single timestamp as an integer, a list of integers, or a
            numpy array of integers representing the timestamps to look up.
        :return: If `timestamps` is a single integer and found, returns its index as
            an integer. If `timestamps` is a list or numpy array of integers, returns
            a list of indexes.
        :raises TypeError: If the input is not an integer or a numpy array of integers.
        :raises TimestampMissingError: If the input is in bound but not in stamps.
        :raises TimestampOutOfBoundError: If the input is out of stamps bound.
        """
        if isinstance(timestamps, list):
            timestamps = np.array(timestamps, dtype=int)

        _check_precondition_nanoseconds_are_integers(timestamps)

        if timestamps not in self:
            if self.is_timestamps_in_bounds(timestamps):
                raise TimestampMissingError(timestamps)
            else:
                raise TimestampOutOfBoundError(timestamps)

        if isinstance(timestamps, np.ndarray):
            mask = np.isin(timestamps, self._stamps, assume_unique=True)
            return np.squeeze(np.nonzero(mask)).tolist()
        else:
            mask = self._stamps == timestamps
            indice = int(np.squeeze(np.nonzero(mask)))
            return indice

    def min(self):
        return self.stamps.min()

    def max(self):
        return self.stamps.max()

    def is_timestamps_in_bounds(
        self, timestamps: Union[int, List[int], np.ndarray[int, np.dtype[int]]]
    ) -> bool:
        """
        Determines whether the provided timestamps are within the bounds of the stamps attribute.

        This function checks if the given timestamps, which can be an integer, a
        list of integers, or a NumPy array of integers, fall within the minimum and
        maximum bounds of an internally defined range. If any of the provided
        timestamps are out of bounds, the function returns `False`. Otherwise, it
        returns `True`.

        :param timestamps: The timestamps to be checked against the predefined
            bounds. Can be an integer, a list of integers, or a NumPy array of
            integers. The type and shape of the timestamps are handled dynamically.
        :return: `True` if all the timestamps are within the predefined bounds,
            otherwise `False`.
        """
        if isinstance(timestamps, list):
            timestamps = np.array(timestamps, dtype=int)

        if isinstance(timestamps, np.ndarray):
            if timestamps.min() < self.min() or self.max() < timestamps.max():
                return False
            else:
                return True
        elif timestamps < self.min() or self.max() < timestamps:
            return False
        else:
            return True

    def get_nearest_stamp(
        self, timestamp: int, future: bool = True, include: bool = True
    ) -> int | None:
        """
        Finds the nearest available timestamp in the dataset based on the given criteria.

        This method determines the nearest timestamp either in the future or in the past
        relative to the specified timestamp. The search criteria can also include whether
        to consider the given timestamp as part of the valid result, depending on the
        value of the `include` parameter.

        :param timestamp: The reference timestamp to find the nearest match.
        :param future: Whether to find the nearest timestamp in the future (default) or the past.
        :param include: Whether to include the given timestamp itself as a valid match if
            it exists in 'Timestamps.stamps'. Defaults to False.
        :return: The nearest timestamp matching the criteria or None if no match is found.
        """
        if include and timestamp in self:
            return timestamp

        if future:
            return self.get_nearest_futur_stamp(timestamp)
        else:
            return self.get_nearest_past_stamp(timestamp)

    def get_nearest_futur_stamp(self, timestamp: int) -> int:
        """
        Finds the nearest next timestamp greater than the given input timestamp.

        :param timestamp: The input timestamp to compare against.
        :return: The nearest next timestamp greater than the input, or None if no such
                 timestamp exists.
        :raises IndexError: If timestamp as no next futur stamp candidate in stamps
        """
        assert isinstance(timestamp, (int, np.integer))
        try:
            mask = timestamp < self._stamps
            nearest_futur_stamp = self._nearest_stamp(mask)
        except IndexError as e:
            raise IndexError(
                f"{timestamp=} as no nearest futur candidat stamp in Timestamps object"
            )
        return nearest_futur_stamp

    def get_nearest_past_stamp(self, timestamp: int) -> int:
        """
        Finds the nearest previous timestamp i.e., the one that is strictly less than the given one

        :param timestamp: The timestamp to compare against, given as an integer.
        :return: The nearest previous timestamp as an integer, or None if no such timestamp
            exists.
        :raises IndexError: If timestamp as no next past stamp candidate in stamps
        """
        assert isinstance(timestamp, (int, np.integer))
        try:
            mask = timestamp > self._stamps
            nearest_past_stamp = self._nearest_stamp(mask, future=False)
        except IndexError as e:
            raise IndexError(
                f"{timestamp=} as no nearest past candidat stamp in Timestamps object"
            )
        return nearest_past_stamp

    def _nearest_stamp(
        self, mask: bool | np.ndarray[Any, np.dtype[bool]], future=True
    ) -> int:
        nearest_index = np.squeeze(np.nonzero(mask))

        # Only pick the first
        if nearest_index.size > 1:
            if future:
                nearest_index = nearest_index[0]
            else:
                nearest_index = nearest_index[-1]

        if nearest_index.size == 1 and self._stamps.size > 0:
            return int(np.squeeze(self._stamps[nearest_index]))
        else:
            raise IndexError

    def __str__(self):
        out_sp = " " * 0
        in_sp = " " * 3
        repr_str = "\nTimestamps(\n"
        for k in ["stamps", "delta_stamps"]:
            repr_str += f"{out_sp}{in_sp}{k}: "
            v = self.__getattribute__(k)
            if k == "delta_stamps" and v.size > 1:
                range_str = f"range {np.min(v[1:])} ←→ {np.max(v[1:])} (nanosec)"
            elif v.size > 0:
                range_str = f"range {np.min(v)} ←→ {np.max(v)} (nanosec)"
            else:
                range_str = "empty"
            repr_str += f"shape {v.shape} {range_str}\n"
        repr_str += f"{out_sp})"
        return repr_str

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
        return to_seconds_nanoseconds(self.stamps[key])

    def causal_ordering_sanity_check(
        self, show_offending_in_nanoseconds: bool = True
    ) -> List[int]:
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
        return validate_timestamps_ordering(self, show_offending_in_nanoseconds)


def validate_timestamps_ordering(
    timestamp_object: Timestamps, show_offending_in_nanoseconds: bool = True
) -> List[int]:
    """Checks the causal order of timestamps in the given data container to ensure they are
    monoticaly increasing.

    This sanity check function validates that each timestamp in the timestamp array is less
    than the next timestamp. If a causal order violation is detected, the function identifies
    and reports the offending timestamps and raises an TimestampCausalOrderingError error.

    Usage example:

    >>> mock_trajectory_timestamp_object: Timestamps
    >>> offending_index = validate_timestamps_ordering(mock_trajectory_timestamp_object)
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
        previous_timestamp = timestamp_object.stamps[ts_idx - 1]
        current_timestamp = timestamp_object.stamps[ts_idx]

        try:
            assert previous_timestamp < current_timestamp
        except AssertionError:
            if not show_offending_in_nanoseconds:
                previous_timestamp = to_seconds_nanoseconds(previous_timestamp)
                current_timestamp = to_seconds_nanoseconds(current_timestamp)
            offending_idx.append(ts_idx)
            offending_ts += (
                f"    {str(previous_timestamp):>25} [{ts_idx - 1:>5}]     !<     "
                f"{str(current_timestamp):>25} [{ts_idx:>5}]\n"
            )

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
            f"          start: {timestamp_object[0].stamps:>22}  "
            f"{str(timestamp_object.seconds_nanoseconds(0)):>25} \n"
            f"          stop:  {timestamp_object[-1].stamps:>22}  "
            f"{str(timestamp_object.seconds_nanoseconds(-1)):>25} \n"
            f"      duration:  "
            f"{(timestamp_object[-1].stamps - timestamp_object[0].stamps):>22}  \n"
            f"    {'—' * 78}\n"
        )
        raise TimestampCausalOrderingError(error_msg)

    return offending_idx


def to_seconds_nanoseconds(
    nanoseconds: Union[int, np.ndarray[int, np.dtype[int]]],
) -> Tuple[
    Union[int, np.ndarray[int, np.dtype[int]]],
    Union[int, np.ndarray[int, np.dtype[int]]],
]:
    """Get timestamp(s) as separate seconds and nanoseconds components.

    Output is compatible with the ROS2 time (seconds nanoseconds) format

    Note: Input are required to be an integer or an array of integer for numerical stability.
    For example, the following input np.array([1711038330132760208], dtype=np.float64) actualy
    truncate the last two digit which would result in the nanosecond part being returned with a
    numerical error (i.e., 132760320) instead of the expected value 132760208.

    :returns: 2-tuple seconds and nanoseconds
    :raises TypeError: If the input is not an integer or a numpy array of integers.
    """
    _check_precondition_nanoseconds_are_integers(nanoseconds)
    NANOSECONDS_CONVERSION_CONSTANT = 10**9
    sec, ns = divmod(nanoseconds, NANOSECONDS_CONVERSION_CONSTANT)
    return sec, ns


def to_seconds(
    nanoseconds: Union[int, np.ndarray[int, np.dtype[int]]],
) -> Union[float, np.ndarray[int, np.dtype[int]]]:
    """Convert timestamp(s) in nanosecond to seconds.

    :returns: Timestamp converted in second
    :raises TypeError: If the input is not an integer or a numpy array of integers.
    """
    _check_precondition_nanoseconds_are_integers(nanoseconds)
    SECONDS_CONVERSION_CONSTANT = 1e9
    return nanoseconds / SECONDS_CONVERSION_CONSTANT


def compute_delta_timestamp(
    time_space: np.ndarray, prepend_zero: bool = True
) -> np.ndarray:
    """Compute the delta timestamps from a given 1D array of time points.

    This function calculates the differences between successive elements in a 1D NumPy array.
    Optionally, it can prepend a zero to the resulting array to return an array of same length
    as the one given as intput.

    :param time_space: 1D NumPy array containing time points.
    :param prepend_zero: Whether to prepend a zero at the beginning of the resulting
        delta timestamps. Defaults to True.
    :return: A NumPy array containing the calculated delta timestamps.
    """
    assert time_space.ndim == 1
    if prepend_zero:
        delta_time = np.ediff1d(time_space, to_begin=0)
    else:
        delta_time = np.ediff1d(time_space)
    return delta_time


def _check_precondition_nanoseconds_are_integers(
    nanoseconds: Union[int, float, np.ndarray],
) -> None:
    """Validates that the input `nanoseconds` is of integer types or a numpy array of integers.

    :param nanoseconds: The input value to validate.
    :return: None.
    :raises TypeError: If the input is not an integer or a numpy array of integers.
    """
    try:
        if isinstance(nanoseconds, np.ndarray):
            assert np.issubdtype(nanoseconds.dtype, np.integer)
        else:
            assert isinstance(nanoseconds, (int, np.integer))
    except AssertionError:
        raise TypeError("Input must be an integer or a numpy array or intergers")
    return None
