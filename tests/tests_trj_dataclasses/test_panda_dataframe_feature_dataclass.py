# coding=utf-8
import pytest
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import (
    CmdStandard,
    StatePose2D,
    Velocity,
)


class TestTrajectoryDataclassFromDataframeCase:
    def test_init_empty_data_properties(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        with pytest.raises(TypeError):
            dc_ = StatePose2D(feature_name=md.name)

    def test_StatePose2D_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = StatePose2D(
            feature_name=md.name,
            x=md.a,
            y=md.b,
            yaw=md.c,
            timesteps_indices=md.ts,
            batch=True,
        )
        print(dc_)

    def test_CmdStandard_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = CmdStandard(
            feature_name=md.name,
            linear_vel=md.a,
            angular_vel=md.b,
            timesteps_indices=md.ts,
            batch=True,
        )
        print(dc_)

    def test_Velocity_init(self, mock_DF_2_trj_DC):
        md = mock_DF_2_trj_DC
        dc_ = Velocity(
            feature_name=md.name,
            linear_vel=md.a,
            angular_vel=md.b,
            timesteps_indices=md.ts,
            batch=True,
        )
        print(dc_)
