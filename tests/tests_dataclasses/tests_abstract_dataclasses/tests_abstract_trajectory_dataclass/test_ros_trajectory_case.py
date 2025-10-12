# coding=utf-8

import pytest
import numpy as np

from ..mock_trj_dataclasses import (
    MockTrajectoryChildRosBagCase,
    )
from trajectory_container_tools.dataclasses.core.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
)
from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    StatePose2D,
)


class TestAbstractTrajectoryDataclassROSbagCase:
    @pytest.fixture
    def setup_mock_feature_child(
        self, mock_ROSbag_2_trj_DC
    ) -> MockTrajectoryChildRosBagCase:
        return MockTrajectoryChildRosBagCase(
            feature_name=mock_ROSbag_2_trj_DC.name,
            aa=mock_ROSbag_2_trj_DC.a,
            bb=mock_ROSbag_2_trj_DC.b,
            cc=mock_ROSbag_2_trj_DC.c,
            timesteps_indices=mock_ROSbag_2_trj_DC.ts_idx,
        )

    @pytest.fixture
    def setup_mock_feature_child_range(
        self, mock_ROSbag_2_trj_DC_range
    ) -> MockTrajectoryChildRosBagCase:
        return MockTrajectoryChildRosBagCase(
            feature_name=mock_ROSbag_2_trj_DC_range.name,
            aa=mock_ROSbag_2_trj_DC_range.a,
            bb=mock_ROSbag_2_trj_DC_range.b,
            cc=mock_ROSbag_2_trj_DC_range.c,
            timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
        )

    def test_FeatureDataclass_baseclass_not_instantiable(self):
        with pytest.raises(TypeError):
            shouldfail = AbstractTrajectoryDataclass(feature_name="try_to_do_it")

    def test_class_feature_post_init_base(
        self, setup_mock_feature_child, mock_ROSbag_2_trj_DC
    ):
        mfc = setup_mock_feature_child
        assert mfc.aa.size == mfc.bb.size
        assert mfc.bb.size * 36 == mfc.cc.size

        assert np.array_equal(
            mfc.dd_metadata, np.array([99, 99, 99])
        ), f"{mfc.dd_metadata=} != np.array([99, 99, 99])"  # test
        # on_begin_post_init_callback

        assert np.array_equal(
            mfc.aa_init, mock_ROSbag_2_trj_DC.a[0, ...]
        ), f"{mfc.aa_init=} != {mock_ROSbag_2_trj_DC.a[0, ...]=}"  # test
        # post_init_feature_callback `aa_init` is a dynamicaly created field

        # Check each post-init-callback overriden method was hit
        assert mfc.__getattribute__("test_on_begin_post_init_callback") == True
        assert mfc.__getattribute__("test_post_init_feature_callback") == True
        assert mfc.__getattribute__("test_on_exit_post_init_callback") == True

    def test_class_feature_post_init_check(
        self, mock_ROSbag_2_trj_DC_uneven_time_index
    ):
        with pytest.raises(ValueError):
            mfc_u = MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_uneven_time_index.name,
                aa=mock_ROSbag_2_trj_DC_uneven_time_index.a,
                bb=mock_ROSbag_2_trj_DC_uneven_time_index.b,
                cc=mock_ROSbag_2_trj_DC_uneven_time_index.c,
                timesteps_indices=mock_ROSbag_2_trj_DC_uneven_time_index.ts_idx,
            )

    def test_get_dimension_names(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mfc = setup_mock_feature_child
        for each in ("feature_name", "timesteps_indices"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        assert mfc.feature_name is mock_ROSbag_2_trj_DC.name
        assert ("aa", "bb", "cc", "dd_metadata") == mfc.get_dimension_names()

    def test_get_dimension_type(self, setup_mock_feature_child):
        mfc = setup_mock_feature_child
        dimension_type, is_list_of_type = mfc.get_dimension_type("aa")
        assert issubclass(dimension_type, np.ndarray)

    def test_set_dynamic_field(self, setup_mock_feature_child):
        mfc = setup_mock_feature_child

        # Case override field
        mfc.set_dynamic_field("aa", None)
        assert mfc.aa is None

        # Case create new field
        mfc.set_dynamic_field("new_field", "new-field-value")
        assert mfc.new_field == "new-field-value"

    def test_get_dynamic_field(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mfc = setup_mock_feature_child
        # Note: should work even if the trj data container has a flat structure
        assert np.allclose(mfc.get_dynamic_field("aa"), mock_ROSbag_2_trj_DC.a)

    @pytest.mark.deprecated(
        "Method fetch_nested_attribute is marked as deprecated (ref task TCT-65)"
    )
    def test_fetch_nested_attribute(
        self, setup_mock_feature_child, mock_ROSbag_2_trj_DC
    ):
        # Note: should work even if the trj data container has a flat structure
        mfc = setup_mock_feature_child
        assert np.allclose(mfc.fetch_nested_attribute("aa"), mock_ROSbag_2_trj_DC.a)

    def test_get_dimension_names_on_uninstiated_class(self):
        stp = StatePose2D
        stp.get_dimension_names()

    def test_string_representation(
        self, setup_mock_feature_child, mock_ROSbag_2_trj_DC
    ):
        mdc = setup_mock_feature_child
        print(mdc)  # <- Don't comment this line

    def test_trajectory_len(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mdc = setup_mock_feature_child
        assert mdc.trajectory_len == mock_ROSbag_2_trj_DC.a.shape[mdc._time_axis]

    # @pytest.mark.skip(reason="todo")
    def test_ravel_dimensions_in_place(
        self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range
    ):
        mdc = setup_mock_feature_child_range
        mdc.ravel_dimensions_in_place()
        assert mdc.aa.shape[0] == mdc.trajectory_len
        assert mdc.cc.shape[0] == mdc.trajectory_len * 36
        # mdc.aa
        # mdc.bb
        # mdc.cc
        # mdc.get_dimension_names()
        # print(mdc)
        # (Priority) ToDo: implement test asserting a range

    def test_get_item(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        mdc_at_t0 = mdc[0]

        assert isinstance(mdc_at_t0, type(mdc))

        assert mdc_at_t0.aa.size == 1
        assert mdc_at_t0.bb.size == 1
        assert mdc_at_t0.cc.size == 36
        assert mdc_at_t0.timesteps_indices.size == 1
        assert mdc_at_t0.aa == mdc.aa[0]
        assert mdc_at_t0.bb == mdc.bb[0]
        assert np.array_equal(mdc_at_t0.cc, np.arange(mdc.cc.shape[-1]))
        assert mdc_at_t0.timesteps_indices == mdc.timesteps_indices[0]
        # mdc.get_dimension_names()
        # print(mdc)
        # print(mdc_at_t0)

    def test_iterator(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mdc):
            assert isinstance(mdc_at_t, type(mdc))

            assert mdc_at_t.aa == mdc.aa[t]
            assert mdc_at_t.bb == mdc.bb[t]
            cc_feature_size = mdc.cc[t].shape[-1]
            assert np.array_equal(
                mdc_at_t.cc, np.arange(cc_feature_size) + mdc.cc[t, 0]
            )
            assert mdc_at_t.timesteps_indices == mdc.timesteps_indices[t]
            # mdc.get_dimension_names()
            # print(mdc_at_t)

    def test_transpose(
        self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range
    ):
        t_ref = mock_ROSbag_2_trj_DC_range
        mdc = setup_mock_feature_child_range

        assert mdc._transposed == False
        assert mdc._time_axis == 0
        assert mdc.current_trj_axe == 0

        assert mdc.trajectory_len == 40
        assert mdc.aa.shape == (40,)
        assert mdc.bb.shape == (40,)
        assert mdc.cc.shape == (40, 36)
        assert mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(mdc.aa, t_ref.a)
        assert np.array_equal(mdc.bb, t_ref.b)
        assert np.array_equal(mdc.cc, t_ref.c)
        # print(mdc)

        t_mdc = mdc.T

        assert t_mdc._transposed == True
        assert t_mdc._time_axis == 0
        assert t_mdc.current_trj_axe == -1

        assert t_mdc.trajectory_len == 40
        assert t_mdc.aa.shape == (40,)
        assert t_mdc.bb.shape == (40,)
        assert t_mdc.cc.shape == (36, 40)
        assert t_mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.cc, t_ref.c.T)
        # print(t_mdc)
        # print(t_mdc.get_dimension_names())

        t_mdc2 = t_mdc.T

        assert t_mdc2._transposed == False
        assert t_mdc2._time_axis == 0
        assert t_mdc2.current_trj_axe == 0

        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.aa.shape == (40,)
        assert t_mdc2.bb.shape == (40,)
        assert t_mdc2.cc.shape == (40, 36)
        assert t_mdc2.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc2.aa, t_ref.a)
        assert np.array_equal(t_mdc2.bb, t_ref.b)
        assert np.array_equal(t_mdc2.cc, t_ref.c)
        # print(t_mdc2)
        # print(t_mdc2.get_dimension_names())
