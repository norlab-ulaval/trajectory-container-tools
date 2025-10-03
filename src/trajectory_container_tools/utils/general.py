# coding=utf-8
import os
import re
from pathlib import Path
from typing import (
    Any,
    AnyStr,
    NoReturn,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

import numpy as np
from tqdm import tqdm


# :::: Numpy utilities ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def check_is_finite(x: np.ndarray) -> None:
    assert np.all(
        np.isfinite(x)
    ), f"Non finite value(s) in x{np.argwhere(np.isfinite(x) == False)}"
    return None


# :::: String utilities :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def extract_class_name_from_type(data_container_type: type) -> str:
    """Extracts the class name from the type provided.

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
        f'Input arg need to be type "type" but "{type(data_container_type)}" was '
        f"provided!"
    )
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
        return (
            _extract_right_most_name_from_class_str(str(type(the_object)))
            .removeprefix("class ")
            .strip("'")
        )
    else:
        return _extract_right_most_name_from_class_str(str(type(the_object)))


def camelcase_to_snake_case(name: str) -> str:
    """Converts a string from camelCase to snake_case.

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
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _extract_right_most_name_from_class_str(class_str: str):
    return class_str.lstrip("<").rstrip("'>").split(".")[-1]


def setup_progressbar(feature_msg_len: int) -> tqdm:
    progressbar = tqdm(
        total=feature_msg_len,
        desc="       ↳ ",
        bar_format="{desc}{percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}",
    )
    return progressbar


# :::: Typing utilities :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


def is_typing_union(type_hint: type) -> bool:
    return get_origin(type_hint) is Union


def is_typing_list(type_hint: type) -> bool:
    return get_origin(type_hint) is list


def check_typing_union_and_extract_first_union_type(
    type_hint: type,
) -> Tuple[bool, type[Any]]:
    """Safely extract the first type from a Union, or return the type if not a Union."""
    if is_typing_union(type_hint):
        return True, get_args(type_hint)[0]  # Return the Union first type.
    else:
        return False, type_hint  # Not a Union, return as-is.


def check_typing_list_and_extract_list_type(type_hint: type) -> Tuple[bool, type[Any]]:
    """Safely extract the first type from a Union, or return the type if not a Union."""
    if is_typing_list(type_hint):
        return True, get_args(type_hint)[0]  # Return the List first type.
    else:
        return False, type_hint  # Not a List, return as-is.


# :::: Directory related ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def dn_validate_path(rosbag_path: str | Path) -> str:
    """
    dockerized-norlab aware path validation and resolution.

    This function ensures that the given file path exists. If the path is not directly
    accessible, it attempts to resolve it within the context of a "Dockerized-NorLab" (DN)
    environment by combining the path with environment variable `DN_PROJECT_PATH`.

    Handle cases: pycharm-born dna run and shell-born dna run

    :param rosbag_path: The relative or absolute path to the ROS bag file.
    :return: An absolute and resolved path to the ROS bag file.
    :raises AssertionError: If the provided or resolved file path does not exist.
    """
    try:
        assert os.path.exists(rosbag_path)
    except AssertionError:
        dn_project_path = os.getenv("DN_PROJECT_PATH")

        if os.path.exists(dn_project_path):
            # Case running in a Dockerized-NorLab docker container
            rosbag_path = os.path.join(dn_project_path, rosbag_path)

        assert os.path.exists(
            rosbag_path
        ), f"[TCT] rosbag path is unreachable at {rosbag_path}"

    rosbag_path = os.path.realpath(rosbag_path)
    return rosbag_path


def show_directory_content(top_dir: Union[AnyStr, Path]):
    """
    Convenient function for displaying the contents of a given directory, including nested
    directories, formatted in a hierarchical structure.

    The function takes a directory path as the input, checks its contents recursively,
    and prints their hierarchy. It primarily handles items in subdirectories,
    ignores system files like ".DS_Store", and formats them with appropriate indentation.

    :param top_dir: The path to the top-level directory whose contents are to be inspected.
    :return: None
    """
    print("."*80)
    print(f"{top_dir}:")
    resolved_top_path = dn_validate_path(top_dir)
    top_level_entries = os.listdir(resolved_top_path)
    if len(top_level_entries) > 0:
        for each_top in sorted(top_level_entries):
            if each_top != ".DS_Store":
                print(f"    {each_top}:")
            each_top_resolved_path = os.path.join(resolved_top_path, each_top)
            if os.path.isdir(each_top_resolved_path) and len(os.listdir(each_top_resolved_path)) > 0:
                for each in sorted(
                    os.listdir(each_top_resolved_path)
                ):
                    if each != ".DS_Store":
                        each_resolved_path = os.path.join(each_top_resolved_path, each)
                        each_size = get_directory_size_mb(each_resolved_path)
                        print(f"        {each:<60}  {each_size:>6.2f} mb")
    else:
        print(f"    empty")
    return None


def get_directory_size_mb(directory_path):
    """
    Get the total size of a directory in megabytes.

    :param directory_path: Path to the directory
    :return: Size in megabytes (float)
    """
    total_size = 0

    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                # Get file size and add to total
                total_size += os.path.getsize(filepath)
            except (OSError, FileNotFoundError):
                # Skip files that can't be accessed
                pass

    # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
    return total_size / (1024 * 1024)
