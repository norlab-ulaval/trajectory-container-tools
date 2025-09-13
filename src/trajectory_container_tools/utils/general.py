# coding=utf-8
import re
from typing import NoReturn, Type, Union, get_args, get_origin, get_type_hints

import numpy as np
from tqdm import tqdm


# :::: Numpy utilities ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def check_is_finite(x: np.ndarray) -> None:
    assert np.all(
            np.isfinite(x)
            ), f"Non finite value(s) in x{np.argwhere(np.isfinite(x) == False)}"
    return None


# :::: String utilities :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def extract_class_name_from_type(data_container_type: Type) -> str:
    """ Extracts the class name from the type provided.

    This function takes a type input and extracts the rightmost name from the class string
    representation of the type. The function will only process objects of type `type` and will
    raise an error otherwise.

    Example:

        >>> extract_class_name_from_type(np.ndarray)
        >>> # "ndarray"

    :param data_container_type: The type from which the class name will be extracted.
    :return: The name of the class extracted from the provided type.
    """
    assert isinstance(data_container_type, type), (
            f"Input arg need to be type \"type\" but \"{type(data_container_type)}\" was "
            f"provided!")
    return _extract_right_most_name_from_class_str(str(data_container_type))


def extract_class_name_from_instance(the_object: object) -> str:
    """Take an object and return the class name as a string

    Example:

        >>> extract_class_name_from_instance(np.ones((2,2)))
        >>> # "ndarray"

    :param the_object: an instance
    :return: the instance class name as a string
    """
    if isinstance(the_object, (str, int, float, tuple, list)):
        return _extract_right_most_name_from_class_str(str(type(the_object))).removeprefix(
                "class ").strip("'")
    else:
        return _extract_right_most_name_from_class_str(str(type(the_object)))


def camelcase_to_snake_case(name: str) -> str:
    """ Converts a string from camelCase to snake_case.

    This function processes a string assumed to be in camelCase format and transforms
    it into snake_case format by inserting underscores before uppercase letters and
    lowercasing all characters.

    Example:

        >>> camelcase_to_snake_case("drive_steeringAngleVelocity")
        >>> # drive_steering_angle_velocity
        >>> camelcase_to_snake_case("drive_SteeringAngleVelocity")
        >>> # drive__steering_angle_velocity

    :param name: The camelCase formatted string that needs to be converted to snake_case.
    :return: A string formatted in snake_case.
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _extract_right_most_name_from_class_str(class_str: str):
    return class_str.lstrip("<").rstrip("'>").split(".")[-1]


def setup_progressbar(feature_msg_len: int) -> tqdm:
    progressbar = tqdm(total=feature_msg_len, desc="       ↳ ",
                       bar_format="{desc}{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}")
    return progressbar

# :::: Typing utilities :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

def extract_first_union_type(type_hint: Type):
    """Safely extract the first type from a Union, or return the type if not a Union."""
    if get_origin(type_hint) is Union:
        return get_args(type_hint)[0] # Return the first element of a Union of types.
    else:
        return type_hint  # Not a Union, return as-is.
