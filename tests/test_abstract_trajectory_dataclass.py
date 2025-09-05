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

    def post_init_callback(self):
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[..., 0]
        self.__setattr__(f"{feature_name}_init", feature_ini)
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

    def post_init_callback(self):  # self.dd_metadata += 99
        feature = self.__getattribute__("dd_metadata")
        self.__setattr__("dd_metadata", feature + 99)
        return None

    def post_init_feature_callback(self, feature_name):
        feature = self.__getattribute__(feature_name)
        feature_ini = feature[0, ...]
        self.__setattr__(f"{feature_name}_init", feature_ini)
        return None


@dataclass
class MockTrajectoryComposedParent(AbstractTrajectoryDataclass):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase
    aa: np.ndarray

    @property
    def _init_trj_axe(self) -> int:
        return 0


@dataclass
class MockTrajectoryComposedParentNestedOnly(AbstractTrajectoryDataclass):
    child_one: MockTrajectoryChildRosBagCase
    child_two: MockTrajectoryChildRosBagCase

    @property
    def _init_trj_axe(self) -> int:
        return 0


class TestAbstractTrajectoryDataclassDataframeCase:

    @pytest.fixture
    def setup_mock_feature_child(self, mock_DF_2_trj_DC):
        return MockTrajectoryChildDFcase(
                feature_name=mock_DF_2_trj_DC.name,
                aa=mock_DF_2_trj_DC.a,
                bb=mock_DF_2_trj_DC.b,
                cc=mock_DF_2_trj_DC.c,
                timestep_index=mock_DF_2_trj_DC.ts,
                )

    @pytest.fixture
    def setup_mock_feature_child_range(self, mock_DF_2_trj_DC_range):
        return MockTrajectoryChildDFcase(
                feature_name=mock_DF_2_trj_DC_range.name,
                aa=mock_DF_2_trj_DC_range.a,
                bb=mock_DF_2_trj_DC_range.b,
                cc=mock_DF_2_trj_DC_range.c,
                timestep_index=mock_DF_2_trj_DC_range.ts,
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
                ), f"{mfc.dd_metadata=} != np.array([99, 99, 99])"  # test post_init_callback

        # ★ post_init_feature_callback `aa_init` is a dynamicaly created field
        assert np.array_equal(
                mfc.aa_init, mock_DF_2_trj_DC.a[..., 0]
                ), f"{mfc.aa_init=} != {mock_DF_2_trj_DC.a[..., 0]=}"  # test

    def test_class_feature_post_init_check(self, mock_DF_2_trj_DC_uneven_time_index):
        with pytest.raises(ValueError):
            mfc_u = MockTrajectoryChildDFcase(
                    feature_name=mock_DF_2_trj_DC_uneven_time_index.name,
                    aa=mock_DF_2_trj_DC_uneven_time_index.a,
                    bb=mock_DF_2_trj_DC_uneven_time_index.b,
                    cc=mock_DF_2_trj_DC_uneven_time_index.c,
                    timestep_index=mock_DF_2_trj_DC_uneven_time_index.ts,
                    )

    def test_get_dimension_names(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mfc = setup_mock_feature_child
        for each in ("feature_name", "timestep_index"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        assert mfc.feature_name is mock_DF_2_trj_DC.name
        assert ("aa", "bb", "cc", "dd_metadata") == mfc.get_dimension_names()

    def test_get_dimension_names_on_uninstiated_class(self):
        stp = StatePose2D
        stp.get_dimension_names()

    def test_string_representation(self, setup_mock_feature_child, mock_DF_2_trj_DC):
        mdc = setup_mock_feature_child
        print(mdc)

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
        print(mdc)
        # (Priority) ToDo: implement test asserting a range

    def test_get_item(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        mdc_at_t0 = mdc[0]

        assert isinstance(mdc_at_t0, type(mdc))

        assert mdc_at_t0.aa.size == 10
        assert mdc_at_t0.bb.size == 10
        assert mdc_at_t0.cc.size == 10
        assert mdc_at_t0.timestep_index.size == 1
        assert np.array_equal(mdc_at_t0.aa, np.arange(mdc.aa.shape[0]))
        assert np.array_equal(mdc_at_t0.bb, np.arange(mdc.bb.shape[0]))
        assert np.array_equal(mdc_at_t0.cc, np.arange(mdc.cc.shape[0]))
        assert mdc_at_t0.timestep_index == mdc.timestep_index[0]
        # mdc.get_dimension_names()
        print(mdc)
        print(mdc_at_t0)

    def test_iterator(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mdc):
            assert isinstance(mdc_at_t, type(mdc))

            assert np.array_equal(mdc_at_t.aa, np.arange(mdc.aa.shape[0]) + mdc.aa[0, t])
            assert np.array_equal(mdc_at_t.bb, np.arange(mdc.bb.shape[0]) + mdc.bb[0, t])
            assert np.array_equal(mdc_at_t.cc, np.arange(mdc.cc.shape[0]) + mdc.cc[0, t])
            assert mdc_at_t.timestep_index == mdc.timestep_index[t]
            # mdc.get_dimension_names()
            print(mdc_at_t)

    def test_transpose(self, setup_mock_feature_child_range, mock_DF_2_trj_DC_range):
        t_ref = mock_DF_2_trj_DC_range
        mdc = setup_mock_feature_child_range

        assert mdc.transposed == False
        assert mdc._init_trj_axe == -1
        assert mdc.current_trj_axe == -1

        assert mdc.trajectory_len == 40
        assert mdc.aa.shape == (10, 40)
        assert mdc.bb.shape == (10, 40)
        assert mdc.cc.shape == (10, 40)
        assert mdc.timestep_index.shape == (40,)
        assert np.array_equal(mdc.aa, t_ref.a)
        assert np.array_equal(mdc.bb, t_ref.b)
        assert np.array_equal(mdc.cc, t_ref.c)
        print(mdc)

        t_mdc = mdc.T

        assert t_mdc.transposed == True
        assert t_mdc._init_trj_axe == -1
        assert t_mdc.current_trj_axe == 0

        assert t_mdc.trajectory_len == 40
        assert t_mdc.aa.shape == (40, 10)
        assert t_mdc.bb.shape == (40, 10)
        assert t_mdc.cc.shape == (40, 10)
        assert t_mdc.timestep_index.shape == (40,)
        assert np.array_equal(t_mdc.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.cc, t_ref.c.T)
        print(t_mdc)
        print(t_mdc.get_dimension_names())

        t_mdc2 = t_mdc.T

        assert t_mdc2.transposed == False
        assert t_mdc2._init_trj_axe == -1
        assert t_mdc2.current_trj_axe == -1

        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.aa.shape == (10, 40)
        assert t_mdc2.bb.shape == (10, 40)
        assert t_mdc2.cc.shape == (10, 40)
        assert t_mdc2.timestep_index.shape == (40,)
        assert np.array_equal(t_mdc2.aa, t_ref.a)
        assert np.array_equal(t_mdc2.bb, t_ref.b)
        assert np.array_equal(t_mdc2.cc, t_ref.c)
        print(t_mdc2)
        print(t_mdc2.get_dimension_names())


class TestAbstractTrajectoryDataclassROSbagCase:

    @pytest.fixture
    def setup_mock_feature_child(self, mock_ROSbag_2_trj_DC) -> MockTrajectoryChildRosBagCase:
        return MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC.name,
                aa=mock_ROSbag_2_trj_DC.a,
                bb=mock_ROSbag_2_trj_DC.b,
                cc=mock_ROSbag_2_trj_DC.c,
                timestep_index=mock_ROSbag_2_trj_DC.ts_idx,
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
                timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
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
                ), f"{mfc.dd_metadata=} != np.array([99, 99, 99])"  # test post_init_callback

        assert np.array_equal(
                mfc.aa_init, mock_ROSbag_2_trj_DC.a[0, ...]
                ), f"{mfc.aa_init=} != {mock_ROSbag_2_trj_DC.a[0, ...]=}"  # test
        # post_init_feature_callback `aa_init` is a dynamicaly created field

    def test_class_feature_post_init_check(self, mock_ROSbag_2_trj_DC_uneven_time_index):
        with pytest.raises(ValueError):
            mfc_u = MockTrajectoryChildRosBagCase(
                    feature_name=mock_ROSbag_2_trj_DC_uneven_time_index.name,
                    aa=mock_ROSbag_2_trj_DC_uneven_time_index.a,
                    bb=mock_ROSbag_2_trj_DC_uneven_time_index.b,
                    cc=mock_ROSbag_2_trj_DC_uneven_time_index.c,
                    timestep_index=mock_ROSbag_2_trj_DC_uneven_time_index.ts_idx,
                    )

    def test_get_dimension_names(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mfc = setup_mock_feature_child
        for each in ("feature_name", "timestep_index"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        assert mfc.feature_name is mock_ROSbag_2_trj_DC.name
        assert ("aa", "bb", "cc", "dd_metadata") == mfc.get_dimension_names()

    def test_get_dimension_names_on_uninstiated_class(self):
        stp = StatePose2D
        stp.get_dimension_names()

    def test_string_representation(self, setup_mock_feature_child, mock_ROSbag_2_trj_DC):
        mdc = setup_mock_feature_child
        print(mdc)

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
        print(mdc)
        # (Priority) ToDo: implement test asserting a range

    def test_get_item(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        mdc_at_t0 = mdc[0]

        assert isinstance(mdc_at_t0, type(mdc))

        assert mdc_at_t0.aa.size == 1
        assert mdc_at_t0.bb.size == 1
        assert mdc_at_t0.cc.size == 36
        assert mdc_at_t0.timestep_index.size == 1
        assert mdc_at_t0.aa == mdc.aa[0]
        assert mdc_at_t0.bb == mdc.bb[0]
        assert np.array_equal(mdc_at_t0.cc, np.arange(mdc.cc.shape[-1]))
        assert mdc_at_t0.timestep_index == mdc.timestep_index[0]
        # mdc.get_dimension_names()
        print(mdc)
        print(mdc_at_t0)

    def test_iterator(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        mdc = setup_mock_feature_child_range
        assert mdc.trajectory_len == 40

        for t, mdc_at_t in enumerate(mdc):
            assert isinstance(mdc_at_t, type(mdc))

            assert mdc_at_t.aa == mdc.aa[t]
            assert mdc_at_t.bb == mdc.bb[t]
            cc_feature_size = mdc.cc[t].shape[-1]
            assert np.array_equal(mdc_at_t.cc, np.arange(cc_feature_size) + mdc.cc[t, 0])
            assert mdc_at_t.timestep_index == mdc.timestep_index[t]
            # mdc.get_dimension_names()
            print(mdc_at_t)

    def test_transpose(self, setup_mock_feature_child_range, mock_ROSbag_2_trj_DC_range):
        t_ref = mock_ROSbag_2_trj_DC_range
        mdc = setup_mock_feature_child_range

        assert mdc.transposed == False
        assert mdc._init_trj_axe == 0
        assert mdc.current_trj_axe == 0

        assert mdc.trajectory_len == 40
        assert mdc.aa.shape == (40,)
        assert mdc.bb.shape == (40,)
        assert mdc.cc.shape == (40, 36)
        assert mdc.timestep_index.shape == (40,)
        assert np.array_equal(mdc.aa, t_ref.a)
        assert np.array_equal(mdc.bb, t_ref.b)
        assert np.array_equal(mdc.cc, t_ref.c)
        print(mdc)

        t_mdc = mdc.T

        assert t_mdc.transposed == True
        assert t_mdc._init_trj_axe == 0
        assert t_mdc.current_trj_axe == -1

        assert t_mdc.trajectory_len == 40
        assert t_mdc.aa.shape == (40,)
        assert t_mdc.bb.shape == (40,)
        assert t_mdc.cc.shape == (36, 40)
        assert t_mdc.timestep_index.shape == (40,)
        assert np.array_equal(t_mdc.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.cc, t_ref.c.T)
        print(t_mdc)
        print(t_mdc.get_dimension_names())

        t_mdc2 = t_mdc.T

        assert t_mdc2.transposed == False
        assert t_mdc2._init_trj_axe == 0
        assert t_mdc2.current_trj_axe == 0

        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.aa.shape == (40,)
        assert t_mdc2.bb.shape == (40,)
        assert t_mdc2.cc.shape == (40, 36)
        assert t_mdc2.timestep_index.shape == (40,)
        assert np.array_equal(t_mdc2.aa, t_ref.a)
        assert np.array_equal(t_mdc2.bb, t_ref.b)
        assert np.array_equal(t_mdc2.cc, t_ref.c)
        print(t_mdc2)
        print(t_mdc2.get_dimension_names())


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
                timestep_index=mock_ROSbag_2_trj_DC.ts_idx,
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
                timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
                )

    @pytest.fixture(scope="function")
    def setup_mock_feature_parent_range(self, mock_ROSbag_2_trj_DC_range):
        the_child_one = MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_range.name,
                aa=mock_ROSbag_2_trj_DC_range.a,
                bb=mock_ROSbag_2_trj_DC_range.b,
                cc=mock_ROSbag_2_trj_DC_range.c,
                timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
                )
        the_child_two = MockTrajectoryChildRosBagCase(
                feature_name=mock_ROSbag_2_trj_DC_range.name + "-two",
                aa=mock_ROSbag_2_trj_DC_range.a,
                bb=mock_ROSbag_2_trj_DC_range.b,
                cc=mock_ROSbag_2_trj_DC_range.c,
                timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
                )

        assert the_child_one is not the_child_two

        def instanciate_nested_case(nested_case: str):
            if nested_case == "nested-and-ndarray":
                mock_parent_dataclass = MockTrajectoryComposedParent(
                        feature_name="Parent",
                        child_one=the_child_one,
                        child_two=the_child_two,
                        aa=mock_ROSbag_2_trj_DC_range.a,
                        timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
                        )
            else:
                mock_parent_dataclass = MockTrajectoryComposedParentNestedOnly(
                        feature_name="Parent nested only",
                        child_one=the_child_one,
                        child_two=the_child_two,
                        timestep_index=mock_ROSbag_2_trj_DC_range.ts_idx,
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

        print(mfc)

        for child_name, each_child in [("child_one", mfc.child_one), ("child_two", mfc.child_two)]:
            assert np.array_equal(
                    each_child.dd_metadata, np.array([99, 99, 99])
                    ), (  # test post_init_callback
                    f"{child_name}.dd_metadata={each_child.dd_metadata} != np.array([99, 99, 99])"
            )

            assert np.array_equal(each_child.aa_init, mock_ROSbag_2_trj_DC_range.a[0, ...]), (
                    # post_init_feature_callback `aa_init` is a dynamicaly created field  # test
                    f"{child_name}.aa_init={each_child.aa_init}"
                    f" != {mock_ROSbag_2_trj_DC_range.a[0, ...]=}"
            )

    def test_class_feature_post_init_check(
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
                                timestep_index=mock_ROSbag_2_trj_DC_longer_range.ts_idx,
                                ),
                        aa=setup_mock_feature_child_range.a,
                        timestep_index=setup_mock_feature_child_range.timestep_index,
                        )
            print(f"{exc_info=}")
            # assert exc_info.value.args == ("<The error message>",)

    def test_get_dimension_names(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        for each in ("feature_name", "timestep_index"):
            assert hasattr(mfc, each)
            assert each not in mfc.get_dimension_names()
        if isinstance(mfc, MockTrajectoryComposedParent):
            assert mfc.feature_name is "Parent"
            assert ("child_one", "child_two", "aa") == mfc.get_dimension_names()
        else:
            assert mfc.feature_name is "Parent nested only"
            assert ("child_one", "child_two") == mfc.get_dimension_names()

    def test_string_representation(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC, t_nested_case
            ):
        mfc = setup_mock_feature_parent_range(t_nested_case)
        print(mfc)

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

        print(mfc)
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
        assert mdc_at_t0.child_one.timestep_index.size == 1
        assert mdc_at_t0.child_one.aa == mfc.child_one.aa[0]
        assert mdc_at_t0.child_one.bb == mfc.child_one.bb[0]
        assert np.array_equal(mdc_at_t0.child_one.cc, np.arange(mfc.child_one.cc.shape[-1]))
        assert mdc_at_t0.timestep_index == mfc.child_one.timestep_index[0]
        # mfc.get_dimension_names()
        print(mfc)
        print(mdc_at_t0)

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
            assert mdc_at_t.child_one.timestep_index == mfc.child_one.timestep_index[t]
            # mfc.get_dimension_names()
            print(mdc_at_t)

    def test_transpose(
            self, setup_mock_feature_parent_range, mock_ROSbag_2_trj_DC_range, t_nested_case
            ):
        t_ref = mock_ROSbag_2_trj_DC_range
        mfc = setup_mock_feature_parent_range(t_nested_case)

        assert mfc.transposed == False
        assert mfc._init_trj_axe == 0
        assert mfc.current_trj_axe == 0
        assert mfc.trajectory_len == 40
        assert mfc.timestep_index.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(mfc.aa, t_ref.a)

        assert mfc.child_one.transposed == False
        assert mfc.child_one._init_trj_axe == 0
        assert mfc.child_one.current_trj_axe == 0
        assert mfc.child_one.trajectory_len == 40
        assert mfc.child_one.timestep_index.shape == (40,)

        assert mfc.child_one.aa.shape == (40,)
        assert mfc.child_one.bb.shape == (40,)
        assert mfc.child_one.cc.shape == (40, 36)
        assert np.array_equal(mfc.child_one.aa, t_ref.a)
        assert np.array_equal(mfc.child_one.bb, t_ref.b)
        assert np.array_equal(mfc.child_one.cc, t_ref.c)

        assert mfc.child_two.transposed == False
        assert mfc.child_two._init_trj_axe == 0
        assert mfc.child_two.current_trj_axe == 0
        assert mfc.child_two.trajectory_len == 40
        assert mfc.child_two.timestep_index.shape == (40,)

        assert mfc.child_two.aa.shape == (40,)
        assert mfc.child_two.bb.shape == (40,)
        assert mfc.child_two.cc.shape == (40, 36)
        assert np.array_equal(mfc.child_two.aa, t_ref.a)
        assert np.array_equal(mfc.child_two.bb, t_ref.b)
        assert np.array_equal(mfc.child_two.cc, t_ref.c)
        print(
                f"{mfc}\n\n",
                f"{mfc.get_dimension_names()}\n\n",
                f"{mfc.child_one}\n\n",
                f"{mfc.child_two}\n\n",
                )

        t_mdc = mfc.T

        assert t_mdc.transposed == True
        assert t_mdc._init_trj_axe == 0
        assert t_mdc.current_trj_axe == -1
        assert t_mdc.trajectory_len == 40
        assert t_mdc.timestep_index.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(t_mdc.aa, t_ref.a)

        assert t_mdc.child_one.transposed == True
        assert t_mdc.child_one._init_trj_axe == 0
        assert t_mdc.child_one.current_trj_axe == -1
        assert t_mdc.child_one.trajectory_len == 40
        assert t_mdc.child_one.timestep_index.shape == (40,)

        assert t_mdc.child_one.aa.shape == (40,)
        assert t_mdc.child_one.bb.shape == (40,)
        assert t_mdc.child_one.cc.shape == (36, 40)
        assert np.array_equal(t_mdc.child_one.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.child_one.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.child_one.cc, t_ref.c.T)

        assert t_mdc.child_two.transposed == True
        assert t_mdc.child_two._init_trj_axe == 0
        assert t_mdc.child_two.current_trj_axe == -1
        assert t_mdc.child_two.trajectory_len == 40
        assert t_mdc.child_two.timestep_index.shape == (40,)

        assert t_mdc.child_two.aa.shape == (40,)
        assert t_mdc.child_two.bb.shape == (40,)
        assert t_mdc.child_two.cc.shape == (36, 40)
        assert np.array_equal(t_mdc.child_two.aa, t_ref.a.T)
        assert np.array_equal(t_mdc.child_two.bb, t_ref.b.T)
        assert np.array_equal(t_mdc.child_two.cc, t_ref.c.T)

        print(
                f"{t_mdc}\n\n",
                f"{t_mdc.get_dimension_names()}\n\n",
                f"{t_mdc.child_one}\n\n",
                f"{t_mdc.child_two}\n\n",
                )

        t_mdc2 = t_mdc.T

        assert t_mdc2.transposed == False
        assert t_mdc2._init_trj_axe == 0
        assert t_mdc2.current_trj_axe == 0
        assert t_mdc2.trajectory_len == 40
        assert t_mdc2.timestep_index.shape == (40,)

        if isinstance(mfc, MockTrajectoryComposedParent):
            assert np.array_equal(t_mdc2.aa, t_ref.a)

        assert t_mdc2.child_one.transposed == False
        assert t_mdc2.child_one._init_trj_axe == 0
        assert t_mdc2.child_one.current_trj_axe == 0
        assert t_mdc2.child_one.trajectory_len == 40
        assert t_mdc2.child_one.timestep_index.shape == (40,)

        assert t_mdc2.child_one.aa.shape == (40,)
        assert t_mdc2.child_one.bb.shape == (40,)
        assert t_mdc2.child_one.cc.shape == (40, 36)
        assert np.array_equal(t_mdc2.child_one.aa, t_ref.a)
        assert np.array_equal(t_mdc2.child_one.bb, t_ref.b)
        assert np.array_equal(t_mdc2.child_one.cc, t_ref.c)

        assert t_mdc2.child_two.transposed == False
        assert t_mdc2.child_two._init_trj_axe == 0
        assert t_mdc2.child_two.current_trj_axe == 0
        assert t_mdc2.child_two.trajectory_len == 40
        assert t_mdc2.child_two.timestep_index.shape == (40,)

        assert t_mdc2.child_two.aa.shape == (40,)
        assert t_mdc2.child_two.bb.shape == (40,)
        assert t_mdc2.child_two.cc.shape == (40, 36)
        assert np.array_equal(t_mdc2.child_two.aa, t_ref.a)
        assert np.array_equal(t_mdc2.child_two.bb, t_ref.b)
        assert np.array_equal(t_mdc2.child_two.cc, t_ref.c)

        print(
                f"{t_mdc2}\n\n",
                f"{t_mdc2.get_dimension_names()}\n\n",
                f"{t_mdc2.child_one}\n\n",
                f"{t_mdc2.child_two}\n\n",
                )
