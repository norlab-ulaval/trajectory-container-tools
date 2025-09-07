# coding=utf-8
from pickle import PicklingError

import numpy as np
from joblib import Parallel, delayed


def process_large_arrays_parallel(data_list, enable: bool = True, n_jobs=-1, chunk_size=1000,
                                  debug: bool = True):
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
    :param debug: Show debug information
    :return: A numpy array representing the processed input list.
    """
    # (NICE TO HAVE) ToDo: unit-test (curently indirectly tested)

    if enable is False or len(data_list) < chunk_size:
        return np.array(data_list)

    try:
        chunks = [data_list[i:i + chunk_size] for i in range(0, len(data_list), chunk_size)]

        # Joblib automatically handles memory-mapping for large arrays
        verbose = 0
        if debug:
            verbose = 8

        chunk_results = Parallel(n_jobs=n_jobs, backend='loky', verbose=verbose)(
                delayed(np.array)(chunk) for chunk in chunks
                )

        return np.concatenate(chunk_results)
    except PicklingError:
        if debug:
            print(
                    "[TCT warning] process large arrays parallel ecounter PicklingError. Process "
                    "sequentialy instead")
        return np.array(data_list)
