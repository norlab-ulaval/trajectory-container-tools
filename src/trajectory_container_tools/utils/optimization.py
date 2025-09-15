# coding=utf-8
from pickle import PicklingError
import multiprocessing as mp
from typing import Any, Callable

import psutil
from joblib import Parallel, delayed
import os
import numpy as np


def process_large_arrays_parallel(
    data_list,
    enable: bool = True,
    n_jobs=-1,
    chunk_size=1000,
    debug: bool = False,
    array_func: Callable = np.array,
):
    """
    Processes a large list of data into a numpy array, with optional parallelization and chunking.

    This function takes a list of data, divides it into smaller chunks for easier processing,
    and converts each chunk into a numpy array. If parallelization is enabled, it uses joblib
    to process the chunks concurrently using the specified number of jobs. If a PicklingError
    occurs during parallelization, the entire data list is processed as a single numpy array
    instead.

    :param data_list: The list of data to process and convert to a numpy array.
    :param enable: Use multiprocessing (default to True)
    :param chunk_size: The size of each chunk in which the data will be divided. Defaults to 1000.
    :param n_jobs: The number of parallel jobs to run.
        Defaults to -1, which uses all available CPUs.
    :param array_func: A numpy function. Default to np.array
    :param debug: Show debug information
    :return: A numpy array representing the processed input list.
    """
    # (NICE TO HAVE) ToDo: unit-test (curently indirectly tested)

    if enable is False or len(data_list) < chunk_size:
        if debug:
            print("[TCT] process_large_arrays_parallel is disable")
        return np.array(data_list)

    try:
        chunks = [
            data_list[i : i + chunk_size] for i in range(0, len(data_list), chunk_size)
        ]

        # Joblib automatically handles memory-mapping for large arrays
        verbose = 1
        if debug:
            verbose = 8

        chunk_results = Parallel(n_jobs=n_jobs, backend="loky", verbose=verbose)(
            delayed(array_func)(chunk) for chunk in chunks
        )

        return np.concatenate(chunk_results)
    except PicklingError:
        if debug:
            print(
                "[TCT warning] process large arrays parallel ecounter PicklingError. Process "
                "sequentialy instead"
            )
        return np.array(data_list)


def detect_docker_cpu_limits():
    """
    Detect actual CPU resources available in Docker container.
    """
    print(f"[TCT] Docker-aware multiprocessing capabilities check")

    # Standard CPU detection
    mp_cpu_count = mp.cpu_count()
    os_cpu_count = os.cpu_count()

    # Docker-specific checks
    docker_cpu_limit = None
    docker_cpu_quota = None

    # Check Docker CPU quota (if available)
    try:
        with open("/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "r") as f:
            quota = int(f.read().strip())
        with open("/sys/fs/cgroup/cpu/cpu.cfs_period_us", "r") as f:
            period = int(f.read().strip())

        if quota > 0 and period > 0:
            docker_cpu_limit = quota / period
    except (FileNotFoundError, ValueError, OSError):
        # Try cgroup v2 format
        try:
            with open("/sys/fs/cgroup/cpu.max", "r") as f:
                cpu_max = f.read().strip()
            if cpu_max != "max":
                quota, period = cpu_max.split()
                docker_cpu_limit = int(quota) / int(period)
        except (FileNotFoundError, ValueError, OSError):
            pass

    # Check if running in Docker
    is_docker = os.path.exists("/.dockerenv") or os.path.exists("/proc/1/cgroup")

    print(
        (
            f"      Multiprocessing CPU count: {mp_cpu_count}\n"
            f"      OS CPU count: {os_cpu_count}\n"
            f"      Docker CPU limit: {docker_cpu_limit}\n"
            f"      Running in Docker: {is_docker}"
        )
    )

    # Determine optimal worker count
    if docker_cpu_limit and docker_cpu_limit < mp_cpu_count:
        optimal_workers = max(1, int(docker_cpu_limit))
        print(f"[TCT] Docker CPU limit: {optimal_workers} workers")
        return optimal_workers
    else:
        print(f"[TCT] System CPU count: {mp_cpu_count} workers")
        return mp_cpu_count
