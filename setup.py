# coding=utf-8

from setuptools import setup
import os


def read_version():
    """Reads and returns the version information from the semantic-versioning generated file.

    :return: The version information as a string.
    """
    version_file = os.path.join(os.path.dirname(__file__), "version.txt")
    with open(version_file, "r") as f:
        return f.read().strip()


setup(version=read_version())

