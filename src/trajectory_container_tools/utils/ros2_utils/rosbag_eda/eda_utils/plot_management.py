# coding=utf-8
import warnings
from contextlib import contextmanager

import matplotlib
from matplotlib import pyplot as plt


@contextmanager
def plot_manager(show_plot: bool, headless: bool):
    """
    Context manager for setting up and tearing down a matplotlib plotting environment.

    :param show_plot: Boolean flag to determine if the plot should be displayed.
    :param headless: Boolean flag to determine if the plotting should run without a display
     (useful for server environments).
    :return: None
    """
    with warnings.catch_warnings():
        manage_matplotlib_warnings()
        manage_matplotlib_backend(show_plot, headless)

        yield

        if show_plot:
            # plt.show(block=False)
            plt.show()

        plt.close()
        return None


def manage_matplotlib_backend(show_plot: bool, headless: bool) -> None:
    if headless:
        if not show_plot:
            """
            Standard matplotlib backend:
              - interactive backends: GTK3Agg, GTK3Cairo, GTK4Agg, GTK4Cairo, MacOSX,
              nbAgg, QtAgg,
                  QtCairo, TkAgg, TkCairo, WebAgg, WX, WXAgg, WXCairo, Qt5Agg, Qt5Cairo
              - non-interactive backends: agg, cairo, pdf, pgf, ps, svg
            """
            matplotlib.use("agg")
    else:
        pass
    return None


def manage_matplotlib_warnings() -> None:
    """Note: use inside a context manager.
    Example:

    >>> with warnings.catch_warnings():
    >>>     manage_matplotlib_warnings()
    >>>     ...

    """
    warnings.filterwarnings(
        "ignore",
        message=(
            "Matplotlib is curently using 'agg', a non-GUI backend, so cannot show the figure."
        ),
        category=UserWarning,
    )
    # It's a fix on a recent released version with a special fix for PyCharm IDE
    warnings.filterwarnings("ignore", category=matplotlib.MatplotlibDeprecationWarning)
    return None
