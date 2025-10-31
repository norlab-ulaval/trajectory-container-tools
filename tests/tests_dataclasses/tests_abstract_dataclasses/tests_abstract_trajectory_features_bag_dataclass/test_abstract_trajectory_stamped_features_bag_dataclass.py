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

import trajectory_container_tools as tct


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
class TestAbstractTrajectoryStampedFeaturesBagAllCasses:

    def test_get_chunk_on_timestamps(
        self,
        setup_mock_mf_container,
        t_timestamp_case,
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)

        # Case: chunk_on has a header field
        assert np.array_equal(
            mf_container.get_chunk_on_timestamps().stamps,
            t_timestamp_case.t_act_timestamps,
        )

        # Case: chunk_on as no a header field
        # (Nice to have) ToDo: add test case where chunk_on has no header (ref task TCT-92)

    def test_get_trajectory_first_timestamp(
        self,
        setup_mock_mf_container,
        t_timestamp_case,
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)

        assert (
            mf_container.get_trajectory_first_timestamp()
            == t_timestamp_case.t_trajectorie_stamps.min()
        )
        assert (
            mf_container.get_trajectory_first_timestamp(include_bag_record=False)
            == t_timestamp_case.t_trajectorie_stamps.min()
        )

    def test_get_trajectory_last_timestamp(
        self,
        setup_mock_mf_container,
        t_timestamp_case,
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)

        assert (
            mf_container.get_trajectory_last_timestamp()
            == t_timestamp_case.t_trajectorie_stamps.max() + 333
        )
        assert (
            mf_container.get_trajectory_last_timestamp(include_bag_record=False)
            == t_timestamp_case.t_trajectorie_stamps.max()
        )

    def test_chunks_total(
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
            print(each)
            print("each._iter_index: ", each._iter_index)
            print(
                "topic_mock_observation stamps: ",
                each.topic_mock_observation.header.timestamps.stamps,
            )
            print(
                "topic_mock_action stamps: ",
                each.topic_mock_action.header.timestamps.stamps,
            )

    @pytest.mark.parametrize(
        argnames="t_startpoint, t_endpoint",
        argvalues=[(True, False), (False, True), (True, True), (False, False)],
        ids=[
            "startpoint=True, endpoint=False",
            "startpoint=False, endpoint=True",
            "startpoint=True, endpoint=True",
            "startpoint=False, endpoint=False",
        ],
    )
    def test_get_timestamps(
        self, setup_mock_mf_container, t_timestamp_case, t_startpoint, t_endpoint
    ):
        # (☕minor) ToDo: update unit-test (ref task TCT-91)

        mf_container = setup_mock_mf_container(t_timestamp_case)

        print(f"\n", "=" * 80, f"\n")
        print(mf_container)
        print(f"\n", "=" * 80, f"\n")

        print(t_timestamp_case.t_trajectorie_stamps)

        t_start_idx = 0
        t_stop_idx = 4
        t_start_stamp = int(t_timestamp_case.t_trajectorie_stamps[t_start_idx])
        t_stop_stamp = int(t_timestamp_case.t_trajectorie_stamps[t_stop_idx])

        mf_container_window = mf_container.get_timestamps(
            start=t_start_stamp,
            stop=t_stop_stamp,
            startpoint=t_startpoint,
            endpoint=t_endpoint,
        )

        print(mf_container_window)

        # .... Check topic published timestamps ...................................................
        for each in mf_container.topic_key_list:
            each_field = mf_container_window.get_dynamic_attribute(each)
            if (
                isinstance(each_field, tct.AbstractTrajectoryFeature)
                and each_field.header.timestamps.stamps.size > 0
            ):
                assert t_start_stamp <= each_field.header.timestamps.stamps[0]
                assert each_field.header.timestamps.stamps[-1] <= t_stop_stamp

            assert t_start_stamp <= each_field.bag_recorded_timestamps.stamps[0]
            if t_endpoint:
                assert each_field.bag_recorded_timestamps.stamps[-1] <= t_stop_stamp + 333
            else:
                assert each_field.bag_recorded_timestamps.stamps[-1] <= t_stop_stamp

        # .... Check bag lvl timestamps ...........................................................
        assert t_start_stamp <= mf_container_window.bag_timestamps.stamps[0]
        assert mf_container_window.bag_timestamps.stamps[-1] <= t_stop_stamp

    def test_get_features_timestamps(self, setup_mock_mf_container, t_timestamp_case):
        mf_container = setup_mock_mf_container(t_timestamp_case)
        print(mf_container.trajectory_timestamps)
        assert np.array_equal(
            mf_container.trajectory_timestamps, t_timestamp_case.t_trajectorie_stamps
        )

    def test_get_features_timestamps_limits(
        self, setup_mock_mf_container, t_timestamp_case
    ):
        mf_container = setup_mock_mf_container(t_timestamp_case)
        print(mf_container.trajectory_timestamps_limits)
        assert (
            mf_container.trajectory_timestamps_limits.start_time
            == t_timestamp_case.t_trajectorie_stamps[0]
        )
        assert (
            mf_container.trajectory_timestamps_limits.end_time
            == t_timestamp_case.t_trajectorie_stamps[-1]
        )
        assert (
            mf_container.trajectory_timestamps_limits.duration
            == t_timestamp_case.t_trajectorie_stamps[-1]
            - t_timestamp_case.t_trajectorie_stamps[0]
        )


class TestAbstractTrajectoryStampedFeaturesBagIndexingAndSlicing:

    def test_indexing_case_alternate(self, setup_mock_mf_container):
        mf_container = setup_mock_mf_container(setup_mock_timestamps_case_alternate())

        print(mf_container)

        for idx in range(mf_container.chunks_total - 1):
            print("\n... idx: ", idx, "." * 80)
            print(mf_container[idx])

            assert (
                mf_container[idx].topic_mock_observation.header.timestamps.stamps
                == mf_container.topic_mock_observation[idx + 1].header.timestamps.stamps
            )
            assert (
                mf_container[idx].topic_mock_observation.mock_feature
                == mf_container.topic_mock_observation[idx + 1].mock_feature
            )

            assert (
                mf_container[idx].topic_mock_action.header.timestamps.stamps
                == mf_container.topic_mock_action[idx].header.timestamps.stamps
            )
            assert (
                mf_container[idx].topic_mock_action.mock_feature
                == mf_container.topic_mock_action[idx].mock_feature
            )

    def test_indexing_case_act_and_obs_shared_stamps(self, setup_mock_mf_container):
        """
        Expected behaviour: next-obs should have an arbitrary delay with respect to intervention.
        i.e., (obs, act, next-obs)
        """
        mf_container = setup_mock_mf_container(
            setup_mock_timestamps_case_act_and_obs_shared_stamps()
        )

        print("==== FULL VIEW", "=" * 80, "\n", mf_container, "\n")

        print("==== Indexed VIEW idx: 0", "=" * 71, "\n", mf_container[0], "\n")
        print("=" * 96, "\n")

        assert np.array_equal(
            mf_container[0].topic_mock_observation.header.timestamps.stamps,
            mf_container.topic_mock_observation[2:4].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0].topic_mock_observation.mock_feature,
            mf_container.topic_mock_observation[2:4].mock_feature,
        )

        assert (
            mf_container[0].topic_mock_action.header.timestamps.stamps
            == mf_container.topic_mock_action[0].header.timestamps.stamps
        )
        assert (
            mf_container[0].topic_mock_action.mock_feature
            == mf_container.topic_mock_action[0].mock_feature
        )

        print("==== Indexed VIEW idx: 1", "=" * 71, "\n", mf_container[1], "\n")
        print("=" * 96, "\n")

        assert np.array_equal(
            mf_container[1].topic_mock_observation.header.timestamps.stamps,
            mf_container.topic_mock_observation[4:5].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[1].topic_mock_observation.mock_feature,
            mf_container.topic_mock_observation[4:5].mock_feature,
        )

        assert (
            mf_container[1].topic_mock_action.header.timestamps.stamps
            == mf_container.topic_mock_action[1].header.timestamps.stamps
        )
        assert (
            mf_container[1].topic_mock_action.mock_feature
            == mf_container.topic_mock_action[1].mock_feature
        )

    def test_indexing_case_last_stamp_on_obs(self, setup_mock_mf_container):
        """
        Expected behaviour: next-obs should have an arbitrary delay with respect to intervention.
        i.e., (obs, act, next-obs)
        """
        mf_container = setup_mock_mf_container(
            setup_mock_timestamps_case_last_stamp_on_obs()
        )

        print("==== FULL VIEW", "=" * 80, "\n", mf_container, "\n")

        print("==== Indexed VIEW", "=" * 78, "\n", mf_container[0], "\n")
        print("=" * 96, "\n")

        assert np.array_equal(
            mf_container[0].topic_mock_observation.header.timestamps.stamps,
            mf_container.topic_mock_observation[2:3].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0].topic_mock_observation.mock_feature,
            mf_container.topic_mock_observation[2:3].mock_feature,
        )

        assert (
            mf_container[1].topic_mock_action.header.timestamps.stamps
            == mf_container.topic_mock_action[1].header.timestamps.stamps
        )
        assert (
            mf_container[1].topic_mock_action.mock_feature
            == mf_container.topic_mock_action[1].mock_feature
        )

        # with pytest.raises(IndexError) as exc_info:
        #     print(mf_container[1])

    def test_slicing_case_alternate(self, setup_mock_mf_container):
        mf_container = setup_mock_mf_container(setup_mock_timestamps_case_alternate())

        print("==== FULL VIEW", "=" * 80, "\n", mf_container, "\n")

        print("==== SLICED VIEW", "=" * 78, "\n", mf_container[0:3], "\n")
        print("\n", "=" * 96, "\n")

        assert np.array_equal(
            mf_container[0:3].topic_mock_observation.header.timestamps.stamps,
            mf_container.topic_mock_observation[1:4].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0:3].topic_mock_observation.mock_feature,
            mf_container.topic_mock_observation[1:4].mock_feature,
        )

        assert np.array_equal(
            mf_container[0:3].topic_mock_action.header.timestamps.stamps,
            mf_container.topic_mock_action[0:3].header.timestamps.stamps,
        )
        assert np.array_equal(
            mf_container[0:3].topic_mock_action.mock_feature,
            mf_container.topic_mock_action[0:3].mock_feature,
        )
