# coding=utf-8
"""
Plotting and visualization utilities for trajectory data.

Usage:
    import trajectory_container_tools as tct
    tct.plot.trajectory_2d(data)
"""

from .utils.plot import (
    plot_trajectory_2d as trajectory_2d
)

__all__ = [
    'trajectory_2d',
]
