# coding=utf-8
from copy import deepcopy
from typing import Union

import pytest
import numpy as np
from dataclasses import dataclass, field

from typing_extensions import Callable

from trajectory_container_tools.trj_dataclasses.abstract_trajectory_dataclass import (
    AbstractTrajectoryDataclass,
    )
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import \
    StatePose2D


@dataclass
class MockTrajectoryChildDFcase(AbstractTrajectoryDataclass):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: np.ndarray = np.array([0, 0, 0])

    @property
    def _init_trj_axe(self) -> int:
        return -1

    @classmethod
    def trajectory_metadata_field(cls):
        return super().trajectory_metadata_field() + ["dd_metadata"]

    def on_begin_post_init_callback(self):
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[..., 0]
        self.__setattr__(f"{feature_name}_init", feature_ini)

        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryChildRosBagCase(AbstractTrajectoryDataclass):
    aa: np.ndarray
    bb: np.ndarray
    cc: np.ndarray
    dd_metadata: np.ndarray = np.array([0, 0, 0])

    @property
    def _init_trj_axe(self) -> int:
        return 0

    @classmethod
    def trajectory_metadata_field(cls):
        return super().trajectory_metadata_field() + ["dd_metadata"]

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)

        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[0, ...]
        self.__setattr__(f"{feature_name}_init", feature_ini)

        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryComposedParent(AbstractTrajectoryDataclass):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase
    aa: np.ndarray

    @property
    def _init_trj_axe(self) -> int:
        return 0

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


@dataclass
class MockTrajectoryComposedParentNestedOnly(AbstractTrajectoryDataclass):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase

    @property
    def _init_trj_axe(self) -> int:
        return 0

    def on_begin_post_init_callback(self):  # self.dd_metadata += 99
        # Create test attribute for post-init-callback logic
        self.__setattr__("test_on_begin_post_init_callback", True)
        self.__setattr__("test_post_init_feature_callback", False)
        self.__setattr__("test_on_exit_post_init_callback", False)
        return None

    def post_init_feature_callback(self, feature_name):
        self.__setattr__("test_post_init_feature_callback", True)
        return None

    def on_exit_post_init_callback(self) -> None:
        self.__setattr__("test_on_exit_post_init_callback", True)
        return None


class TestAbstractTrajectoryDataclassDataframeCase:

    @pytest.fixture
    def setup_mock_feature_child(self, mock_DF_2_trj_DC):
        return MockTrajectoryChildDFcase(
                feature_name=mock_DF_2_trj_DC.name,
                aa=mock_DF_2_trj_DC.a,
                bb=mock_DF_2_trj_DC.b,
                cc=mock_DF_2_trj_DC.c,
                timesteps_indices=mock_DF_2_trj_DC.ts,
                )

    @pytest.fixture
    def setup_mock_feature_child_range(self, mock_DF_2_trj_DC_range):
        return MockTrajectoryChildDFcase(
                feature_name=mock_DF_2_trj_DC_range.name,
                aa=mock_DF_2_trj_DC_range.a,
                bb=mock_DF_2_trj_DC_range.b,
                cc=mock_DF_2_trj_DC_range.c,
                timesteps_indices=mock_DF_2_trj_DC_range.ts,
                )

    def test_FeatureDataclass_baseclass_not_instantiable(self):
        with pytest.raises(TypeError):
            shouldfail = AbstractTrajectoryDataclass(feature_name="try_to_do_it")

    def test_class_feature_post_init_base(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mfc = setup_mock_feature_child
        assert mfc.aa.size == mfc.bb.size
        assert mfc.bb.size == mfc.cc.size

        assert np.array_equal(
                mfc.dd_metadata, np.array([99, 99, 99])
                ), f"{mfc.dd_metadata=} != np.array([99, 99, 99])"  # test on_begin_post_init_callback

        # ★ post_init_feature_callback `aa_init` is a dynamicaly created field
        assert np.array_equal(
                mfc.aa_init, mock_DF_2_trj_DC.a[..., 0]
                ), f"{mfc.aa_init=} != {mock_DF_2_trj_DC.a[..., 0]=}"  # test

        # Check each post-init-callback overriden method was hit
        assert mfc.__getattribute__("test_on_begin_post_init_callback") == True
        assert mfc.__getattribute__("test_post_init_feature_callback") == True
        assert mfc.__getattribute__("test_on_exit_post_init_callback") == True

    def test_class_feature_post_init_check(self, mock_DF_2_trj_DC_uneven_time_index):
        with pytest.raises(ValueError):
            mfc_u = MockTrajectoryChildDFcase(
                    feature_name=mock_DF_2_trj_DC_uneven_time_index.name,
                    aa=mock_DF_2_trj_DC_uneven_time_index.a,
                    bb=mock_DF_2_trj_DC_uneven_time_index.b,
                    cc=mock_DF_2_trj_DC_uneven_time_index.c,
                    timesteps_indices=mock_DF_2_trj_DC_uneven_time_index.ts,
                    )

    def test_get_dimension_names(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mfc = setup_mock_feature_child
        for each in ("feature_name", "timesteps_indices"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        assert mfc.feature_name is mock_DF_2_trj_DC.name
        assert ("aa", "bb", "cc", "dd_metadata") == mfc.get_dimension_names()

    def test_get_dimension_type(self, setup_mock_feature_child):
        mfc = setup_mock_feature_child
        assert issubclass(mfc.get_dimension_type("aa"), np.ndarray)

    def test_set_dynamic_field(self, setup_mock_feature_child):
        mfc = setup_mock_feature_child

        # Case override field
        mfc.set_dynamic_field("aa", None)
        assert mfc.aa is None

        # Case create new field
        mfc.set_dynamic_field("new_field", "new-field-value")
        assert mfc.new_field == "new-field-value"

    def test_get_dynamic_field(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mfc = setup_mock_feature_child
        assert np.allclose(mfc.get_dynamic_field("aa"),
                           mock_DF_2_trj_DC.a)

    def test_fetch_nested_attribute(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        # Note: should work even if the trj data container has a flat structure
        mfc = setup_mock_feature_child
        assert np.allclose(mfc.fetch_nested_attribute("aa"), mock_DF_2_trj_DC.a)

    def test_get_dimension_names_on_uninstiated_class(self):
        stp = StatePose2D
        stp.get_dimension_names()

    def test_string_representation(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mdc = setup_mock_feature_child
        #print(mdc) # <- Don't comment this line

    def test_trajectory_len(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mdc = setup_mock_feature_child
        assert mdc.trajectory_len == mock_DF_2_trj_DC.a.shape[1]

    def test_ravel_dimensions_in_place(
            self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range
            ):
        mdc = setup_mock_feature_child_range
        mdc.ravel_dimensions_in_place()
        assert mdc.aa.shape == (
                mock_DF_2_trj_DC_range.a.shape[0] * mock_DF_2_trj_DC_range.a.shape[1],
                )
        assert mdc.bb.shape == (
                mock_DF_2_trj_DC_range.b.shape[0] * mock_DF_2_trj_DC_range.b.shape[1],
                )
        assert mdc.cc.shape == (
                mock_DF_2_trj_DC_range.c.shape[0] * mock_DF_2_trj_DC_range.c.shape[1],
                )
        #print(mdc)
        # (Priority) ToDo: implement test asserting a range

    def test_get_item(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        mdc_at_t0 = mdc[0]

        assert isinstance(mdc_at_t0, type(mdc))

        assert mdc_at_t0.aa.size == 10
        assert mdc_at_t0.bb.size == 10
        assert mdc_at_t0.cc.size == 10
        assert mdc_at_t0.timesteps_indices.size == 1
        assert np.array_equal(mdc_at_t0.aa, np.arange(mdc.aa.shape[0]))
        assert np.array_equal(mdc_at_t0.bb, np.arange(mdc.bb.shape[0]))
        assert np.array_equal(mdc_at_t0.cc, np.arange(mdc.cc.shape[0]))
        assert mdc_at_t0.timesteps_indices == mdc.timesteps_indices[0]
        # mdc.get_dimension_names()
        #print(mdc)
        #print(mdc_at_t0)

    def test_iterator(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mdc):
            assert isinstance(mdc_at_t, type(mdc))

            assert np.array_equal(mdc_at_t.aa, np.arange(mdc.aa.shape[0]) + mdc.aa[0, t])
            assert np.array_equal(mdc_at_t.bb, np.arange(mdc.bb.shape[0]) + mdc.bb[0, t])
            assert np.array_equal(mdc_at_t.cc, np.arange(mdc.cc.shape[0]) + mdc.cc[0, t])
            assert mdc_at_t.timesteps_indices == mdc.timesteps_indices[t]
            # mdc.get_dimension_names()
            #print(mdc_at_t)

    def test_transpose(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        t_ref = mock_DF_2_trj_DC_range
        mdc = setup_mock_feature_child_range

        assert mdc._transposed == False
        assert mdc._init_trj_axe == -1
        assert mdc.current_trj_axe == -1

        assert mdc.trajectory_len == 40
        assert mdc.aa.shape == (10, 40)
        assert mdc.bb.shape == (10, 40)
        assert mdc.cc.shape == (10, 40)
        assert mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(mdc.aa, t_ref.a)
        assert np.array_equal(mdc.bb, t_ref.b)
        assert np.array_equal(mdc.cc, t_ref.c)
        #print(mdc)

        t_mdc = mdc.T

        assert t_mdc._transposed == True
        assert t_mdc._init_trj_axe == -1
        assert t_mdc.current_trj_axe == 0

        assert t_mdc.trajectory_len == 40
        assert t_mdc.aa.shape == (40, 10)
        assert t_mdc.bb.shape == (40, 10)
        assert t_mdc.cc.shape == (40, 10)
        assert t_mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.cc, t_ref.c.T)
        #print(t_mdc)
        #print(t_mdc.get_dimension_names())

        t_mdc2 = t_mdc.T

        assert t_mdc2._transposed == False
        assert t_mdc2._init_trj_axe == -1
        assert t_mdc2.current_trj_axe == -1

        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.aa.shape == (10, 40)
        assert t_mdc2.bb.shape == (10, 40)
        assert t_mdc2.cc.shape == (10, 40)
        assert t_mdc2.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc2.aa, t_ref.a)
        assert np.array_equal(t_mdc2.bb, t_ref.b)
        assert np.array_equal(t_mdc2.cc, t_ref.c)
        #print(t_mdc2)
        #print(t_mdc2.get_dimension_names())


class TestAbstractTrajectoryDataclassROSbagCase:

    @pytest.fixture
    def setup_mock_feature_child(self, mock_ROSbag_2_trj_DC) -> MockTrajectoryChildRosBagCase:
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

    def test_class_feature_post_init_base(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mfc = setup_mock_feature_child
        assert mfc.aa.size == mfc.bb.size
        assert mfc.bb.size * 36 == mfc.cc.size

        assert np.array_equal(
                mfc.dd_metadata, np.array([99, 99, 99])
                ), f"{mfc.dd_metadata=} != np.array([99, 99, 99])"  # test on_begin_post_init_callback

        assert np.array_equal(
                mfc.aa_init, mock_ROSbag_2_trj_DC.a[0, ...]
                ), f"{mfc.aa_init=} != {mock_ROSbag_2_trj_DC.a[0, ...]=}"  # test
        # post_init_feature_callback `aa_init` is a dynamicaly created field

        # Check each post-init-callback overriden method was hit
        assert mfc.__getattribute__("test_on_begin_post_init_callback") == True
        assert mfc.__getattribute__("test_post_init_feature_callback") == True
        assert mfc.__getattribute__("test_on_exit_post_init_callback") == True

    def test_class_feature_post_init_check(self, mock_ROSbag_2_trj_DC_uneven_time_index):
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
        assert issubclass(mfc.get_dimension_type("aa"), np.ndarray)

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
        assert np.allclose(mfc.get_dynamic_field("aa"),
                           mock_ROSbag_2_trj_DC.a)

    def test_fetch_nested_attribute(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        # Note: should work even if the trj data container has a flat structure
        mfc = setup_mock_feature_child
        assert np.allclose(mfc.fetch_nested_attribute("aa"), mock_ROSbag_2_trj_DC.a)

    def test_get_dimension_names_on_uninstiated_class(self):
        stp = StatePose2D
        stp.get_dimension_names()

    def test_string_representation(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mdc = setup_mock_feature_child
        print(mdc) # <- Don't comment this line

    def test_trajectory_len(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mdc = setup_mock_feature_child
        assert mdc.trajectory_len == mock_ROSbag_2_trj_DC.a.shape[mdc._init_trj_axe]

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
        #print(mdc)
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
        #print(mdc)
        #print(mdc_at_t0)

    def test_iterator(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mdc):
            assert isinstance(mdc_at_t, type(mdc))

            assert mdc_at_t.aa == mdc.aa[t]
            assert mdc_at_t.bb == mdc.bb[t]
            cc_feature_size = mdc.cc[t].shape[-1]
            assert np.array_equal(mdc_at_t.cc, np.arange(cc_feature_size) + mdc.cc[t, 0])
            assert mdc_at_t.timesteps_indices == mdc.timesteps_indices[t]
            # mdc.get_dimension_names()
            #print(mdc_at_t)

    def test_transpose(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        t_ref = mock_ROSbag_2_trj_DC_range
        mdc = setup_mock_feature_child_range

        assert mdc._transposed == False
        assert mdc._init_trj_axe == 0
        assert mdc.current_trj_axe == 0

        assert mdc.trajectory_len == 40
        assert mdc.aa.shape == (40,)
        assert mdc.bb.shape == (40,)
        assert mdc.cc.shape == (40, 36)
        assert mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(mdc.aa, t_ref.a)
        assert np.array_equal(mdc.bb, t_ref.b)
        assert np.array_equal(mdc.cc, t_ref.c)
        #print(mdc)

        t_mdc = mdc.T

        assert t_mdc._transposed == True
        assert t_mdc._init_trj_axe == 0
        assert t_mdc.current_trj_axe == -1

        assert t_mdc.trajectory_len == 40
        assert t_mdc.aa.shape == (40,)
        assert t_mdc.bb.shape == (40,)
        assert t_mdc.cc.shape == (36, 40)
        assert t_mdc.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.cc, t_ref.c.T)
        #print(t_mdc)
        #print(t_mdc.get_dimension_names())

        t_mdc2 = t_mdc.T

        assert t_mdc2._transposed == False
        assert t_mdc2._init_trj_axe == 0
        assert t_mdc2.current_trj_axe == 0

        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.aa.shape == (40,)
        assert t_mdc2.bb.shape == (40,)
        assert t_mdc2.cc.shape == (40, 36)
        assert t_mdc2.timesteps_indices.shape == (40,)
        assert np.array_equal(t_mdc2.aa, t_ref.a)
        assert np.array_equal(t_mdc2.bb, t_ref.b)
        assert np.array_equal(t_mdc2.cc, t_ref.c)
        #print(t_mdc2)
        #print(t_mdc2.get_dimension_names())


@pytest.mark.parametrize(
        argnames="t_nested_case",
        argvalues=[
                "nested-and-ndarray",
                "nested-only",
                ],
        ids=["t_nested_case=nested-and-ndarray", "t_nested_case=nested-only"],
        )
class TestAbstractTrajectoryDataclassNestedROSbagCase:

    @pytest.fixture(scope="function")
    def setup_mock_feature_child(self, mock_ROSbag_2_trj_DC) -> MockTrajectoryChildRosBagCase:
        return MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC.name,
                aa=mock_ROSbag_2_trj_DC.a,
                bb=mock_ROSbag_2_trj_DC.b,
                cc=mock_ROSbag_2_trj_DC.c,
                #timesteps_indices=mock_ROSbag_2_trj_DC.ts_idx,
                )

    @pytest.fixture(scope="function")
    def setup_mock_feature_child_range(
            self, mock_ROSbag_2_trj_DC_range
            ) -> MockTrajectoryChildRosBagCase:
        return MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_range.name,
                aa=mock_ROSbag_2_trj_DC_range.a,
                bb=mock_ROSbag_2_trj_DC_range.b,
                cc=mock_ROSbag_2_trj_DC_range.c,
                #timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
                )

    @pytest.fixture(scope="function")
    def setup_mock_feature_parent_range(self, mock_ROSbag_2_trj_DC_range):
        the_child_one = MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_range.name,
                aa=mock_ROSbag_2_trj_DC_range.a,
                bb=mock_ROSbag_2_trj_DC_range.b,
                cc=mock_ROSbag_2_trj_DC_range.c,
                #timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
                )
        the_child_two = MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_range.name + "-two",
                aa=mock_ROSbag_2_trj_DC_range.a,
                bb=mock_ROSbag_2_trj_DC_range.b,
                cc=mock_ROSbag_2_trj_DC_range.c,
                #timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
                )

        assert the_child_one is not the_child_two

        def instanciate_nested_case(nested_case: str):
            if nested_case == "nested-and-ndarray":
                mock_parent_dataclass = MockTrajectoryComposedParent(
                        feature_name="Parent",
                        child_one=the_child_one,
                        child_two=the_child_two,
                        aa=mock_ROSbag_2_trj_DC_range.a,
                        #timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
                        )
            else:
                mock_parent_dataclass = MockTrajectoryComposedParentNestedOnly(
                        feature_name="Parent nested only",
                        child_one=the_child_one,
                        child_two=the_child_two,
                        #timesteps_indices=mock_ROSbag_2_trj_DC_range.ts_idx,
                        )

            return mock_parent_dataclass

        yield instanciate_nested_case
        del the_child_one, the_child_two

    def test_class_feature_post_init_base(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)

        # .... Sanity check .......................................................................
        assert mfc.child_one is not mfc.child_two

        # .... execute tests ......................................................................
        assert mfc.trajectory_len == mfc.child_one.trajectory_len == mfc.child_two.trajectory_len
        if isinstance(mfc, MockTrajectoryComposedParent):
            assert mfc.child_one.aa.size == mfc.aa.size

        #print(mfc)

        for child_name, each_child in [("child_one", mfc.child_one), ("child_two", mfc.child_two)]:
            assert np.array_equal(
                    each_child.dd_metadata, np.array([99, 99, 99])
                    ), (  # test on_begin_post_init_callback
                    f"{child_name}.dd_metadata={each_child.dd_metadata} != np.array([99, 99, 99])"
            )

            assert np.array_equal(each_child.aa_init, mock_ROSbag_2_trj_DC_range.a[0, ...]), (
                    # post_init_feature_callback `aa_init` is a dynamicaly created field  # test
                    f"{child_name}.aa_init={each_child.aa_init}"
                    f" != {mock_ROSbag_2_trj_DC_range.a[0, ...]=}"
            )

        # Check each post-init-callback overriden method was hit
        assert mfc.__getattribute__("test_on_begin_post_init_callback") == True
        assert mfc.__getattribute__("test_post_init_feature_callback") == True
        assert mfc.__getattribute__("test_on_exit_post_init_callback") == True
        assert mfc.child_one.__getattribute__("test_on_begin_post_init_callback") == True
        assert mfc.child_one.__getattribute__("test_post_init_feature_callback") == True
        assert mfc.child_one.__getattribute__("test_on_exit_post_init_callback") == True

    def test_post_init_check_unexpected_timestep_indices_len(
            self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_longer_range, t_nested_case
            ):
        if t_nested_case == "nested-and-ndarray":
            with pytest.raises((ValueError, AttributeError, AssertionError)) as exc_info:
                mfc_u = MockTrajectoryComposedParent(
                        feature_name="Parent uneven",
                        child_one=setup_mock_feature_child_range,
                        child_two=MockTrajectoryChildRosBagCase(
                                feature_name=mock_ROSbag_2_trj_DC_longer_range.name,
                                aa=mock_ROSbag_2_trj_DC_longer_range.a,
                                bb=mock_ROSbag_2_trj_DC_longer_range.b,
                                cc=mock_ROSbag_2_trj_DC_longer_range.c,
                                timesteps_indices=mock_ROSbag_2_trj_DC_longer_range.ts_idx,
                                ),
                        aa=setup_mock_feature_child_range.aa,
                        timesteps_indices=setup_mock_feature_child_range.timesteps_indices,
                        )
            print(f"{exc_info=}")
            assert exc_info.value.args == ("[TCT error] timesteps_indices expecte lemgth 49 != 40",)

    def test_post_init_check_timestep_indices_not_monoticaly_increassing(
            self, setup_mock_feature_child_range, t_nested_case
            ):
        if t_nested_case == "nested-and-ndarray":
            with pytest.raises(IndexError) as exc_info:
                indices_with_jump = setup_mock_feature_child_range.timesteps_indices
                indices_with_jump[3] = indices_with_jump[3] -10
                mfc_u = MockTrajectoryComposedParent(
                        feature_name="Parent uneven",
                        child_one=setup_mock_feature_child_range,
                        child_two=MockTrajectoryChildRosBagCase(
                                feature_name="child 2",
                                aa=setup_mock_feature_child_range.aa,
                                bb=setup_mock_feature_child_range.bb,
                                cc=setup_mock_feature_child_range.cc,
                                timesteps_indices=setup_mock_feature_child_range.timesteps_indices,
                                ),
                        aa=setup_mock_feature_child_range.aa,
                        timesteps_indices=indices_with_jump,
                        )
            print(f"{exc_info=}")
            assert exc_info.value.args == (
                    "[TCT error] The timestep index is either missing a step or not monotonicaly increassing",)

    def test_arbitrary_timestep_indices(
            self, setup_mock_feature_child_range, t_nested_case
            ):
        if t_nested_case == "nested-and-ndarray":
            mfc_u = MockTrajectoryComposedParent(
                    feature_name="Parent uneven",
                    child_one=MockTrajectoryChildRosBagCase(
                            feature_name="child 1",
                            aa=setup_mock_feature_child_range.aa,
                            bb=setup_mock_feature_child_range.bb,
                            cc=setup_mock_feature_child_range.cc,
                            timesteps_indices=setup_mock_feature_child_range.timesteps_indices + 9,
                            ),
                    child_two=MockTrajectoryChildRosBagCase(
                            feature_name="child 2",
                            aa=setup_mock_feature_child_range.aa,
                            bb=setup_mock_feature_child_range.bb,
                            cc=setup_mock_feature_child_range.cc,
                            timesteps_indices=setup_mock_feature_child_range.timesteps_indices + 9,
                            ),
                    aa=setup_mock_feature_child_range.aa,
                    timesteps_indices=setup_mock_feature_child_range.timesteps_indices + 9,
                    )

            assert np.allclose(mfc_u.child_two.timesteps_indices, setup_mock_feature_child_range.timesteps_indices + 9)
            # assert np.allclose(mfc_u.timesteps_indices, setup_mock_feature_child_range.timesteps_indices + 9)

    def test_get_dimension_names(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        for each in ("feature_name", "timesteps_indices"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        if isinstance(mfc, MockTrajectoryComposedParent):
            assert mfc.feature_name is "Parent"
            assert ("child_one", "child_two", "aa") == mfc.get_dimension_names()
        else:
            assert mfc.feature_name is "Parent nested only"
            assert ("child_one", "child_two") == mfc.get_dimension_names()

    def test_get_dimension_type(self, setup_mock_feature_parent_range, t_nested_case):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        if t_nested_case == "nested-and-ndarray":
            assert issubclass(mfc.get_dimension_type("aa"), np.ndarray)
        assert issubclass(mfc.get_dimension_type("child_one"), MockTrajectoryChildRosBagCase)

    def test_set_dynamic_field(self, setup_mock_feature_parent_range, t_nested_case):
        mfc = setup_mock_feature_parent_range(t_nested_case)

        # Case override nested field
        mfc.child_one.set_dynamic_field("aa", None)
        assert mfc.child_one.aa is None

        # Case create new nested field
        mfc.child_one.set_dynamic_field("new_field", "new-field-value")
        assert mfc.child_one.new_field == "new-field-value"

        if t_nested_case == "nested-and-ndarray":
            # Case override top field
            mfc.set_dynamic_field("aa", "mock-value")
            assert mfc.aa == "mock-value"

            # Case create new top field
            mfc.set_dynamic_field("new_field", "new-field-value")
            assert mfc.new_field == "new-field-value"

    def test_get_dynamic_field(self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        assert np.allclose(mfc.child_one.get_dynamic_field("aa"),
                           mock_ROSbag_2_trj_DC_range.a)
        if t_nested_case == "nested-and-ndarray":
            assert np.allclose(mfc.get_dynamic_field("aa"), mock_ROSbag_2_trj_DC_range.a)

    def test_fetch_nested_attribute(self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        assert np.allclose(mfc.fetch_nested_attribute("child_one.aa"), mock_ROSbag_2_trj_DC_range.a)
        if t_nested_case == "nested-and-ndarray":
            assert np.allclose(mfc.fetch_nested_attribute("aa"), mock_ROSbag_2_trj_DC_range.a)

    def test_string_representation(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        print(mfc) # <- Don't comment this line

    def test_trajectory_len(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        assert mfc.trajectory_len == mock_ROSbag_2_trj_DC.a.shape[mfc._init_trj_axe]

    # @pytest.mark.skip(reason="todo")
    def test_ravel_dimensions_in_place(
            self,
            setup_mock_feature_parent_range,
            setup_mock_feature_child_range,
            mock_ROSbag_2_trj_DC_range,
            t_nested_case,
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        mfc.ravel_dimensions_in_place()

        for child_name, each_child in [("child_one", mfc.child_one), ("child_two", mfc.child_two)]:
            assert each_child.aa.shape[0] == mfc.trajectory_len
            assert each_child.cc.shape[0] == mfc.trajectory_len * 36

        #print(mfc)
        # (Priority) ToDo: implement test asserting a range

    def test_get_item(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        assert mfc.trajectory_len == 40

        mdc_at_t0 = mfc[0]

        assert isinstance(mdc_at_t0, type(mfc))

        assert mdc_at_t0.child_one.aa.size == 1
        assert mdc_at_t0.child_one.bb.size == 1
        assert mdc_at_t0.child_one.cc.size == 36
        assert mdc_at_t0.child_one.timesteps_indices.size == 1
        assert mdc_at_t0.child_one.aa == mfc.child_one.aa[0]
        assert mdc_at_t0.child_one.bb == mfc.child_one.bb[0]
        assert np.array_equal(mdc_at_t0.child_one.cc, np.arange(mfc.child_one.cc.shape[-1]))
        assert mdc_at_t0.timesteps_indices == mfc.child_one.timesteps_indices[0]
        # mfc.get_dimension_names()
        #print(mfc)
        #print(mdc_at_t0)

    def test_iterator(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        assert mfc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mfc):
            assert isinstance(mdc_at_t, type(mfc))

            assert mdc_at_t.child_one.aa == mfc.child_one.aa[t]
            assert mdc_at_t.child_one.bb == mfc.child_one.bb[t]
            cc_feature_size = mfc.child_one.cc[t].shape[-1]
            assert np.array_equal(
                    mdc_at_t.child_one.cc, np.arange(cc_feature_size) + mfc.child_one.cc[t, 0]
                    )
            assert mdc_at_t.child_one.timesteps_indices == mfc.child_one.timesteps_indices[t]
            # mfc.get_dimension_names()
            #print(mdc_at_t)

    def test_transpose(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case
            ):
        t_ref = mock_ROSbag_2_trj_DC_range
        mfc = setup_mock_feature_parent_range(t_nested_case)

        assert mfc._transposed == False
        assert mfc._init_trj_axe == 0
        assert mfc.current_trj_axe == 0
        assert mfc.trajectory_len == 40
        assert mfc.timesteps_indices.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(mfc.aa, t_ref.a)

        assert mfc.child_one._transposed == False
        assert mfc.child_one._init_trj_axe == 0
        assert mfc.child_one.current_trj_axe == 0
        assert mfc.child_one.trajectory_len == 40
        assert mfc.child_one.timesteps_indices.shape == (40,)

        assert mfc.child_one.aa.shape == (40,)
        assert mfc.child_one.bb.shape == (40,)
        assert mfc.child_one.cc.shape == (40, 36)
        assert np.array_equal(mfc.child_one.aa, t_ref.a)
        assert np.array_equal(mfc.child_one.bb, t_ref.b)
        assert np.array_equal(mfc.child_one.cc, t_ref.c)

        assert mfc.child_two._transposed == False
        assert mfc.child_two._init_trj_axe == 0
        assert mfc.child_two.current_trj_axe == 0
        assert mfc.child_two.trajectory_len == 40
        assert mfc.child_two.timesteps_indices.shape == (40,)

        assert mfc.child_two.aa.shape == (40,)
        assert mfc.child_two.bb.shape == (40,)
        assert mfc.child_two.cc.shape == (40, 36)
        assert np.array_equal(mfc.child_two.aa, t_ref.a)
        assert np.array_equal(mfc.child_two.bb, t_ref.b)
        assert np.array_equal(mfc.child_two.cc, t_ref.c)
        #print(
        #        f"{mfc}\n\n",
        #        f"{mfc.get_dimension_names()}\n\n",
        #        f"{mfc.child_one}\n\n",
        #        f"{mfc.child_two}\n\n",
        #        )

        t_mdc = mfc.T

        assert t_mdc._transposed == True
        assert t_mdc._init_trj_axe == 0
        assert t_mdc.current_trj_axe == -1
        assert t_mdc.trajectory_len == 40
        assert t_mdc.timesteps_indices.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(t_mdc.aa, t_ref.a)

        assert t_mdc.child_one._transposed == True
        assert t_mdc.child_one._init_trj_axe == 0
        assert t_mdc.child_one.current_trj_axe == -1
        assert t_mdc.child_one.trajectory_len == 40
        assert t_mdc.child_one.timesteps_indices.shape == (40,)

        assert t_mdc.child_one.aa.shape == (40,)
        assert t_mdc.child_one.bb.shape == (40,)
        assert t_mdc.child_one.cc.shape == (36, 40)
        assert np.array_equal(t_mdc.child_one.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.child_one.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.child_one.cc, t_ref.c.T)

        assert t_mdc.child_two._transposed == True
        assert t_mdc.child_two._init_trj_axe == 0
        assert t_mdc.child_two.current_trj_axe == -1
        assert t_mdc.child_two.trajectory_len == 40
        assert t_mdc.child_two.timesteps_indices.shape == (40,)

        assert t_mdc.child_two.aa.shape == (40,)
        assert t_mdc.child_two.bb.shape == (40,)
        assert t_mdc.child_two.cc.shape == (36, 40)
        assert np.array_equal(t_mdc.child_two.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.child_two.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.child_two.cc, t_ref.c.T)

        #print(
        #        f"{t_mdc}\n\n",
        #        f"{t_mdc.get_dimension_names()}\n\n",
        #        f"{t_mdc.child_one}\n\n",
        #        f"{t_mdc.child_two}\n\n",
        #        )

        t_mdc2 = t_mdc.T

        assert t_mdc2._transposed == False
        assert t_mdc2._init_trj_axe == 0
        assert t_mdc2.current_trj_axe == 0
        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.timesteps_indices.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(t_mdc2.aa, t_ref.a)

        assert t_mdc2.child_one._transposed == False
        assert t_mdc2.child_one._init_trj_axe == 0
        assert t_mdc2.child_one.current_trj_axe == 0
        assert t_mdc2.child_one.trajectory_len == 40
        assert t_mdc2.child_one.timesteps_indices.shape == (40,)

        assert t_mdc2.child_one.aa.shape == (40,)
        assert t_mdc2.child_one.bb.shape == (40,)
        assert t_mdc2.child_one.cc.shape == (40, 36)
        assert np.array_equal(t_mdc2.child_one.aa, t_ref.a)
        assert np.array_equal(t_mdc2.child_one.bb, t_ref.b)
        assert np.array_equal(t_mdc2.child_one.cc, t_ref.c)

        assert t_mdc2.child_two._transposed == False
        assert t_mdc2.child_two._init_trj_axe == 0
        assert t_mdc2.child_two.current_trj_axe == 0
        assert t_mdc2.child_two.trajectory_len == 40
        assert t_mdc2.child_two.timesteps_indices.shape == (40,)

        assert t_mdc2.child_two.aa.shape == (40,)
        assert t_mdc2.child_two.bb.shape == (40,)
        assert t_mdc2.child_two.cc.shape == (40, 36)
        assert np.array_equal(t_mdc2.child_two.aa, t_ref.a)
        assert np.array_equal(t_mdc2.child_two.bb, t_ref.b)
        assert np.array_equal(t_mdc2.child_two.cc, t_ref.c)

        #print(
        #        f"{t_mdc2}\n\n",
        #        f"{t_mdc2.get_dimension_names()}\n\n",
        #        f"{t_mdc2.child_one}\n\n",
        #        f"{t_mdc2.child_two}\n\n",
        #        )
