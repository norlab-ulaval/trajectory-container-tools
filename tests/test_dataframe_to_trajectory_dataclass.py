# coding=utf-8
import os
import os.path as os_path
import pytest
import numpy as np
import pandas as pd

from trajectory_container_tools.dataframe_to_tct import unpack_dataframe_and_show_topic
from trajectory_container_tools.trj_dataclasses.panda_dataframe_feature_dataclass import (
    CmdSkidSteer,
    CmdStandard,
    StatePose2D,
)
from trajectory_container_tools import dataframe_to_tct as dtd
from trajectory_container_tools.trj_dataclasses import (
    abstract_trajectory_dataclass as atd,
)

@pytest.fixture(scope="function")
def setup_panda_dataframe() -> pd.DataFrame:
    slip_dataset_all_path = os.path.join(
        "data",
        "repository_data",
        "demo_data",
        "dataframe_test_data",
        "marmotte",
        "ga_hard_snow_25_01_a",
        "slip_dataset_all.pkl",
    )

    dataframe_, dataframe_real_path = unpack_dataframe_and_show_topic(
        slip_dataset_all_path
    )
    return dataframe_


class TestExtractDataframeFeature:
    def test_StatePose_working(self, setup_panda_dataframe):
        fn = "body_vel_disturption"
        check_property = "x"

        container = dtd.extract_single_feature_from_dataframe(
            dataset=setup_panda_dataframe,
            feature_name=fn,
            data_container_type=StatePose2D,
        )

        df = setup_panda_dataframe.filter(like=f"{fn}_{check_property}")
        assert container.feature_name is fn
        assert container.trajectory_len == df.shape[1]

    def test_CmdSkidSteer_working(self, setup_panda_dataframe):
        fn = "cmd"
        check_property = "left"

        container = dtd.extract_single_feature_from_dataframe(
            dataset=setup_panda_dataframe,
            feature_name=fn,
            data_container_type=CmdSkidSteer,
        )

        df = setup_panda_dataframe.filter(like=f"{fn}_{check_property}")
        assert container.feature_name is fn
        assert container.trajectory_len == df.shape[1]

    def test_bad_argument(self, setup_panda_dataframe):
        fn = "body_vel_disturption"

        mock_value = np.arange(10)
        state_pose = StatePose2D(
            feature_name=fn,
            x=mock_value,
            y=mock_value,
            yaw=mock_value,
            timesteps_indices=mock_value,
        )

        with pytest.raises(AttributeError):
            container = dtd.extract_single_feature_from_dataframe(
                dataset=setup_panda_dataframe,
                feature_name=fn,
                data_container_type=state_pose,
            )

    def test_fail_no_existing_feature(self, setup_panda_dataframe):
        with pytest.raises(ValueError):
            dtd.extract_single_feature_from_dataframe(
                dataset=setup_panda_dataframe,
                feature_name="bodyy_vel_ddisturption",
                data_container_type=StatePose2D,
            )

    def test_no_existing_feature_dimension(self, setup_panda_dataframe):
        with pytest.raises(ValueError):
            dtd.extract_single_feature_from_dataframe(
                dataset=setup_panda_dataframe,
                feature_name="body_vel_disturption",
                data_container_type=CmdStandard,
            )

    def test_missing_timestep(self, setup_panda_dataframe):
        col_label = "body_vel_disturption"
        df_missing = setup_panda_dataframe.drop(f"{col_label}_x_9", axis=1)

        with pytest.raises(ValueError):
            dtd.extract_single_feature_from_dataframe(
                dataset=df_missing,
                feature_name=col_label,
                data_container_type=StatePose2D,
            )


class TestExtractDataframeMultifeature:
    @pytest.fixture(scope="function")
    def setup_configuration_dict_OK(self):
        feature_config = {
            "icp_interpolated": StatePose2D,
            "idd_vel": StatePose2D,
            "icp": ("StatePose3D", "x", "y", "z", "roll", "pitch", "yaw"),
        }
        return feature_config

    def test_aggregate_multiple_features_from_dataframe_working(
        self, setup_panda_dataframe, setup_configuration_dict_OK
    ):
        feats = dtd.aggregate_multiple_features_from_dataframe(
            dataset_frame=setup_panda_dataframe,
            dataset_info="marmotte-ga_hard_snow_25_01_a",
            features_config=setup_configuration_dict_OK,
        )

        assert isinstance(
            feats.icp_interpolated,
            StatePose2D,
        )
        assert feats.icp_interpolated.feature_name == "icp_interpolated"
        assert feats.icp_interpolated.get_dimension_names() == ("x", "y", "yaw")

        assert isinstance(
            feats.idd_vel,
            StatePose2D,
        )
        assert feats.idd_vel.feature_name == "idd_vel"
        assert feats.idd_vel.get_dimension_names() == ("x", "y", "yaw")

        assert isinstance(feats.icp, atd.AbstractTrajectoryDataclass)
        assert feats.icp.feature_name == "icp"
        assert feats.icp.get_dimension_names() == (
            "x",
            "y",
            "z",
            "roll",
            "pitch",
            "yaw",
        )

        # marmotte / ga_hard_snow_25_01_a
        print(feats)

    def test_aggregate_multiple_features_from_dataframe_misspecification(
        self, setup_panda_dataframe, setup_configuration_dict_OK
    ):
        setup_configuration_dict_bad = setup_configuration_dict_OK.copy()
        setup_configuration_dict_bad["icp"] = ("StatePose3D",)

        with pytest.raises(KeyError):
            feats = dtd.aggregate_multiple_features_from_dataframe(
                dataset_frame=setup_panda_dataframe,
                dataset_info="marmotte-ga_hard_snow_25_01_a",
                features_config=setup_configuration_dict_bad,
            )

            print(feats)

    @pytest.mark.skip(reason="Feature nice to have. Not implemented yet")
    def test_aggregate_multiple_features_from_dataframe_single_dimension_feature_no_index(
        self, setup_panda_dataframe
    ):
        feats = dtd.aggregate_multiple_features_from_dataframe(
            dataset_frame=setup_panda_dataframe,
            dataset_info="marmotte-ga_hard_snow_25_01_a",
            features_config={"calib": ("calib_step", "step")},
        )

        print(feats)
