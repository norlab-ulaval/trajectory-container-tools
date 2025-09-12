# coding=utf-8
from typing import List

import numpy as np
from rclpy.time import Time as ROSTime


def timestamp_causal_ordering_sanity_check(shadow_data_container: dict,
                                           nanoseconds: bool = True) -> List[int]:
    """ Checks the causal order of timestamps in the given data container to ensure they are
    sequentially increasing.

    This sanity check function validates that each timestamp in the timestamp array is less
    than the next timestamp. If a causal order violation is detected, the function identifies
    and reports the offending timestamps and raises an assertion error.

    Usage example:

    >>> mock_shadow_data_container = {
    >>>     'feature_name': "/mock_teleop",
    >>>     "timestamps": mock_trajectory_timestamp_in_ros_time,
    >>> }
    >>> offending_index = timestamp_causal_ordering_sanity_check(mock_shadow_data_container)
    >>> # AssertionError: Timestamp causal ordering sanity check failed! Number of offending timestamps 4/3409
    >>> # [TCT error] Timestamp causal ordering violations:
    >>> #
    >>> #     Offending /mock_teleop timestamps:
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

    :param shadow_data_container: A dictionary containing a "timestamps" entry which is a list
    of ROS time instances.
    :param nanoseconds: Display in nanosecond or ( seconds nanoseconds ). Default nanoseconds
    :return: The list of offending timestamps indexes.
    :raises AssertionError: Raises an AssertionError if the "timestamps" array is empty
        or if any timestamp violates the causal ordering.
    """
    # .... Pre-conditions .........................................................................
    assert "feature_name" in shadow_data_container, ("[TCT error] missing required key "
                                                     "'feature_name'!")
    if "timestamps" in shadow_data_container or "header" in shadow_data_container:
        if "timestamps" in shadow_data_container:
            timestamps_ = shadow_data_container["timestamps"]
        else:
            timestamps_ = shadow_data_container["header"].__getattribute__("timestamps")
    else:
        raise AssertionError("[TCT error] missing required key 'timestamps' or 'header'!")

    assert len(timestamps_) > 0, "[TCT error] timestamp array is empty!"
    assert isinstance(timestamps_[0], ROSTime), "[TCT error] timestamp are not ros time objects!"

    # .... Begin ..................................................................................
    offending_idx = []
    offending_ts = ""
    for ts_idx in np.arange(start=1, stop=len(timestamps_)):
        previous_timestamp: ROSTime = timestamps_[ts_idx - 1]
        current_timestamp: ROSTime = timestamps_[ts_idx]

        try:
            assert previous_timestamp < current_timestamp
        except AssertionError:
            if nanoseconds:
                previous_timestamp = previous_timestamp.nanoseconds
                current_timestamp = current_timestamp.nanoseconds
            else:
                previous_timestamp = previous_timestamp.seconds_nanoseconds()
                current_timestamp = current_timestamp.seconds_nanoseconds()
            offending_idx.append(ts_idx)
            offending_ts += (
                    f"    {str(previous_timestamp):>25} [{ts_idx - 1:>5}]     !<     "
                    f"{str(current_timestamp):>25} [{ts_idx:>5}]\n")

    if len(offending_idx) > 0:
        if nanoseconds:
            timestamp_display = "nanoseconds"
        else:
            timestamp_display = "( seconds nanoseconds )"
        offending_ts_header = (
                f"    {'—' * 78}\n"
                f"    {timestamp_display:>25} [  T  ]            {timestamp_display:>25} [ T+1 ]\n"
                f"    {'—' * 78}"
        )
        error_msg = (
                f"Timestamp causal ordering sanity check failed! "
                f"Number of offending timestamps {len(offending_idx)}/{len(timestamps_)}\n"
                f"[TCT error] Timestamp causal ordering violations:\n\n"
                f"    Offending {shadow_data_container['feature_name']} timestamps:\n"
                f"{offending_ts_header}\n"
                f"{offending_ts}\n"
                f"    Rosbag timestamps metadate:\n"
                f"    {'—' * 78}\n"
                f"                            nanoseconds    ( seconds nanoseconds )\n"
                f"          start: {timestamps_[0].nanoseconds:>22}  "
                f"{str(timestamps_[0].seconds_nanoseconds()):>25} \n"
                f"          stop:  {timestamps_[-1].nanoseconds:>22}  "
                f"{str(timestamps_[-1].seconds_nanoseconds()):>25} \n"
                f"      duration:  "
                f"{(timestamps_[-1].nanoseconds - timestamps_[0].nanoseconds):>22}  \n"
                f"    {'—' * 78}\n"
        )
        raise AssertionError(error_msg)

    return offending_idx
