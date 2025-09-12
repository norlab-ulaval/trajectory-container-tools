# coding=utf-8
import numpy as np
import pandas as pd
import pytest

from trajectory_container_tools.utils.temporal_tools.timestep_indexing import \
    (
    dataframe_timestep_indexing_sanity_check, timestep_indices_sanity_check,
    )


class TestTimestepIndexingSanityCheck:

    def test_base_case_pass(self):
        mock_trj_indices = np.arange(20)

        # Case default arg
        timestep_indices_sanity_check(timestep_index=mock_trj_indices,
                                      trajectory_expected_len=None)

        # Case explicit expected len
        timestep_indices_sanity_check(timestep_index=mock_trj_indices,
                                      trajectory_expected_len=len(mock_trj_indices))

    def test_expect_error(self):
        mock_trj_indices = np.arange(20)
        mock_trj_indices[9] = mock_trj_indices[9] - 1
        expected_error_msg = ('[TCT error] The timestep index is either missing a step or not '
                              'monotonicaly increassing')

        # Case default arg
        with pytest.raises(IndexError) as exc_info:
            timestep_indices_sanity_check(timestep_index=mock_trj_indices,
                                          trajectory_expected_len=None)

        print(f"{exc_info=}")
        assert exc_info.value.args == (expected_error_msg,)

        # Case explicit expected len
        with pytest.raises(IndexError) as exc_info:
            timestep_indices_sanity_check(timestep_index=mock_trj_indices,
                                          trajectory_expected_len=len(mock_trj_indices))

        print(f"{exc_info=}")
        assert exc_info.value.args == (expected_error_msg,)


class TestDataframeTimestepIndexingSanityCheck:
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
        the_dataframe = setup_dataframe_monotonic_col_label()
        tisc = dataframe_timestep_indexing_sanity_check(
                the_dataframe=the_dataframe,
                indexed_column_label=self.COL_LABEL,
                )

        assert type(tisc) is np.ndarray

    def test_index_start_non_zero(self, setup_dataframe_monotonic_col_label):
        tisc = dataframe_timestep_indexing_sanity_check(
                the_dataframe=setup_dataframe_monotonic_col_label(start_index=2),
                indexed_column_label=self.COL_LABEL,
                )

    def test_missing_step(self, setup_dataframe_monotonic_col_label):
        with pytest.raises(IndexError):
            df_missing = setup_dataframe_monotonic_col_label().drop(f"{self.COL_LABEL}9", axis=1)
            tisc = dataframe_timestep_indexing_sanity_check(
                    the_dataframe=df_missing, indexed_column_label=self.COL_LABEL
                    )
