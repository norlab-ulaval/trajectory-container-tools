# coding=utf-8
"""
Tests for CSV to TCT extractor functionality.
"""
import pytest
from pathlib import Path

import numpy as np
import pandas as pd

from trajectory_container_tools.dataclasses.panda_dataframe_feature_dataclass import (
    StatePose2DStamped,
)
from trajectory_container_tools.extractor.csv_to_tct import (
    from_csv,
    extract_csv_feature,
)
from trajectory_container_tools.dataclasses.primitive_dataclass import (
    Point2D,
    Pose2D,
    Velocity2D,
)


# =============================================================================
# Fixtures - Reusable test data
# =============================================================================


@pytest.fixture
def basic_csv_data():
    """Standard CSV data with pose information (6 rows) - suitable for most tests"""
    return pd.DataFrame(
        {
            "t": [1, 2, 3, 4, 5, 6],
            "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
            "y": [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],
            "yaw": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
        }
    )


@pytest.fixture
def multi_feature_csv_data():
    """CSV data with multiple features (pose and velocity)"""
    return pd.DataFrame(
        {
            "t": [1, 2, 3],
            "x": [1.0, 2.0, 3.0],
            "y": [0.5, 1.5, 2.5],
            "yaw": [0.0, 0.1, 0.2],
            "vx": [1.0, 1.0, 1.0],
            "vy": [0.0, 0.0, 0.0],
        }
    )


@pytest.fixture
def csv_data_missing_column():
    """CSV data missing required feature column (yaw) - for error testing"""
    return pd.DataFrame(
        {
            "t": [1, 2, 3],
            "x": [1.0, 2.0, 3.0],
            "y": [0.5, 1.5, 2.5],
            # Missing 'yaw' column
        }
    )


@pytest.fixture
def csv_data_unordered_timestamps():
    """CSV data with unordered timestamps - for error testing"""
    return pd.DataFrame(
        {
            "t": [1, 3, 2, 5, 4],  # Deliberately unordered
            "x": [1.0, 3.0, 2.0, 5.0, 4.0],
            "y": [0.5, 2.5, 1.5, 4.5, 3.5],
            "yaw": [0.0, 0.2, 0.1, 0.4, 0.3],
        }
    )


@pytest.fixture
def csv_data_float_timestamps():
    """CSV data with float timestamps (e.g., seconds with decimals)"""
    return pd.DataFrame(
        {
            "t": [1000.0, 1000.5, 1001.0, 1001.5, 1002.0],
            "x": [1.0, 1.5, 2.0, 2.5, 3.0],
            "y": [0.5, 1.0, 1.5, 2.0, 2.5],
            "yaw": [0.0, 0.05, 0.1, 0.15, 0.2],
        }
    )


# =============================================================================
# Tests for extract_csv_feature
# =============================================================================


class TestExtractCsvFeature:
    """Test suite for extract_csv_feature function"""

    def test_extract_simple_feature(self, basic_csv_data):
        """Test extracting a simple (flat) feature from CSV"""
        # Extract feature
        feature = extract_csv_feature(
            csv_dataframe=basic_csv_data,
            feature_name="position",
            data_container_type=StatePose2DStamped,
            timestamp_column="t",
        )

        # Verify
        assert feature is not None
        assert hasattr(feature, "x")
        assert hasattr(feature, "y")
        assert hasattr(feature, "timestamps")
        assert len(feature.x) == len(basic_csv_data)
        assert len(feature.y) == len(basic_csv_data)
        assert len(feature.timestamps) == len(basic_csv_data)
        assert np.allclose(feature.x, basic_csv_data["x"].values)
        assert np.allclose(feature.y, basic_csv_data["y"].values)
        assert np.allclose(feature.yaw, basic_csv_data["yaw"].values)

    def test_extract_with_time_filtering(self, basic_csv_data):
        """Test extracting CSV data with time range filtering"""
        start_time = 2  # nanoseconds
        stop_time = 4  # nanoseconds

        # Extract with time filtering
        feature = extract_csv_feature(
            csv_dataframe=basic_csv_data,
            feature_name="position",
            data_container_type=StatePose2DStamped,
            timestamp_column="t",
            start=start_time,
            stop=stop_time,
        )

        # Filter the expected data
        filtered_data = basic_csv_data[
            (basic_csv_data["t"] >= start_time) & (basic_csv_data["t"] <= stop_time)
        ]

        # Verify filtered data
        assert len(feature.x) == len(filtered_data)
        assert feature.timestamps.stamps[0] == start_time
        assert feature.timestamps.stamps[-1] == stop_time

    def test_missing_column_error(self, csv_data_missing_column):
        """Test that missing feature column raises appropriate error"""
        # Should raise KeyError for missing column
        with pytest.raises(KeyError):
            extract_csv_feature(
                csv_dataframe=csv_data_missing_column,
                feature_name="position",
                data_container_type=StatePose2DStamped,
                timestamp_column="t",
            )

    def test_extract_with_start_time_only(self, basic_csv_data):
        """Test extracting CSV data with only start time filter"""
        start_time = 3  # nanoseconds

        # Extract with start time only
        feature = extract_csv_feature(
            csv_dataframe=basic_csv_data,
            feature_name="position",
            data_container_type=StatePose2DStamped,
            timestamp_column="t",
            start=start_time,
        )

        # Filter the expected data
        filtered_data = basic_csv_data[basic_csv_data["t"] >= start_time]

        # Verify filtered data
        assert len(feature.x) == len(filtered_data)
        assert feature.timestamps.stamps[0] == start_time

    def test_extract_with_stop_time_only(self, basic_csv_data):
        """Test extracting CSV data with only stop time filter"""
        stop_time = 4  # nanoseconds

        # Extract with stop time only
        feature = extract_csv_feature(
            csv_dataframe=basic_csv_data,
            feature_name="position",
            data_container_type=StatePose2DStamped,
            timestamp_column="t",
            stop=stop_time,
        )

        # Filter the expected data
        filtered_data = basic_csv_data[basic_csv_data["t"] <= stop_time]

        # Verify filtered data
        assert len(feature.x) == len(filtered_data)
        assert feature.timestamps.stamps[-1] == stop_time

    def test_empty_data_after_filtering_error(self, basic_csv_data):
        """Test that filtering resulting in empty data raises appropriate error"""
        # Should raise ValueError for empty data after filtering
        with pytest.raises(ValueError):
            extract_csv_feature(
                csv_dataframe=basic_csv_data,
                feature_name="position",
                data_container_type=StatePose2DStamped,
                timestamp_column="t",
                start=100,  # Beyond data range
                stop=200,
            )

    def test_invalid_data_container_type_error(self, basic_csv_data):
        """Test that invalid data_container_type raises appropriate error"""
        # Should raise ValueError for non-BaseTrajectoryFeature type
        with pytest.raises(ValueError):
            extract_csv_feature(
                csv_dataframe=basic_csv_data,
                feature_name="position",
                data_container_type=str,  # Not a valid type
                timestamp_column="t",
            )

    def test_instantiated_data_container_type_error(self, basic_csv_data):
        """Test that passing instantiated class raises appropriate error"""
        # Create a simple instance to pass (this will fail type checking in the function)
        # We need to use a valid instantiation or mock
        # Note: This test verifies the TypeError catch block in extract_csv_feature
        with pytest.raises(AttributeError):
            # Pass an instance instead of a class by using an integer (not a class)
            extract_csv_feature(
                csv_dataframe=basic_csv_data,
                feature_name="position",
                data_container_type=123,  # Not a class at all
                timestamp_column="t",
            )

    def test_unordered_timestamps_error(self, csv_data_unordered_timestamps):
        """Test that unordered timestamps raise an error by default"""
        # Should raise TimestampCausalOrderingError for unordered timestamps
        from trajectory_container_tools.temporal.timestamps import (
            TimestampCausalOrderingError,
        )

        with pytest.raises(TimestampCausalOrderingError):
            extract_csv_feature(
                csv_dataframe=csv_data_unordered_timestamps,
                feature_name="position",
                data_container_type=StatePose2DStamped,
                timestamp_column="t",
                fail_causal_ordering_violation=True,  # Default behavior
            )


# =============================================================================
# Tests for from_csv
# =============================================================================


class TestFromCsv:
    """Test suite for from_csv function"""

    def test_from_csv_with_multiple_features(self, tmp_path, multi_feature_csv_data):
        """Test extracting multiple features from CSV into a feature bag"""
        # Create CSV file
        csv_path = tmp_path / "test_multi.csv"
        multi_feature_csv_data.to_csv(csv_path, index=False)

        # Define features config
        features_config = {
            "pose": StatePose2DStamped,
            "velocity": ("Vel2DFeature", "vx", "vy"),
        }

        # Extract features
        bag = from_csv(
            csv_path=csv_path,
            dataset_info="Test dataset",
            features_config=features_config,
            timestamp_column="t",
        )

        # Verify
        expected_length = len(multi_feature_csv_data)
        assert bag is not None
        assert hasattr(bag, "pose")
        assert hasattr(bag, "velocity")
        assert hasattr(bag, "bag_timestamps")
        assert len(bag.pose.x) == expected_length
        assert len(bag.velocity.vx) == expected_length
        assert len(bag.bag_timestamps) == expected_length

    def test_missing_timestamp_column_error(self, tmp_path, csv_data_missing_column):
        """Test that missing timestamp column raises appropriate error"""
        # Remove timestamp column to create error condition
        csv_data_no_ts = csv_data_missing_column.drop(columns=["t"])

        # Create CSV file
        csv_path = tmp_path / "test_missing_time.csv"
        csv_data_no_ts.to_csv(csv_path, index=False)

        # Should raise ValueError for missing timestamp column
        with pytest.raises(ValueError):
            from_csv(
                csv_path=csv_path,
                dataset_info="Test",
                features_config={"pos": StatePose2DStamped},
                timestamp_column="t",
            )

    def test_from_csv_single_feature(self, tmp_path, basic_csv_data):
        """Test extracting a single feature from CSV"""
        # Create CSV file
        csv_path = tmp_path / "test_single.csv"
        basic_csv_data.to_csv(csv_path, index=False)

        # Extract single feature
        bag = from_csv(
            csv_path=csv_path,
            dataset_info="Single feature test",
            features_config={"pose": StatePose2DStamped},
            timestamp_column="t",
        )

        # Verify
        expected_length = len(basic_csv_data)
        assert bag is not None
        assert hasattr(bag, "pose")
        assert len(bag.pose.x) == expected_length
        assert len(bag.bag_timestamps) == expected_length

    def test_from_csv_with_tuple_feature_spec(self, tmp_path, multi_feature_csv_data):
        """Test extracting features using tuple-based feature specification"""
        # Create CSV file
        csv_path = tmp_path / "test_tuple_spec.csv"
        multi_feature_csv_data.to_csv(csv_path, index=False)

        # Define features with tuple specification
        features_config = {
            "velocity": ("Velocity2DFeature", "vx", "vy"),
            "position": ("Position2DFeature", "x", "y"),
        }

        # Extract features
        bag = from_csv(
            csv_path=csv_path,
            dataset_info="Tuple spec test",
            features_config=features_config,
            timestamp_column="t",
        )

        # Verify
        expected_length = len(multi_feature_csv_data)
        assert bag is not None
        assert hasattr(bag, "velocity")
        assert hasattr(bag, "position")
        assert len(bag.velocity.vx) == expected_length
        assert len(bag.position.x) == expected_length

    def test_from_csv_with_time_filtering(self, tmp_path, basic_csv_data):
        """Test from_csv with time range filtering"""
        # Create CSV file
        csv_path = tmp_path / "test_time_filter.csv"
        basic_csv_data.to_csv(csv_path, index=False)

        start_time = 2  # nanoseconds
        stop_time = 5  # nanoseconds

        # Extract with time filtering
        bag = from_csv(
            csv_path=csv_path,
            dataset_info="Time filter test",
            features_config={"pose": StatePose2DStamped},
            timestamp_column="t",
            start=start_time,
            stop=stop_time,
        )

        # Filter the expected data
        filtered_data = basic_csv_data[
            (basic_csv_data["t"] >= start_time) & (basic_csv_data["t"] <= stop_time)
        ]

        # Verify
        assert bag is not None
        assert len(bag.pose.x) == len(filtered_data)
        assert bag.bag_timestamps.stamps[0] == start_time
        assert bag.bag_timestamps.stamps[-1] == stop_time

    def test_from_csv_with_dataset_info(self, tmp_path, basic_csv_data):
        """Test that dataset_info is properly stored"""
        # Create CSV file
        csv_path = tmp_path / "test_info.csv"
        basic_csv_data.to_csv(csv_path, index=False)

        dataset_info = "Test dataset with metadata"

        # Extract features
        bag = from_csv(
            csv_path=csv_path,
            dataset_info=dataset_info,
            features_config={"pose": StatePose2DStamped},
            timestamp_column="t",
        )

        # Verify dataset info
        assert bag.dataset_info == dataset_info

    def test_from_csv_mixed_feature_specs(self, tmp_path, multi_feature_csv_data):
        """Test mixing class-based and tuple-based feature specifications"""
        # Create CSV file
        csv_path = tmp_path / "test_mixed.csv"
        multi_feature_csv_data.to_csv(csv_path, index=False)

        # Mix class and tuple specifications
        features_config = {
            "pose": StatePose2DStamped,  # Class-based
            "velocity": ("Vel2D", "vx", "vy"),  # Tuple-based
        }

        # Extract features
        bag = from_csv(
            csv_path=csv_path,
            dataset_info="Mixed spec test",
            features_config=features_config,
            timestamp_column="t",
        )

        # Verify
        expected_length = len(multi_feature_csv_data)
        assert bag is not None
        assert hasattr(bag, "pose")
        assert hasattr(bag, "velocity")
        assert len(bag.pose.x) == expected_length
        assert len(bag.velocity.vx) == expected_length
