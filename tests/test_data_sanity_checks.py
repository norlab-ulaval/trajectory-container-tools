# coding=utf-8
import numpy as np
import pandas as pd
import pytest

from trajectory_container_tools.utils.data_sanity_checks import (
    timestamp_sanity_check,
    timestep_indexing_sanity_check,
)


class TestTimestepIndexingSanityCheck:
    COL_LABEL = "col_"
    ROW_NB = 10
    COL_NB = 40

    @pytest.fixture(scope="function")
    def setup_dataframe_monotonic_col_label(self):
        def _setup_dataframe_monotonic_col_label(start_index=0):
            return pd.DataFrame(
                np.ones((self.ROW_NB, self.COL_NB - start_index)),
                columns=[self.COL_LABEL + str(i) for i in range(start_index, self.COL_NB)],
                index=np.arange(start=0, stop=self.ROW_NB),
            )

        return _setup_dataframe_monotonic_col_label

    def test_base_case_pass(self, setup_dataframe_monotonic_col_label):
        tisc = timestep_indexing_sanity_check(
            the_dataframe=setup_dataframe_monotonic_col_label(),
            unindexed_column_label=self.COL_LABEL,
        )
        assert type(tisc) is np.ndarray

    def test_index_start_non_zero(self, setup_dataframe_monotonic_col_label):
        with pytest.raises(IndexError):
            tisc = timestep_indexing_sanity_check(
                the_dataframe=setup_dataframe_monotonic_col_label(start_index=2),
                unindexed_column_label=self.COL_LABEL,
            )

    def test_missing_step(self, setup_dataframe_monotonic_col_label):
        with pytest.raises(IndexError):
            df_missing = setup_dataframe_monotonic_col_label().drop(f"{self.COL_LABEL}9", axis=1)
            tisc = timestep_indexing_sanity_check(
                the_dataframe=df_missing, unindexed_column_label=self.COL_LABEL
            )


class TestTimestampSanityCheck:
    @pytest.mark.skip(reason="ToDo: unit-test")
    def test_base_case_pass(self):
        raise NotImplementedError(
            "(Priority) ToDo: unit-test (its tested indirectly at the moment)"
        )  # todo
        timestamp_sanity_check()
