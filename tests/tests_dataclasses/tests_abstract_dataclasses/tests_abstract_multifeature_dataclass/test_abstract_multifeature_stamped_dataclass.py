# coding=utf-8
import numpy as np
import pytest

from .conftest import (
    setup_mock_timestamps_case_act_and_obs_shared_stamps,
    setup_mock_timestamps_case_alternate,
    setup_mock_timestamps_case_last_stamp_on_obs,
    setup_mock_timestamps_case_mixing,
    setup_mock_timestamps_case_more_act,
    setup_mock_timestamps_case_more_obs,
)


@pytest.mark.parametrize(
    argnames="t_timestamp_case",
    argvalues=[
        setup_mock_timestamps_case_alternate(),
        setup_mock_timestamps_case_more_obs(),
        setup_mock_timestamps_case_more_act(),
        setup_mock_timestamps_case_act_and_obs_shared_stamps(),
        setup_mock_timestamps_case_last_stamp_on_obs(),
        setup_mock_timestamps_case_mixing(),
    ],
    ids=[
        "Mock timestamps case alternate",
        "Mock timestamps case more obs",
        "Mock timestamps case more act",
        "Mock timestamps case act and obs shared stamps",
        "Mock timestamps case last stamp on obs",
        "Mock timestamps case mixing",
    ],
)
class TestAbstractMultifeatureStampedDataclassAllCasses:

    def test_total_chunks(
        self,
        setup_mock_mf_container,
        t_timestamp_case,
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)
        assert mf_container.chunks_total == t_timestamp_case.t_act_timestamps.size

    def test_len(
        self,
        setup_mock_mf_container,
        t_timestamp_case,
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)
        assert len(mf_container) == t_timestamp_case.t_act_timestamps.size

    def test_string_representation(self, setup_mock_mf_container, t_timestamp_case):
        mf_container = setup_mock_mf_container(t_timestamp_case)
        print(mf_container)

    def test_chunk_iterator(self, setup_mock_mf_container, t_timestamp_case):
        mf_container = setup_mock_mf_container(t_timestamp_case)

        print(f"\n", "=" * 80, f"\n")
        print(mf_container)
        print(f"\n", "=" * 80, f"\n")

        for each in mf_container:
            print(f"\n", "." * 80, f"\n")
            # if each._iter_index == 0:
            #     print(each)
            # print(each)
            print("each._iter_index: ", each._iter_index)
            print(
                "topic_mock_observation stamps: ",
                each.topic_mock_observation.header.timestamps.stamps,
            )
            print(
                "topic_mock_action stamps: ",
                each.topic_mock_action.header.timestamps.stamps,
            )


class TestAbstractMultifeatureStampedDataclassSelectCasses:

    def test_indexing_case_alternate(self, setup_mock_mf_container):
        mf_container = setup_mock_mf_container(setup_mock_timestamps_case_alternate())

        print(mf_container)

        for idx in range(mf_container.chunks_total):
            print("\n... idx: ", idx, "." * 80)
            print(mf_container[idx])

            assert (
                mf_container[idx].topic_mock_observation.header.timestamps.stamps
                == mf_container.topic_mock_observation[idx].header.timestamps.stamps
            )
            assert (
                mf_container[idx].topic_mock_observation.mock_feature
                == mf_container.topic_mock_observation[idx].mock_feature
            )

            assert (
                mf_container[idx].topic_mock_action.header.timestamps.stamps
                == mf_container.topic_mock_action[idx].header.timestamps.stamps
            )
            assert (
                mf_container[idx].topic_mock_action.mock_feature
                == mf_container.topic_mock_action[idx].mock_feature
            )

    def test_slicing_case_alternate(self, setup_mock_mf_container):
        mf_container = setup_mock_mf_container(setup_mock_timestamps_case_alternate())

        print("==== FULL VIEW", "=" * 80, "\n", mf_container, "\n")

        print("==== SLICED VIEW", "=" * 78, "\n", mf_container[0:3], "\n")
        print("\n", "=" * 96, "\n")

        assert np.array_equal(
            mf_container[0:3].topic_mock_observation.header.timestamps.stamps,
            mf_container.topic_mock_observation[0:3].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0:3].topic_mock_observation.mock_feature,
            mf_container.topic_mock_observation[0:3].mock_feature,
        )

        assert np.array_equal(
            mf_container[0:3].topic_mock_action.header.timestamps.stamps,
            mf_container.topic_mock_action[0:3].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0:3].topic_mock_action.mock_feature,
            mf_container.topic_mock_action[0:3].mock_feature,
        )
