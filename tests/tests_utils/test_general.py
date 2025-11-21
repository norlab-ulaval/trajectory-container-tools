# coding=utf-8
import os
from pathlib import Path

import pytest
import numpy as np

from trajectory_container_tools.utils.general import (
    camelcase_to_snake_case,
    check_is_finite,
    dn_sanitize_path,
    extract_class_name_from_type,
    extract_class_name_from_instance,
)


class TestNumpyUtilities:
    def test_check_is_finite(self):
        finite = np.ones((1, 2, 3))

        # Case: input is finite
        assert check_is_finite(finite) is None, "Wrong output type"

        # Case: input is NOT finite
        with pytest.raises(AssertionError) as exc_info:
            not_finite = np.array([1, np.inf, 3])
            assert check_is_finite(not_finite) is None, "Wrong output type"

        print(f"{exc_info=}")
        assert exc_info.value.args == ("Non finite value(s) in x[[1]]",)


class TestStringUtilities:
    def test_extract_class_name_from_instance(self):
        assert extract_class_name_from_instance(np.ones((2, 2))) == "ndarray"
        assert extract_class_name_from_instance("hello") == "str"

    def test_extract_class_name_from_type(self):
        assert extract_class_name_from_type(np.ndarray) == "ndarray"

    def test_extract_class_name_from_type_wrong_arg_expect_fail(self):
        with pytest.raises(AssertionError) as exc_info:
            extract_class_name_from_type(np.array((2, 2)))

        # print(f"{exc_info=}")
        assert exc_info.value.args == (
            'Input arg need to be type "type" but "<class \'numpy.ndarray\'>" was provided!',
        )

    def test_camelcase_to_snake_case(self):
        assert (
            camelcase_to_snake_case("SteeringAngleVelocity")
            == "steering_angle_velocity"
        )
        assert (
            camelcase_to_snake_case("drive_steeringAngleVelocity")
            == "drive_steering_angle_velocity"
        )
        assert (
            camelcase_to_snake_case("drive_SteeringAngleVelocity")
            == "drive__steering_angle_velocity"
        )
        assert camelcase_to_snake_case("MSG") == "m_s_g"


def test_dn_sanitize_path():
    existing_path = os.path.join(
        "data",
        "repository_data",
        "tests_data",
        "dataframe_test_data",
        "marmotte",
        "ga_hard_snow_25_01_a",
        "slip_dataset_all.pkl",
    )

    # Case: relative path
    t_path = dn_sanitize_path(existing_path)
    assert isinstance(t_path, Path)
    assert os.path.basename(t_path) == "slip_dataset_all.pkl"

    # Note: skip test if TCT is a sub-project e.g., run from RLRC or MG
    if os.path.exists(os.path.join("/", "ros2_ws", "src", "trajectory-container-tools")):
        # Case: no dna by bypassing dna env var related logic using an absolute path
        t_path = dn_sanitize_path(
            os.path.join("/", "ros2_ws", "src", "trajectory-container-tools", existing_path)
        )
        assert isinstance(t_path, Path)
        assert os.path.basename(t_path) == "slip_dataset_all.pkl"

    # Case: path does'nt exist
    with pytest.raises(AssertionError) as exc_info:
        dn_sanitize_path("data999")
    print(f"{exc_info=}")
    assert "[TCT] path is unreachable at" in exc_info.value.args[0]
