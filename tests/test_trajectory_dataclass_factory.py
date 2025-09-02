# coding=utf-8
import numpy as np
import pytest

from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    DataframeFeatureDataclass,
)
from trajectory_container_tools.dataclasses.rosbag_feature_dataclass import (
    RosBagFeatureDataclass,
)
from trajectory_container_tools.utils.factory import (
    TrjDataClassFeatureSpecification,
    trajectory_dataclass_factory,
)
from trajectory_container_tools.dataclasses import abstract_trajectory_dataclass as atd


# ====Pandas dataframe cases=======================================================================
class TestTrajectoryDataclassFactoryDataframeCase:
    @pytest.fixture
    def setup_dataframe_style_config(self):
        spec = TrjDataClassFeatureSpecification(
            new_feature_dataclass_type="new_feature_dataclass",
            dimension_names=("xx", "yy", "yaww"),
        )
        return spec

    def test_spec_ok(self, setup_dataframe_style_config):
        trajectory_dataclass_factory(
            specification=setup_dataframe_style_config,
            trj_dataclass_subclass=DataframeFeatureDataclass,
        )

    def test_bad_spec(self):
        with pytest.raises(AttributeError):
            fdf3 = trajectory_dataclass_factory(
                specification=TrjDataClassFeatureSpecification(
                    new_feature_dataclass_type="new_feature_dataclass",
                    dimension_names=("xx", "yy", 999),
                ),
                trj_dataclass_subclass=DataframeFeatureDataclass,
            )

        # ToDo: assessment >> next bloc ↓↓ is not relevant since refactoring to
        # specification object as a dataclass
        # with pytest.raises(KeyError):
        #     fdf1 = atd.trajectory_dataclass_factory(
        #             specification=atd.TrjDataClassFeatureSpecification(
        #             feature_AAAA='new_feature_dataclass',
        #                                                     dimension_names=('xx', 'yy',
        #                                                     'yaww')))
        #     fdf2 = atd.trajectory_dataclass_factory(
        #             specification=atd.TrjDataClassFeatureSpecification(
        #             new_feature_dataclass_type='new_feature_dataclass',
        #                                                     dimension_AAAA=('xx', 'yy', 'yaww')))

    def test_output_ok(self, setup_dataframe_style_config):
        mock_cls = trajectory_dataclass_factory(
            specification=setup_dataframe_style_config,
            trj_dataclass_subclass=DataframeFeatureDataclass,
        )
        mock_value = np.arange(10)
        assert issubclass(mock_cls, atd.AbstractTrajectoryDataclass)
        assert not isinstance(mock_cls, atd.AbstractTrajectoryDataclass)
        mock_cls_instance = mock_cls(
            feature_name="mock_data",
            xx=mock_value,
            yy=mock_value,
            yaww=mock_value,
            timestep_index=mock_value,
        )
        assert isinstance(mock_cls_instance, atd.AbstractTrajectoryDataclass)
        assert mock_cls.get_dimension_names() == ("xx", "yy", "yaww")
        assert hasattr(mock_cls_instance, "feature_name")
        assert hasattr(mock_cls_instance, "xx")
        assert hasattr(mock_cls_instance, "yy")
        assert hasattr(mock_cls_instance, "yaww")

        print("\n" * 2, mock_cls_instance)


# ====Rosbag topics cases==========================================================================
class TestTrajectoryDataclassFactoryROSbagCase:
    @pytest.fixture
    def setup_rosbag_style_config(self):
        spec = TrjDataClassFeatureSpecification(
            new_feature_dataclass_type="NewTopicMsgType",
            dimension_names=("pose_xx", "pose_yy", "pose_zz", "header_FrameId", "timestamps"),
        )
        return spec

    def test_spec_ok(self, setup_rosbag_style_config):
        trajectory_dataclass_factory(
            specification=setup_rosbag_style_config, trj_dataclass_subclass=RosBagFeatureDataclass
        )

    def test_bad_spec(self):
        with pytest.raises(AttributeError):
            fdf3 = trajectory_dataclass_factory(
                specification=TrjDataClassFeatureSpecification(
                    new_feature_dataclass_type="new_topic_msg_type",
                    dimension_names=("pose.xx", "pose_yy", 999),
                ),
                trj_dataclass_subclass=RosBagFeatureDataclass,
            )

    def test_output_ok(self, setup_rosbag_style_config):
        mock_cls = trajectory_dataclass_factory(
            specification=setup_rosbag_style_config,
            trj_dataclass_subclass=RosBagFeatureDataclass,
        )
        mock_value = np.arange(10)
        assert issubclass(mock_cls, atd.AbstractTrajectoryDataclass)
        assert not isinstance(mock_cls, atd.AbstractTrajectoryDataclass)
        mock_cls_instance = mock_cls(
            feature_name="mock_data",
            pose_xx=mock_value,
            pose_yy=mock_value,
            pose_zz=mock_value,
            timestep_index=mock_value,
            header_FrameId=999,
            timestamps=mock_value,
        )
        assert isinstance(mock_cls_instance, atd.AbstractTrajectoryDataclass)
        assert mock_cls.get_dimension_names() == (
            "header_FrameId",
            "timestamps",
            "pose_xx",
            "pose_yy",
            "pose_zz",
        )
        assert hasattr(mock_cls_instance, "feature_name")
        assert hasattr(mock_cls_instance, "header_FrameId")
        assert hasattr(mock_cls_instance, "timestamps")
        assert hasattr(mock_cls_instance, "pose_xx")
        assert hasattr(mock_cls_instance, "pose_yy")
        assert hasattr(mock_cls_instance, "pose_zz")

        print("\n" * 2, mock_cls_instance)
