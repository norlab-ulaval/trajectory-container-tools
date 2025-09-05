# coding=utf-8

import pytest
import numpy as np

from trajectory_container_tools.utils.general import (
    camelcase_to_snake_case, check_is_finite, extract_class_name_from_type,
    extract_class_name_from_instance,
    )


class TestNumpyUtilities:

    def test_check_is_finite(self):
        finite = np.ones((1, 2, 3))

        # Case: input is finite
        assert check_is_finite(finite) is None, "Wrong output type"

        # Case: input is NOT finite
        with pytest.raises(AssertionError) as exc_info:
            not_finite = np.array([1, np.infty, 3])
            assert check_is_finite(not_finite) is None, "Wrong output type"

        print(f"{exc_info=}")
        assert exc_info.value.args == ('Non finite value(s) in x[[1]]',)


class TestStringUtilities:

    def test_extract_class_name_from_instance(self):
        assert extract_class_name_from_instance(np.ones((2, 2))) == "ndarray"
        assert extract_class_name_from_instance('hello') == "str"

    def test_extract_class_name_from_type(self):
        assert extract_class_name_from_type(np.ndarray) == "ndarray"

    def test_extract_class_name_from_type_wrong_arg_expect_fail(self):
        with pytest.raises(AssertionError) as exc_info:
            extract_class_name_from_type(np.array((2, 2)))

        # print(f"{exc_info=}")
        assert exc_info.value.args == (
                'Input arg need to be type "type" but "<class \'numpy.ndarray\'>" was provided!',)

    def test_camelcase_to_snake_case(self):
        assert camelcase_to_snake_case("SteeringAngleVelocity") == "steering_angle_velocity"
        assert camelcase_to_snake_case(
                "drive_steeringAngleVelocity") == "drive_steering_angle_velocity"
        assert camelcase_to_snake_case(
                "drive_SteeringAngleVelocity") == "drive__steering_angle_velocity"
        assert camelcase_to_snake_case("MSG") == "m_s_g"
