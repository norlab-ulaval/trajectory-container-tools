# coding=utf-8
import numpy as np
import pandas as pd
import pytest

from rclpy.time import Time as ROSTime

from trajectory_container_tools.utils.data_sanity_checks import (
    timestamp_causal_ordering_sanity_check,
    dataframe_timestep_indexing_sanity_check,
    )


class TestTimestampSanityCheck:

    @pytest.fixture
    def setup_mock_timestamps(self):
        mock_timestamps = [1711038330346603696,
                           1711038330351773872,
                           1711038330362038128,
                           1711038330376558992,
                           1711038330381711344,
                           1711038330391960208,
                           1711038330406476944,
                           1711038330411627056,
                           1711038330421882896,
                           1711038330436485488, ]

        mock_timestamps = [ROSTime(nanoseconds=each) for each in mock_timestamps]

        mock_container = {
                "feature_name": "/mock_topic",
                "timestamps": np.array(mock_timestamps)
                }

        return mock_container

    def test_base_case_pass(self, setup_mock_timestamps):
        assert timestamp_causal_ordering_sanity_check(setup_mock_timestamps) == []

    def test_case_empty_input(self, setup_mock_timestamps):
        setup_mock_timestamps['timestamps'] = []

        with pytest.raises(AssertionError) as exc_info:
            assert timestamp_causal_ordering_sanity_check(setup_mock_timestamps) == [5, 9]

        # print(f"{exc_info=}")
        expected_error_msg = "[TCT error] timestamp array is empty!"
        assert exc_info.value.args == (expected_error_msg,)

    def test_case_non_causal_ordering_detected(self, setup_mock_timestamps):
        setup_mock_timestamps['timestamps'][5] = ROSTime(nanoseconds=1711038330132760208)
        setup_mock_timestamps['timestamps'][9] = ROSTime(nanoseconds=1711038330177285488)

        with pytest.raises(AssertionError) as exc_info:
            assert timestamp_causal_ordering_sanity_check(setup_mock_timestamps) == [5, 9]

#         print(f"{exc_info=}")
        expected_error_msg = (
                f"Timestamp causal ordering sanity check failed! "
                f"Number of offending timestamps 2/10\n"
                f"[TCT error] Timestamp causal ordering violations:"
        )
        assert expected_error_msg in exc_info.value.args[0]


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
        the_dataframe = setup_dataframe_monotonic_col_label()
        tisc = dataframe_timestep_indexing_sanity_check(
                the_dataframe=the_dataframe,
                unindexed_column_label=self.COL_LABEL,
                )

        print(the_dataframe)  # (Priority) ToDo: on task end >> delete this line ←

        assert type(tisc) is np.ndarray

    def test_index_start_non_zero(self, setup_dataframe_monotonic_col_label):
        with pytest.raises(IndexError):
            tisc = dataframe_timestep_indexing_sanity_check(
                    the_dataframe=setup_dataframe_monotonic_col_label(start_index=2),
                    unindexed_column_label=self.COL_LABEL,
                    )

    def test_missing_step(self, setup_dataframe_monotonic_col_label):
        with pytest.raises(IndexError):
            df_missing = setup_dataframe_monotonic_col_label().drop(f"{self.COL_LABEL}9", axis=1)
            tisc = dataframe_timestep_indexing_sanity_check(
                    the_dataframe=df_missing, unindexed_column_label=self.COL_LABEL
                    )
