# coding=utf-8
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, Optional
import numpy as np


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
    """
    Represents a metadata bag containing recorded and published trajectory timestamps.

    This class provides a structure for storing metadata about trajectory timestamps,
    including recorded and published timestamps metadata. It can be used to encapsulate
    timestamp-related data in a single object for further processing or analysis.

    :ivar recorded: Metadata of the recorded trajectory timestamps.
    :type recorded: TrajectoryTimestampsMetadata | None
    :ivar published: Metadata of the published trajectory timestamps.
    :type published: TrajectoryTimestampsMetadata | None
    """

    recorded: TrajectoryTimestampsMetadata | None
    published: TrajectoryTimestampsMetadata | None


@dataclass
class RateMetric:
    """
    Represents a data structure for storing rate metrics.

    The RateMetric class encapsulates various statistical metrics calculated on
    frequency data (in Hz). Common statistics such as mean, median, standard
    deviation, minimum, and maximum values are stored as attributes. It is used
    to represent and provide easy access to these metrics in a structured format.

    :ivar mean_hz: The arithmetic mean of frequency values in hertz.
    :type mean_hz: float
    :ivar median_hz: The median of frequency values in hertz.
    :type median_hz: float
    :ivar std_hz: The standard deviation of frequency values in hertz.
    :type std_hz: float
    :ivar min_hz: The minimum frequency value in hertz.
    :type min_hz: float
    :ivar max_hz: The maximum frequency value in hertz.
    :type max_hz: float
    """

    mean_hz: Optional[float]
    median_hz: Optional[float]
    std_hz: Optional[float]
    min_hz: Optional[float]
    max_hz: Optional[float]

    def __str__(self) -> str:
        def _str_preprocess_callback(field_name: str, field_value: Any):
            append_to_field_value = ""
            if '_hz' in field_name:
                field_name = field_name.removesuffix('_hz')
                append_to_field_value = " (hz)"
            return field_name, field_value, append_to_field_value

        return pretty_print_dataclass(self, decimals=2, preprocess_callback=_str_preprocess_callback)


def pretty_print_dataclass(
    dataclass_obj,
    decimals: int = 4,
    preprocess_callback: Optional[Callable] = None
) -> str:
    """
    Formats a dataclass object into a human-readable string with specified decimal rounding
    for float and numpy array attributes.

    This function takes a dataclass object and iterates over its fields to retrieve their
    values. It then generates a well-formatted string representation of the dataclass.
    Float values are rounded to the specified number of decimal places. Strings are wrapped
    in quotes, and other types are directly included in their string representation.

    :param dataclass_obj: The dataclass object to format.
    :param decimals: Number of decimal places to round the float values. Defaults to 4.
    :param preprocess_callback: function that take two argumen 'field_name: str', 'field_value: Any' and return a tuple  'field_name: str', 'field_value: Any' and 'append_to_field_value: str'
    :return: A string representing the dataclass object with its fields and values properly formatted.
    """
    assert is_dataclass(dataclass_obj)

    field_strs = []
    with np.printoptions(precision=decimals, suppress=True):
        for field in fields(dataclass_obj):
            field_value = getattr(dataclass_obj, field.name)
            field_name = field.name

            field_name, field_value, append_to_field_value = preprocess_callback(
                field_name, field_value
            )

            if isinstance(field_value, float):
                field_strs.append(
                    f"{field_name}={field_value:.{decimals}f}{append_to_field_value}"
                )
            elif isinstance(field_value, str):
                field_strs.append(
                    f"{field_name}='{field_value}'{append_to_field_value}"
                )
            else:
                field_strs.append(f"{field_name}={field_value}{append_to_field_value}")

    return f"{dataclass_obj.__class__.__name__}({', '.join(field_strs)})"
